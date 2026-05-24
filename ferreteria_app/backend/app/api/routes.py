from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import timedelta

from app.db.database import get_db, init_db
from app.models.models import User, UserRole
from app.schemas.schemas import (
    UserCreate, UserResponse, UserUpdate,
    ProductCreate, ProductResponse, ProductUpdate,
    CustomerCreate, CustomerResponse, CustomerUpdate,
    InvoiceCreate, InvoiceResponse, InvoiceUpdate,
    ExchangeRateResponse, Token, AuditLogResponse
)
from app.services.crud_services import (
    UserService, ProductService, CustomerService,
    InvoiceService, ExchangeRateService, AuditLogService
)
from app.services.bcv_service import bcv_service
from app.core.security import verify_password, get_password_hash
from app.core.config import settings
from jose import JWTError, jwt
from pydantic import BaseModel


router = APIRouter()


# Dependency para obtener el usuario actual
async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    # En producción, validar token JWT del header
    # Por ahora, retornamos None para permitir desarrollo
    return None


# ==================== AUTH ROUTES ====================

@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Registrar un nuevo usuario"""
    existing_user = await UserService.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya existe"
        )
    
    db_user = await UserService.create_user(db, user_data)
    
    # Log de auditoría
    await AuditLogService.log_action(
        db=db,
        user_id=db_user.id,
        action="CREATE",
        table_name="users",
        record_id=db_user.id,
        new_values={"username": db_user.username, "role": db_user.role.value}
    )
    
    return db_user


@router.post("/auth/login", response_model=Token)
async def login(username: str, password: str, db: AsyncSession = Depends(get_db)):
    """Iniciar sesión y obtener token"""
    user = await UserService.get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    
    # Crear token JWT
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": user.username, "role": user.role.value}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return {"access_token": encoded_jwt, "token_type": "bearer"}


# ==================== USER ROUTES ====================

@router.get("/users", response_model=List[UserResponse])
async def get_users(db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100):
    """Obtener lista de usuarios"""
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Obtener información del usuario actual"""
    if not current_user:
        raise HTTPException(status_code=401, detail="No autenticado")
    return current_user


# ==================== PRODUCT ROUTES ====================

@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_db)):
    """Crear un nuevo producto"""
    existing = await ProductService.get_product_by_sku(db, product.sku)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El SKU ya existe"
        )
    
    db_product = await ProductService.create_product(db, product)
    
    await AuditLogService.log_action(
        db=db,
        user_id=None,
        action="CREATE",
        table_name="products",
        record_id=db_product.id,
        new_values={"sku": db_product.sku, "name": db_product.name}
    )
    
    return db_product


@router.get("/products", response_model=List[ProductResponse])
async def get_products(db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100):
    """Obtener lista de productos"""
    return await ProductService.get_all_products(db, skip, limit)


@router.get("/products/low-stock", response_model=List[ProductResponse])
async def get_low_stock_products(db: AsyncSession = Depends(get_db)):
    """Obtener productos con stock bajo"""
    return await ProductService.get_low_stock_products(db)


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """Obtener producto por ID"""
    product = await ProductService.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, product_update: ProductUpdate, db: AsyncSession = Depends(get_db)):
    """Actualizar producto"""
    db_product = await ProductService.update_product(db, product_id, product_update)
    if not db_product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    await AuditLogService.log_action(
        db=db,
        user_id=None,
        action="UPDATE",
        table_name="products",
        record_id=product_id,
        old_values={},
        new_values=product_update.model_dump(exclude_unset=True)
    )
    
    return db_product


# ==================== CUSTOMER ROUTES ====================

@router.post("/customers", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(customer: CustomerCreate, db: AsyncSession = Depends(get_db)):
    """Crear un nuevo cliente"""
    existing = await CustomerService.get_customer_by_rif(db, customer.rif)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El RIF ya está registrado"
        )
    
    db_customer = await CustomerService.create_customer(db, customer)
    
    await AuditLogService.log_action(
        db=db,
        user_id=None,
        action="CREATE",
        table_name="customers",
        record_id=db_customer.id,
        new_values={"rif": db_customer.rif, "name": db_customer.name}
    )
    
    return db_customer


@router.get("/customers", response_model=List[CustomerResponse])
async def get_customers(db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100):
    """Obtener lista de clientes"""
    return await CustomerService.get_all_customers(db, skip, limit)


@router.get("/customers/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: int, db: AsyncSession = Depends(get_db)):
    """Obtener cliente por ID"""
    customer = await CustomerService.get_customer_by_id(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return customer


# ==================== INVOICE ROUTES ====================

@router.post("/invoices", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(invoice: InvoiceCreate, db: AsyncSession = Depends(get_db)):
    """Crear una nueva factura"""
    # Obtener tasa de cambio actual
    current_rate = await ExchangeRateService.get_current_rate(db)
    if not current_rate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No hay tasa de cambio disponible. Actualice la tasa del BCV."
        )
    
    # Verificar que el cliente existe
    customer = await CustomerService.get_customer_by_id(db, invoice.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Determinar si aplica IGTF (pagos en divisas)
    apply_igtf = invoice.apply_igtf or invoice.payment_method.lower() in ['divisas', 'efectivo_usd']
    
    # Crear datos actualizados
    invoice_data = invoice.model_copy(update={"apply_igtf": apply_igtf})
    
    db_invoice = await InvoiceService.create_invoice(
        db=db,
        invoice_data=invoice_data,
        user_id=1,  # En producción, usar el usuario autenticado
        exchange_rate=current_rate.rate
    )
    
    await AuditLogService.log_action(
        db=db,
        user_id=None,
        action="CREATE",
        table_name="invoices",
        record_id=db_invoice.id,
        new_values={"invoice_number": db_invoice.invoice_number, "total_usd": db_invoice.total_usd}
    )
    
    return db_invoice


@router.get("/invoices", response_model=List[InvoiceResponse])
async def get_invoices(db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100):
    """Obtener lista de facturas"""
    return await InvoiceService.get_all_invoices(db, skip, limit)


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(invoice_id: int, db: AsyncSession = Depends(get_db)):
    """Obtener factura por ID"""
    invoice = await InvoiceService.get_invoice_by_id(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return invoice


# ==================== EXCHANGE RATE ROUTES ====================

@router.get("/exchange-rate/current", response_model=ExchangeRateResponse)
async def get_current_exchange_rate(db: AsyncSession = Depends(get_db)):
    """Obtener tasa de cambio actual"""
    rate = await ExchangeRateService.get_current_rate(db)
    if not rate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay tasa de cambio registrada"
        )
    return rate


@router.post("/exchange-rate/update")
async def update_exchange_rate(db: AsyncSession = Depends(get_db)):
    """
    Actualizar tasa de cambio desde el BCV.
    Intenta obtener la tasa automáticamente con reintentos.
    """
    rate_value, message, is_fallback = await bcv_service.get_rate_with_fallback()
    
    # Guardar la tasa en la base de datos
    db_rate = await ExchangeRateService.create_exchange_rate(
        db=db,
        rate=rate_value,
        source="BCV" if not is_fallback else "BCV_FALLBACK"
    )
    
    return {
        "rate": rate_value,
        "message": message,
        "is_fallback": is_fallback,
        "fetched_at": db_rate.fetched_at
    }


@router.get("/system/init")
async def initialize_system(db: AsyncSession = Depends(get_db)):
    """
    Inicializar el sistema:
    1. Intentar obtener tasa del BCV con 3 reintentos
    2. Mostrar alerta si falla
    3. Retornar estado del sistema
    """
    rate_value, message, is_fallback = await bcv_service.get_rate_with_fallback()
    
    # Guardar la tasa
    db_rate = await ExchangeRateService.create_exchange_rate(
        db=db,
        rate=rate_value,
        source="BCV" if not is_fallback else "BCV_FALLBACK"
    )
    
    system_status = {
        "initialized": True,
        "exchange_rate": rate_value,
        "base_currency": settings.BASE_CURRENCY,
        "bcv_message": message,
        "using_fallback": is_fallback,
        "alert": is_fallback  # Si es fallback, mostrar alerta al usuario
    }
    
    return system_status


# ==================== AUDIT LOG ROUTES ====================

@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def get_audit_logs(db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100):
    """Obtener logs de auditoría"""
    result = await db.execute(select(AuditLog).offset(skip).limit(limit))
    return result.scalars().all()


# Import necessary for select
from sqlalchemy import select
from app.models.models import AuditLog

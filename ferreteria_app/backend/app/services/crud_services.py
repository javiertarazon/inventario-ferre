from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional, List
from datetime import datetime
import json

from app.models.models import (
    User, Product, Customer, Invoice, InvoiceItem, 
    ExchangeRate, AuditLog, UserRole, InvoiceStatus
)
from app.schemas.schemas import (
    UserCreate, UserUpdate, ProductCreate, ProductUpdate,
    CustomerCreate, CustomerUpdate, InvoiceCreate, InvoiceItemCreate
)
from app.core.security import get_password_hash
from app.core.config import settings


class UserService:
    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            role=user_data.role,
            hashed_password=hashed_password
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, user_data: UserUpdate) -> Optional[User]:
        db_user = await UserService.get_user_by_id(db, user_id)
        if not db_user:
            return None
        
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        await db.commit()
        await db.refresh(db_user)
        return db_user


class ProductService:
    @staticmethod
    async def create_product(db: AsyncSession, product_data: ProductCreate) -> Product:
        db_product = Product(**product_data.model_dump())
        db.add(db_product)
        await db.commit()
        await db.refresh(db_product)
        return db_product
    
    @staticmethod
    async def get_product_by_id(db: AsyncSession, product_id: int) -> Optional[Product]:
        result = await db.execute(select(Product).where(Product.id == product_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_product_by_sku(db: AsyncSession, sku: str) -> Optional[Product]:
        result = await db.execute(select(Product).where(Product.sku == sku))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all_products(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Product]:
        result = await db.execute(select(Product).offset(skip).limit(limit))
        return result.scalars().all()
    
    @staticmethod
    async def update_product(db: AsyncSession, product_id: int, product_data: ProductUpdate) -> Optional[Product]:
        db_product = await ProductService.get_product_by_id(db, product_id)
        if not db_product:
            return None
        
        update_data = product_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_product, field, value)
        
        await db.commit()
        await db.refresh(db_product)
        return db_product
    
    @staticmethod
    async def get_low_stock_products(db: AsyncSession) -> List[Product]:
        result = await db.execute(
            select(Product).where(
                (Product.stock_quantity <= Product.min_stock) & 
                (Product.is_active == True)
            )
        )
        return result.scalars().all()


class CustomerService:
    @staticmethod
    async def create_customer(db: AsyncSession, customer_data: CustomerCreate) -> Customer:
        db_customer = Customer(**customer_data.model_dump())
        db.add(db_customer)
        await db.commit()
        await db.refresh(db_customer)
        return db_customer
    
    @staticmethod
    async def get_customer_by_id(db: AsyncSession, customer_id: int) -> Optional[Customer]:
        result = await db.execute(select(Customer).where(Customer.id == customer_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_customer_by_rif(db: AsyncSession, rif: str) -> Optional[Customer]:
        result = await db.execute(select(Customer).where(Customer.rif == rif.upper()))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all_customers(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Customer]:
        result = await db.execute(select(Customer).offset(skip).limit(limit))
        return result.scalars().all()
    
    @staticmethod
    async def update_customer(db: AsyncSession, customer_id: int, customer_data: CustomerUpdate) -> Optional[Customer]:
        db_customer = await CustomerService.get_customer_by_id(db, customer_id)
        if not db_customer:
            return None
        
        update_data = customer_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_customer, field, value)
        
        await db.commit()
        await db.refresh(db_customer)
        return db_customer


class ExchangeRateService:
    @staticmethod
    async def get_current_rate(db: AsyncSession) -> Optional[ExchangeRate]:
        result = await db.execute(
            select(ExchangeRate)
            .where(ExchangeRate.is_active == True)
            .order_by(desc(ExchangeRate.fetched_at))
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_exchange_rate(db: AsyncSession, rate: float, source: str = "BCV") -> ExchangeRate:
        # Desactivar tasas anteriores
        await db.execute(
            update(ExchangeRate)
            .values(is_active=False)
        )
        
        db_rate = ExchangeRate(rate=rate, source=source)
        db.add(db_rate)
        await db.commit()
        await db.refresh(db_rate)
        return db_rate


class InvoiceService:
    @staticmethod
    async def create_invoice(
        db: AsyncSession, 
        invoice_data: InvoiceCreate, 
        user_id: int, 
        exchange_rate: float
    ) -> Invoice:
        # Generar número de factura
        result = await db.execute(
            select(Invoice)
            .order_by(desc(Invoice.id))
            .limit(1)
        )
        last_invoice = result.scalar_one_or_none()
        
        if last_invoice:
            next_number = int(last_invoice.invoice_number.split('-')[-1]) + 1
        else:
            next_number = 1
        
        invoice_number = f"FAC-{next_number:06d}"
        
        # Calcular totales
        subtotal_usd = 0.0
        iva_amount_usd = 0.0
        
        for item_data in invoice_data.items:
            subtotal = item_data.quantity * item_data.unit_price_usd
            iva = subtotal * item_data.iva_rate
            subtotal_usd += subtotal
            iva_amount_usd += iva
        
        # Calcular IGTF si aplica (3% para pagos en divisas)
        igtf_amount_usd = 0.0
        if invoice_data.apply_igtf:
            igtf_amount_usd = subtotal_usd * settings.IGTF_RATE
        
        total_usd = subtotal_usd + iva_amount_usd + igtf_amount_usd
        total_vef = total_usd * exchange_rate
        
        # Crear factura
        db_invoice = Invoice(
            invoice_number=invoice_number,
            customer_id=invoice_data.customer_id,
            user_id=user_id,
            subtotal_usd=subtotal_usd,
            iva_amount_usd=iva_amount_usd,
            igtf_amount_usd=igtf_amount_usd,
            total_usd=total_usd,
            exchange_rate=exchange_rate,
            total_vef=total_vef,
            payment_method=invoice_data.payment_method,
            apply_igtf=invoice_data.apply_igtf,
            notes=invoice_data.notes,
            status=InvoiceStatus.COMPLETED
        )
        
        db.add(db_invoice)
        await db.flush()  # Obtener ID de la factura
        
        # Crear items de la factura y actualizar stock
        for item_data in invoice_data.items:
            db_item = InvoiceItem(
                invoice_id=db_invoice.id,
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                unit_price_usd=item_data.unit_price_usd,
                subtotal_usd=item_data.quantity * item_data.unit_price_usd,
                iva_rate=item_data.iva_rate,
                iva_amount_usd=item_data.quantity * item_data.unit_price_usd * item_data.iva_rate,
                total_usd=(item_data.quantity * item_data.unit_price_usd) * (1 + item_data.iva_rate)
            )
            db.add(db_item)
            
            # Actualizar stock del producto
            product = await ProductService.get_product_by_id(db, item_data.product_id)
            if product:
                product.stock_quantity -= item_data.quantity
        
        await db.commit()
        await db.refresh(db_invoice)
        
        # Cargar items en la factura retornada
        result = await db.execute(
            select(InvoiceItem).where(InvoiceItem.invoice_id == db_invoice.id)
        )
        db_invoice.items = result.scalars().all()
        
        return db_invoice
    
    @staticmethod
    async def get_invoice_by_id(db: AsyncSession, invoice_id: int) -> Optional[Invoice]:
        result = await db.execute(
            select(Invoice)
            .where(Invoice.id == invoice_id)
        )
        invoice = result.scalar_one_or_none()
        
        if invoice:
            items_result = await db.execute(
                select(InvoiceItem).where(InvoiceItem.invoice_id == invoice_id)
            )
            invoice.items = items_result.scalars().all()
        
        return invoice
    
    @staticmethod
    async def get_invoice_by_number(db: AsyncSession, invoice_number: str) -> Optional[Invoice]:
        result = await db.execute(
            select(Invoice)
            .where(Invoice.invoice_number == invoice_number)
        )
        invoice = result.scalar_one_or_none()
        
        if invoice:
            items_result = await db.execute(
                select(InvoiceItem).where(InvoiceItem.invoice_id == invoice.id)
            )
            invoice.items = items_result.scalars().all()
        
        return invoice
    
    @staticmethod
    async def get_all_invoices(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Invoice]:
        result = await db.execute(
            select(Invoice)
            .order_by(desc(Invoice.created_at))
            .offset(skip)
            .limit(limit)
        )
        invoices = result.scalars().all()
        
        # Cargar items para cada factura
        for invoice in invoices:
            items_result = await db.execute(
                select(InvoiceItem).where(InvoiceItem.invoice_id == invoice.id)
            )
            invoice.items = items_result.scalars().all()
        
        return invoices


class AuditLogService:
    @staticmethod
    async def log_action(
        db: AsyncSession,
        user_id: Optional[int],
        action: str,
        table_name: str,
        record_id: Optional[int] = None,
        old_values: Optional[dict] = None,
        new_values: Optional[dict] = None,
        ip_address: Optional[str] = None
    ):
        db_log = AuditLog(
            user_id=user_id,
            action=action,
            table_name=table_name,
            record_id=record_id,
            old_values=json.dumps(old_values) if old_values else None,
            new_values=json.dumps(new_values) if new_values else None,
            ip_address=ip_address
        )
        db.add(db_log)
        await db.commit()


# Import needed for ExchangeRateService
from sqlalchemy import update

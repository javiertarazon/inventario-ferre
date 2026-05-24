from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List
from datetime import datetime
import logging

from app.models import User, Product, Customer, Sale, SaleItem, InventoryMovement, AuditLog, ExchangeRate, UserRole
from app.schemas import (
    UserCreate, UserUpdate,
    ProductCreate, ProductUpdate,
    CustomerCreate, CustomerUpdate,
    SaleCreate,
    InventoryMovementCreate
)
from app.core.security import get_password_hash
from app.core.config import settings


logger = logging.getLogger(__name__)


class UserService:
    
    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        hashed_password = get_password_hash(user_data.password)
        
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            role=user_data.role,
            is_active=True
        )
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        
        # Log de auditoría
        await AuditLogService.log_action(
            db=db,
            user_id=db_user.id,
            action="CREATE",
            entity="user",
            entity_id=db_user.id,
            new_values=f"Username: {db_user.username}, Role: {db_user.role}"
        )
        
        return db_user
    
    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
        result = await db.execute(select(User).filter(User.username == username))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        result = await db.execute(select(User).filter(User.id == user_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, user_data: UserUpdate) -> Optional[User]:
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            return None
        
        update_data = user_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await db.commit()
        await db.refresh(user)
        
        return user


class ProductService:
    
    @staticmethod
    async def create_product(db: AsyncSession, product_data: ProductCreate, exchange_rate: float) -> Product:
        # Verificar que el código no exista
        existing = await ProductService.get_product_by_code(db, product_data.code)
        if existing:
            raise ValueError(f"El producto con código {product_data.code} ya existe")
        
        price_bsf = product_data.price_usd * exchange_rate
        
        db_product = Product(
            code=product_data.code,
            name=product_data.name,
            description=product_data.description,
            category=product_data.category,
            brand=product_data.brand,
            price_usd=product_data.price_usd,
            price_bsf=price_bsf,
            stock_quantity=product_data.stock_quantity,
            min_stock=product_data.min_stock,
            unit_of_measure=product_data.unit_of_measure,
            iva_rate=product_data.iva_rate,
            is_exempt=product_data.is_exempt,
            is_active=True
        )
        
        db.add(db_product)
        await db.commit()
        await db.refresh(db_product)
        
        # Log de auditoría
        await AuditLogService.log_action(
            db=db,
            action="CREATE",
            entity="product",
            entity_id=db_product.id,
            new_values=f"Código: {db_product.code}, Nombre: {db_product.name}"
        )
        
        return db_product
    
    @staticmethod
    async def get_product_by_code(db: AsyncSession, code: str) -> Optional[Product]:
        result = await db.execute(select(Product).filter(Product.code == code))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_product_by_id(db: AsyncSession, product_id: int) -> Optional[Product]:
        result = await db.execute(select(Product).filter(Product.id == product_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_products(
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100,
        category: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Product]:
        query = select(Product).filter(Product.is_active == True)
        
        if category:
            query = query.filter(Product.category == category)
        
        if search:
            query = query.filter(
                (Product.name.ilike(f"%{search}%")) | 
                (Product.code.ilike(f"%{search}%"))
            )
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def update_product(
        db: AsyncSession, 
        product_id: int, 
        product_data: ProductUpdate,
        exchange_rate: Optional[float] = None
    ) -> Optional[Product]:
        product = await ProductService.get_product_by_id(db, product_id)
        if not product:
            return None
        
        update_data = product_data.model_dump(exclude_unset=True)
        
        # Si se actualiza el precio en USD y tenemos tasa, actualizar BSF
        if 'price_usd' in update_data and exchange_rate:
            update_data['price_bsf'] = update_data['price_usd'] * exchange_rate
        
        for field, value in update_data.items():
            setattr(product, field, value)
        
        await db.commit()
        await db.refresh(product)
        
        return product
    
    @staticmethod
    async def update_prices_with_new_rate(db: AsyncSession, exchange_rate: float) -> int:
        """Actualiza todos los precios en BSF con una nueva tasa de cambio"""
        products = await ProductService.get_products(db, limit=10000)
        updated_count = 0
        
        for product in products:
            product.price_bsf = product.price_usd * exchange_rate
            updated_count += 1
        
        await db.commit()
        return updated_count


class CustomerService:
    
    @staticmethod
    async def create_customer(db: AsyncSession, customer_data: CustomerCreate) -> Customer:
        # Verificar que el RIF no exista
        existing = await CustomerService.get_customer_by_rif(db, customer_data.rif)
        if existing:
            raise ValueError(f"El cliente con RIF {customer_data.rif} ya existe")
        
        db_customer = Customer(
            rif=customer_data.rif.upper(),
            name=customer_data.name,
            email=customer_data.email,
            phone=customer_data.phone,
            address=customer_data.address,
            customer_type=customer_data.customer_type,
            is_active=True
        )
        
        db.add(db_customer)
        await db.commit()
        await db.refresh(db_customer)
        
        return db_customer
    
    @staticmethod
    async def get_customer_by_rif(db: AsyncSession, rif: str) -> Optional[Customer]:
        result = await db.execute(select(Customer).filter(Customer.rif == rif.upper()))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_customer_by_id(db: AsyncSession, customer_id: int) -> Optional[Customer]:
        result = await db.execute(select(Customer).filter(Customer.id == customer_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_customers(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Customer]:
        query = select(Customer).filter(Customer.is_active == True).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()


class SaleService:
    
    @staticmethod
    async def create_sale(
        db: AsyncSession, 
        sale_data: SaleCreate, 
        exchange_rate: float,
        user_id: int
    ) -> Sale:
        # Generar número de factura
        invoice_number = await SaleService._generate_invoice_number(db)
        
        # Obtener cliente
        customer = await CustomerService.get_customer_by_id(db, sale_data.customer_id)
        if not customer:
            raise ValueError("Cliente no encontrado")
        
        # Calcular totales
        subtotal_usd = 0
        subtotal_bsf = 0
        iva_amount_usd = 0
        iva_amount_bsf = 0
        
        sale_items = []
        
        for item_data in sale_data.items:
            # Obtener producto
            product = await ProductService.get_product_by_id(db, item_data.product_id)
            if not product:
                raise ValueError(f"Producto ID {item_data.product_id} no encontrado")
            
            # Verificar stock
            if product.stock_quantity < item_data.quantity:
                raise ValueError(f"Stock insuficiente para {product.name}. Disponible: {product.stock_quantity}")
            
            # Calcular precios del ítem
            unit_price_usd = product.price_usd
            unit_price_bsf = unit_price_usd * exchange_rate
            
            quantity = item_data.quantity
            
            item_subtotal_usd = unit_price_usd * quantity
            item_subtotal_bsf = unit_price_bsf * quantity
            
            # Calcular IVA
            item_iva_usd = item_subtotal_usd * product.iva_rate if not product.is_exempt else 0
            item_iva_bsf = item_subtotal_bsf * product.iva_rate if not product.is_exempt else 0
            
            # Total del ítem
            item_total_usd = item_subtotal_usd + item_iva_usd
            item_total_bsf = item_subtotal_bsf + item_iva_bsf
            
            # Crear ítem de venta
            sale_item = SaleItem(
                sale_id=None,  # Se asignará después
                product_id=product.id,
                quantity=quantity,
                unit_price_usd=unit_price_usd,
                unit_price_bsf=unit_price_bsf,
                subtotal_usd=item_subtotal_usd,
                subtotal_bsf=item_subtotal_bsf,
                iva_rate=product.iva_rate,
                iva_amount_usd=item_iva_usd,
                iva_amount_bsf=item_iva_bsf,
                total_usd=item_total_usd,
                total_bsf=item_total_bsf
            )
            
            sale_items.append(sale_item)
            
            # Acumular totales
            subtotal_usd += item_subtotal_usd
            subtotal_bsf += item_subtotal_bsf
            iva_amount_usd += item_iva_usd
            iva_amount_bsf += item_iva_bsf
            
            # Descontar stock
            product.stock_quantity -= quantity
            
            # Registrar movimiento de inventario
            movement = InventoryMovement(
                product_id=product.id,
                movement_type="exit",
                quantity=-quantity,
                reference_type="sale",
                reason=f"Venta {invoice_number}",
                user_id=user_id
            )
            db.add(movement)
        
        # Calcular IGTF (3% si paga en divisas)
        igtf_amount_usd = 0
        igtf_amount_bsf = 0
        
        if sale_data.payment_currency == "USD":
            igtf_amount_usd = subtotal_usd * settings.IGTF_RATE
            igtf_amount_bsf = igtf_amount_usd * exchange_rate
        
        # Totales finales
        total_usd = subtotal_usd + iva_amount_usd + igtf_amount_usd
        total_bsf = subtotal_bsf + iva_amount_bsf + igtf_amount_bsf
        
        # Crear venta
        sale = Sale(
            invoice_number=invoice_number,
            customer_id=sale_data.customer_id,
            user_id=user_id,
            subtotal_usd=subtotal_usd,
            subtotal_bsf=subtotal_bsf,
            iva_amount_usd=iva_amount_usd,
            iva_amount_bsf=iva_amount_bsf,
            igtf_amount_usd=igtf_amount_usd,
            igtf_amount_bsf=igtf_amount_bsf,
            total_usd=total_usd,
            total_bsf=total_bsf,
            exchange_rate=exchange_rate,
            payment_method=sale_data.payment_method,
            payment_currency=sale_data.payment_currency,
            status="completed",
            notes=sale_data.notes
        )
        
        db.add(sale)
        await db.flush()  # Para obtener el ID de la venta
        
        # Asignar sale_id a los items
        for item in sale_items:
            item.sale_id = sale.id
            db.add(item)
        
        await db.commit()
        await db.refresh(sale)
        
        # Log de auditoría
        await AuditLogService.log_action(
            db=db,
            user_id=user_id,
            action="CREATE",
            entity="sale",
            entity_id=sale.id,
            new_values=f"Factura {invoice_number}, Total: {total_usd} USD"
        )
        
        return sale
    
    @staticmethod
    async def _generate_invoice_number(db: AsyncSession) -> str:
        """Genera un número de factura único"""
        # Obtener la última factura
        result = await db.execute(
            select(Sale).order_by(Sale.created_at.desc()).limit(1)
        )
        last_sale = result.scalar_one_or_none()
        
        if last_sale:
            # Extraer número secuencial
            try:
                last_num = int(last_sale.invoice_number.split('-')[-1])
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            new_num = 1
        
        # Formato: FAC-YYYYMMDD-00001
        date_str = datetime.now().strftime("%Y%m%d")
        return f"FAC-{date_str}-{new_num:05d}"
    
    @staticmethod
    async def get_sale_by_id(db: AsyncSession, sale_id: int) -> Optional[Sale]:
        result = await db.execute(
            select(Sale)
            .filter(Sale.id == sale_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_sales(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Sale]:
        query = select(Sale).order_by(Sale.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()


class ExchangeRateService:
    
    @staticmethod
    async def get_current_rate(db: AsyncSession) -> Optional[ExchangeRate]:
        result = await db.execute(
            select(ExchangeRate)
            .filter(ExchangeRate.is_active == True)
            .order_by(ExchangeRate.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def set_new_rate(
        db: AsyncSession, 
        rate: float, 
        source: str = "BCV",
        deactivate_previous: bool = True
    ) -> ExchangeRate:
        # Desactivar tasas anteriores si se solicita
        if deactivate_previous:
            await db.execute(
                update(ExchangeRate)
                .where(ExchangeRate.is_active == True)
                .values(is_active=False)
            )
        
        # Crear nueva tasa
        db_rate = ExchangeRate(
            rate=rate,
            source=source,
            is_active=True
        )
        
        db.add(db_rate)
        await db.commit()
        await db.refresh(db_rate)
        
        # Actualizar precios de productos
        await ProductService.update_prices_with_new_rate(db, rate)
        
        return db_rate


class AuditLogService:
    
    @staticmethod
    async def log_action(
        db: AsyncSession,
        action: str,
        entity: str,
        entity_id: Optional[int] = None,
        user_id: Optional[int] = None,
        old_values: Optional[str] = None,
        new_values: Optional[str] = None,
        ip_address: Optional[str] = None
    ):
        log = AuditLog(
            user_id=user_id,
            action=action,
            entity=entity,
            entity_id=entity_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address
        )
        
        db.add(log)
        await db.commit()


# Import necesario para update
from sqlalchemy import update

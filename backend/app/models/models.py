from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    CAJERO = "cajero"
    ALMACENISTA = "almacenista"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.CAJERO)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    sales = relationship("Sale", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), index=True)
    brand = Column(String(100))
    
    # Precios
    price_usd = Column(Float, nullable=False)  # Precio base en USD
    price_bsf = Column(Float, nullable=True)   # Precio en Bolívares (calculado)
    
    # Stock
    stock_quantity = Column(Float, default=0)
    min_stock = Column(Float, default=5)
    unit_of_measure = Column(String(20), default="unidad")  # unidad, kg, m, litro
    
    # Impuestos
    iva_rate = Column(Float, default=0.16)  # 16% general
    is_exempt = Column(Boolean, default=False)
    
    # Estado
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    sale_items = relationship("SaleItem", back_populates="product")
    inventory_movements = relationship("InventoryMovement", back_populates="product")


class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    rif = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    customer_type = Column(String(20), default="natural")  # natural o juridica
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    sales = relationship("Sale", back_populates="customer")


class Sale(Base):
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, index=True, nullable=False)
    
    # Cliente
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    
    # Usuario que realizó la venta
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Montos
    subtotal_usd = Column(Float, nullable=False)
    subtotal_bsf = Column(Float, nullable=False)
    
    # IVA
    iva_amount_usd = Column(Float, default=0)
    iva_amount_bsf = Column(Float, default=0)
    
    # IGTF (3% para pagos en divisas)
    igtf_amount_usd = Column(Float, default=0)
    igtf_amount_bsf = Column(Float, default=0)
    
    # Total
    total_usd = Column(Float, nullable=False)
    total_bsf = Column(Float, nullable=False)
    
    # Tipo de cambio usado
    exchange_rate = Column(Float, nullable=False)
    
    # Método de pago
    payment_method = Column(String(50), default="efectivo")  # efectivo, punto, transferencia, divisa
    payment_currency = Column(String(10), default="USD")  # USD o VES
    
    # Estado
    status = Column(String(20), default="completed")  # completed, cancelled, refunded
    notes = Column(Text, nullable=True)
    
    # Fechas
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="sales")
    user = relationship("User", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")


class SaleItem(Base):
    __tablename__ = "sale_items"
    
    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    quantity = Column(Float, nullable=False)
    unit_price_usd = Column(Float, nullable=False)
    unit_price_bsf = Column(Float, nullable=False)
    
    # Subtotal por ítem
    subtotal_usd = Column(Float, nullable=False)
    subtotal_bsf = Column(Float, nullable=False)
    
    # IVA por ítem
    iva_rate = Column(Float, default=0.16)
    iva_amount_usd = Column(Float, default=0)
    iva_amount_bsf = Column(Float, default=0)
    
    # Total por ítem
    total_usd = Column(Float, nullable=False)
    total_bsf = Column(Float, nullable=False)
    
    # Relationships
    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")


class InventoryMovement(Base):
    __tablename__ = "inventory_movements"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    movement_type = Column(String(20), nullable=False)  # entry, exit, adjustment
    quantity = Column(Float, nullable=False)
    
    # Referencia (venta, compra, ajuste)
    reference_type = Column(String(50), nullable=True)  # sale, purchase, adjustment
    reference_id = Column(Integer, nullable=True)
    
    reason = Column(Text, nullable=True)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="inventory_movements")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    action = Column(String(50), nullable=False)  # CREATE, UPDATE, DELETE, LOGIN, etc.
    entity = Column(String(50), nullable=False)  # product, sale, customer, user
    entity_id = Column(Integer, nullable=True)
    
    old_values = Column(Text, nullable=True)  # JSON
    new_values = Column(Text, nullable=True)  # JSON
    
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"
    
    id = Column(Integer, primary_key=True, index=True)
    rate = Column(Float, nullable=False)
    source = Column(String(50), default="BCV")  # BCV, manual, API
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

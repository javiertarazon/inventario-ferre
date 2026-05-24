from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import enum

from app.db.database import Base


class UserRole(enum.Enum):
    ADMIN = "admin"
    CASHIER = "cajero"
    INVENTORY = "inventario"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.CASHIER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    invoices = relationship("Invoice", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), index=True, nullable=True)
    unit_price_usd = Column(Float, nullable=False)  # Precio base en USD
    stock_quantity = Column(Float, default=0.0, nullable=False)
    min_stock = Column(Float, default=5.0, nullable=False)  # Alerta de stock mínimo
    unit_measure = Column(String(20), default="unidad", nullable=False)  # unidad, kg, m, etc.
    iva_rate = Column(Float, default=0.16, nullable=False)  # Tasa de IVA aplicable
    is_exempt = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    invoice_items = relationship("InvoiceItem", back_populates="product")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    rif = Column(String(20), unique=True, index=True, nullable=False)  # RIF venezolano
    name = Column(String(200), nullable=False)
    address = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    customer_type = Column(String(20), default="natural", nullable=False)  # natural o juridica
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    invoices = relationship("Invoice", back_populates="customer")


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    id = Column(Integer, primary_key=True, index=True)
    rate = Column(Float, nullable=False)  # Tasa BCV
    source = Column(String(50), default="BCV", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    fetched_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class InvoiceStatus(enum.Enum):
    DRAFT = "borrador"
    COMPLETED = "completada"
    CANCELLED = "cancelada"


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, index=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Monetary values in USD (base currency)
    subtotal_usd = Column(Float, nullable=False)
    iva_amount_usd = Column(Float, nullable=False)
    igtf_amount_usd = Column(Float, default=0.0, nullable=False)  # 3% IGTF si aplica
    total_usd = Column(Float, nullable=False)
    
    # Values in VES using BCV rate
    exchange_rate = Column(Float, nullable=False)  # Tasa BCV al momento de la factura
    total_vef = Column(Float, nullable=False)  # Total en Bolívares
    
    status = Column(SQLEnum(InvoiceStatus), default=InvoiceStatus.DRAFT, nullable=False)
    payment_method = Column(String(50), nullable=False)  # efectivo, punto, transferencia, divisas
    apply_igtf = Column(Boolean, default=False, nullable=False)  # Si aplica IGTF (pagos en divisas)
    
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    printed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="invoices")
    customer = relationship("Customer", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")


class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    quantity = Column(Float, nullable=False)
    unit_price_usd = Column(Float, nullable=False)  # Precio unitario en USD
    subtotal_usd = Column(Float, nullable=False)
    iva_rate = Column(Float, nullable=False)
    iva_amount_usd = Column(Float, nullable=False)
    total_usd = Column(Float, nullable=False)

    # Relationships
    invoice = relationship("Invoice", back_populates="items")
    product = relationship("Product", back_populates="invoice_items")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    table_name = Column(String(50), nullable=False)
    record_id = Column(Integer, nullable=True)
    old_values = Column(Text, nullable=True)  # JSON con valores anteriores
    new_values = Column(Text, nullable=True)  # JSON con valores nuevos
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRoleEnum(str, Enum):
    ADMIN = "admin"
    CASHIER = "cajero"
    INVENTORY = "inventario"


class InvoiceStatusEnum(str, Enum):
    DRAFT = "borrador"
    COMPLETED = "completada"
    CANCELLED = "cancelada"


# User Schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    role: UserRoleEnum = UserRoleEnum.CASHIER


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRoleEnum] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Product Schemas
class ProductBase(BaseModel):
    sku: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None
    unit_price_usd: float = Field(..., gt=0)
    stock_quantity: float = Field(default=0.0, ge=0)
    min_stock: float = Field(default=5.0, ge=0)
    unit_measure: str = "unidad"
    iva_rate: float = Field(default=0.16, ge=0, le=1)
    is_exempt: bool = False


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    unit_price_usd: Optional[float] = None
    stock_quantity: Optional[float] = None
    min_stock: Optional[float] = None
    unit_measure: Optional[str] = None
    iva_rate: Optional[float] = None
    is_exempt: Optional[bool] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Customer Schemas
class CustomerBase(BaseModel):
    rif: str = Field(..., min_length=9, max_length=20)
    name: str = Field(..., min_length=1, max_length=200)
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    customer_type: str = "natural"

    @validator('rif')
    def validate_rif(cls, v):
        # Validación básica de RIF venezolano
        v = v.upper().replace("-", "").replace(" ", "")
        if len(v) < 9:
            raise ValueError('RIF inválido. Debe tener al menos 9 caracteres')
        if not v[0] in ['V', 'E', 'J', 'G', 'P']:
            raise ValueError('RIF inválido. Debe comenzar con V, E, J, G o P')
        return v


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    customer_type: Optional[str] = None
    is_active: Optional[bool] = None


class CustomerResponse(CustomerBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Exchange Rate Schemas
class ExchangeRateBase(BaseModel):
    rate: float = Field(..., gt=0)
    source: str = "BCV"


class ExchangeRateResponse(ExchangeRateBase):
    id: int
    is_active: bool
    fetched_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# Invoice Item Schemas
class InvoiceItemBase(BaseModel):
    product_id: int
    quantity: float = Field(..., gt=0)
    unit_price_usd: float = Field(..., gt=0)
    iva_rate: float = Field(default=0.16, ge=0, le=1)


class InvoiceItemCreate(InvoiceItemBase):
    pass


class InvoiceItemResponse(InvoiceItemBase):
    id: int
    invoice_id: int
    subtotal_usd: float
    iva_amount_usd: float
    total_usd: float

    class Config:
        from_attributes = True


# Invoice Schemas
class InvoiceCreate(BaseModel):
    customer_id: int
    items: List[InvoiceItemCreate]
    payment_method: str
    apply_igtf: bool = False
    notes: Optional[str] = None


class InvoiceUpdate(BaseModel):
    status: Optional[InvoiceStatusEnum] = None
    notes: Optional[str] = None


class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    customer_id: int
    user_id: int
    subtotal_usd: float
    iva_amount_usd: float
    igtf_amount_usd: float
    total_usd: float
    exchange_rate: float
    total_vef: float
    status: InvoiceStatusEnum
    payment_method: str
    apply_igtf: bool
    notes: Optional[str]
    created_at: datetime
    printed_at: Optional[datetime]
    items: List[InvoiceItemResponse] = []

    class Config:
        from_attributes = True


# Audit Log Schema
class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    action: str
    table_name: str
    record_id: Optional[int]
    ip_address: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Token Schema
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

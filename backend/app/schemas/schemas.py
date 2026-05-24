from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRoleEnum(str, Enum):
    ADMIN = "admin"
    CAJERO = "cajero"
    ALMACENISTA = "almacenista"


# User Schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    role: UserRoleEnum = UserRoleEnum.CAJERO


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
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str


# Product Schemas
class ProductBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    price_usd: float = Field(..., gt=0)
    stock_quantity: float = Field(default=0, ge=0)
    min_stock: float = Field(default=5, ge=0)
    unit_of_measure: str = "unidad"
    iva_rate: float = 0.16
    is_exempt: bool = False


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    price_usd: Optional[float] = None
    stock_quantity: Optional[float] = None
    min_stock: Optional[float] = None
    unit_of_measure: Optional[str] = None
    iva_rate: Optional[float] = None
    is_exempt: Optional[bool] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    id: int
    price_bsf: Optional[float] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Customer Schemas
class CustomerBase(BaseModel):
    rif: str = Field(..., min_length=9, max_length=20)
    name: str = Field(..., min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    customer_type: str = "natural"
    
    @validator('rif')
    def validate_rif(cls, v):
        # Validación básica de RIF venezolano
        v = v.upper().strip()
        if len(v) < 9:
            raise ValueError('RIF muy corto')
        # Debe empezar con V, E, J, G, P seguido de números
        if v[0] not in ['V', 'E', 'J', 'G', 'P']:
            raise ValueError('RIF debe comenzar con V, E, J, G o P')
        return v


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    customer_type: Optional[str] = None
    is_active: Optional[bool] = None


class CustomerResponse(CustomerBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Sale Item Schemas
class SaleItemBase(BaseModel):
    product_id: int
    quantity: float = Field(..., gt=0)


class SaleItemCreate(SaleItemBase):
    pass


class SaleItemResponse(BaseModel):
    id: int
    sale_id: int
    product_id: int
    quantity: float
    unit_price_usd: float
    unit_price_bsf: float
    subtotal_usd: float
    subtotal_bsf: float
    iva_rate: float
    iva_amount_usd: float
    iva_amount_bsf: float
    total_usd: float
    total_bsf: float
    
    class Config:
        from_attributes = True


# Sale Schemas
class SaleBase(BaseModel):
    customer_id: int
    payment_method: str = "efectivo"
    payment_currency: str = "USD"
    notes: Optional[str] = None


class SaleCreate(SaleBase):
    items: List[SaleItemCreate]


class SaleResponse(BaseModel):
    id: int
    invoice_number: str
    customer_id: int
    user_id: int
    subtotal_usd: float
    subtotal_bsf: float
    iva_amount_usd: float
    iva_amount_bsf: float
    igtf_amount_usd: float
    igtf_amount_bsf: float
    total_usd: float
    total_bsf: float
    exchange_rate: float
    payment_method: str
    payment_currency: str
    status: str
    notes: Optional[str] = None
    created_at: datetime
    items: List[SaleItemResponse] = []
    
    class Config:
        from_attributes = True


# Inventory Movement Schemas
class InventoryMovementBase(BaseModel):
    product_id: int
    movement_type: str  # entry, exit, adjustment
    quantity: float
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    reason: Optional[str] = None


class InventoryMovementCreate(InventoryMovementBase):
    pass


class InventoryMovementResponse(InventoryMovementBase):
    id: int
    user_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Exchange Rate Schema
class ExchangeRateBase(BaseModel):
    rate: float = Field(..., gt=0)
    source: str = "BCV"


class ExchangeRateResponse(ExchangeRateBase):
    id: int
    is_active: bool
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

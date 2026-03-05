"""
API REST schemas for products.
"""

from marshmallow import Schema, fields, validates, ValidationError as MarshmallowValidationError
from decimal import Decimal
import re


class ProductCreateSchema(Schema):
    """Schema for creating a product via API."""
    codigo = fields.Str(required=True, description="Product code in format X-XX-XX")
    descripcion = fields.Str(required=True, description="Product description")
    stock = fields.Int(load_default=0, description="Product stock quantity")
    precio_dolares = fields.Decimal(required=True, places=2, as_string=True, description="Price in USD")
    proveedor_id = fields.Int(allow_none=True, load_default=None, description="Supplier ID")
    category_id = fields.Int(allow_none=True, load_default=None, description="Category/Item Group ID")
    reorder_point = fields.Int(allow_none=True, load_default=10, description="Minimum stock to trigger reorder")
    
    @validates('codigo')
    def validate_codigo(self, value, **kwargs):
        """Validate product code format X-XX-XX."""
        if not value or not value.strip():
            raise MarshmallowValidationError('Product code cannot be empty')
        
        code_pattern = re.compile(r'^[A-Z]-[A-Z]{2}-\d{2}$')
        if not code_pattern.match(value.upper().strip()):
            raise MarshmallowValidationError('Invalid code format. Must be: X-XX-XX (e.g., A-BC-01)')
    
    @validates('descripcion')
    def validate_descripcion(self, value, **kwargs):
        """Validate product description."""
        if not value or not value.strip():
            raise MarshmallowValidationError('Description cannot be empty')
        
        if len(value) > 200:
            raise MarshmallowValidationError('Description cannot exceed 200 characters')
    
    @validates('stock')
    def validate_stock(self, value, **kwargs):
        """Validate stock is non-negative."""
        if value < 0:
            raise MarshmallowValidationError('Stock cannot be negative')
    
    @validates('precio_dolares')
    def validate_precio(self, value, **kwargs):
        """Validate price is non-negative."""
        if value < 0:
            raise MarshmallowValidationError('Price cannot be negative')


class ProductUpdateSchema(Schema):
    """Schema for updating a product via API."""
    descripcion = fields.Str(allow_none=True)
    stock = fields.Int(allow_none=True)
    precio_dolares = fields.Decimal(places=2, as_string=True, allow_none=True)
    proveedor_id = fields.Int(allow_none=True)
    category_id = fields.Int(allow_none=True)
    reorder_point = fields.Int(allow_none=True)
    
    @validates('descripcion')
    def validate_descripcion(self, value, **kwargs):
        """Validate product description."""
        if value is not None:
            if not value.strip():
                raise MarshmallowValidationError('Description cannot be empty')
            if len(value) > 200:
                raise MarshmallowValidationError('Description cannot exceed 200 characters')
    
    @validates('stock')
    def validate_stock(self, value, **kwargs):
        """Validate stock is non-negative."""
        if value is not None and value < 0:
            raise MarshmallowValidationError('Stock cannot be negative')
    
    @validates('precio_dolares')
    def validate_precio(self, value, **kwargs):
        """Validate price is non-negative."""
        if value is not None and value < 0:
            raise MarshmallowValidationError('Price cannot be negative')


class ProductResponseSchema(Schema):
    """Schema for product API response."""
    id = fields.Int(dump_only=True)
    codigo = fields.Str()
    descripcion = fields.Str()
    stock = fields.Int()
    precio_dolares = fields.Decimal(places=2, as_string=True)
    proveedor_id = fields.Int(allow_none=True)
    categoria = fields.Str(allow_none=True)
    reorder_point = fields.Int(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    class Meta:
        ordered = True


class ProductListSchema(Schema):
    """Schema for paginated product list response."""
    items = fields.List(fields.Nested(ProductResponseSchema))
    total = fields.Int()
    page = fields.Int()
    per_page = fields.Int()
    pages = fields.Int()

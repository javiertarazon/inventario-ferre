"""
Product validation schemas using Marshmallow.
"""

from marshmallow import Schema, fields, validates, ValidationError as MarshmallowValidationError
from decimal import Decimal
import re


class ProductSchema(Schema):
    """Schema for product validation."""
    
    codigo = fields.Str(required=True)
    descripcion = fields.Str(required=True)
    stock = fields.Int(load_default=0)
    precio_dolares = fields.Decimal(places=2, as_string=True, load_default=Decimal('0.00'))
    factor_ajuste = fields.Decimal(places=2, as_string=True, load_default=Decimal('1.00'))
    proveedor_id = fields.Int(allow_none=True, load_default=None)
    
    @validates('codigo')
    def validate_codigo(self, value, **kwargs):
        """Validate product code format X-XX-XX."""
        if not value or not value.strip():
            raise MarshmallowValidationError('El código del producto no puede estar vacío')
        
        code_pattern = re.compile(r'^[A-Z]-[A-Z]{2}-\d{2}$')
        if not code_pattern.match(value.upper().strip()):
            raise MarshmallowValidationError('El formato del código es inválido. Debe ser: X-XX-XX (ej: A-BC-01)')
    
    @validates('descripcion')
    def validate_descripcion(self, value, **kwargs):
        """Validate product description."""
        if not value or not value.strip():
            raise MarshmallowValidationError('La descripción no puede estar vacía')
        
        if len(value) > 200:
            raise MarshmallowValidationError('La descripción no puede exceder 200 caracteres')
    
    @validates('stock')
    def validate_stock(self, value, **kwargs):
        """Validate stock is non-negative."""
        if value < 0:
            raise MarshmallowValidationError('El stock no puede ser negativo')
    
    @validates('precio_dolares')
    def validate_precio(self, value, **kwargs):
        """Validate price is non-negative."""
        if value < 0:
            raise MarshmallowValidationError('El precio no puede ser negativo')
    
    @validates('factor_ajuste')
    def validate_factor(self, value, **kwargs):
        """Validate adjustment factor is positive."""
        if value <= 0:
            raise MarshmallowValidationError('El factor de ajuste debe ser mayor que cero')


class ProductUpdateSchema(Schema):
    """Schema for product updates (all fields optional)."""
    
    codigo = fields.Str()
    descripcion = fields.Str()
    stock = fields.Int()
    precio_dolares = fields.Decimal(places=2, as_string=True)
    factor_ajuste = fields.Decimal(places=2, as_string=True)
    proveedor_id = fields.Int(allow_none=True)
    
    @validates('codigo')
    def validate_codigo(self, value, **kwargs):
        """Validate product code format X-XX-XX."""
        if value:
            code_pattern = re.compile(r'^[A-Z]-[A-Z]{2}-\d{2}$')
            if not code_pattern.match(value.upper().strip()):
                raise MarshmallowValidationError('El formato del código es inválido. Debe ser: X-XX-XX (ej: A-BC-01)')
    
    @validates('descripcion')
    def validate_descripcion(self, value, **kwargs):
        """Validate product description."""
        if value and len(value) > 200:
            raise MarshmallowValidationError('La descripción no puede exceder 200 caracteres')
    
    @validates('stock')
    def validate_stock(self, value, **kwargs):
        """Validate stock is non-negative."""
        if value is not None and value < 0:
            raise MarshmallowValidationError('El stock no puede ser negativo')
    
    @validates('precio_dolares')
    def validate_precio(self, value, **kwargs):
        """Validate price is non-negative."""
        if value is not None and value < 0:
            raise MarshmallowValidationError('El precio no puede ser negativo')
    
    @validates('factor_ajuste')
    def validate_factor(self, value, **kwargs):
        """Validate adjustment factor is positive."""
        if value is not None and value <= 0:
            raise MarshmallowValidationError('El factor de ajuste debe ser mayor que cero')

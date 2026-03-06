"""
API REST schemas for inventory movements.
"""

from marshmallow import Schema, fields, validates, ValidationError as MarshmallowValidationError
from enum import Enum


class MovementTypeEnum(str, Enum):
    """Enum for movement types."""
    ENTRADA = "ENTRADA"
    SALIDA = "SALIDA"
    AJUSTE = "AJUSTE"
    DEVOLUCION = "DEVOLUCION"


class MovementCreateSchema(Schema):
    """Schema for creating an inventory movement via API."""
    tipo = fields.Str(required=True, metadata={"description": "Movement type: ENTRADA, SALIDA, AJUSTE, DEVOLUCION"})
    producto_id = fields.Int(required=True, metadata={"description": "Product ID"})
    cantidad = fields.Int(required=True, metadata={"description": "Quantity moved"})
    referencia = fields.Str(allow_none=True, metadata={"description": "Reference document or number"})
    razon = fields.Str(allow_none=True, metadata={"description": "Reason for movement"})
    
    @validates('tipo')
    def validate_tipo(self, value, **kwargs):
        """Validate movement type."""
        valid_types = ["ENTRADA", "SALIDA", "AJUSTE", "DEVOLUCION"]
        if value.upper() not in valid_types:
            raise MarshmallowValidationError(f'Invalid movement type. Must be one of: {", ".join(valid_types)}')
    
    @validates('cantidad')
    def validate_cantidad(self, value, **kwargs):
        """Validate quantity is positive."""
        if value <= 0:
            raise MarshmallowValidationError('Quantity must be greater than 0')
    
    @validates('referencia')
    def validate_referencia(self, value, **kwargs):
        """Validate reference."""
        if value is not None and len(value) > 100:
            raise MarshmallowValidationError('Reference cannot exceed 100 characters')


class MovementResponseSchema(Schema):
    """Schema for movement API response."""
    id = fields.Int(dump_only=True)
    tipo = fields.Str()
    producto_id = fields.Int()
    producto_codigo = fields.Str(allow_none=True)
    cantidad = fields.Int()
    stock_anterior = fields.Int(allow_none=True)
    stock_nuevo = fields.Int(allow_none=True)
    referencia = fields.Str(allow_none=True)
    razon = fields.Str(allow_none=True)
    usuario_id = fields.Int(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    
    class Meta:
        ordered = True


class MovementListSchema(Schema):
    """Schema for paginated movement list response."""
    items = fields.List(fields.Nested(MovementResponseSchema))
    total = fields.Int()
    page = fields.Int()
    per_page = fields.Int()
    pages = fields.Int()

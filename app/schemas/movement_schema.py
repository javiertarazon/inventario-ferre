"""
Movement validation schemas using Marshmallow.
"""

from marshmallow import Schema, fields, validates, ValidationError as MarshmallowValidationError


class MovementSchema(Schema):
    """Schema for movement validation."""
    
    producto_id = fields.Int(required=True)
    tipo_movimiento = fields.Str(required=True)
    cantidad = fields.Int(required=True)
    fecha = fields.Date(allow_none=True, load_default=None)
    motivo = fields.Str(allow_none=True, load_default=None)
    
    @validates('tipo_movimiento')
    def validate_tipo(self, value, **kwargs):
        """Validate movement type."""
        if not value or not value.strip():
            raise MarshmallowValidationError('El tipo de movimiento no puede estar vacío')
        
        valid_types = ['ENTRADA', 'SALIDA', 'AJUSTE']
        if value.upper().strip() not in valid_types:
            raise MarshmallowValidationError('El tipo de movimiento debe ser: ENTRADA, SALIDA o AJUSTE')
    
    @validates('cantidad')
    def validate_cantidad(self, value, **kwargs):
        """Validate quantity is positive."""
        if value <= 0:
            raise MarshmallowValidationError('La cantidad debe ser mayor que cero')
    
    @validates('motivo')
    def validate_motivo(self, value, **kwargs):
        """Validate reason length."""
        if value and len(value) > 500:
            raise MarshmallowValidationError('El motivo no puede exceder 500 caracteres')


class MovementUpdateSchema(Schema):
    """Schema for movement updates (all fields optional)."""
    
    producto_id = fields.Int()
    tipo_movimiento = fields.Str()
    cantidad = fields.Int()
    fecha = fields.Date(allow_none=True)
    motivo = fields.Str(allow_none=True)
    
    @validates('tipo_movimiento')
    def validate_tipo(self, value, **kwargs):
        """Validate movement type."""
        if value:
            valid_types = ['ENTRADA', 'SALIDA', 'AJUSTE']
            if value.upper().strip() not in valid_types:
                raise MarshmallowValidationError('El tipo de movimiento debe ser: ENTRADA, SALIDA o AJUSTE')
    
    @validates('cantidad')
    def validate_cantidad(self, value, **kwargs):
        """Validate quantity is positive."""
        if value is not None and value <= 0:
            raise MarshmallowValidationError('La cantidad debe ser mayor que cero')
    
    @validates('motivo')
    def validate_motivo(self, value, **kwargs):
        """Validate reason length."""
        if value and len(value) > 500:
            raise MarshmallowValidationError('El motivo no puede exceder 500 caracteres')

"""
Supplier validation schemas using Marshmallow.
"""

from marshmallow import Schema, fields, validates, ValidationError as MarshmallowValidationError
import re


class SupplierSchema(Schema):
    """Schema for supplier validation."""
    
    nombre = fields.Str(required=True)
    rif = fields.Str(required=True)
    telefono = fields.Str(allow_none=True, load_default=None)
    email = fields.Email(allow_none=True, load_default=None)
    direccion = fields.Str(allow_none=True, load_default=None)
    
    @validates('nombre')
    def validate_nombre(self, value, **kwargs):
        """Validate supplier name."""
        if not value or not value.strip():
            raise MarshmallowValidationError('El nombre del proveedor no puede estar vacío')
        
        if len(value) > 200:
            raise MarshmallowValidationError('El nombre no puede exceder 200 caracteres')
    
    @validates('rif')
    def validate_rif(self, value, **kwargs):
        """Validate Venezuelan RIF format."""
        if not value or not value.strip():
            raise MarshmallowValidationError('El RIF no puede estar vacío')
        
        rif_pattern = re.compile(r'^[JVEGP]-\d{8,9}-\d$')
        if not rif_pattern.match(value.upper().strip()):
            raise MarshmallowValidationError('El formato del RIF es inválido. Debe ser: J-12345678-9 o V-12345678-9')
    
    @validates('telefono')
    def validate_telefono(self, value, **kwargs):
        """Validate phone number length."""
        if value and len(value) > 20:
            raise MarshmallowValidationError('El teléfono no puede exceder 20 caracteres')
    
    @validates('email')
    def validate_email_length(self, value, **kwargs):
        """Validate email length."""
        if value and len(value) > 255:
            raise MarshmallowValidationError('El email no puede exceder 255 caracteres')
    
    @validates('direccion')
    def validate_direccion(self, value, **kwargs):
        """Validate address length."""
        if value and len(value) > 500:
            raise MarshmallowValidationError('La dirección no puede exceder 500 caracteres')


class SupplierUpdateSchema(Schema):
    """Schema for supplier updates (all fields optional)."""
    
    nombre = fields.Str()
    rif = fields.Str()
    telefono = fields.Str(allow_none=True)
    email = fields.Email(allow_none=True)
    direccion = fields.Str(allow_none=True)
    
    @validates('nombre')
    def validate_nombre(self, value, **kwargs):
        """Validate supplier name."""
        if value and len(value) > 200:
            raise MarshmallowValidationError('El nombre no puede exceder 200 caracteres')
    
    @validates('rif')
    def validate_rif(self, value, **kwargs):
        """Validate Venezuelan RIF format."""
        if value:
            rif_pattern = re.compile(r'^[JVEGP]-\d{8,9}-\d$')
            if not rif_pattern.match(value.upper().strip()):
                raise MarshmallowValidationError('El formato del RIF es inválido. Debe ser: J-12345678-9 o V-12345678-9')
    
    @validates('telefono')
    def validate_telefono(self, value, **kwargs):
        """Validate phone number length."""
        if value and len(value) > 20:
            raise MarshmallowValidationError('El teléfono no puede exceder 20 caracteres')
    
    @validates('email')
    def validate_email_length(self, value, **kwargs):
        """Validate email length."""
        if value and len(value) > 255:
            raise MarshmallowValidationError('El email no puede exceder 255 caracteres')
    
    @validates('direccion')
    def validate_direccion(self, value, **kwargs):
        """Validate address length."""
        if value and len(value) > 500:
            raise MarshmallowValidationError('La dirección no puede exceder 500 caracteres')

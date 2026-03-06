"""
API REST schemas for customers.
"""

from marshmallow import Schema, fields, validates, ValidationError as MarshmallowValidationError
import re


class CustomerCreateSchema(Schema):
    """Schema for creating a customer via API."""
    nombre = fields.Str(required=True, metadata={"description": "Customer name"})
    apellido = fields.Str(required=True, metadata={"description": "Customer last name"})
    email = fields.Email(required=True, metadata={"description": "Customer email"})
    telefono = fields.Str(allow_none=True, metadata={"description": "Customer phone"})
    direccion = fields.Str(allow_none=True, metadata={"description": "Customer address"})
    ciudad = fields.Str(allow_none=True, metadata={"description": "Customer city"})
    
    @validates('nombre')
    def validate_nombre(self, value, **kwargs):
        """Validate customer name."""
        if not value or not value.strip():
            raise MarshmallowValidationError('Customer name cannot be empty')
        if len(value) > 100:
            raise MarshmallowValidationError('Customer name cannot exceed 100 characters')
    
    @validates('apellido')
    def validate_apellido(self, value, **kwargs):
        """Validate customer last name."""
        if not value or not value.strip():
            raise MarshmallowValidationError('Customer last name cannot be empty')
        if len(value) > 100:
            raise MarshmallowValidationError('Customer last name cannot exceed 100 characters')
    
    @validates('email')
    def validate_email(self, value, **kwargs):
        """Validate customer email."""
        if not value or not value.strip():
            raise MarshmallowValidationError('Customer email cannot be empty')


class CustomerUpdateSchema(Schema):
    """Schema for updating a customer via API."""
    nombre = fields.Str(allow_none=True)
    apellido = fields.Str(allow_none=True)
    email = fields.Email(allow_none=True)
    telefono = fields.Str(allow_none=True)
    direccion = fields.Str(allow_none=True)
    ciudad = fields.Str(allow_none=True)
    
    @validates('nombre')
    def validate_nombre(self, value, **kwargs):
        """Validate customer name."""
        if value is not None:
            if not value.strip():
                raise MarshmallowValidationError('Customer name cannot be empty')
            if len(value) > 100:
                raise MarshmallowValidationError('Customer name cannot exceed 100 characters')
    
    @validates('apellido')
    def validate_apellido(self, value, **kwargs):
        """Validate customer last name."""
        if value is not None:
            if not value.strip():
                raise MarshmallowValidationError('Customer last name cannot be empty')
            if len(value) > 100:
                raise MarshmallowValidationError('Customer last name cannot exceed 100 characters')


class CustomerResponseSchema(Schema):
    """Schema for customer API response."""
    id = fields.Int(dump_only=True)
    nombre = fields.Str()
    apellido = fields.Str()
    email = fields.Email()
    telefono = fields.Str(allow_none=True)
    direccion = fields.Str(allow_none=True)
    ciudad = fields.Str(allow_none=True)
    is_active = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    class Meta:
        ordered = True


class CustomerListSchema(Schema):
    """Schema for paginated customer list response."""
    items = fields.List(fields.Nested(CustomerResponseSchema))
    total = fields.Int()
    page = fields.Int()
    per_page = fields.Int()
    pages = fields.Int()

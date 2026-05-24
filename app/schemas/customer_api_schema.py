"""
API REST schemas for customers.
"""

from marshmallow import Schema, fields, validates, ValidationError as MarshmallowValidationError
import re


class CustomerCreateSchema(Schema):
    """Schema for creating a customer via API."""
    name = fields.Str(required=True, metadata={"description": "Customer name"})
    email = fields.Email(required=True, metadata={"description": "Customer email"})
    phone = fields.Str(allow_none=True, metadata={"description": "Customer phone"})
    address = fields.Str(allow_none=True, metadata={"description": "Customer address"})
    city = fields.Str(allow_none=True, metadata={"description": "Customer city"})
    
    @validates('name')
    def validate_name(self, value, **kwargs):
        """Validate customer name."""
        if not value or not value.strip():
            raise MarshmallowValidationError('Customer name cannot be empty')
        if len(value) > 200:
            raise MarshmallowValidationError('Customer name cannot exceed 200 characters')
    
    @validates('email')
    def validate_email(self, value, **kwargs):
        """Validate customer email."""
        if not value or not value.strip():
            raise MarshmallowValidationError('Customer email cannot be empty')


class CustomerUpdateSchema(Schema):
    """Schema for updating a customer via API."""
    name = fields.Str(allow_none=True)
    email = fields.Email(allow_none=True)
    phone = fields.Str(allow_none=True)
    address = fields.Str(allow_none=True)
    city = fields.Str(allow_none=True)
    
    @validates('name')
    def validate_name(self, value, **kwargs):
        """Validate customer name."""
        if value is not None:
            if not value.strip():
                raise MarshmallowValidationError('Customer name cannot be empty')
            if len(value) > 200:
                raise MarshmallowValidationError('Customer name cannot exceed 200 characters')


class CustomerResponseSchema(Schema):
    """Schema for customer API response."""
    id = fields.Int(dump_only=True)
    name = fields.Str()
    email = fields.Email()
    phone = fields.Str(allow_none=True)
    address = fields.Str(allow_none=True)
    city = fields.Str(allow_none=True)
    tax_id = fields.Str(allow_none=True)
    company_name = fields.Str(allow_none=True)
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

"""
User authentication schemas for API REST.
"""

from marshmallow import Schema, fields, validates, ValidationError as MarshmallowValidationError
import re


class UserLoginSchema(Schema):
    """Schema for user login request."""
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
    
    class Meta:
        strict = True


class UserResponseSchema(Schema):
    """Schema for user response (without password)."""
    id = fields.Int(dump_only=True)
    email = fields.Email()
    username = fields.Str()
    role = fields.Str()
    is_active = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    
    class Meta:
        strict = True


class TokenResponseSchema(Schema):
    """Schema for JWT token response."""
    access_token = fields.Str(required=True)
    refresh_token = fields.Str(required=False)
    token_type = fields.Str(dump_default='Bearer')
    expires_in = fields.Int()
    user = fields.Nested(UserResponseSchema)
    
    class Meta:
        strict = True


class RefreshTokenSchema(Schema):
    """Schema for token refresh request."""
    refresh_token = fields.Str(required=True)
    
    class Meta:
        strict = True

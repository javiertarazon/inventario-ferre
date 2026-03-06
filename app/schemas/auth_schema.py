"""
API REST schemas for authentication.
"""

from marshmallow import Schema, fields, validates, ValidationError as MarshmallowValidationError
import re


class LoginSchema(Schema):
    """Schema for user login."""
    email = fields.Email(required=True, metadata={"description": "User email"})
    password = fields.Str(required=True, metadata={"description": "User password"})
    
    @validates('email')
    def validate_email(self, value, **kwargs):
        """Validate email is not empty."""
        if not value or not value.strip():
            raise MarshmallowValidationError('Email cannot be empty')
    
    @validates('password')
    def validate_password(self, value, **kwargs):
        """Validate password is not empty."""
        if not value or not value.strip():
            raise MarshmallowValidationError('Password cannot be empty')
        if len(value) < 6:
            raise MarshmallowValidationError('Password must be at least 6 characters')


class RefreshTokenSchema(Schema):
    """Schema for token refresh."""
    refresh_token = fields.Str(required=True, metadata={"description": "Refresh token"})
    
    @validates('refresh_token')
    def validate_token(self, value, **kwargs):
        """Validate refresh token is not empty."""
        if not value or not value.strip():
            raise MarshmallowValidationError('Refresh token cannot be empty')


class TokenResponseSchema(Schema):
    """Schema for token response."""
    access_token = fields.Str(metadata={"description": "JWT access token"})
    refresh_token = fields.Str(allow_none=True, metadata={"description": "JWT refresh token"})
    token_type = fields.Str(metadata={"description": "Token type (Bearer)"})
    expires_in = fields.Int(metadata={"description": "Expiration time in seconds"})


class UserLoginResponseSchema(Schema):
    """Schema for login response with user info."""
    id = fields.Int(metadata={"description": "User ID"})
    email = fields.Email(metadata={"description": "User email"})
    nombre = fields.Str(metadata={"description": "User first name"})
    apellido = fields.Str(metadata={"description": "User last name"})
    access_token = fields.Str(metadata={"description": "JWT access token"})
    refresh_token = fields.Str(allow_none=True, metadata={"description": "JWT refresh token"})
    token_type = fields.Str(metadata={"description": "Token type (Bearer)"})
    expires_in = fields.Int(metadata={"description": "Expiration time in seconds"})

"""
Authentication decorators for JWT-protected endpoints.
"""

from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from functools import wraps


def jwt_required_custom(fn):
    """
    Custom JWT required decorator that handles errors gracefully.
    Returns 401 with proper error message if JWT is missing or invalid.
    """
    @wraps(fn)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        return fn(*args, **kwargs)
    return decorated_function


def admin_required(fn):
    """
    Decorator for endpoints that require admin role.
    Checks JWT claims for 'role' == 'admin'.
    """
    @wraps(fn)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        claims = get_jwt()
        is_admin = claims.get('role') == 'admin'
        
        if not is_admin:
            return jsonify({
                'error': 'Insufficient permissions',
                'message': 'This endpoint requires admin role'
            }), 403
        
        return fn(*args, **kwargs)
    
    return decorated_function


def optional_jwt(fn):
    """
    Decorator for endpoints that work with or without JWT.
    User identity is available but not required.
    """
    @wraps(fn)
    def decorated_function(*args, **kwargs):
        try:
            # Try to get JWT identity if present
            user_id = get_jwt_identity()
            kwargs['user_id'] = user_id
        except Exception:
            # JWT not present or invalid, continue anyway
            kwargs['user_id'] = None
        
        return fn(*args, **kwargs)
    
    return decorated_function

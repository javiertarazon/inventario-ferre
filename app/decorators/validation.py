"""
Request validation decorators for JSON schema validation.
"""

from flask import request, jsonify
from marshmallow import ValidationError
from functools import wraps


def validate_json(schema_class):
    """
    Decorator to validate incoming JSON request against a Marshmallow schema.
    
    Usage:
        @app.post('/api/products')
        @validate_json(ProductCreateSchema())
        def create_product():
            data = request.get_json()  # Already validated
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def decorated_function(*args, **kwargs):
            # Check if request has JSON
            if not request.is_json:
                return jsonify({
                    'error': 'Invalid request',
                    'message': 'Request must be JSON'
                }), 400
            
            try:
                # Get data and validate
                data = request.get_json()
                schema = schema_class
                validated_data = schema.load(data)
                
                # Pass validated data to endpoint
                kwargs['validated_data'] = validated_data
                return fn(*args, **kwargs)
            
            except ValidationError as err:
                return jsonify({
                    'error': 'Validation error',
                    'errors': err.messages
                }), 400
            
            except Exception as e:
                return jsonify({
                    'error': 'Invalid JSON',
                    'message': str(e)
                }), 400
        
        return decorated_function
    return decorator


def validate_query_params(schema_class):
    """
    Decorator to validate query parameters against a Marshmallow schema.
    
    Usage:
        @app.get('/api/products')
        @validate_query_params(PaginationSchema())
        def list_products(validated_params):
            page = validated_params.get('page', 1)
            per_page = validated_params.get('per_page', 20)
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def decorated_function(*args, **kwargs):
            try:
                schema = schema_class
                validated_params = schema.load(request.args)
                kwargs['validated_params'] = validated_params
                return fn(*args, **kwargs)
            
            except ValidationError as err:
                return jsonify({
                    'error': 'Validation error',
                    'errors': err.messages
                }), 400
            
            except Exception as e:
                return jsonify({
                    'error': 'Invalid parameters',
                    'message': str(e)
                }), 400
        
        return decorated_function
    return decorator

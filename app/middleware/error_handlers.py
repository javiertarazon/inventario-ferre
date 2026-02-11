"""
Global error handlers for the application.
Handles HTTP errors and exceptions with proper logging and user-friendly messages.
"""
from flask import render_template, jsonify, request
from werkzeug.exceptions import HTTPException
import logging
from app.utils.exceptions import (
    ApplicationError, ValidationError, NotFoundError,
    AuthenticationError, AuthorizationError, DatabaseError
)

logger = logging.getLogger(__name__)


def handle_400(error):
    """Handle 400 Bad Request errors."""
    logger.warning(f'Bad request: {request.url}')
    
    if request.is_json or request.path.startswith('/api/'):
        return jsonify({
            'error': {
                'code': 'BAD_REQUEST',
                'message': 'La solicitud no pudo ser procesada',
                'status': 400
            }
        }), 400
    
    return render_template('errors/400.html'), 400


def handle_401(error):
    """Handle 401 Unauthorized errors."""
    logger.warning(f'Unauthorized access attempt: {request.url}')
    
    if request.is_json or request.path.startswith('/api/'):
        return jsonify({
            'error': {
                'code': 'UNAUTHORIZED',
                'message': 'Autenticación requerida',
                'status': 401
            }
        }), 401
    
    return render_template('errors/401.html'), 401


def handle_403(error):
    """Handle 403 Forbidden errors."""
    logger.warning(f'Forbidden access attempt: {request.url}')
    
    if request.is_json or request.path.startswith('/api/'):
        return jsonify({
            'error': {
                'code': 'FORBIDDEN',
                'message': 'No tienes permisos para acceder a este recurso',
                'status': 403
            }
        }), 403
    
    return render_template('errors/403.html'), 403


def handle_404(error):
    """Handle 404 Not Found errors."""
    logger.info(f'Page not found: {request.url}')
    
    if request.is_json or request.path.startswith('/api/'):
        return jsonify({
            'error': {
                'code': 'NOT_FOUND',
                'message': 'Recurso no encontrado',
                'status': 404
            }
        }), 404
    
    return render_template('errors/404.html'), 404


def handle_500(error):
    """Handle 500 Internal Server Error."""
    logger.error(f'Internal server error: {error}', exc_info=True)
    
    if request.is_json or request.path.startswith('/api/'):
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Error interno del servidor',
                'status': 500
            }
        }), 500
    
    return render_template('errors/500.html'), 500


def handle_exception(error):
    """Handle all unhandled exceptions."""
    # Pass through HTTP errors
    if isinstance(error, HTTPException):
        return error
    
    # Handle custom application errors
    if isinstance(error, ApplicationError):
        logger.error(f'Application error: {error.message}', exc_info=True)
        
        # Rollback database session on database errors
        if isinstance(error, DatabaseError):
            from app.extensions import db
            try:
                db.session.rollback()
            except Exception:
                pass
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({'error': error.to_dict()}), error.status_code
        
        # Render appropriate error template
        template_map = {
            ValidationError: 'errors/400.html',
            NotFoundError: 'errors/404.html',
            AuthenticationError: 'errors/401.html',
            AuthorizationError: 'errors/403.html',
            DatabaseError: 'errors/500.html'
        }
        template = template_map.get(type(error), 'errors/500.html')
        return render_template(template, error=error), error.status_code
    
    # Handle all other exceptions
    logger.exception(f'Unhandled exception: {error}')
    
    # Rollback database session on error
    from app.extensions import db
    try:
        db.session.rollback()
    except Exception:
        pass
    
    if request.is_json or request.path.startswith('/api/'):
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Ha ocurrido un error inesperado',
                'status': 500
            }
        }), 500
    
    return render_template('errors/500.html'), 500

"""
Request logging middleware.
Logs all incoming requests and responses with timing information.
"""
import time
import logging
import uuid
from flask import request, g
from functools import wraps

logger = logging.getLogger(__name__)


def setup_request_logging(app):
    """
    Set up request logging for the application.
    
    Args:
        app: Flask application instance
    """
    
    @app.before_request
    def before_request():
        """Log request details before processing."""
        # Generate unique request ID
        g.request_id = str(uuid.uuid4())
        g.start_time = time.time()
        
        # Log request details
        logger.info(
            f'Request started: {request.method} {request.path}',
            extra={
                'request_id': g.request_id,
                'method': request.method,
                'path': request.path,
                'ip': request.remote_addr,
                'user_agent': request.user_agent.string
            }
        )
    
    @app.after_request
    def after_request(response):
        """Log response details after processing."""
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            
            logger.info(
                f'Request completed: {request.method} {request.path} - {response.status_code} ({duration:.3f}s)',
                extra={
                    'request_id': getattr(g, 'request_id', 'unknown'),
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'duration': duration
                }
            )
        
        # Add request ID to response headers
        if hasattr(g, 'request_id'):
            response.headers['X-Request-ID'] = g.request_id
        
        return response
    
    @app.teardown_request
    def teardown_request(exception=None):
        """Log any exceptions that occurred during request processing."""
        if exception:
            logger.error(
                f'Request failed with exception: {exception}',
                extra={
                    'request_id': getattr(g, 'request_id', 'unknown'),
                    'method': request.method,
                    'path': request.path
                },
                exc_info=True
            )


def log_action(action: str):
    """
    Decorator to log specific actions.
    
    Args:
        action: Description of the action being performed
        
    Returns:
        Decorated function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            logger.info(
                f'Action: {action}',
                extra={
                    'request_id': getattr(g, 'request_id', 'unknown'),
                    'action': action
                }
            )
            return f(*args, **kwargs)
        return decorated_function
    return decorator

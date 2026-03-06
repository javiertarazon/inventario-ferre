"""
Application factory for the inventory management system.
Creates and configures Flask application instances.
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from app.config import get_config
from app.extensions import init_extensions, db, login_manager


def create_app(config_name=None):
    """
    Create and configure Flask application instance.
    
    Args:
        config_name: Configuration environment (development, testing, production)
        
    Returns:
        Configured Flask application instance
    """
    # Create Flask app
    app = Flask(__name__, instance_relative_config=True)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    config_class = get_config(config_name)
    app.config.from_object(config_class)
    
    # Validate configuration
    if config_name == 'production':
        config_class.validate()
    
    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass
    
    # Ensure logs folder exists
    log_dir = os.path.dirname(app.config.get('LOG_FILE', 'logs/app.log'))
    os.makedirs(log_dir, exist_ok=True)
    
    # Ensure upload folder exists
    upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    
    # Ensure backup folder exists
    backup_dir = app.config.get('BACKUP_DIR', 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    
    # Initialize extensions
    init_extensions(app)
    
    # Set up logging
    setup_logging(app)
    
    # Set up request logging middleware
    from app.middleware.request_logger import setup_request_logging
    setup_request_logging(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register CLI commands
    register_commands(app)
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))
    
    app.logger.info(f'Application started in {config_name} mode')
    
    return app


def setup_logging(app):
    """
    Configure application logging.
    
    Args:
        app: Flask application instance
    """
    if not app.debug and not app.testing:
        # File handler for general logs
        file_handler = RotatingFileHandler(
            app.config['LOG_FILE'],
            maxBytes=app.config.get('LOG_MAX_BYTES', 10485760),
            backupCount=app.config.get('LOG_BACKUP_COUNT', 10)
        )
        file_handler.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        ))
        file_handler.setLevel(getattr(logging, app.config.get('LOG_LEVEL', 'INFO')))
        app.logger.addHandler(file_handler)
        
        # File handler for errors
        error_file = app.config['LOG_FILE'].replace('.log', '_error.log')
        error_handler = RotatingFileHandler(
            error_file,
            maxBytes=app.config.get('LOG_MAX_BYTES', 10485760),
            backupCount=app.config.get('LOG_BACKUP_COUNT', 10)
        )
        error_handler.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s'
        ))
        error_handler.setLevel(logging.ERROR)
        app.logger.addHandler(error_handler)
    
    app.logger.setLevel(getattr(logging, app.config.get('LOG_LEVEL', 'INFO')))


def register_error_handlers(app):
    """
    Register error handlers for the application.
    
    Args:
        app: Flask application instance
    """
    from app.middleware.error_handlers import (
        handle_400, handle_401, handle_403, handle_404, 
        handle_500, handle_exception
    )
    
    app.register_error_handler(400, handle_400)
    app.register_error_handler(401, handle_401)
    app.register_error_handler(403, handle_403)
    app.register_error_handler(404, handle_404)
    app.register_error_handler(500, handle_500)
    app.register_error_handler(Exception, handle_exception)


def register_blueprints(app):
    """
    Register application blueprints.
    
    Args:
        app: Flask application instance
    """
    # Import blueprints
    from app.blueprints import (
        main_bp, products_bp, suppliers_bp, movements_bp,
        item_groups_bp, customers_bp, sales_orders_bp, pricing_bp,
        reports_bp
    )
    
    # Import API v1 blueprints
    from app.blueprints.api.v1 import auth_bp as api_auth_bp, products_bp as api_products_bp, customers_bp as api_customers_bp, movements_bp as api_movements_bp

    # Register traditional blueprints (Web UI)
    app.register_blueprint(main_bp)
    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(suppliers_bp, url_prefix='/suppliers')
    app.register_blueprint(movements_bp, url_prefix='/movements')
    app.register_blueprint(item_groups_bp, url_prefix='/categories')
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(sales_orders_bp, url_prefix='/orders')
    app.register_blueprint(pricing_bp, url_prefix='/pricing')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    
    # Register API v1 blueprints (REST API)
    app.register_blueprint(api_auth_bp)
    app.register_blueprint(api_products_bp)
    app.register_blueprint(api_customers_bp)
    app.register_blueprint(api_movements_bp)

    # Set up security headers
    setup_security_headers(app)


def setup_security_headers(app):
    """
    Configure HTTP security headers.
    
    Args:
        app: Flask application instance
    """
    @app.after_request
    def set_security_headers(response):
        """Add security headers to every response."""
        # Prevent MIME type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # Enable XSS protection in older browsers
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        
        # Referrer policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions policy (formerly Feature Policy)
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # Content Security Policy (permisivo para desarrollo)
        if not app.debug:
            response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' https://cdn.jsdelivr.net; style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; font-src 'self' https://cdn.jsdelivr.net; img-src 'self' data:"
        
        # HSTS header (solo en producción)
        if app.config.get('PREFERRED_URL_SCHEME') == 'https':
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response



def register_commands(app):
    """
    Register CLI commands for the application.
    
    Args:
        app: Flask application instance
    """
    @app.cli.command()
    def init_db():
        """Initialize the database."""
        db.create_all()
        app.logger.info('Database initialized successfully')
    
    @app.cli.command()
    def validate_config():
        """Validate application configuration."""
        try:
            config_class = get_config(os.environ.get('FLASK_ENV', 'development'))
            config_class.validate()
            app.logger.info('Configuration is valid')
        except ValueError as e:
            app.logger.error(f'Configuration validation error: {e}')
            return 1

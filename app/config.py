"""
Configuration management for the inventory system.
Supports multiple environments: development, testing, production.
"""
import os
from datetime import timedelta

# Directorio raíz del proyecto (un nivel arriba de app/)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


class Config:
    """Base configuration class with common settings."""
    
    # Security - MUST be set via environment variable
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    
    # Database — resolver rutas relativas de SQLite contra BASE_DIR
    _db_url = os.environ.get('DATABASE_URL', '')
    if _db_url.startswith('sqlite:///') and not os.path.isabs(_db_url[len('sqlite:///'):]):
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, _db_url[len("sqlite:///"):])}'
    else:
        SQLALCHEMY_DATABASE_URI = _db_url or f'sqlite:///{os.path.join(BASE_DIR, "instance", "inventario.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Session
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # Rate Limiting
    RATELIMIT_ENABLED = os.environ.get('RATELIMIT_ENABLED', '1').lower() in ('1', 'true', 'yes')
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')
    RATELIMIT_DEFAULT = '100 per minute'
    RATELIMIT_LOGIN = '5 per minute'
    
    # File Upload
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 10 * 1024 * 1024))
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/app.log')
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 10
    
    # Backup
    BACKUP_DIR = os.environ.get('BACKUP_DIR', 'backups')
    BACKUP_RETENTION_DAYS = int(os.environ.get('BACKUP_RETENTION_DAYS', 30))
    
    # Cache
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_REDIS_URL = os.environ.get('REDIS_URL')
    
    # Pagination
    ITEMS_PER_PAGE = int(os.environ.get('ITEMS_PER_PAGE', 20))
    
    # JWT
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Feature flags
    ENABLE_API = os.environ.get('ENABLE_API', '1').lower() in ('1', 'true', 'yes')
    ENABLE_WEBHOOKS = os.environ.get('ENABLE_WEBHOOKS', '0').lower() in ('1', 'true', 'yes')
    ENABLE_OFFLINE_MODE = os.environ.get('ENABLE_OFFLINE_MODE', '0').lower() in ('1', 'true', 'yes')

    # BCV sync
    BCV_RATE_URL = os.environ.get('BCV_RATE_URL', 'https://www.bcv.org.ve/')
    BCV_CURRENCY_CODE = os.environ.get('BCV_CURRENCY_CODE', 'USD')
    BCV_TIMEOUT_SECONDS = int(os.environ.get('BCV_TIMEOUT_SECONDS', 15))
    BCV_USER_AGENT = os.environ.get(
        'BCV_USER_AGENT',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) FerreExitoInventario/1.0'
    )
    BCV_ALLOW_INSECURE_SSL_FALLBACK = os.environ.get(
        'BCV_ALLOW_INSECURE_SSL_FALLBACK',
        '1'
    ).lower() in ('1', 'true', 'yes')
    
    @staticmethod
    def validate():
        """
        Validate required configuration values.
        Called in production to ensure all critical settings are present.
        """
        required_vars = []
        
        # Check if SECRET_KEY is set and not a default value
        secret_key = os.environ.get('SECRET_KEY', '')
        if not secret_key or len(secret_key) < 32:
            required_vars.append('SECRET_KEY (must be at least 32 characters)')
        
        # Check JWT_SECRET_KEY
        jwt_secret = os.environ.get('JWT_SECRET_KEY', '')
        if not jwt_secret or len(jwt_secret) < 32:
            required_vars.append('JWT_SECRET_KEY (must be at least 32 characters)')
        
        if required_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(required_vars)}")


class DevelopmentConfig(Config):
    """Development environment configuration."""
    
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = True
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')
    
    # Disable some security features for development
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False
    
    # Set default secrets for development if not provided
    if not Config.SECRET_KEY:
        SECRET_KEY = 'dev-key-change-in-production-min-32-characters-here!!!!'
    if not Config.JWT_SECRET_KEY:
        JWT_SECRET_KEY = 'dev-jwt-key-change-in-production-min-32-characters-here!!!'


class TestingConfig(Config):
    """Testing environment configuration."""
    
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False
    
    # Use simple cache for testing
    CACHE_TYPE = 'simple'
    
    # Set testing secrets (safe values for testing only)
    SECRET_KEY = os.environ.get('SECRET_KEY', 'test-secret-key-must-be-at-least-32-characters-long!!')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'test-jwt-secret-key-must-be-at-least-32-chars-long!!')


class ProductionConfig(Config):
    """Production environment configuration."""
    
    DEBUG = False
    TESTING = False
    
    # Enhanced security for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # Require HTTPS
    PREFERRED_URL_SCHEME = 'https'
    
    # Use Redis for caching and rate limiting in production
    CACHE_TYPE = 'redis'
    
    @staticmethod
    def validate():
        """Additional validation for production."""
        Config.validate()
        
        required_prod_vars = []
        
        if not os.environ.get('SECRET_KEY'):
            required_prod_vars.append('SECRET_KEY')
        
        if not os.environ.get('DATABASE_URL'):
            required_prod_vars.append('DATABASE_URL')
        
        if not os.environ.get('REDIS_URL'):
            required_prod_vars.append('REDIS_URL')
        
        if required_prod_vars:
            raise ValueError(
                f"Missing required production environment variables: {', '.join(required_prod_vars)}"
            )


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """
    Get configuration class based on environment.
    
    Args:
        config_name: Configuration name (development, testing, production)
        
    Returns:
        Configuration class
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    return config.get(config_name, config['default'])

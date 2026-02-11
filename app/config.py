"""
Configuration management for the inventory system.
Supports multiple environments: development, testing, production.
"""
import os
from datetime import timedelta


class Config:
    """Base configuration class with common settings."""
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{os.path.abspath("instance/inventario.db")}'
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
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL') or 'memory://'
    RATELIMIT_DEFAULT = '100 per minute'
    RATELIMIT_LOGIN = '5 per minute'
    
    # File Upload
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.environ.get('LOG_FILE') or 'logs/app.log'
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 10
    
    # Backup
    BACKUP_DIR = os.environ.get('BACKUP_DIR') or 'backups'
    BACKUP_RETENTION_DAYS = int(os.environ.get('BACKUP_RETENTION_DAYS') or 30)
    
    # Cache
    CACHE_TYPE = os.environ.get('CACHE_TYPE') or 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_REDIS_URL = os.environ.get('REDIS_URL')
    
    # Pagination
    ITEMS_PER_PAGE = int(os.environ.get('ITEMS_PER_PAGE') or 20)
    
    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    @staticmethod
    def validate():
        """Validate required configuration values."""
        required_vars = []
        
        if Config.SECRET_KEY == 'dev-secret-key-change-in-production':
            required_vars.append('SECRET_KEY')
        
        if required_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(required_vars)}")


class DevelopmentConfig(Config):
    """Development environment configuration."""
    
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = True
    LOG_LEVEL = 'DEBUG'
    
    # Disable some security features for development
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False


class TestingConfig(Config):
    """Testing environment configuration."""
    
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False
    
    # Use simple cache for testing
    CACHE_TYPE = 'simple'


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

"""
Flask extensions initialization.
Extensions are initialized here and then imported by the application factory.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_bcrypt import Bcrypt

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per minute"],
    storage_uri="memory://"
)
cache = Cache()
bcrypt = Bcrypt()


def init_extensions(app):
    """
    Initialize Flask extensions with the application instance.
    
    Args:
        app: Flask application instance
    """
    # Database
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Authentication
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'
    
    # Security
    csrf.init_app(app)
    bcrypt.init_app(app)
    
    # Rate limiting
    if app.config.get('RATELIMIT_ENABLED', True):
        limiter.init_app(app)
        # Update storage if Redis is configured
        if app.config.get('RATELIMIT_STORAGE_URL'):
            limiter.storage_uri = app.config['RATELIMIT_STORAGE_URL']
    
    # Caching
    cache.init_app(app)

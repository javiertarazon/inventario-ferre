# API v1 package

from app.blueprints.api.v1.auth import auth_bp
from app.blueprints.api.v1.products import products_bp
from app.blueprints.api.v1.customers import customers_bp
from app.blueprints.api.v1.movements import movements_bp

__all__ = ['auth_bp', 'products_bp', 'customers_bp', 'movements_bp']

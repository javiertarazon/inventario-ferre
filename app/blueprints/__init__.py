"""
Blueprints package initialization.
"""

from app.blueprints.main import main_bp
from app.blueprints.products import products_bp
from app.blueprints.suppliers import suppliers_bp
from app.blueprints.movements import movements_bp
from app.blueprints.item_groups import item_groups_bp
from app.blueprints.customers import customers_bp
from app.blueprints.sales_orders import sales_orders_bp

__all__ = [
    'main_bp',
    'products_bp',
    'suppliers_bp',
    'movements_bp',
    'item_groups_bp',
    'customers_bp',
    'sales_orders_bp'
]

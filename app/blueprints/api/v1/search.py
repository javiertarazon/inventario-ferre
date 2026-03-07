"""
API v1 global search endpoint.
"""

from flask import Blueprint, request, jsonify, url_for
from flask_login import login_required
from app.extensions import db
from app.models import Product, Customer

search_bp = Blueprint('api_search', __name__, url_prefix='/api/v1')


@search_bp.route('/search', methods=['GET'])
@login_required
def global_search():
    """Search across products and customers."""
    q = request.args.get('q', '').strip()
    if len(q) < 2:
        return jsonify({'items': []})

    items = []
    term = f'%{q}%'

    # Products
    products = (
        db.session.query(Product)
        .filter(
            Product.deleted_at.is_(None),
            db.or_(
                Product.codigo.ilike(term),
                Product.descripcion.ilike(term),
            )
        )
        .limit(8)
        .all()
    )
    for p in products:
        items.append({
            'title': p.codigo,
            'subtitle': p.descripcion,
            'icon': 'box',
            'url': url_for('products.view', product_id=p.id),
        })

    # Customers
    customers = (
        db.session.query(Customer)
        .filter(
            Customer.deleted_at.is_(None),
            db.or_(
                Customer.name.ilike(term),
                Customer.email.ilike(term),
                Customer.tax_id.ilike(term),
            )
        )
        .limit(5)
        .all()
    )
    for c in customers:
        items.append({
            'title': c.name,
            'subtitle': c.email or c.tax_id or '',
            'icon': 'person',
            'url': url_for('customers.view', customer_id=c.id),
        })

    return jsonify({'items': items})

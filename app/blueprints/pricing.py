"""
Pricing configuration blueprint - Exchange rate and price adjustment.
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from datetime import date, datetime
from decimal import Decimal

from app.models import ExchangeRate, Product, ItemGroup
from app.extensions import db
from app.services import ProductService, ItemGroupService

pricing_bp = Blueprint('pricing', __name__, url_prefix='/pricing')


@pricing_bp.route('/')
@login_required
def index():
    """Pricing configuration page."""
    try:
        # Get current exchange rate
        current_rate = ExchangeRate.get_current_rate()
        
        # Get recent rates (last 10 days)
        recent_rates = ExchangeRate.query.order_by(ExchangeRate.date.desc()).limit(10).all()
        
        # Get all categories for filter
        item_group_service = ItemGroupService()
        categories = item_group_service.get_all_groups()
        
        return render_template('pricing_config.html',
                             current_rate=current_rate,
                             recent_rates=recent_rates,
                             categories=categories)
    
    except Exception as e:
        flash(f'Error al cargar configuración: {str(e)}', 'error')
        return render_template('pricing_config.html',
                             current_rate=None,
                             recent_rates=[],
                             categories=[])


@pricing_bp.route('/update-rate', methods=['POST'])
@login_required
def update_rate():
    """Update exchange rate for today."""
    try:
        rate_value = request.form.get('rate', type=float)
        
        if not rate_value or rate_value <= 0:
            flash('La tasa de cambio debe ser mayor que cero', 'error')
            return redirect(url_for('pricing.index'))
        
        today = date.today()
        
        # Check if rate exists for today
        existing_rate = ExchangeRate.query.filter_by(date=today).first()
        
        if existing_rate:
            # Update existing rate
            existing_rate.rate = Decimal(str(rate_value))
            existing_rate.created_by = current_user.id
            existing_rate.created_at = datetime.utcnow()
        else:
            # Create new rate
            new_rate = ExchangeRate(
                date=today,
                rate=Decimal(str(rate_value)),
                created_by=current_user.id
            )
            db.session.add(new_rate)
        
        db.session.commit()
        
        flash(f'Tasa de cambio actualizada: {rate_value} Bs/$', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar tasa: {str(e)}', 'error')
    
    return redirect(url_for('pricing.index'))


@pricing_bp.route('/apply-factor', methods=['POST'])
@login_required
def apply_factor():
    """Apply adjustment factor to products."""
    try:
        factor_value = request.form.get('factor', type=float)
        apply_to = request.form.get('apply_to')  # 'all', 'category', 'product'
        target_id = request.form.get('target_id', type=int)
        
        if not factor_value or factor_value <= 0:
            flash('El factor de ajuste debe ser mayor que cero', 'error')
            return redirect(url_for('pricing.index'))
        
        factor_decimal = Decimal(str(factor_value))
        updated_count = 0
        
        if apply_to == 'all':
            # Apply to all products
            products = Product.query.filter_by(deleted_at=None).all()
            for product in products:
                product.factor_ajuste = factor_decimal
                product.updated_by = current_user.id
                product.updated_at = datetime.utcnow()
                updated_count += 1
        
        elif apply_to == 'category' and target_id:
            # Apply to category
            products = Product.query.filter_by(
                item_group_id=target_id,
                deleted_at=None
            ).all()
            for product in products:
                product.factor_ajuste = factor_decimal
                product.updated_by = current_user.id
                product.updated_at = datetime.utcnow()
                updated_count += 1
        
        elif apply_to == 'product' and target_id:
            # Apply to single product
            product = Product.query.get(target_id)
            if product and product.deleted_at is None:
                product.factor_ajuste = factor_decimal
                product.updated_by = current_user.id
                product.updated_at = datetime.utcnow()
                updated_count = 1
        
        db.session.commit()
        
        flash(f'Factor de ajuste {factor_value} aplicado a {updated_count} producto(s)', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al aplicar factor: {str(e)}', 'error')
    
    return redirect(url_for('pricing.index'))


@pricing_bp.route('/search-products')
@login_required
def search_products():
    """Search products and show calculated prices."""
    try:
        query = request.args.get('q', '').strip()
        category_id = request.args.get('category_id', type=int)
        
        # Get current rate
        current_rate = ExchangeRate.get_current_rate()
        rate_value = float(current_rate.rate) if current_rate else 36.50
        
        # Build query
        products_query = Product.query.filter_by(deleted_at=None)
        
        if query:
            products_query = products_query.filter(
                db.or_(
                    Product.codigo.ilike(f'%{query}%'),
                    Product.descripcion.ilike(f'%{query}%')
                )
            )
        
        if category_id:
            products_query = products_query.filter_by(item_group_id=category_id)
        
        products = products_query.limit(50).all()
        
        # Calculate prices
        results = []
        for product in products:
            precio_bs = float(product.precio_dolares) * rate_value
            precio_final = precio_bs * float(product.factor_ajuste)
            
            results.append({
                'id': product.id,
                'codigo': product.codigo,
                'descripcion': product.descripcion,
                'precio_dolares': float(product.precio_dolares),
                'factor_ajuste': float(product.factor_ajuste),
                'precio_bs': round(precio_bs, 2),
                'precio_final_bs': round(precio_final, 2),
                'categoria': product.item_group.name if product.item_group else 'Sin categoría'
            })
        
        return jsonify({
            'success': True,
            'rate': rate_value,
            'products': results,
            'count': len(results)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

"""
Pricing configuration blueprint - Exchange rate and price adjustment.
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from datetime import date

from app.models import ExchangeRate, Product, ItemGroup, Proveedor
from app.extensions import db
from app.services import ProductService, ItemGroupService
from app.services.exchange_rate_service import ExchangeRateService

pricing_bp = Blueprint('pricing', __name__, url_prefix='/pricing')


@pricing_bp.route('/')
@login_required
def index():
    """Pricing configuration page."""
    try:
        rate_service = ExchangeRateService()
        current_rate = rate_service.get_current_rate()
        recent_rates = rate_service.get_recent_rates(limit=10)
        
        # Get all categories for filter
        item_group_service = ItemGroupService()
        categories = item_group_service.get_all_groups()
        
        # Get all proveedores for filter
        proveedores = Proveedor.query.filter_by(deleted_at=None).order_by(Proveedor.nombre).all()
        
        return render_template('pricing_config.html',
                             current_rate=current_rate,
                             recent_rates=recent_rates,
                             categories=categories,
                             proveedores=proveedores)
    
    except Exception as e:
        flash(f'Error al cargar configuración: {str(e)}', 'error')
        return render_template('pricing_config.html',
                             current_rate=None,
                             recent_rates=[],
                             categories=[],
                             proveedores=[])


@pricing_bp.route('/update-rate', methods=['POST'])
@login_required
def update_rate():
    """Update exchange rate for today."""
    try:
        rate_value = request.form.get('rate', type=float)
        rate_record, _ = ExchangeRateService().upsert_rate(rate_value, target_date=date.today(), user_id=current_user.id)
        flash(f'Tasa de cambio actualizada: {float(rate_record.rate):.4f} Bs/$', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar tasa: {str(e)}', 'error')
    
    return redirect(url_for('pricing.index'))


@pricing_bp.route('/sync-rate', methods=['POST'])
@login_required
def sync_rate():
    """Fetch today's rate directly from BCV and store it."""
    try:
        result = ExchangeRateService().sync_today_from_bcv(user_id=current_user.id)
        action = 'registrada' if result['created'] else 'actualizada'
        flash(
            f"Tasa BCV sincronizada correctamente: {result['rate']:.4f} Bs/$ ({action})",
            'success'
        )
    except Exception as e:
        db.session.rollback()
        flash(f'Error al sincronizar tasa BCV: {str(e)}', 'error')

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
def search_products():
    """Search products and show calculated prices."""
    if not current_user.is_authenticated:
        return jsonify({
            'success': False,
            'error': 'Debe iniciar sesi\u00f3n para acceder a esta funci\u00f3n'
        }), 401
    
    try:
        query = request.args.get('q', '').strip()
        category_id = request.args.get('category_id', type=int)
        proveedor_id = request.args.get('proveedor_id', type=int)
        
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
        
        if proveedor_id:
            products_query = products_query.filter_by(proveedor_id=proveedor_id)
        
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
                'categoria': product.item_group.name if product.item_group else 'Sin categoría',
                'proveedor': product.proveedor.nombre if product.proveedor else 'Sin proveedor'
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

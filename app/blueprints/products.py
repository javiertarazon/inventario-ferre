"""
Products blueprint - Routes for product management.
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.exceptions import BadRequest

from app.services import ProductService, SupplierService
from app.utils.exceptions import ValidationError, NotFoundError, BusinessLogicError, DatabaseError

products_bp = Blueprint('products', __name__)


@products_bp.route('/')
@login_required
def index():
    """List all products with search and pagination."""
    try:
        # Get query parameters
        query = request.args.get('q', '')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Get products
        product_service = ProductService()
        result = product_service.search_products(query=query, page=page, per_page=per_page)
        
        return render_template('productos.html',
                             productos=result.items,
                             pagination=result,
                             query=query)
    
    except Exception as e:
        flash(f'Error al cargar productos: {str(e)}', 'error')
        return render_template('productos.html', productos=[], pagination=None)


@products_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new product."""
    if request.method == 'GET':
        # Get suppliers and item groups for dropdowns
        supplier_service = SupplierService()
        suppliers = supplier_service.get_all_suppliers()
        
        from app.services import ItemGroupService
        item_group_service = ItemGroupService()
        item_groups = item_group_service.get_all_groups()
        
        return render_template('productos_form.html', producto=None, suppliers=suppliers, item_groups=item_groups)
    
    try:
        # Get form data
        data = {
            'codigo': request.form.get('codigo', '').strip(),
            'descripcion': request.form.get('descripcion', '').strip(),
            'stock': int(request.form.get('stock', 0)),
            'precio_dolares': float(request.form.get('precio_dolares', 0)),
            'factor_ajuste': float(request.form.get('factor_ajuste', 1.0)),
            'proveedor_id': request.form.get('proveedor_id', type=int),
            'item_group_id': request.form.get('item_group_id', type=int) or None,
            'reorder_point': request.form.get('reorder_point', type=int) or None,
            'reorder_quantity': request.form.get('reorder_quantity', type=int) or None
        }
        
        # Remove empty codigo to trigger auto-generation
        if not data['codigo']:
            data.pop('codigo')
        
        # Create product
        product_service = ProductService()
        product = product_service.create_product(data, current_user.id)
        
        flash(f'Producto {product.codigo} creado exitosamente', 'success')
        return redirect(url_for('products.index'))
    
    except ValidationError as e:
        flash(f'Error de validación: {e.message}', 'error')
        supplier_service = SupplierService()
        suppliers = supplier_service.get_all_suppliers()
        from app.services import ItemGroupService
        item_group_service = ItemGroupService()
        item_groups = item_group_service.get_all_groups()
        return render_template('productos_form.html', producto=None, suppliers=suppliers, item_groups=item_groups, form_data=request.form)
    
    except (BusinessLogicError, DatabaseError) as e:
        flash(f'Error: {e.message}', 'error')
        supplier_service = SupplierService()
        suppliers = supplier_service.get_all_suppliers()
        return render_template('productos_form.html', producto=None, suppliers=suppliers, form_data=request.form)


@products_bp.route('/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(product_id):
    """Edit existing product."""
    product_service = ProductService()
    
    if request.method == 'GET':
        try:
            product = product_service.get_product(product_id)
            if not product:
                flash('Producto no encontrado', 'error')
                return redirect(url_for('products.index'))
            
            supplier_service = SupplierService()
            suppliers = supplier_service.get_all_suppliers()
            
            from app.services import ItemGroupService
            item_group_service = ItemGroupService()
            item_groups = item_group_service.get_all_groups()
            
            return render_template('productos_form.html', producto=product, suppliers=suppliers, item_groups=item_groups)
        
        except Exception as e:
            flash(f'Error al cargar producto: {str(e)}', 'error')
            return redirect(url_for('products.index'))
    
    try:
        # Get form data
        data = {
            'codigo': request.form.get('codigo', '').strip(),
            'descripcion': request.form.get('descripcion', '').strip(),
            'stock': int(request.form.get('stock', 0)),
            'precio_dolares': float(request.form.get('precio_dolares', 0)),
            'factor_ajuste': float(request.form.get('factor_ajuste', 1.0)),
            'proveedor_id': request.form.get('proveedor_id', type=int),
            'item_group_id': request.form.get('item_group_id', type=int) or None,
            'reorder_point': request.form.get('reorder_point', type=int) or None,
            'reorder_quantity': request.form.get('reorder_quantity', type=int) or None
        }
        
        # Update product
        product = product_service.update_product(product_id, data, current_user.id)
        
        flash(f'Producto {product.codigo} actualizado exitosamente', 'success')
        return redirect(url_for('products.index'))
    
    except NotFoundError:
        flash('Producto no encontrado', 'error')
        return redirect(url_for('products.index'))
    
    except ValidationError as e:
        flash(f'Error de validación: {e.message}', 'error')
        product = product_service.get_product(product_id)
        supplier_service = SupplierService()
        suppliers = supplier_service.get_all_suppliers()
        from app.services import ItemGroupService
        item_group_service = ItemGroupService()
        item_groups = item_group_service.get_all_groups()
        return render_template('productos_form.html', producto=product, suppliers=suppliers, item_groups=item_groups, form_data=request.form)
    
    except ValidationError as e:
        flash(f'Error de validación: {e.message}', 'error')
        product = product_service.get_product(product_id)
        supplier_service = SupplierService()
        suppliers = supplier_service.get_all_suppliers()
        return render_template('productos_form.html', producto=product, suppliers=suppliers, form_data=request.form)
    
    except (BusinessLogicError, DatabaseError) as e:
        flash(f'Error: {e.message}', 'error')
        product = product_service.get_product(product_id)
        supplier_service = SupplierService()
        suppliers = supplier_service.get_all_suppliers()
        return render_template('productos_form.html', producto=product, suppliers=suppliers, form_data=request.form)


@products_bp.route('/<int:product_id>/delete', methods=['POST'])
@login_required
def delete(product_id):
    """Delete product (soft delete)."""
    try:
        product_service = ProductService()
        product_service.delete_product(product_id, current_user.id)
        
        flash('Producto eliminado exitosamente', 'success')
    
    except NotFoundError:
        flash('Producto no encontrado', 'error')
    
    except (BusinessLogicError, DatabaseError) as e:
        flash(f'Error al eliminar producto: {e.message}', 'error')
    
    return redirect(url_for('products.index'))


@products_bp.route('/<int:product_id>')
@login_required
def view(product_id):
    """View product details."""
    try:
        product_service = ProductService()
        product = product_service.get_product(product_id)
        
        if not product:
            flash('Producto no encontrado', 'error')
            return redirect(url_for('products.index'))
        
        # Get movement history
        from app.services import MovementService
        movement_service = MovementService()
        movements = movement_service.get_movement_history(product_id)
        
        return render_template('productos_detail.html', producto=product, movements=movements)
    
    except Exception as e:
        flash(f'Error al cargar producto: {str(e)}', 'error')
        return redirect(url_for('products.index'))


@products_bp.route('/low-stock')
@login_required
def low_stock():
    """List products with low stock."""
    try:
        threshold = request.args.get('threshold', 10, type=int)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        product_service = ProductService()
        result = product_service.get_low_stock_products(threshold=threshold, page=page, per_page=per_page)
        
        return render_template('productos_low_stock.html',
                             productos=result.items,
                             pagination=result,
                             threshold=threshold)
    
    except Exception as e:
        flash(f'Error al cargar productos con bajo stock: {str(e)}', 'error')
        return render_template('productos_low_stock.html', productos=[], pagination=None)

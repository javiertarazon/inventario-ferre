"""
Sales Orders blueprint - Routes for sales order management.
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user

from app.services import SalesOrderService, CustomerService, ProductService
from app.utils.exceptions import ValidationError, NotFoundError, BusinessLogicError, DatabaseError

sales_orders_bp = Blueprint('sales_orders', __name__)


@sales_orders_bp.route('/')
@login_required
def index():
    """List all sales orders with filtering and pagination."""
    try:
        # Get query parameters
        status = request.args.get('status', '')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Get sales orders
        sales_order_service = SalesOrderService()
        
        if status:
            result = sales_order_service.get_orders_by_status(status, page=page, per_page=per_page)
        else:
            result = sales_order_service.get_all_orders(page=page, per_page=per_page)
        
        return render_template('sales_orders.html',
                             orders=result.items,
                             pagination=result,
                             status_filter=status)
    
    except Exception as e:
        flash(f'Error al cargar órdenes: {str(e)}', 'error')
        return render_template('sales_orders.html', orders=[], pagination=None)


@sales_orders_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new sales order."""
    if request.method == 'GET':
        # Get customers and products for dropdowns
        customer_service = CustomerService()
        product_service = ProductService()
        customers = customer_service.get_all_customers()
        products = product_service.get_all_products()
        return render_template('sales_orders_form.html', order=None, customers=customers, products=products)
    
    try:
        # Get form data
        customer_id = request.form.get('customer_id', type=int)
        notes = request.form.get('notes', '').strip() or None
        
        # Get order items from form
        items = []
        product_ids = request.form.getlist('product_id[]')
        quantities = request.form.getlist('quantity[]')
        prices = request.form.getlist('unit_price[]')
        
        for i in range(len(product_ids)):
            if product_ids[i]:
                items.append({
                    'product_id': int(product_ids[i]),
                    'quantity': int(quantities[i]),
                    'unit_price': float(prices[i])
                })
        
        if not items:
            raise ValidationError('Debe agregar al menos un producto a la orden')
        
        # Create sales order
        sales_order_service = SalesOrderService()
        order = sales_order_service.create_sales_order(
            customer_id=customer_id,
            items=items,
            notes=notes,
            user_id=current_user.id
        )
        
        flash(f'Orden {order.order_number} creada exitosamente', 'success')
        return redirect(url_for('sales_orders.view', order_id=order.id))
    
    except ValidationError as e:
        flash(f'Error de validación: {e.message}', 'error')
        customer_service = CustomerService()
        product_service = ProductService()
        customers = customer_service.get_all_customers()
        products = product_service.get_all_products()
        return render_template('sales_orders_form.html', order=None, customers=customers, products=products, form_data=request.form)
    
    except (BusinessLogicError, DatabaseError) as e:
        flash(f'Error: {e.message}', 'error')
        customer_service = CustomerService()
        product_service = ProductService()
        customers = customer_service.get_all_customers()
        products = product_service.get_all_products()
        return render_template('sales_orders_form.html', order=None, customers=customers, products=products, form_data=request.form)


@sales_orders_bp.route('/<int:order_id>')
@login_required
def view(order_id):
    """View sales order details."""
    try:
        sales_order_service = SalesOrderService()
        order = sales_order_service.get_sales_order(order_id)
        
        if not order:
            flash('Orden no encontrada', 'error')
            return redirect(url_for('sales_orders.index'))
        
        return render_template('sales_orders_detail.html', order=order)
    
    except Exception as e:
        flash(f'Error al cargar orden: {str(e)}', 'error')
        return redirect(url_for('sales_orders.index'))


@sales_orders_bp.route('/<int:order_id>/confirm', methods=['POST'])
@login_required
def confirm(order_id):
    """Confirm sales order and reduce stock."""
    try:
        sales_order_service = SalesOrderService()
        order = sales_order_service.confirm_order(order_id, current_user.id)
        
        flash(f'Orden {order.order_number} confirmada exitosamente', 'success')
    
    except NotFoundError:
        flash('Orden no encontrada', 'error')
    
    except (ValidationError, BusinessLogicError, DatabaseError) as e:
        flash(f'Error al confirmar orden: {e.message}', 'error')
    
    return redirect(url_for('sales_orders.view', order_id=order_id))


@sales_orders_bp.route('/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel(order_id):
    """Cancel sales order and restore stock if confirmed."""
    try:
        sales_order_service = SalesOrderService()
        order = sales_order_service.cancel_order(order_id, current_user.id)
        
        flash(f'Orden {order.order_number} cancelada exitosamente', 'success')
    
    except NotFoundError:
        flash('Orden no encontrada', 'error')
    
    except (ValidationError, BusinessLogicError, DatabaseError) as e:
        flash(f'Error al cancelar orden: {e.message}', 'error')
    
    return redirect(url_for('sales_orders.view', order_id=order_id))


@sales_orders_bp.route('/<int:order_id>/status', methods=['POST'])
@login_required
def update_status(order_id):
    """Update sales order status."""
    try:
        new_status = request.form.get('status', '').strip()
        
        if not new_status:
            raise ValidationError('Estado requerido')
        
        sales_order_service = SalesOrderService()
        order = sales_order_service.update_order_status(order_id, new_status, current_user.id)
        
        flash(f'Estado de orden {order.order_number} actualizado a {new_status}', 'success')
    
    except NotFoundError:
        flash('Orden no encontrada', 'error')
    
    except (ValidationError, BusinessLogicError, DatabaseError) as e:
        flash(f'Error al actualizar estado: {e.message}', 'error')
    
    return redirect(url_for('sales_orders.view', order_id=order_id))


@sales_orders_bp.route('/api/product/<int:product_id>')
@login_required
def get_product_info(product_id):
    """API endpoint to get product info for order form."""
    try:
        product_service = ProductService()
        product = product_service.get_product(product_id)
        
        if not product:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        return jsonify({
            'id': product.id,
            'codigo': product.codigo,
            'descripcion': product.descripcion,
            'stock': product.stock,
            'precio_dolares': float(product.precio_dolares or 0)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

"""
Customers blueprint - Routes for customer management.
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user

from app.services import CustomerService
from app.utils.exceptions import ValidationError, NotFoundError, BusinessLogicError, DatabaseError

customers_bp = Blueprint('customers', __name__)


@customers_bp.route('/')
@login_required
def index():
    """List all customers with search and pagination."""
    try:
        # Get query parameters
        query = request.args.get('q', '')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Get customers
        customer_service = CustomerService()
        result = customer_service.search_customers(query=query, page=page, per_page=per_page)
        
        return render_template('customers.html',
                             customers=result.items,
                             pagination=result,
                             query=query)
    
    except Exception as e:
        flash(f'Error al cargar clientes: {str(e)}', 'error')
        return render_template('customers.html', customers=[], pagination=None)


@customers_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new customer."""
    if request.method == 'GET':
        return render_template('customers_form.html', customer=None)
    
    try:
        # Get form data
        data = {
            'name': request.form.get('name', '').strip(),
            'email': request.form.get('email', '').strip() or None,
            'phone': request.form.get('phone', '').strip() or None,
            'tax_id': request.form.get('tax_id', '').strip() or None,
            'billing_address': request.form.get('billing_address', '').strip() or None,
            'shipping_address': request.form.get('shipping_address', '').strip() or None,
            'credit_limit': float(request.form.get('credit_limit', 0) or 0),
            'payment_terms': request.form.get('payment_terms', '').strip() or None,
            'notes': request.form.get('notes', '').strip() or None
        }
        
        # Create customer
        customer_service = CustomerService()
        customer = customer_service.create_customer(data, current_user.id)
        
        flash(f'Cliente "{customer.name}" creado exitosamente', 'success')
        return redirect(url_for('customers.index'))
    
    except ValidationError as e:
        flash(f'Error de validación: {e.message}', 'error')
        return render_template('customers_form.html', customer=None, form_data=request.form)
    
    except (BusinessLogicError, DatabaseError) as e:
        flash(f'Error: {e.message}', 'error')
        return render_template('customers_form.html', customer=None, form_data=request.form)


@customers_bp.route('/<int:customer_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(customer_id):
    """Edit existing customer."""
    customer_service = CustomerService()
    
    if request.method == 'GET':
        try:
            customer = customer_service.get_customer(customer_id)
            if not customer:
                flash('Cliente no encontrado', 'error')
                return redirect(url_for('customers.index'))
            
            return render_template('customers_form.html', customer=customer)
        
        except Exception as e:
            flash(f'Error al cargar cliente: {str(e)}', 'error')
            return redirect(url_for('customers.index'))
    
    try:
        # Get form data
        data = {
            'name': request.form.get('name', '').strip(),
            'email': request.form.get('email', '').strip() or None,
            'phone': request.form.get('phone', '').strip() or None,
            'tax_id': request.form.get('tax_id', '').strip() or None,
            'billing_address': request.form.get('billing_address', '').strip() or None,
            'shipping_address': request.form.get('shipping_address', '').strip() or None,
            'credit_limit': float(request.form.get('credit_limit', 0) or 0),
            'payment_terms': request.form.get('payment_terms', '').strip() or None,
            'notes': request.form.get('notes', '').strip() or None
        }
        
        # Update customer
        customer = customer_service.update_customer(customer_id, data, current_user.id)
        
        flash(f'Cliente "{customer.name}" actualizado exitosamente', 'success')
        return redirect(url_for('customers.index'))
    
    except NotFoundError:
        flash('Cliente no encontrado', 'error')
        return redirect(url_for('customers.index'))
    
    except ValidationError as e:
        flash(f'Error de validación: {e.message}', 'error')
        customer = customer_service.get_customer(customer_id)
        return render_template('customers_form.html', customer=customer, form_data=request.form)
    
    except (BusinessLogicError, DatabaseError) as e:
        flash(f'Error: {e.message}', 'error')
        customer = customer_service.get_customer(customer_id)
        return render_template('customers_form.html', customer=customer, form_data=request.form)


@customers_bp.route('/<int:customer_id>/delete', methods=['POST'])
@login_required
def delete(customer_id):
    """Delete customer (soft delete)."""
    try:
        customer_service = CustomerService()
        customer_service.delete_customer(customer_id, current_user.id)
        
        flash('Cliente eliminado exitosamente', 'success')
    
    except NotFoundError:
        flash('Cliente no encontrado', 'error')
    
    except (BusinessLogicError, DatabaseError) as e:
        flash(f'Error al eliminar cliente: {e.message}', 'error')
    
    return redirect(url_for('customers.index'))


@customers_bp.route('/<int:customer_id>')
@login_required
def view(customer_id):
    """View customer details and orders."""
    try:
        customer_service = CustomerService()
        customer = customer_service.get_customer(customer_id)
        
        if not customer:
            flash('Cliente no encontrado', 'error')
            return redirect(url_for('customers.index'))
        
        # Get customer's orders
        from app.services import SalesOrderService
        sales_order_service = SalesOrderService()
        orders = sales_order_service.get_customer_orders(customer_id)
        
        return render_template('customers_detail.html', customer=customer, orders=orders)
    
    except Exception as e:
        flash(f'Error al cargar cliente: {str(e)}', 'error')
        return redirect(url_for('customers.index'))

"""
Movements blueprint - Routes for inventory movement management.
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from datetime import datetime, date

from app.services import MovementService, ProductService
from app.utils.exceptions import ValidationError, NotFoundError, BusinessLogicError, DatabaseError

movements_bp = Blueprint('movements', __name__)


@movements_bp.route('/')
@login_required
def index():
    """List movements with date filtering and pagination."""
    try:
        # Get query parameters
        fecha_str = request.args.get('fecha', date.today().isoformat())
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        # Parse date
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            fecha = date.today()
        
        # Get movements
        movement_service = MovementService()
        result = movement_service.get_movements_by_date(fecha=fecha, page=page, per_page=per_page)
        
        return render_template('movimientos.html',
                             movimientos=result.items,
                             pagination=result,
                             fecha=fecha)
    
    except Exception as e:
        flash(f'Error al cargar movimientos: {str(e)}', 'error')
        return render_template('movimientos.html', movimientos=[], pagination=None, fecha=date.today())


@movements_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new movement."""
    if request.method == 'GET':
        # Get products for dropdown - use get_all_products instead of search with high limit
        product_service = ProductService()
        productos = product_service.get_all_products()
        return render_template('movimientos_form.html', movimiento=None, productos=productos)
    
    try:
        # Get form data
        data = {
            'tipo': request.form.get('tipo', '').strip().upper(),
            'producto_id': int(request.form.get('producto_id')),
            'cantidad': int(request.form.get('cantidad')),
            'descripcion': request.form.get('descripcion', '').strip(),
            'fecha': request.form.get('fecha', date.today().isoformat())
        }
        
        # Parse date
        if isinstance(data['fecha'], str):
            data['fecha'] = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
        
        # Remove empty descripcion
        if not data['descripcion']:
            data.pop('descripcion')
        
        # Create movement
        movement_service = MovementService()
        movement = movement_service.create_movement(data, current_user.id)
        
        flash(f'Movimiento registrado exitosamente', 'success')
        return redirect(url_for('movements.index'))
    
    except ValidationError as e:
        flash(f'Error de validación: {e.message}', 'error')
        product_service = ProductService()
        productos = product_service.get_all_products()
        return render_template('movimientos_form.html', movimiento=None, productos=productos, form_data=request.form)
    
    except NotFoundError as e:
        flash(f'Error: {e.message}', 'error')
        product_service = ProductService()
        productos = product_service.get_all_products()
        return render_template('movimientos_form.html', movimiento=None, productos=productos, form_data=request.form)
    
    except (BusinessLogicError, DatabaseError) as e:
        flash(f'Error: {e.message}', 'error')
        product_service = ProductService()
        productos = product_service.get_all_products()
        return render_template('movimientos_form.html', movimiento=None, productos=productos, form_data=request.form)


@movements_bp.route('/<int:movement_id>')
@login_required
def view(movement_id):
    """View movement details."""
    try:
        movement_service = MovementService()
        movement = movement_service.get_movement(movement_id)
        
        if not movement:
            flash('Movimiento no encontrado', 'error')
            return redirect(url_for('movements.index'))
        
        return render_template('movimientos_detail.html', movimiento=movement)
    
    except Exception as e:
        flash(f'Error al cargar movimiento: {str(e)}', 'error')
        return redirect(url_for('movements.index'))


@movements_bp.route('/today')
@login_required
def today():
    """Show today's movements."""
    return redirect(url_for('movements.index', fecha=date.today().isoformat()))


@movements_bp.route('/history/<int:product_id>')
@login_required
def product_history(product_id):
    """View movement history for a product."""
    try:
        # Get date range from query params
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        start_date = None
        end_date = None
        
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        # Get product
        product_service = ProductService()
        product = product_service.get_product(product_id)
        
        if not product:
            flash('Producto no encontrado', 'error')
            return redirect(url_for('products.index'))
        
        # Get movement history
        movement_service = MovementService()
        movements = movement_service.get_movement_history(
            product_id=product_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return render_template('movimientos_history.html',
                             producto=product,
                             movimientos=movements,
                             start_date=start_date,
                             end_date=end_date)
    
    except Exception as e:
        flash(f'Error al cargar historial: {str(e)}', 'error')
        return redirect(url_for('products.index'))

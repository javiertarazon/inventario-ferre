"""
Suppliers blueprint - Routes for supplier management.
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user

from app.services import SupplierService
from app.utils.exceptions import ValidationError, NotFoundError, BusinessLogicError, DatabaseError

suppliers_bp = Blueprint('suppliers', __name__)


@suppliers_bp.route('/')
@login_required
def index():
    """List all suppliers with pagination."""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Get suppliers
        supplier_service = SupplierService()
        result = supplier_service.list_suppliers(page=page, per_page=per_page)
        
        return render_template('proveedores.html',
                             proveedores=result.items,
                             pagination=result)
    
    except Exception as e:
        flash(f'Error al cargar proveedores: {str(e)}', 'error')
        return render_template('proveedores.html', proveedores=[], pagination=None)


@suppliers_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new supplier."""
    if request.method == 'GET':
        return render_template('proveedores_form.html', proveedor=None)
    
    try:
        # Get form data
        data = {
            'nombre': request.form.get('nombre', '').strip(),
            'rif': request.form.get('rif', '').strip(),
            'rubro_material': request.form.get('rubro_material', '').strip(),
            'telefono': request.form.get('telefono', '').strip(),
            'direccion': request.form.get('direccion', '').strip(),
            'email': request.form.get('email', '').strip()
        }
        
        # Remove empty optional fields
        data = {k: v for k, v in data.items() if v}
        
        # Create supplier
        supplier_service = SupplierService()
        supplier = supplier_service.create_supplier(data, current_user.id)
        
        flash(f'Proveedor {supplier.nombre} creado exitosamente', 'success')
        return redirect(url_for('suppliers.index'))
    
    except ValidationError as e:
        flash(f'Error de validación: {e.message}', 'error')
        return render_template('proveedores_form.html', proveedor=None, form_data=request.form)
    
    except (BusinessLogicError, DatabaseError) as e:
        flash(f'Error: {e.message}', 'error')
        return render_template('proveedores_form.html', proveedor=None, form_data=request.form)


@suppliers_bp.route('/<int:supplier_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(supplier_id):
    """Edit existing supplier."""
    supplier_service = SupplierService()
    
    if request.method == 'GET':
        try:
            supplier = supplier_service.get_supplier(supplier_id)
            if not supplier:
                flash('Proveedor no encontrado', 'error')
                return redirect(url_for('suppliers.index'))
            
            return render_template('proveedores_form.html', proveedor=supplier)
        
        except Exception as e:
            flash(f'Error al cargar proveedor: {str(e)}', 'error')
            return redirect(url_for('suppliers.index'))
    
    try:
        # Get form data
        data = {
            'nombre': request.form.get('nombre', '').strip(),
            'rif': request.form.get('rif', '').strip(),
            'rubro_material': request.form.get('rubro_material', '').strip(),
            'telefono': request.form.get('telefono', '').strip(),
            'direccion': request.form.get('direccion', '').strip(),
            'email': request.form.get('email', '').strip()
        }
        
        # Remove empty optional fields
        data = {k: v for k, v in data.items() if v}
        
        # Update supplier
        supplier = supplier_service.update_supplier(supplier_id, data, current_user.id)
        
        flash(f'Proveedor {supplier.nombre} actualizado exitosamente', 'success')
        return redirect(url_for('suppliers.index'))
    
    except NotFoundError:
        flash('Proveedor no encontrado', 'error')
        return redirect(url_for('suppliers.index'))
    
    except ValidationError as e:
        flash(f'Error de validación: {e.message}', 'error')
        supplier = supplier_service.get_supplier(supplier_id)
        return render_template('proveedores_form.html', proveedor=supplier, form_data=request.form)
    
    except (BusinessLogicError, DatabaseError) as e:
        flash(f'Error: {e.message}', 'error')
        supplier = supplier_service.get_supplier(supplier_id)
        return render_template('proveedores_form.html', proveedor=supplier, form_data=request.form)


@suppliers_bp.route('/<int:supplier_id>/delete', methods=['POST'])
@login_required
def delete(supplier_id):
    """Delete supplier (soft delete)."""
    try:
        supplier_service = SupplierService()
        supplier_service.delete_supplier(supplier_id, current_user.id)
        
        flash('Proveedor eliminado exitosamente', 'success')
    
    except NotFoundError:
        flash('Proveedor no encontrado', 'error')
    
    except (BusinessLogicError, DatabaseError) as e:
        flash(f'Error al eliminar proveedor: {e.message}', 'error')
    
    return redirect(url_for('suppliers.index'))


@suppliers_bp.route('/<int:supplier_id>')
@login_required
def view(supplier_id):
    """View supplier details and products."""
    try:
        supplier_service = SupplierService()
        supplier = supplier_service.get_supplier(supplier_id)
        
        if not supplier:
            flash('Proveedor no encontrado', 'error')
            return redirect(url_for('suppliers.index'))
        
        # Get products from this supplier
        from app.services import ProductService
        product_service = ProductService()
        products_result = product_service.search_products(
            filters={'proveedor_id': supplier_id},
            page=1,
            per_page=100
        )
        
        return render_template('proveedores_detail.html',
                             proveedor=supplier,
                             productos=products_result.items)
    
    except Exception as e:
        flash(f'Error al cargar proveedor: {str(e)}', 'error')
        return redirect(url_for('suppliers.index'))

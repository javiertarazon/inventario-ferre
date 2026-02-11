"""
Item Groups blueprint - Routes for category management.
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user

from app.services import ItemGroupService
from app.utils.exceptions import ValidationError, NotFoundError, BusinessLogicError, DatabaseError

item_groups_bp = Blueprint('item_groups', __name__)


@item_groups_bp.route('/')
@login_required
def index():
    """List all item groups."""
    try:
        item_group_service = ItemGroupService()
        
        # Get root groups (no parent)
        root_groups = item_group_service.get_root_groups()
        
        return render_template('item_groups.html', groups=root_groups)
    
    except Exception as e:
        flash(f'Error al cargar categorías: {str(e)}', 'error')
        return render_template('item_groups.html', groups=[])


@item_groups_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new item group."""
    if request.method == 'GET':
        # Get all groups for parent selection
        item_group_service = ItemGroupService()
        all_groups = item_group_service.get_all_groups()
        return render_template('item_groups_form.html', group=None, all_groups=all_groups)
    
    try:
        # Get form data
        data = {
            'name': request.form.get('name', '').strip(),
            'description': request.form.get('description', '').strip() or None,
            'parent_id': request.form.get('parent_id', type=int) or None,
            'color': request.form.get('color', '').strip() or None,
            'icon': request.form.get('icon', '').strip() or None
        }
        
        # Create item group
        item_group_service = ItemGroupService()
        group = item_group_service.create_item_group(data, current_user.id)
        
        flash(f'Categoría "{group.name}" creada exitosamente', 'success')
        return redirect(url_for('item_groups.index'))
    
    except ValidationError as e:
        flash(f'Error de validación: {e.message}', 'error')
        item_group_service = ItemGroupService()
        all_groups = item_group_service.get_all_groups()
        return render_template('item_groups_form.html', group=None, all_groups=all_groups, form_data=request.form)
    
    except (BusinessLogicError, DatabaseError) as e:
        flash(f'Error: {e.message}', 'error')
        item_group_service = ItemGroupService()
        all_groups = item_group_service.get_all_groups()
        return render_template('item_groups_form.html', group=None, all_groups=all_groups, form_data=request.form)


@item_groups_bp.route('/<int:group_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(group_id):
    """Edit existing item group."""
    item_group_service = ItemGroupService()
    
    if request.method == 'GET':
        try:
            group = item_group_service.get_item_group(group_id)
            if not group:
                flash('Categoría no encontrada', 'error')
                return redirect(url_for('item_groups.index'))
            
            # Get all groups except current and its children (to prevent circular references)
            all_groups = [g for g in item_group_service.get_all_groups() if g.id != group_id]
            return render_template('item_groups_form.html', group=group, all_groups=all_groups)
        
        except Exception as e:
            flash(f'Error al cargar categoría: {str(e)}', 'error')
            return redirect(url_for('item_groups.index'))
    
    try:
        # Get form data
        data = {
            'name': request.form.get('name', '').strip(),
            'description': request.form.get('description', '').strip() or None,
            'parent_id': request.form.get('parent_id', type=int) or None,
            'color': request.form.get('color', '').strip() or None,
            'icon': request.form.get('icon', '').strip() or None
        }
        
        # Update item group
        group = item_group_service.update_item_group(group_id, data, current_user.id)
        
        flash(f'Categoría "{group.name}" actualizada exitosamente', 'success')
        return redirect(url_for('item_groups.index'))
    
    except NotFoundError:
        flash('Categoría no encontrada', 'error')
        return redirect(url_for('item_groups.index'))
    
    except ValidationError as e:
        flash(f'Error de validación: {e.message}', 'error')
        group = item_group_service.get_item_group(group_id)
        all_groups = [g for g in item_group_service.get_all_groups() if g.id != group_id]
        return render_template('item_groups_form.html', group=group, all_groups=all_groups, form_data=request.form)
    
    except (BusinessLogicError, DatabaseError) as e:
        flash(f'Error: {e.message}', 'error')
        group = item_group_service.get_item_group(group_id)
        all_groups = [g for g in item_group_service.get_all_groups() if g.id != group_id]
        return render_template('item_groups_form.html', group=group, all_groups=all_groups, form_data=request.form)


@item_groups_bp.route('/<int:group_id>/delete', methods=['POST'])
@login_required
def delete(group_id):
    """Delete item group (soft delete)."""
    try:
        item_group_service = ItemGroupService()
        item_group_service.delete_item_group(group_id, current_user.id)
        
        flash('Categoría eliminada exitosamente', 'success')
    
    except NotFoundError:
        flash('Categoría no encontrada', 'error')
    
    except (BusinessLogicError, DatabaseError) as e:
        flash(f'Error al eliminar categoría: {e.message}', 'error')
    
    return redirect(url_for('item_groups.index'))


@item_groups_bp.route('/<int:group_id>')
@login_required
def view(group_id):
    """View item group details and products."""
    try:
        item_group_service = ItemGroupService()
        group = item_group_service.get_item_group(group_id)
        
        if not group:
            flash('Categoría no encontrada', 'error')
            return redirect(url_for('item_groups.index'))
        
        # Get products in this category
        from app.services import ProductService
        product_service = ProductService()
        products = product_service.get_products_by_category(group_id)
        
        return render_template('item_groups_detail.html', group=group, products=products)
    
    except Exception as e:
        flash(f'Error al cargar categoría: {str(e)}', 'error')
        return redirect(url_for('item_groups.index'))

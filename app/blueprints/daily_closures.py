"""Blueprint for daily sales closures and estimated 60/40 reconstruction."""
from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.models import ExchangeRate
from app.services import DailySalesClosureService, ImportService
from app.utils.exceptions import BusinessLogicError, NotFoundError, ValidationError

daily_closures_bp = Blueprint('daily_closures', __name__)


@daily_closures_bp.route('/')
@login_required
def index():
    """List daily closures."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        pagination = DailySalesClosureService().list_closures(page=page, per_page=per_page)
        exchange_rates = {
            cierre.id: ExchangeRate.get_rate_for_date(cierre.closure_date)
            for cierre in pagination.items
        }
        return render_template(
            'cierres_diarios.html',
            cierres=pagination.items,
            pagination=pagination,
            exchange_rates=exchange_rates,
        )
    except Exception as e:
        flash(f'Error al cargar cierres diarios: {str(e)}', 'error')
        return render_template('cierres_diarios.html', cierres=[], pagination=None, exchange_rates={})


@daily_closures_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Register one daily closure and reconstruct estimated exits."""
    if request.method == 'GET':
        return render_template('cierres_diarios_form.html', form_data=None, today=date.today().isoformat())

    try:
        payload = {
            'closure_date': request.form.get('closure_date', '').strip(),
            'total_sales_bs': request.form.get('total_sales_bs', '').strip() or None,
            'invoiced_share': request.form.get('invoiced_share', '').strip() or None,
            'non_invoiced_share': request.form.get('non_invoiced_share', '').strip() or None,
            'invoiced_sales_bs': request.form.get('invoiced_sales_bs', '').strip() or None,
            'non_invoiced_sales_bs': request.form.get('non_invoiced_sales_bs', '').strip() or None,
            'notes': request.form.get('notes', '').strip(),
        }
        closure = DailySalesClosureService().create_closure(payload, current_user.id)
        flash(f'Cierre diario {closure.closure_date.isoformat()} registrado correctamente', 'success')
        return redirect(url_for('daily_closures.view', closure_id=closure.id))
    except ValidationError as e:
        flash(f'Error de validación: {e.message}', 'error')
    except BusinessLogicError as e:
        flash(f'Error: {e.message}', 'error')
    except Exception as e:
        flash(f'Error al registrar cierre diario: {str(e)}', 'error')

    return render_template('cierres_diarios_form.html', form_data=request.form, today=request.form.get('closure_date', date.today().isoformat()))


@daily_closures_bp.route('/import', methods=['GET', 'POST'])
@login_required
def import_closures():
    """Import daily closures from CSV/XLS/XLSX."""
    if request.method == 'GET':
        return render_template('cierres_diarios_import.html')

    try:
        if 'file' not in request.files:
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(request.url)
        results = ImportService().import_daily_sales_closures_from_file(request.files['file'], current_user.id)
        flash(f'Importación completada: {results["created"]} cierres procesados', 'success')
        if results['errors']:
            flash(f'Se encontraron {len(results["errors"])} incidencias durante la importación', 'warning')
        return render_template('cierres_diarios_import.html', results=results)
    except Exception as e:
        flash(f'Error al importar cierres diarios: {str(e)}', 'error')
        return redirect(request.url)


@daily_closures_bp.route('/<int:closure_id>')
@login_required
def view(closure_id):
    """Show one closure with reconstructed allocations."""
    try:
        cierre = DailySalesClosureService().get_closure(closure_id)
        exchange_rate = ExchangeRate.get_rate_for_date(cierre.closure_date)
        return render_template('cierres_diarios_detail.html', cierre=cierre, exchange_rate=exchange_rate)
    except NotFoundError:
        flash('Cierre diario no encontrado', 'error')
        return redirect(url_for('daily_closures.index'))
    except Exception as e:
        flash(f'Error al cargar cierre diario: {str(e)}', 'error')
        return redirect(url_for('daily_closures.index'))
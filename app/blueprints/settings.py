"""
Settings blueprint for company profile administration.
"""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.services.company_settings_service import CompanySettingsService
from app.utils.exceptions import ValidationError

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/company', methods=['GET', 'POST'])
@login_required
def company():
    """View and update the company profile used across reports."""
    service = CompanySettingsService()

    if request.method == 'GET':
        return render_template('company_settings.html', company=service.get_company_context())

    try:
        service.update_settings({
            'company_name': request.form.get('company_name', ''),
            'rif': request.form.get('rif', ''),
            'fiscal_address': request.form.get('fiscal_address', ''),
            'phone': request.form.get('phone', ''),
            'email': request.form.get('email', ''),
        }, current_user.id)
        flash('Configuración de empresa actualizada correctamente', 'success')
        return redirect(url_for('settings.company'))
    except ValidationError as exc:
        flash(f'Error de validación: {exc.message}', 'error')
        return render_template('company_settings.html', company=request.form.to_dict())
    except Exception as exc:
        flash(f'No fue posible guardar la configuración: {exc}', 'error')
        return render_template('company_settings.html', company=request.form.to_dict())
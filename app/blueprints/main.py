"""
Main blueprint for basic routes.
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user, login_user, logout_user
import pandas as pd
from app.models import User

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Home page - redirect to login if not authenticated."""
    if current_user.is_authenticated:
        from app.models import Product
        productos = Product.query.filter_by(deleted_at=None).limit(20).all()
        return render_template('index.html', productos=productos)
    return redirect(url_for('main.login'))


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            # Check if account is locked
            if user.is_locked():
                flash('Tu cuenta está bloqueada. Intenta más tarde.', 'error')
                return redirect(url_for('main.login'))
            
            # Record successful login
            user.record_successful_login()
            login_user(user)
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            # Record failed login if user exists
            if user:
                user.record_failed_login()
            
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login.html')


@main_bp.route('/logout')
@login_required
def logout():
    """Logout user."""
    logout_user()
    flash('Has cerrado sesión exitosamente', 'success')
    return redirect(url_for('main.login'))


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard page with metrics and KPIs."""
    from app.services import DashboardService
    
    try:
        dashboard_service = DashboardService()
        metrics = dashboard_service.get_dashboard_metrics()
        sales_chart = dashboard_service.get_sales_chart_data(days=30)
        top_products = dashboard_service.get_top_products(limit=5)
        
        return render_template('dashboard.html',
                             metrics=metrics,
                             sales_chart=sales_chart,
                             top_products=top_products)
    except Exception as e:
        flash(f'Error al cargar el dashboard: {str(e)}', 'error')
        from app.models import Product
        productos = Product.query.filter_by(deleted_at=None).limit(20).all()
        return render_template('index.html', productos=productos)



@main_bp.route('/import', methods=['GET', 'POST'])
@login_required
def import_inventory():
    """Import inventory from Excel/CSV file."""
    if request.method == 'GET':
        return render_template('import_inventory.html')
    
    try:
        from app.services import ImportService
        
        if 'file' not in request.files:
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        import_service = ImportService()
        results = import_service.import_from_file(file, current_user.id)
        
        flash(f'Importación completada: {results["created"]} creados, {results["updated"]} actualizados', 'success')
        
        if results['errors']:
            flash(f'Se encontraron {len(results["errors"])} errores durante la importación', 'warning')
        
        return render_template('import_inventory.html', results=results)
        
    except Exception as e:
        flash(f'Error al importar archivo: {str(e)}', 'error')
        return redirect(request.url)


@main_bp.route('/inventory-report')
@login_required
def inventory_report():
    """Display inventory report in Art 177 format."""
    from datetime import datetime, timedelta
    from app.services import ImportService
    
    try:
        # Get date range from query params or default to current month
        end_date = datetime.now()
        start_date = datetime(end_date.year, end_date.month, 1)
        
        if request.args.get('start_date'):
            start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d')
        if request.args.get('end_date'):
            end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d')
        
        import_service = ImportService()
        df = import_service.export_inventory_report(start_date, end_date)
        
        # Convert to list of dicts for template
        report_data = df.to_dict('records')
        
        # Calculate totals
        totals = {
            'initial_amount': df['Existencia Inicial - Monto (Bs)'].sum(),
            'entries_amount': df['Entradas - Monto (Bs)'].sum(),
            'exits_amount': df['Salidas - Monto (Bs)'].sum(),
            'final_amount': df['Inv.final - Monto (Bs)'].sum()
        }
        
        return render_template('inventario_diario.html',
                             report_data=report_data,
                             totals=totals,
                             start_date=start_date,
                             end_date=end_date)
        
    except Exception as e:
        flash(f'Error al generar reporte: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))


@main_bp.route('/inventory-report/export')
@login_required
def export_inventory_report():
    """Export inventory report to Excel."""
    from datetime import datetime
    from app.services import ImportService
    from flask import send_file
    import io
    
    try:
        # Get date range
        end_date = datetime.now()
        start_date = datetime(end_date.year, end_date.month, 1)
        
        if request.args.get('start_date'):
            start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d')
        if request.args.get('end_date'):
            end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d')
        
        import_service = ImportService()
        df = import_service.export_inventory_report(start_date, end_date)
        
        # Create Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Add header rows
            header_df = pd.DataFrame([
                ['EMPRESA: INVERSIONES FERRE-EXITO, C.A', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
                ['R.I.F. J31764195-7', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
                ['DIRECCION: Calle Bolívar. Palo Negro, Municipio Libertador. Estado Aragua', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
                ['TELEFONO: 0412-7434522', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
                ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
                ['Relacion de movimiento de entradas y salidas de los inventarios', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
                ['De acuerdo al Reglamento de la ley de I.S.L.R artículo 177.', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
                [f'Fecha Desde: {start_date.strftime("%Y-%m-%d")}', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
                [f'Fecha Hasta: {end_date.strftime("%Y-%m-%d")}', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
            ])
            
            header_df.to_excel(writer, sheet_name='Inventario', index=False, header=False)
            df.to_excel(writer, sheet_name='Inventario', startrow=9, index=False)
        
        output.seek(0)
        
        filename = f'inventario_diario_{start_date.strftime("%Y-%m-%d")}_{end_date.strftime("%Y-%m-%d")}.xlsx'
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        flash(f'Error al exportar reporte: {str(e)}', 'error')
        return redirect(url_for('main.inventory_report'))

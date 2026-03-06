"""
Reports blueprint - Routes for inventory and sales reports.
"""
import io
from datetime import datetime, date, timedelta

import pandas as pd
from flask import (
    Blueprint, render_template, redirect, url_for,
    request, flash, send_file, current_app
)
from flask_login import login_required

from app.services.reports_service import ReportsService

reports_bp = Blueprint('reports', __name__)


# ---------------------------------------------------------------------------
# Index
# ---------------------------------------------------------------------------

@reports_bp.route('/')
@login_required
def index():
    """Reports landing page."""
    return render_template('reports/index.html')


# ---------------------------------------------------------------------------
# Inventario completo
# ---------------------------------------------------------------------------

@reports_bp.route('/inventario')
@login_required
def inventario():
    """Full inventory report."""
    try:
        service = ReportsService()
        items = service.get_inventario_completo()
        total_usd = sum(i['valor_total_usd'] for i in items)
        total_bs = sum(i['valor_total_bs'] for i in items)
        return render_template(
            'reports/inventario.html',
            items=items,
            total_usd=round(total_usd, 2),
            total_bs=round(total_bs, 2),
            today=date.today(),
        )
    except Exception as e:
        flash(f'Error al generar reporte: {str(e)}', 'error')
        return redirect(url_for('reports.index'))


@reports_bp.route('/inventario/export')
@login_required
def inventario_export():
    """Export full inventory to Excel."""
    try:
        service = ReportsService()
        items = service.get_inventario_completo()
        df = pd.DataFrame([{
            'Codigo': i['codigo'],
            'Descripcion': i['descripcion'],
            'Categoria': i['categoria'],
            'Proveedor': i['proveedor'],
            'Stock': i['stock'],
            'Precio USD': i['precio_dolares'],
            'Factor Ajuste': i['factor_ajuste'],
            'Precio Ajustado USD': i['precio_ajustado_usd'],
            'Precio Bs': i['precio_bs'],
            'Valor Total USD': i['valor_total_usd'],
            'Valor Total Bs': i['valor_total_bs'],
        } for i in items])
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Inventario')
        output.seek(0)
        filename = f"inventario_completo_{date.today().strftime('%Y-%m-%d')}.xlsx"
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename,
        )
    except Exception as e:
        flash(f'Error al exportar: {str(e)}', 'error')
        return redirect(url_for('reports.inventario'))


# ---------------------------------------------------------------------------
# Stock bajo
# ---------------------------------------------------------------------------

@reports_bp.route('/stock-bajo')
@login_required
def stock_bajo():
    """Low stock report."""
    try:
        service = ReportsService()
        items = service.get_stock_bajo()
        return render_template(
            'reports/stock_bajo.html',
            items=items,
            today=date.today(),
        )
    except Exception as e:
        flash(f'Error al generar reporte: {str(e)}', 'error')
        return redirect(url_for('reports.index'))


@reports_bp.route('/stock-bajo/export')
@login_required
def stock_bajo_export():
    """Export low stock report to Excel."""
    try:
        service = ReportsService()
        items = service.get_stock_bajo()
        df = pd.DataFrame([{
            'Codigo': i['codigo'],
            'Descripcion': i['descripcion'],
            'Categoria': i['categoria'],
            'Proveedor': i['proveedor'],
            'Stock Actual': i['stock'],
            'Punto de Reorden': i['reorder_point'],
            'Cantidad a Pedir': i['reorder_quantity'],
            'Deficit': i['deficit'],
            'Estado': 'AGOTADO' if i['agotado'] else 'STOCK BAJO',
        } for i in items])
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Stock Bajo')
        output.seek(0)
        filename = f"stock_bajo_{date.today().strftime('%Y-%m-%d')}.xlsx"
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename,
        )
    except Exception as e:
        flash(f'Error al exportar: {str(e)}', 'error')
        return redirect(url_for('reports.stock_bajo'))


# ---------------------------------------------------------------------------
# Movimientos por periodo
# ---------------------------------------------------------------------------

@reports_bp.route('/movimientos')
@login_required
def movimientos():
    """Movement report with date range filter."""
    try:
        service = ReportsService()
        default_start, default_end = service.get_default_date_range(30)

        start_str = request.args.get('start_date', default_start.isoformat())
        end_str = request.args.get('end_date', default_end.isoformat())
        tipo = request.args.get('tipo', '')

        try:
            start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
        except ValueError:
            start_date, end_date = default_start, default_end

        items = service.get_movimientos_periodo(start_date, end_date, tipo or None)
        resumen = service.get_resumen_movimientos(start_date, end_date)

        return render_template(
            'reports/movimientos.html',
            items=items,
            resumen=resumen,
            start_date=start_date,
            end_date=end_date,
            tipo=tipo,
        )
    except Exception as e:
        flash(f'Error al generar reporte: {str(e)}', 'error')
        return redirect(url_for('reports.index'))


@reports_bp.route('/movimientos/export')
@login_required
def movimientos_export():
    """Export movements report to Excel."""
    try:
        service = ReportsService()
        default_start, default_end = service.get_default_date_range(30)
        start_str = request.args.get('start_date', default_start.isoformat())
        end_str = request.args.get('end_date', default_end.isoformat())
        tipo = request.args.get('tipo', '')
        try:
            start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
        except ValueError:
            start_date, end_date = default_start, default_end

        items = service.get_movimientos_periodo(start_date, end_date, tipo or None)
        df = pd.DataFrame([{
            'Fecha': i['fecha'].strftime('%Y-%m-%d') if i['fecha'] else '',
            'Tipo': i['tipo'],
            'Cantidad': i['cantidad'],
            'Codigo Producto': i['producto_codigo'],
            'Descripcion': i['producto_descripcion'],
            'Descripcion Movimiento': i['descripcion'],
            'Usuario': i['usuario'],
        } for i in items])
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Movimientos')
        output.seek(0)
        filename = f"movimientos_{start_date}_{end_date}.xlsx"
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename,
        )
    except Exception as e:
        flash(f'Error al exportar: {str(e)}', 'error')
        return redirect(url_for('reports.movimientos'))


# ---------------------------------------------------------------------------
# Ventas por periodo
# ---------------------------------------------------------------------------

@reports_bp.route('/ventas')
@login_required
def ventas():
    """Sales report with date range filter."""
    try:
        service = ReportsService()
        default_start, default_end = service.get_default_date_range(30)

        start_str = request.args.get('start_date', default_start.isoformat())
        end_str = request.args.get('end_date', default_end.isoformat())
        status_filter = request.args.get('status', '')

        try:
            start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
        except ValueError:
            start_date, end_date = default_start, default_end

        orders = service.get_ventas_periodo(start_date, end_date, status_filter or None)
        resumen = service.get_resumen_ventas(start_date, end_date)

        return render_template(
            'reports/ventas.html',
            orders=orders,
            resumen=resumen,
            start_date=start_date,
            end_date=end_date,
            status_filter=status_filter,
        )
    except Exception as e:
        flash(f'Error al generar reporte: {str(e)}', 'error')
        return redirect(url_for('reports.index'))


@reports_bp.route('/ventas/export')
@login_required
def ventas_export():
    """Export sales report to Excel."""
    try:
        service = ReportsService()
        default_start, default_end = service.get_default_date_range(30)
        start_str = request.args.get('start_date', default_start.isoformat())
        end_str = request.args.get('end_date', default_end.isoformat())
        status_filter = request.args.get('status', '')
        try:
            start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
        except ValueError:
            start_date, end_date = default_start, default_end

        orders = service.get_ventas_periodo(start_date, end_date, status_filter or None)
        df = pd.DataFrame([{
            'N. Orden': o['order_number'],
            'Fecha': o['order_date'].strftime('%Y-%m-%d') if o['order_date'] else '',
            'Cliente': o['customer'],
            'Estado': o['status'],
            'Estado Pago': o['payment_status'],
            'Total USD': o['total_amount'],
            'Cobrado USD': o['paid_amount'],
            'Pendiente USD': o['pending_amount'],
        } for o in orders])
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Ventas')
        output.seek(0)
        filename = f"ventas_{start_date}_{end_date}.xlsx"
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename,
        )
    except Exception as e:
        flash(f'Error al exportar: {str(e)}', 'error')
        return redirect(url_for('reports.ventas'))


# ---------------------------------------------------------------------------
# Productos mas vendidos
# ---------------------------------------------------------------------------

@reports_bp.route('/top-productos')
@login_required
def top_productos():
    """Top selling products report."""
    try:
        service = ReportsService()
        default_start, default_end = service.get_default_date_range(30)

        start_str = request.args.get('start_date', default_start.isoformat())
        end_str = request.args.get('end_date', default_end.isoformat())
        limit = request.args.get('limit', 20, type=int)

        try:
            start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
        except ValueError:
            start_date, end_date = default_start, default_end

        items = service.get_top_productos(limit=limit, start_date=start_date, end_date=end_date)
        return render_template(
            'reports/top_productos.html',
            items=items,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
        )
    except Exception as e:
        flash(f'Error al generar reporte: {str(e)}', 'error')
        return redirect(url_for('reports.index'))


# ---------------------------------------------------------------------------
# Libro de Inventario (Art. 177 ISLR)
# ---------------------------------------------------------------------------

@reports_bp.route('/libro-inventario')
@login_required
def libro_inventario():
    """Libro de Inventario diario (Art. 177 ISLR Venezuela)."""
    try:
        fecha_str = request.args.get('fecha', date.today().isoformat())
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            fecha = date.today()

        service = ReportsService()
        data = service.get_libro_inventario(fecha)
        return render_template('reports/libro_inventario.html', data=data, fecha=fecha)
    except Exception as e:
        flash(f'Error al generar Libro de Inventario: {str(e)}', 'error')
        return redirect(url_for('reports.index'))


@reports_bp.route('/libro-inventario/export')
@login_required
def libro_inventario_export():
    """Export Libro de Inventario to Excel."""
    try:
        fecha_str = request.args.get('fecha', date.today().isoformat())
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            fecha = date.today()

        service = ReportsService()
        data = service.get_libro_inventario(fecha)

        df = pd.DataFrame([{
            'Codigo': i['codigo'],
            'Descripcion': i['descripcion'],
            'Proveedor': i['proveedor'],
            'Stock': i['stock'],
            'Precio USD': i['precio_usd'],
            'Precio Bs': i['precio_bs'],
            'Valor Total USD': i['valor_usd'],
            'Valor Total Bs': i['valor_bs'],
        } for i in data['items']])

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Libro Inventario')
            ws = writer.sheets['Libro Inventario']
            # Header rows before the table
            ws.insert_rows(1, amount=4)
            ws['A1'] = data['empresa']
            ws['A2'] = f"RIF: {data['rif']}"
            ws['A3'] = f"LIBRO DE INVENTARIO - Art. 177 ISLR"
            ws['A4'] = f"Fecha: {fecha.strftime('%d/%m/%Y')}  |  Tasa USD/Bs: {data['exchange_rate']}"
        output.seek(0)
        filename = f"libro_inventario_{fecha.strftime('%Y-%m-%d')}.xlsx"
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename,
        )
    except Exception as e:
        flash(f'Error al exportar: {str(e)}', 'error')
        return redirect(url_for('reports.libro_inventario'))


# ---------------------------------------------------------------------------
# Libro Diario de Movimientos
# ---------------------------------------------------------------------------

MESES_ES = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre',
}


@reports_bp.route('/libro-diario')
@login_required
def libro_diario():
    """
    Libro diario de movimientos.
    Modos: 'hoy', 'dia', 'semana', 'semana_anterior', 'rango'.
    """
    try:
        modo = request.args.get('modo', 'hoy')
        if modo not in {'hoy', 'dia', 'semana', 'semana_anterior', 'rango'}:
            modo = 'hoy'
        today = date.today()

        if modo == 'hoy':
            start_date = end_date = today
        elif modo == 'dia':
            fecha_str = request.args.get('fecha', today.isoformat())
            try:
                start_date = end_date = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            except ValueError:
                start_date = end_date = today
        elif modo == 'semana':
            # Lunes al domingo de la semana actual
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
            if end_date > today:
                end_date = today
        elif modo == 'semana_anterior':
            # Lunes al domingo de la semana pasada
            start_date = today - timedelta(days=today.weekday() + 7)
            end_date = start_date + timedelta(days=6)
        else:  # rango
            default_start = today - timedelta(days=6)
            start_str = request.args.get('start_date', default_start.isoformat())
            end_str = request.args.get('end_date', today.isoformat())
            try:
                start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
            except ValueError:
                start_date, end_date = today - timedelta(days=6), today

        service = ReportsService()
        data = service.get_libro_diario(start_date, end_date)

        return render_template(
            'reports/libro_diario.html',
            data=data,
            modo=modo,
            start_date=start_date,
            end_date=end_date,
            today=today,
        )
    except Exception as e:
        flash(f'Error al generar Libro Diario: {str(e)}', 'error')
        return redirect(url_for('reports.index'))


@reports_bp.route('/libro-diario/export')
@login_required
def libro_diario_export():
    """Export libro diario to Excel."""
    try:
        today = date.today()
        start_str = request.args.get('start_date', today.isoformat())
        end_str = request.args.get('end_date', today.isoformat())
        try:
            start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
        except ValueError:
            start_date = end_date = today

        service = ReportsService()
        data = service.get_libro_diario(start_date, end_date)

        # Sheet 1: journal entries
        lineas_rows = []
        for asiento in data['asientos']:
            for l in asiento['lineas']:
                lineas_rows.append({
                    'Fecha': asiento['fecha'].strftime('%d/%m/%Y') if asiento['fecha'] else '',
                    'Hora': l['hora'],
                    'Tipo': l['tipo'],
                    'Codigo': l['codigo'],
                    'Descripcion': l['descripcion'],
                    'Cantidad': l['cantidad'],
                    'Descripcion Mov.': l['descripcion_mov'],
                    'Usuario': l['usuario'],
                    'Precio USD': l['precio_usd'],
                    'Valor USD': l['valor_usd'],
                    'Valor Bs': l['valor_bs'],
                })

        # Sheet 2: product summary
        resumen_rows = [{
            'Codigo': r['codigo'],
            'Descripcion': r['descripcion'],
            'Stock Apertura': r['stock_apertura'],
            'Entradas': r['entradas'],
            'Salidas': r['salidas'],
            'Stock Cierre': r['stock_cierre'],
            'Precio USD': r['precio_usd'],
            'Valor Cierre USD': r['valor_cierre_usd'],
            'Valor Cierre Bs': r['valor_cierre_bs'],
        } for r in data['resumen_productos']]

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            pd.DataFrame(lineas_rows).to_excel(writer, index=False, sheet_name='Asientos')
            pd.DataFrame(resumen_rows).to_excel(writer, index=False, sheet_name='Resumen')
        output.seek(0)
        filename = f"libro_diario_{start_date}_{end_date}.xlsx"
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename,
        )
    except Exception as e:
        flash(f'Error al exportar: {str(e)}', 'error')
        return redirect(url_for('reports.libro_diario'))


# ---------------------------------------------------------------------------
# Resumen Mensual
# ---------------------------------------------------------------------------

@reports_bp.route('/resumen-mensual')
@login_required
def resumen_mensual():
    """Monthly inventory summary with opening/closing balances."""
    try:
        today = date.today()
        year = request.args.get('year', today.year, type=int)
        month = request.args.get('month', today.month, type=int)
        month = max(1, min(12, month))

        service = ReportsService()
        data = service.get_resumen_mensual(year, month)

        # Build year/month selectors
        years = list(range(today.year - 3, today.year + 1))

        return render_template(
            'reports/resumen_mensual.html',
            data=data,
            year=year,
            month=month,
            years=years,
            meses=MESES_ES,
            today=today,
        )
    except Exception as e:
        flash(f'Error al generar Resumen Mensual: {str(e)}', 'error')
        return redirect(url_for('reports.index'))


@reports_bp.route('/resumen-mensual/export')
@login_required
def resumen_mensual_export():
    """Export monthly summary to Excel."""
    try:
        today = date.today()
        year = request.args.get('year', today.year, type=int)
        month = request.args.get('month', today.month, type=int)
        month = max(1, min(12, month))

        service = ReportsService()
        data = service.get_resumen_mensual(year, month)

        filas = [{
            'Codigo': f['codigo'],
            'Descripcion': f['descripcion'],
            'Proveedor': f['proveedor'],
            'Stock Apertura': f['stock_apertura'],
            'Entradas Mes': f['entradas'],
            'Salidas Mes': f['salidas'],
            'Stock Cierre': f['stock_cierre'],
            'Precio USD': f['precio_usd'],
            'Valor Apertura USD': f['valor_apertura_usd'],
            'Valor Cierre USD': f['valor_cierre_usd'],
            'Valor Apertura Bs': f['valor_apertura_bs'],
            'Valor Cierre Bs': f['valor_cierre_bs'],
        } for f in data['filas']]

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df = pd.DataFrame(filas)
            df.to_excel(writer, index=False, sheet_name='Resumen Mensual')
            ws = writer.sheets['Resumen Mensual']
            ws.insert_rows(1, amount=3)
            ws['A1'] = data['empresa']
            ws['A2'] = f"RESUMEN MENSUAL DE INVENTARIO - {MESES_ES.get(month, '')} {year}"
            ws['A3'] = (
                f"Periodo: {data['first_day'].strftime('%d/%m/%Y')} - "
                f"{data['last_day'].strftime('%d/%m/%Y')}  |  Tasa: {data['exchange_rate']} Bs/$"
            )
        output.seek(0)
        filename = f"resumen_mensual_{year}_{month:02d}.xlsx"
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename,
        )
    except Exception as e:
        flash(f'Error al exportar: {str(e)}', 'error')
        return redirect(url_for('reports.resumen_mensual'))


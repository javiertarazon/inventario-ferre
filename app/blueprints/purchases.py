"""
Purchases blueprint - Routes for purchase invoice registration and import.
"""
from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.services import ImportService, ProductService, PurchaseInvoiceService, SupplierService
from app.utils.exceptions import BusinessLogicError, NotFoundError, ValidationError

purchases_bp = Blueprint('purchases', __name__)


@purchases_bp.route('/')
@login_required
def index():
    """List registered purchase invoices."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        pagination = PurchaseInvoiceService().list_purchase_invoices(page=page, per_page=per_page)
        return render_template(
            'compras_facturas.html',
            facturas=pagination.items,
            pagination=pagination,
        )
    except Exception as e:
        flash(f'Error al cargar facturas de compra: {str(e)}', 'error')
        return render_template('compras_facturas.html', facturas=[], pagination=None)


@purchases_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Register a purchase invoice manually."""
    supplier_service = SupplierService()
    product_service = ProductService()
    suppliers = supplier_service.get_all_suppliers()
    products = product_service.search_products(page=1, per_page=100).items

    if request.method == 'GET':
        return render_template(
            'compras_facturas_form.html',
            factura=None,
            suppliers=suppliers,
            products=products,
            today=date.today().isoformat(),
            form_data=None,
            line_items=None,
        )

    try:
        payload = _build_invoice_payload_from_form(request)
        invoice = PurchaseInvoiceService().create_purchase_invoice(payload, current_user.id)
        flash(f'Factura de compra {invoice.invoice_number} registrada correctamente', 'success')
        return redirect(url_for('purchases.view', invoice_id=invoice.id))
    except ValidationError as e:
        flash(f'Error de validación: {e.message}', 'error')
    except BusinessLogicError as e:
        flash(f'Error: {e.message}', 'error')
    except Exception as e:
        flash(f'Error al registrar factura de compra: {str(e)}', 'error')

    return render_template(
        'compras_facturas_form.html',
        factura=None,
        suppliers=suppliers,
        products=products,
        today=request.form.get('invoice_date', date.today().isoformat()),
        form_data=request.form,
        line_items=_extract_line_items(request),
    )


@purchases_bp.route('/import', methods=['GET', 'POST'])
@login_required
def import_invoices():
    """Import supplier invoices from CSV/XLS/XLSX."""
    if request.method == 'GET':
        return render_template('compras_facturas_import.html')

    try:
        if 'file' not in request.files:
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(request.url)

        file = request.files['file']
        results = ImportService().import_purchase_invoices_from_file(file, current_user.id)
        flash(
            f'Importación completada: {results["created"]} facturas y {results["items_processed"]} líneas procesadas',
            'success',
        )
        if results['errors']:
            flash(f'Se encontraron {len(results["errors"])} incidencias durante la importación', 'warning')
        return render_template('compras_facturas_import.html', results=results)
    except Exception as e:
        flash(f'Error al importar facturas de compra: {str(e)}', 'error')
        return redirect(request.url)


@purchases_bp.route('/<int:invoice_id>')
@login_required
def view(invoice_id):
    """View purchase invoice detail."""
    try:
        invoice = PurchaseInvoiceService().get_purchase_invoice(invoice_id)
        return render_template('compras_facturas_detail.html', factura=invoice)
    except NotFoundError:
        flash('Factura de compra no encontrada', 'error')
        return redirect(url_for('purchases.index'))
    except Exception as e:
        flash(f'Error al cargar factura de compra: {str(e)}', 'error')
        return redirect(url_for('purchases.index'))


def _build_invoice_payload_from_form(req):
    """Build purchase invoice payload from posted form arrays."""
    items = _extract_line_items(req)
    return {
        'supplier_id': req.form.get('supplier_id'),
        'invoice_number': req.form.get('invoice_number', '').strip(),
        'invoice_date': req.form.get('invoice_date', '').strip(),
        'currency_code': req.form.get('currency_code', 'USD').strip(),
        'taxable_base_usd': req.form.get('taxable_base_usd', '').strip() or None,
        'tax_amount_usd': req.form.get('tax_amount_usd', '').strip() or None,
        'total_usd': req.form.get('total_usd', '').strip() or None,
        'notes': req.form.get('notes', '').strip(),
        'items': items,
    }


def _extract_line_items(req):
    """Extract non-empty line items from repeated form fields."""
    product_ids = req.form.getlist('product_id')
    quantities = req.form.getlist('quantity')
    unit_prices = req.form.getlist('unit_price_usd')
    line_subtotals = req.form.getlist('line_subtotal_usd')

    items = []
    row_count = max(len(product_ids), len(quantities), len(unit_prices), len(line_subtotals))
    for index in range(row_count):
        product_id = product_ids[index].strip() if index < len(product_ids) and product_ids[index] else ''
        quantity = quantities[index].strip() if index < len(quantities) and quantities[index] else ''
        unit_price = unit_prices[index].strip() if index < len(unit_prices) and unit_prices[index] else ''
        line_subtotal = line_subtotals[index].strip() if index < len(line_subtotals) and line_subtotals[index] else ''
        if not any([product_id, quantity, unit_price, line_subtotal]):
            continue
        items.append({
            'product_id': product_id,
            'quantity': quantity,
            'unit_price_usd': unit_price,
            'line_subtotal_usd': line_subtotal,
        })
    return items
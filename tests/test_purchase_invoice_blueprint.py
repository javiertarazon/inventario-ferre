"""Tests for purchase invoice web routes and file import flow."""

import io
from decimal import Decimal

from app.extensions import db
from app.models import Product, PurchaseInvoice


def login_test_user(client):
    """Authenticate the shared test user through the real login form."""
    return client.post(
        '/login',
        data={'username': 'testuser', 'password': 'testpass123'},
        follow_redirects=False,
    )


def test_purchase_invoice_create_route_registers_invoice(app, client, test_user, test_supplier, test_item_group):
    """Manual purchase invoice form should create history and redirect to detail view."""
    user_id, _ = test_user
    supplier_id, _ = test_supplier
    group_id, _ = test_item_group

    with app.app_context():
        product = Product(
            codigo='C-PI-01',
            descripcion='Compra desde UI',
            stock=2,
            precio_dolares=Decimal('5.00'),
            factor_ajuste=Decimal('1.00'),
            item_group_id=group_id,
            created_by=user_id,
            updated_by=user_id,
        )
        db.session.add(product)
        db.session.commit()
        product_id = product.id

    login_response = login_test_user(client)
    assert login_response.status_code == 302

    response = client.post(
        '/purchases/create',
        data={
            'supplier_id': str(supplier_id),
            'invoice_number': 'WEB-001',
            'invoice_date': '2025-03-01',
            'currency_code': 'USD',
            'taxable_base_usd': '12.0000',
            'tax_amount_usd': '1.9200',
            'total_usd': '13.9200',
            'product_id': [str(product_id)],
            'quantity': ['2'],
            'unit_price_usd': ['6.0000'],
            'line_subtotal_usd': ['12.0000'],
        },
        follow_redirects=True,
    )

    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'Factura de compra WEB-001 registrada correctamente' in html
    assert 'Factura WEB-001' in html

    with app.app_context():
        invoice = PurchaseInvoice.query.filter_by(invoice_number='WEB-001').first()
        assert invoice is not None
        assert invoice.supplier_id == supplier_id
        assert len(invoice.items) == 1


def test_purchase_invoice_import_route_processes_csv(app, client, test_user, test_supplier, test_item_group, tmp_path):
    """Purchase import route should read CSV files and create grouped supplier invoices."""
    user_id, _ = test_user
    _, supplier = test_supplier
    group_id, _ = test_item_group
    app.config['UPLOAD_FOLDER'] = str(tmp_path)

    with app.app_context():
        product = Product(
            codigo='I-PI-01',
            descripcion='Importado desde CSV',
            stock=1,
            precio_dolares=Decimal('2.00'),
            factor_ajuste=Decimal('1.00'),
            item_group_id=group_id,
            created_by=user_id,
            updated_by=user_id,
        )
        db.session.add(product)
        db.session.commit()

    login_response = login_test_user(client)
    assert login_response.status_code == 302

    csv_content = (
        'Proveedor,Numero Factura,Fecha Factura,Codigo,Cantidad,Precio Unitario,Subtotal,Base Imponible,IVA,Total\n'
        f'{supplier.nombre},IMP-001,2025-03-02,I-PI-01,3,4.5000,13.5000,13.5000,2.1600,15.6600\n'
    )

    response = client.post(
        '/purchases/import',
        data={'file': (io.BytesIO(csv_content.encode('utf-8')), 'facturas.csv')},
        content_type='multipart/form-data',
        follow_redirects=True,
    )

    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'Importación completada: 1 facturas y 1 líneas procesadas' in html
    assert 'Facturas creadas' in html

    with app.app_context():
        invoice = PurchaseInvoice.query.filter_by(invoice_number='IMP-001').first()
        assert invoice is not None
        assert len(invoice.items) == 1
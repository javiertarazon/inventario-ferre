"""Functional tests for daily closures web flow."""

from datetime import date
from decimal import Decimal

from app.extensions import db
from app.models import DailySalesClosureAllocation, ExchangeRate, Product, PurchaseInvoice, PurchaseInvoiceItem



def login_test_user(client):
    return client.post(
        '/login',
        data={'username': 'testuser', 'password': 'testpass123'},
        follow_redirects=False,
    )



def test_daily_closure_create_flow_renders_bs_detail_and_groups(app, client, test_user, test_supplier, test_item_group):
    """Posting a closure in bolivars should redirect to a detail page with Bs summary and both groups."""
    user_id, _ = test_user
    supplier_id, supplier = test_supplier
    group_id, _ = test_item_group

    with app.app_context():
        invoiced_product = Product(
            codigo='H-WC-01',
            descripcion='Producto web con factura',
            stock=10,
            precio_dolares=Decimal('2.00'),
            factor_ajuste=Decimal('1.00'),
            item_group_id=group_id,
            created_by=user_id,
            updated_by=user_id,
        )
        non_invoiced_product = Product(
            codigo='H-WC-02',
            descripcion='Producto web sin factura',
            stock=10,
            precio_dolares=Decimal('2.00'),
            factor_ajuste=Decimal('1.00'),
            item_group_id=group_id,
            created_by=user_id,
            updated_by=user_id,
        )
        db.session.add_all([invoiced_product, non_invoiced_product])
        db.session.flush()

        db.session.add(ExchangeRate(date=date(2025, 3, 10), rate=Decimal('10.0000'), created_by=user_id))

        purchase_invoice = PurchaseInvoice(
            supplier_id=supplier_id,
            invoice_number='FAC-WEB-001',
            invoice_date=date(2025, 3, 1),
            currency_code='USD',
            subtotal_usd=Decimal('2.0000'),
            taxable_base_usd=Decimal('2.0000'),
            tax_amount_usd=Decimal('0.0000'),
            total_usd=Decimal('2.0000'),
            created_by=user_id,
            updated_by=user_id,
        )
        db.session.add(purchase_invoice)
        db.session.flush()
        db.session.add(PurchaseInvoiceItem(
            invoice_id=purchase_invoice.id,
            product_id=invoiced_product.id,
            description_snapshot=invoiced_product.descripcion,
            quantity=1,
            unit_price_usd=Decimal('2.0000'),
            line_subtotal_usd=Decimal('2.0000'),
        ))
        db.session.commit()

    login_response = login_test_user(client)
    assert login_response.status_code == 302

    response = client.post(
        '/daily-closures/create',
        data={
            'closure_date': '2025-03-10',
            'total_sales_bs': '100.0000',
            'invoiced_share': '0.6000',
            'non_invoiced_share': '0.4000',
            'notes': 'Cierre funcional web',
        },
        follow_redirects=True,
    )

    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'Tasa BCV' in html
    assert 'Total Bs' in html
    assert '100.0000' in html
    assert 'con factura' in html
    assert 'sin factura' in html

    with app.app_context():
        allocations = DailySalesClosureAllocation.query.all()
        assert len(allocations) == 2
        assert {allocation.allocation_group for allocation in allocations} == {'con factura', 'sin factura'}

"""Tests for daily sales closure reconstruction rules."""

from datetime import date
from decimal import Decimal

import pytest

from app.extensions import db
from app.models import (
    DailySalesClosureAllocation,
    ExchangeRate,
    Movimiento,
    Product,
    PurchaseInvoice,
    PurchaseInvoiceItem,
)
from app.services import DailySalesClosureService
from app.utils.exceptions import ValidationError



def test_daily_closure_requires_exact_exchange_rate_for_bs_input(app, test_user):
    """Bolivar closures must use the exchange rate registered for the exact closure date."""
    user_id, _ = test_user

    with app.app_context():
        db.session.add(ExchangeRate(date=date(2025, 3, 9), rate=Decimal('35.0000'), created_by=user_id))
        db.session.commit()

        with pytest.raises(ValidationError) as exc_info:
            DailySalesClosureService().create_closure(
                {
                    'closure_date': '2025-03-10',
                    'total_sales_bs': '350.0000',
                },
                user_id,
            )

        assert 'No existe tasa BCV registrada para la fecha 2025-03-10' in exc_info.value.message



def test_daily_closure_reconstructs_using_invoice_history_groups(app, test_user, test_supplier, test_item_group):
    """The 60/40 rule must split products by whether they have purchase invoice history."""
    user_id, _ = test_user
    supplier_id, _ = test_supplier
    group_id, _ = test_item_group

    with app.app_context():
        invoiced_product = Product(
            codigo='H-CD-01',
            descripcion='Producto con historial de factura',
            stock=10,
            precio_dolares=Decimal('2.00'),
            factor_ajuste=Decimal('1.00'),
            item_group_id=group_id,
            created_by=user_id,
            updated_by=user_id,
        )
        non_invoiced_product = Product(
            codigo='H-CD-02',
            descripcion='Producto sin historial de factura',
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
            invoice_number='FAC-CIERRE-001',
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

        closure = DailySalesClosureService().create_closure(
            {
                'closure_date': '2025-03-10',
                'total_sales_bs': '100.0000',
                'invoiced_share': '0.6000',
                'non_invoiced_share': '0.4000',
            },
            user_id,
        )

        allocations = DailySalesClosureAllocation.query.filter_by(closure_id=closure.id).all()
        movements = Movimiento.query.filter(Movimiento.descripcion.contains('Cierre diario 2025-03-10')).all()
        refreshed_invoiced = db.session.get(Product, invoiced_product.id)
        refreshed_non_invoiced = db.session.get(Product, non_invoiced_product.id)

        assert closure.total_sales_usd == Decimal('10.0000')
        assert closure.invoiced_sales_usd == Decimal('6.0000')
        assert closure.non_invoiced_sales_usd == Decimal('4.0000')
        assert closure.reconstructed_sales_usd == Decimal('10.0000')
        assert closure.generated_exit_units == 5
        assert len(allocations) == 2
        assert {allocation.allocation_group for allocation in allocations} == {'con factura', 'sin factura'}

        allocation_by_group = {allocation.allocation_group: allocation for allocation in allocations}
        assert allocation_by_group['con factura'].product_id == invoiced_product.id
        assert allocation_by_group['sin factura'].product_id == non_invoiced_product.id
        assert allocation_by_group['con factura'].estimated_quantity == 3
        assert allocation_by_group['sin factura'].estimated_quantity == 2

        assert len(movements) == 2
        assert any('[con factura]' in movement.descripcion for movement in movements)
        assert any('[sin factura]' in movement.descripcion for movement in movements)
        assert refreshed_invoiced.stock == 7
        assert refreshed_non_invoiced.stock == 8

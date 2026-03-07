"""Tests for purchase invoice history and stock entry registration."""

from datetime import date
from decimal import Decimal

from app.models import Movimiento, Product, PurchaseInvoice
from app.services import PurchaseInvoiceService


def test_purchase_invoice_creates_history_and_stock_entries(app, test_user, test_supplier, test_item_group):
    """A purchase invoice should preserve line history and create ENTRADA movements."""
    user_id, _ = test_user
    supplier_id, _ = test_supplier
    group_id, _ = test_item_group

    with app.app_context():
        product = Product(
            codigo='H-PI-01',
            descripcion='Producto historial compra',
            stock=5,
            precio_dolares=Decimal('3.00'),
            factor_ajuste=Decimal('1.00'),
            item_group_id=group_id,
            created_by=user_id,
            updated_by=user_id,
        )
        from app.extensions import db
        db.session.add(product)
        db.session.commit()

        invoice = PurchaseInvoiceService().create_purchase_invoice(
            {
                'supplier_id': supplier_id,
                'invoice_number': 'FAC-001',
                'invoice_date': '2025-02-20',
                'tax_amount_usd': '1.6000',
                'total_usd': '11.6000',
                'items': [
                    {
                        'product_id': product.id,
                        'quantity': 3,
                        'unit_price_usd': '3.3333',
                    }
                ],
            },
            user_id,
        )

        refreshed_product = Product.query.get(product.id)
        movement = Movimiento.query.filter_by(producto_id=product.id, tipo='ENTRADA').first()
        stored_invoice = PurchaseInvoice.query.get(invoice.id)

        assert stored_invoice is not None
        assert stored_invoice.invoice_number == 'FAC-001'
        assert stored_invoice.invoice_date == date(2025, 2, 20)
        assert len(stored_invoice.items) == 1
        assert stored_invoice.items[0].unit_price_usd == Decimal('3.3333')
        assert refreshed_product.stock == 8
        assert refreshed_product.proveedor_id == supplier_id
        assert refreshed_product.precio_dolares == Decimal('3.33')
        assert movement is not None
        assert 'FAC-001' in movement.descripcion
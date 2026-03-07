"""
Purchase invoice service for supplier-specific historical entries.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List

from flask import current_app
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import ExchangeRate, Movimiento, Product, Proveedor, PurchaseInvoice, PurchaseInvoiceItem
from app.utils.exceptions import BusinessLogicError, NotFoundError, ValidationError


class PurchaseInvoiceService:
    """Create and query purchase invoices with inventory impact."""

    def list_purchase_invoices(self, page: int = 1, per_page: int = 20):
        """Return paginated supplier invoices ordered by newest first."""
        return (
            PurchaseInvoice.query
            .filter_by(deleted_at=None)
            .options(selectinload(PurchaseInvoice.supplier), selectinload(PurchaseInvoice.items))
            .order_by(PurchaseInvoice.invoice_date.desc(), PurchaseInvoice.id.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )

    def get_purchase_invoice(self, invoice_id: int) -> PurchaseInvoice:
        """Return one purchase invoice with supplier and line details."""
        invoice = (
            PurchaseInvoice.query
            .filter_by(id=invoice_id, deleted_at=None)
            .options(
                selectinload(PurchaseInvoice.supplier),
                selectinload(PurchaseInvoice.items).selectinload(PurchaseInvoiceItem.product),
            )
            .first()
        )
        if not invoice:
            raise NotFoundError('PurchaseInvoice', invoice_id)
        return invoice

    def create_purchase_invoice(self, data: Dict[str, Any], user_id: int) -> PurchaseInvoice:
        """Persist a supplier invoice, line history and entry movements in one transaction."""
        try:
            supplier_id = int(data.get('supplier_id') or 0)
        except (TypeError, ValueError):
            raise ValidationError('El proveedor de la factura es requerido', field='supplier_id')

        supplier = Proveedor.query.filter_by(id=supplier_id, deleted_at=None).first()
        if not supplier:
            raise NotFoundError('Supplier', supplier_id)

        invoice_number = (data.get('invoice_number') or '').strip()
        if not invoice_number:
            raise ValidationError('El número de factura es requerido', field='invoice_number')

        invoice_date = self._parse_date(data.get('invoice_date'), field='invoice_date')
        items_data = data.get('items') or []
        if not isinstance(items_data, list) or not items_data:
            raise ValidationError('La factura debe incluir al menos un producto', field='items')

        existing_invoice = PurchaseInvoice.query.filter_by(
            supplier_id=supplier_id,
            invoice_number=invoice_number,
            deleted_at=None,
        ).first()
        if existing_invoice:
            raise ValidationError(
                f'La factura {invoice_number} ya existe para el proveedor seleccionado',
                field='invoice_number'
            )

        current_rate = ExchangeRate.get_rate_for_date(invoice_date) or ExchangeRate.get_current_rate()
        exchange_rate_value = Decimal(str(current_rate.rate)) if current_rate else None

        subtotal_usd = Decimal('0.0000')
        validated_items: List[Dict[str, Any]] = []

        for item_data in items_data:
            product_id = item_data.get('product_id')
            product = Product.query.filter_by(id=product_id, deleted_at=None).first()
            if not product:
                raise NotFoundError('Product', product_id)

            quantity = self._parse_positive_int(item_data.get('quantity'), field='quantity')
            unit_price_usd = self._parse_decimal(item_data.get('unit_price_usd'), field='unit_price_usd')
            if unit_price_usd < 0:
                raise ValidationError('El precio unitario no puede ser negativo', field='unit_price_usd')

            line_subtotal = self._parse_decimal(
                item_data.get('line_subtotal_usd', unit_price_usd * quantity),
                field='line_subtotal_usd'
            )
            description_snapshot = (item_data.get('description') or product.descripcion or '').strip()
            if not description_snapshot:
                raise ValidationError('Cada línea debe tener descripción', field='description')

            subtotal_usd += line_subtotal
            validated_items.append({
                'product': product,
                'quantity': quantity,
                'unit_price_usd': unit_price_usd.quantize(Decimal('0.0001')),
                'line_subtotal_usd': line_subtotal.quantize(Decimal('0.0001')),
                'description_snapshot': description_snapshot[:200],
            })

        taxable_base_usd = self._parse_decimal(data.get('taxable_base_usd', subtotal_usd), field='taxable_base_usd')
        tax_amount_usd = self._parse_decimal(data.get('tax_amount_usd', Decimal('0.0000')), field='tax_amount_usd')
        total_usd = self._parse_decimal(data.get('total_usd', taxable_base_usd + tax_amount_usd), field='total_usd')

        invoice = PurchaseInvoice(
            supplier_id=supplier_id,
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            currency_code=(data.get('currency_code') or 'USD').strip().upper() or 'USD',
            exchange_rate_value=exchange_rate_value,
            subtotal_usd=subtotal_usd.quantize(Decimal('0.0001')),
            taxable_base_usd=taxable_base_usd.quantize(Decimal('0.0001')),
            tax_amount_usd=tax_amount_usd.quantize(Decimal('0.0001')),
            total_usd=total_usd.quantize(Decimal('0.0001')),
            notes=(data.get('notes') or '').strip() or None,
            created_by=user_id,
            updated_by=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        try:
            db.session.add(invoice)
            db.session.flush()

            for item in validated_items:
                product = item['product']
                purchase_item = PurchaseInvoiceItem(
                    invoice_id=invoice.id,
                    product_id=product.id,
                    description_snapshot=item['description_snapshot'],
                    quantity=item['quantity'],
                    unit_price_usd=item['unit_price_usd'],
                    line_subtotal_usd=item['line_subtotal_usd'],
                )
                db.session.add(purchase_item)

                movement = Movimiento(
                    producto_id=product.id,
                    tipo='ENTRADA',
                    cantidad=item['quantity'],
                    fecha=invoice_date,
                    descripcion=f'Compra factura {invoice_number} - {supplier.nombre}',
                    created_by=user_id,
                    updated_by=user_id,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                db.session.add(movement)

                product.stock = int(product.stock or 0) + item['quantity']
                product.proveedor_id = supplier_id
                product.precio_dolares = item['unit_price_usd'].quantize(Decimal('0.01'))
                product.updated_by = user_id
                product.updated_at = datetime.utcnow()

            db.session.commit()
            current_app.logger.info(
                'Purchase invoice created: %s supplier=%s items=%s by user %s',
                invoice_number,
                supplier_id,
                len(validated_items),
                user_id,
            )
            return self.get_purchase_invoice(invoice.id)
        except SQLAlchemyError as exc:
            db.session.rollback()
            current_app.logger.error('Database error creating purchase invoice: %s', str(exc))
            raise BusinessLogicError(f'Error al registrar la factura de compra: {exc}') from exc

    def get_product_purchase_history(self, product_id: int) -> List[PurchaseInvoiceItem]:
        """Return historical purchase lines for a product ordered by newest invoice first."""
        product = Product.query.filter_by(id=product_id, deleted_at=None).first()
        if not product:
            raise NotFoundError('Product', product_id)

        return (
            PurchaseInvoiceItem.query
            .join(PurchaseInvoice, PurchaseInvoiceItem.invoice_id == PurchaseInvoice.id)
            .filter(
                PurchaseInvoiceItem.product_id == product_id,
                PurchaseInvoice.deleted_at.is_(None),
            )
            .order_by(PurchaseInvoice.invoice_date.desc(), PurchaseInvoice.id.desc())
            .all()
        )

    def _parse_date(self, raw_value: Any, field: str):
        if not raw_value:
            raise ValidationError('La fecha de factura es requerida', field=field)
        if hasattr(raw_value, 'year') and hasattr(raw_value, 'month') and hasattr(raw_value, 'day'):
            return raw_value
        try:
            return datetime.strptime(str(raw_value), '%Y-%m-%d').date()
        except (TypeError, ValueError) as exc:
            raise ValidationError('La fecha de factura debe tener formato YYYY-MM-DD', field=field) from exc

    def _parse_decimal(self, raw_value: Any, field: str) -> Decimal:
        try:
            return Decimal(str(raw_value)).quantize(Decimal('0.0001'))
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise ValidationError(f'El campo {field} debe ser numérico', field=field) from exc

    def _parse_positive_int(self, raw_value: Any, field: str) -> int:
        try:
            parsed = int(raw_value)
        except (TypeError, ValueError) as exc:
            raise ValidationError(f'El campo {field} debe ser entero', field=field) from exc

        if parsed <= 0:
            raise ValidationError(f'El campo {field} debe ser mayor que cero', field=field)
        return parsed
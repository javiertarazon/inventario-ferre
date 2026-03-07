"""
Purchase invoice models to preserve supplier-specific history per product.
"""
from datetime import datetime

from app.extensions import db


class PurchaseInvoice(db.Model):
    """Header table for supplier purchase invoices."""

    __tablename__ = 'purchase_invoices'

    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'), nullable=False, index=True)
    invoice_number = db.Column(db.String(100), nullable=False)
    invoice_date = db.Column(db.Date, nullable=False, index=True)
    currency_code = db.Column(db.String(10), nullable=False, default='USD')
    exchange_rate_value = db.Column(db.Numeric(12, 4), nullable=True)
    subtotal_usd = db.Column(db.Numeric(14, 4), nullable=False, default=0)
    taxable_base_usd = db.Column(db.Numeric(14, 4), nullable=False, default=0)
    tax_amount_usd = db.Column(db.Numeric(14, 4), nullable=False, default=0)
    total_usd = db.Column(db.Numeric(14, 4), nullable=False, default=0)
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    deleted_at = db.Column(db.DateTime, nullable=True)

    supplier = db.relationship('Proveedor', backref='purchase_invoices')
    items = db.relationship(
        'PurchaseInvoiceItem',
        back_populates='invoice',
        cascade='all, delete-orphan',
        lazy='selectin'
    )

    __table_args__ = (
        db.UniqueConstraint('supplier_id', 'invoice_number', name='uq_purchase_invoice_supplier_number'),
    )

    def __repr__(self):
        return f'<PurchaseInvoice {self.invoice_number} supplier={self.supplier_id}>'


class PurchaseInvoiceItem(db.Model):
    """Line items for purchase invoices."""

    __tablename__ = 'purchase_invoice_items'

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('purchase_invoices.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    description_snapshot = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price_usd = db.Column(db.Numeric(12, 4), nullable=False)
    line_subtotal_usd = db.Column(db.Numeric(14, 4), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    invoice = db.relationship('PurchaseInvoice', back_populates='items')
    product = db.relationship('Product', back_populates='purchase_invoice_items')

    __table_args__ = (
        db.CheckConstraint('quantity > 0', name='check_purchase_item_quantity_positive'),
        db.CheckConstraint('unit_price_usd >= 0', name='check_purchase_item_price_non_negative'),
        db.CheckConstraint('line_subtotal_usd >= 0', name='check_purchase_item_subtotal_non_negative'),
    )

    def __repr__(self):
        return f'<PurchaseInvoiceItem invoice={self.invoice_id} product={self.product_id}>'
"""Daily sales closures and reconstructed output allocations."""
from datetime import datetime

from app.extensions import db


class DailySalesClosure(db.Model):
    """Stores one daily closure source row used to reconstruct exits."""

    __tablename__ = 'daily_sales_closures'

    id = db.Column(db.Integer, primary_key=True)
    closure_date = db.Column(db.Date, nullable=False, unique=True, index=True)
    total_sales_usd = db.Column(db.Numeric(14, 4), nullable=False, default=0)
    invoiced_share = db.Column(db.Numeric(5, 4), nullable=False, default=0.6000)
    non_invoiced_share = db.Column(db.Numeric(5, 4), nullable=False, default=0.4000)
    invoiced_sales_usd = db.Column(db.Numeric(14, 4), nullable=False, default=0)
    non_invoiced_sales_usd = db.Column(db.Numeric(14, 4), nullable=False, default=0)
    reconstructed_sales_usd = db.Column(db.Numeric(14, 4), nullable=False, default=0)
    generated_exit_units = db.Column(db.Integer, nullable=False, default=0)
    source_file_name = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    deleted_at = db.Column(db.DateTime, nullable=True)

    allocations = db.relationship(
        'DailySalesClosureAllocation',
        back_populates='closure',
        cascade='all, delete-orphan',
        lazy='selectin',
    )

    def __repr__(self):
        return f'<DailySalesClosure {self.closure_date} total={self.total_sales_usd}>'


class DailySalesClosureAllocation(db.Model):
    """Estimated product-level allocation generated from one daily closure."""

    __tablename__ = 'daily_sales_closure_allocations'

    id = db.Column(db.Integer, primary_key=True)
    closure_id = db.Column(db.Integer, db.ForeignKey('daily_sales_closures.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    movement_id = db.Column(db.Integer, db.ForeignKey('movimientos.id'), nullable=True, index=True)
    reference_unit_price_usd = db.Column(db.Numeric(12, 4), nullable=False)
    allocated_sales_usd = db.Column(db.Numeric(14, 4), nullable=False, default=0)
    estimated_quantity = db.Column(db.Integer, nullable=False)
    weighting_value_usd = db.Column(db.Numeric(14, 4), nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    closure = db.relationship('DailySalesClosure', back_populates='allocations')
    product = db.relationship('Product', backref='daily_sales_closure_allocations')
    movement = db.relationship('Movimiento', backref='daily_sales_closure_allocations')

    __table_args__ = (
        db.CheckConstraint('estimated_quantity > 0', name='check_daily_closure_alloc_qty_positive'),
        db.CheckConstraint('allocated_sales_usd >= 0', name='check_daily_closure_alloc_sales_non_negative'),
    )

    def __repr__(self):
        return f'<DailySalesClosureAllocation closure={self.closure_id} product={self.product_id}>'
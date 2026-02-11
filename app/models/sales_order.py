"""
Sales Order model for managing customer orders.
"""
from datetime import datetime, date
from app.extensions import db


class SalesOrder(db.Model):
    """Sales Order model."""
    
    __tablename__ = 'sales_orders'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Order information
    order_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    order_date = db.Column(db.Date, default=date.today, nullable=False, index=True)
    expected_delivery_date = db.Column(db.Date, nullable=True)
    
    # Customer
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False, index=True)
    
    # Status
    status = db.Column(db.String(20), default='draft', nullable=False, index=True)
    # Status options: draft, confirmed, packed, shipped, delivered, cancelled
    
    # Financial information
    subtotal = db.Column(db.Numeric(12, 2), default=0.0, nullable=False)
    tax_amount = db.Column(db.Numeric(12, 2), default=0.0, nullable=False)
    discount_amount = db.Column(db.Numeric(12, 2), default=0.0, nullable=False)
    shipping_cost = db.Column(db.Numeric(12, 2), default=0.0, nullable=False)
    total_amount = db.Column(db.Numeric(12, 2), default=0.0, nullable=False)
    
    # Payment
    payment_status = db.Column(db.String(20), default='pending')
    # Payment status: pending, partial, paid
    paid_amount = db.Column(db.Numeric(12, 2), default=0.0, nullable=False)
    
    # Shipping information
    shipping_address = db.Column(db.Text, nullable=True)
    shipping_method = db.Column(db.String(100), nullable=True)
    tracking_number = db.Column(db.String(100), nullable=True)
    
    # Notes
    notes = db.Column(db.Text, nullable=True)
    internal_notes = db.Column(db.Text, nullable=True)
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    items = db.relationship('SalesOrderItem', backref='sales_order', lazy='dynamic', cascade='all, delete-orphan')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_sales_orders')
    updater = db.relationship('User', foreign_keys=[updated_by], backref='updated_sales_orders')
    
    def __repr__(self):
        return f'<SalesOrder {self.order_number}>'
    
    def calculate_totals(self):
        """Calculate order totals from items."""
        self.subtotal = sum(item.total_price for item in self.items)
        self.total_amount = self.subtotal + self.tax_amount + self.shipping_cost - self.discount_amount
    
    def get_status_badge_class(self):
        """Get Bootstrap badge class for status."""
        status_classes = {
            'draft': 'secondary',
            'confirmed': 'primary',
            'packed': 'info',
            'shipped': 'warning',
            'delivered': 'success',
            'cancelled': 'danger'
        }
        return status_classes.get(self.status, 'secondary')
    
    def get_payment_status_badge_class(self):
        """Get Bootstrap badge class for payment status."""
        payment_classes = {
            'pending': 'warning',
            'partial': 'info',
            'paid': 'success'
        }
        return payment_classes.get(self.payment_status, 'secondary')
    
    def can_be_cancelled(self):
        """Check if order can be cancelled."""
        return self.status in ['draft', 'confirmed']
    
    def can_be_confirmed(self):
        """Check if order can be confirmed."""
        return self.status == 'draft'
    
    def to_dict(self):
        """Convert sales order to dictionary."""
        return {
            'id': self.id,
            'order_number': self.order_number,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'customer_id': self.customer_id,
            'customer_name': self.customer.name if self.customer else None,
            'status': self.status,
            'payment_status': self.payment_status,
            'subtotal': float(self.subtotal),
            'tax_amount': float(self.tax_amount),
            'total_amount': float(self.total_amount),
            'paid_amount': float(self.paid_amount),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class SalesOrderItem(db.Model):
    """Sales Order Item model."""
    
    __tablename__ = 'sales_order_items'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    sales_order_id = db.Column(db.Integer, db.ForeignKey('sales_orders.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    
    # Item information
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    discount_percent = db.Column(db.Numeric(5, 2), default=0.0)
    tax_percent = db.Column(db.Numeric(5, 2), default=0.0)
    total_price = db.Column(db.Numeric(12, 2), nullable=False)
    
    # Notes
    notes = db.Column(db.Text, nullable=True)
    
    # Relationships
    product = db.relationship('Product', backref='sales_order_items')
    
    def __repr__(self):
        return f'<SalesOrderItem {self.product_id} x {self.quantity}>'
    
    def calculate_total(self):
        """Calculate total price for this item."""
        subtotal = self.quantity * self.unit_price
        discount = subtotal * (self.discount_percent / 100)
        after_discount = subtotal - discount
        tax = after_discount * (self.tax_percent / 100)
        self.total_price = after_discount + tax
    
    def to_dict(self):
        """Convert sales order item to dictionary."""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_code': self.product.codigo if self.product else None,
            'product_name': self.product.descripcion if self.product else None,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price),
            'discount_percent': float(self.discount_percent),
            'tax_percent': float(self.tax_percent),
            'total_price': float(self.total_price)
        }

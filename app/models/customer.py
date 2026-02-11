"""
Customer model for sales orders.
"""
from datetime import datetime
from app.extensions import db


class Customer(db.Model):
    """Customer model for managing clients."""
    
    __tablename__ = 'customers'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Customer information
    name = db.Column(db.String(200), nullable=False, index=True)
    email = db.Column(db.String(255), nullable=True, index=True)
    phone = db.Column(db.String(20), nullable=True)
    
    # Tax information
    tax_id = db.Column(db.String(50), nullable=True, unique=True, index=True)  # RIF/NIT/Tax ID
    tax_id_type = db.Column(db.String(10), nullable=True)  # J, V, E, G, P
    
    # Address
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), default='Venezuela')
    postal_code = db.Column(db.String(20), nullable=True)
    
    # Business information
    company_name = db.Column(db.String(200), nullable=True)
    website = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    # Customer type
    customer_type = db.Column(db.String(20), default='individual')  # individual, business
    
    # Credit settings
    credit_limit = db.Column(db.Numeric(12, 2), default=0.0)
    payment_terms = db.Column(db.Integer, default=0)  # Days for payment
    
    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    sales_orders = db.relationship('SalesOrder', backref='customer', lazy='dynamic')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_customers')
    updater = db.relationship('User', foreign_keys=[updated_by], backref='updated_customers')
    
    def __repr__(self):
        return f'<Customer {self.name}>'
    
    def get_full_address(self):
        """Get formatted full address."""
        parts = [self.address, self.city, self.state, self.country, self.postal_code]
        return ', '.join([p for p in parts if p])
    
    def get_total_orders(self):
        """Get total number of orders."""
        return self.sales_orders.filter_by(deleted_at=None).count()
    
    def get_total_sales(self):
        """Get total sales amount."""
        from app.models.sales_order import SalesOrder
        total = db.session.query(db.func.sum(SalesOrder.total_amount)).filter(
            SalesOrder.customer_id == self.id,
            SalesOrder.deleted_at == None
        ).scalar()
        return float(total) if total else 0.0
    
    def to_dict(self):
        """Convert customer to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'tax_id': self.tax_id,
            'address': self.get_full_address(),
            'company_name': self.company_name,
            'customer_type': self.customer_type,
            'is_active': self.is_active,
            'total_orders': self.get_total_orders(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

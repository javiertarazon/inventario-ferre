"""
Enhanced Product model with audit fields and constraints.
"""
from datetime import date, datetime
from app.extensions import db


DEFAULT_INVENTORY_ENTRY_DATE = date(2024, 8, 1)


class Product(db.Model):
    """Product model with audit fields and data integrity constraints."""
    
    __tablename__ = 'products'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Product information
    codigo = db.Column(db.String(50), unique=True, nullable=False, index=True)
    descripcion = db.Column(db.String(200), nullable=False, index=True)
    stock = db.Column(db.Integer, default=0, nullable=False)
    precio_dolares = db.Column(db.Numeric(10, 2), default=0.0, nullable=False)
    factor_ajuste = db.Column(db.Numeric(5, 2), default=1.0, nullable=False)
    inventory_entry_date = db.Column(db.Date, nullable=False, default=lambda: DEFAULT_INVENTORY_ENTRY_DATE)
    
    # Inventory management
    reorder_point = db.Column(db.Integer, default=10, nullable=False)  # Punto de reorden
    reorder_quantity = db.Column(db.Integer, default=50, nullable=False)  # Cantidad a reordenar
    
    # Foreign keys
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'), index=True)
    item_group_id = db.Column(db.Integer, db.ForeignKey('item_groups.id'), index=True)
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    deleted_at = db.Column(db.DateTime, nullable=True)  # Soft delete
    
    # Relationships
    proveedor = db.relationship('Proveedor', backref='products')
    movimientos = db.relationship('Movimiento', backref='producto', lazy='dynamic')
    purchase_invoice_items = db.relationship('PurchaseInvoiceItem', back_populates='product', lazy='dynamic')
    
    # Constraints
    __table_args__ = (
        db.CheckConstraint('stock >= 0', name='check_stock_positive'),
        db.CheckConstraint('precio_dolares >= 0', name='check_price_positive'),
        db.CheckConstraint('factor_ajuste > 0', name='check_factor_positive'),
    )
    
    def __repr__(self):
        return f'<Product {self.codigo}: {self.descripcion}>'
    
    def is_deleted(self) -> bool:
        """Check if product is soft deleted."""
        return self.deleted_at is not None
    
    def needs_reorder(self) -> bool:
        """Check if product needs to be reordered."""
        return self.stock <= self.reorder_point
    
    def get_stock_status(self) -> str:
        """Get stock status: critical, low, medium, good."""
        if self.stock == 0:
            return 'critical'
        elif self.stock <= self.reorder_point:
            return 'low'
        elif self.stock <= self.reorder_point * 2:
            return 'medium'
        else:
            return 'good'
    
    def soft_delete(self):
        """Soft delete the product."""
        self.deleted_at = datetime.utcnow()
    
    def restore(self):
        """Restore a soft deleted product."""
        self.deleted_at = None
    
    def to_dict(self):
        """Convert product to dictionary."""
        return {
            'id': self.id,
            'codigo': self.codigo,
            'descripcion': self.descripcion,
            'stock': self.stock,
            'precio_dolares': float(self.precio_dolares) if self.precio_dolares else 0.0,
            'factor_ajuste': float(self.factor_ajuste) if self.factor_ajuste else 1.0,
            'proveedor_id': self.proveedor_id,
            'inventory_entry_date': self.inventory_entry_date.isoformat() if self.inventory_entry_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None
        }

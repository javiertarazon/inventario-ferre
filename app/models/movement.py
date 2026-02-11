"""
Enhanced Movement (Movimiento) model with audit fields.
"""
from datetime import datetime
from app.extensions import db


class Movimiento(db.Model):
    """Movement model with audit fields."""
    
    __tablename__ = 'movimientos'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Movement information
    producto_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    tipo = db.Column(db.String(20), nullable=False, index=True)  # entrada, salida
    cantidad = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.Date, nullable=False, index=True)
    descripcion = db.Column(db.Text, nullable=True)
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_movements')
    updater = db.relationship('User', foreign_keys=[updated_by], backref='updated_movements')
    
    # Constraints
    __table_args__ = (
        db.CheckConstraint('cantidad > 0', name='check_cantidad_positive'),
        db.CheckConstraint("tipo IN ('ENTRADA', 'SALIDA', 'AJUSTE', 'entrada', 'salida', 'ajuste')", name='check_tipo_valid'),
        db.Index('idx_movement_product_date', 'producto_id', 'fecha'),
    )
    
    def __repr__(self):
        return f'<Movimiento {self.tipo} {self.cantidad} - Product:{self.producto_id}>'
    
    def to_dict(self):
        """Convert movement to dictionary."""
        return {
            'id': self.id,
            'producto_id': self.producto_id,
            'tipo': self.tipo,
            'cantidad': self.cantidad,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'descripcion': self.descripcion,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

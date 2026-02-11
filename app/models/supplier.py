"""
Enhanced Supplier (Proveedor) model with audit fields.
"""
from datetime import datetime
from app.extensions import db


class Proveedor(db.Model):
    """Supplier model with audit fields."""
    
    __tablename__ = 'proveedores'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Supplier information
    nombre = db.Column(db.String(200), nullable=False, index=True)
    rif = db.Column(db.String(20), unique=True, nullable=True, index=True)
    telefono = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    direccion = db.Column(db.Text, nullable=True)
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    deleted_at = db.Column(db.DateTime, nullable=True)  # Soft delete
    
    def __repr__(self):
        return f'<Proveedor {self.nombre}>'
    
    def is_deleted(self) -> bool:
        """Check if supplier is soft deleted."""
        return self.deleted_at is not None
    
    def soft_delete(self):
        """Soft delete the supplier."""
        self.deleted_at = datetime.utcnow()
    
    def restore(self):
        """Restore a soft deleted supplier."""
        self.deleted_at = None
    
    def to_dict(self):
        """Convert supplier to dictionary."""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'rif': self.rif,
            'telefono': self.telefono,
            'email': self.email,
            'direccion': self.direccion,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None
        }

"""
Audit log model for tracking system changes.
Records all create, update, delete operations with before/after values.
"""
from datetime import datetime
from app.extensions import db


class AuditLog(db.Model):
    """Audit log model for tracking system changes."""
    
    __tablename__ = 'audit_logs'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # User information
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Action information
    action = db.Column(db.String(50), nullable=False, index=True)  # CREATE, UPDATE, DELETE, LOGIN, etc.
    entity_type = db.Column(db.String(50), nullable=False, index=True)  # Product, Supplier, Movement, etc.
    entity_id = db.Column(db.Integer, nullable=False, index=True)
    
    # Change tracking
    old_values = db.Column(db.JSON, nullable=True)
    new_values = db.Column(db.JSON, nullable=True)
    
    # Request information
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    
    # Timestamp
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Indexes for efficient querying
    __table_args__ = (
        db.Index('idx_audit_user_timestamp', 'user_id', 'timestamp'),
        db.Index('idx_audit_entity', 'entity_type', 'entity_id'),
        db.Index('idx_audit_action_timestamp', 'action', 'timestamp'),
    )
    
    def __repr__(self):
        return f'<AuditLog {self.action} {self.entity_type}:{self.entity_id} by User:{self.user_id}>'
    
    def to_dict(self):
        """Convert audit log to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

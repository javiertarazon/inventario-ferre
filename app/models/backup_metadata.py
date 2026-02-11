"""
Backup metadata model for tracking backup operations.
"""
from datetime import datetime
from app.extensions import db


class BackupMetadata(db.Model):
    """Backup metadata model for tracking backup operations."""
    
    __tablename__ = 'backup_metadata'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Backup information
    backup_name = db.Column(db.String(255), unique=True, nullable=False, index=True)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.BigInteger, nullable=False)
    checksum = db.Column(db.String(64), nullable=False)  # SHA-256
    
    # Backup metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    backup_type = db.Column(db.String(20), nullable=False)  # MANUAL, SCHEDULED
    status = db.Column(db.String(20), nullable=False)  # SUCCESS, FAILED
    error_message = db.Column(db.Text, nullable=True)
    
    # Constraints
    __table_args__ = (
        db.CheckConstraint("backup_type IN ('MANUAL', 'SCHEDULED')", name='check_backup_type_valid'),
        db.CheckConstraint("status IN ('SUCCESS', 'FAILED')", name='check_status_valid'),
    )
    
    def __repr__(self):
        return f'<BackupMetadata {self.backup_name} - {self.status}>'
    
    def to_dict(self):
        """Convert backup metadata to dictionary."""
        return {
            'id': self.id,
            'backup_name': self.backup_name,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'checksum': self.checksum,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by,
            'backup_type': self.backup_type,
            'status': self.status,
            'error_message': self.error_message
        }

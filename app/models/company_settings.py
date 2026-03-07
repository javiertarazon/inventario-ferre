"""
Company settings model for fiscal and contact information.
"""
from datetime import datetime

from app.extensions import db


class CompanySettings(db.Model):
    """Singleton-style company profile used by reports and exports."""

    __tablename__ = 'company_settings'

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(200), nullable=False)
    rif = db.Column(db.String(20), nullable=False)
    fiscal_address = db.Column(db.Text, nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    creator = db.relationship('User', foreign_keys=[created_by], backref='created_company_settings')
    updater = db.relationship('User', foreign_keys=[updated_by], backref='updated_company_settings')

    def __repr__(self):
        return f'<CompanySettings {self.company_name}>'

    def to_dict(self):
        """Convert settings to a serializable dictionary."""
        return {
            'id': self.id,
            'company_name': self.company_name,
            'rif': self.rif,
            'fiscal_address': self.fiscal_address,
            'phone': self.phone,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
        }
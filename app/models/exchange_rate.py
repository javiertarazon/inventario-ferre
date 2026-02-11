"""
Exchange Rate model for currency conversion tracking.
"""
from datetime import datetime, date
from app.extensions import db


class ExchangeRate(db.Model):
    """Exchange rate model for USD to Bs conversion."""
    
    __tablename__ = 'exchange_rates'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Rate information
    date = db.Column(db.Date, nullable=False, unique=True, index=True)
    rate = db.Column(db.Numeric(10, 2), nullable=False)  # USD to Bs rate
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_exchange_rates')
    
    def __repr__(self):
        return f'<ExchangeRate {self.date}: {self.rate} Bs/$>'
    
    def to_dict(self):
        """Convert exchange rate to dictionary."""
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'rate': float(self.rate) if self.rate else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by
        }
    
    @staticmethod
    def get_current_rate():
        """Get the most recent exchange rate."""
        return ExchangeRate.query.order_by(ExchangeRate.date.desc()).first()
    
    @staticmethod
    def get_rate_for_date(target_date):
        """Get exchange rate for a specific date."""
        return ExchangeRate.query.filter_by(date=target_date).first()

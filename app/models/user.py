"""
User model with enhanced security features.
Includes password hashing, account lockout, and role-based access control.
"""
from datetime import datetime, timedelta
from flask_login import UserMixin
from app.extensions import db, bcrypt


class User(db.Model, UserMixin):
    """User model with security enhancements."""
    
    __tablename__ = 'users'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic information
    username = db.Column(db.String(150), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Role-based access control
    role = db.Column(db.String(50), default='user', nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Security fields
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password: str):
        """Hash and set user password."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """Verify password against stored hash."""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def is_locked(self) -> bool:
        """Check if account is currently locked."""
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until
    
    def lock_account(self, duration_minutes: int = 30):
        """Lock account for specified duration."""
        self.locked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
        db.session.commit()
    
    def unlock_account(self):
        """Unlock account and reset failed login attempts."""
        self.locked_until = None
        self.failed_login_attempts = 0
        db.session.commit()
    
    def record_failed_login(self, max_attempts: int = 5):
        """Record failed login attempt and lock if threshold exceeded."""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= max_attempts:
            self.lock_account()
        db.session.commit()
    
    def record_successful_login(self):
        """Record successful login and reset failed attempts."""
        self.last_login = datetime.utcnow()
        self.failed_login_attempts = 0
        self.locked_until = None
        db.session.commit()
    
    def has_role(self, role: str) -> bool:
        """Check if user has specified role."""
        return self.role == role
    
    def is_admin(self) -> bool:
        """Check if user is an administrator."""
        return self.role == 'admin'

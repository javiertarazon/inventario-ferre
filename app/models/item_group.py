"""
Item Group (Category) model for organizing products.
"""
from datetime import datetime
from app.extensions import db


class ItemGroup(db.Model):
    """Item Group model for product categorization."""
    
    __tablename__ = 'item_groups'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Group information
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('item_groups.id'), nullable=True, index=True)
    
    # Display settings
    color = db.Column(db.String(7), default='#007bff')  # Hex color for UI
    icon = db.Column(db.String(50), default='bi-box')  # Bootstrap icon class
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    parent = db.relationship('ItemGroup', remote_side=[id], backref='children')
    products = db.relationship('Product', backref='item_group', lazy='dynamic')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_item_groups')
    updater = db.relationship('User', foreign_keys=[updated_by], backref='updated_item_groups')
    
    def __repr__(self):
        return f'<ItemGroup {self.name}>'
    
    def get_full_path(self):
        """Get full hierarchical path of the category."""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name
    
    def get_all_children(self):
        """Get all children recursively."""
        children = []
        # Filter out deleted children
        active_children = [c for c in self.children if c.deleted_at is None]
        for child in active_children:
            children.append(child)
            children.extend(child.get_all_children())
        return children
    
    def get_product_count(self):
        """Get total number of products in this category and subcategories."""
        count = self.products.filter_by(deleted_at=None).count()
        # Filter out deleted children
        active_children = [c for c in self.children if c.deleted_at is None]
        for child in active_children:
            count += child.get_product_count()
        return count
    
    def to_dict(self):
        """Convert item group to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'parent_id': self.parent_id,
            'parent_name': self.parent.name if self.parent else None,
            'full_path': self.get_full_path(),
            'color': self.color,
            'icon': self.icon,
            'product_count': self.get_product_count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

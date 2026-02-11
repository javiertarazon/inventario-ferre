"""
Item Group Repository - Data access for item groups/categories.
"""
from typing import Optional, List
from app.models.item_group import ItemGroup
from app.repositories.base_repository import BaseRepository


class ItemGroupRepository(BaseRepository[ItemGroup]):
    """Repository for item group data access."""
    
    def __init__(self):
        """Initialize repository."""
        super().__init__(ItemGroup)
    
    def get_by_name(self, name: str) -> Optional[ItemGroup]:
        """
        Get item group by name.
        
        Args:
            name: Item group name
            
        Returns:
            ItemGroup instance or None
        """
        return self.model.query.filter_by(name=name, deleted_at=None).first()
    
    def get_root_groups(self) -> List[ItemGroup]:
        """
        Get all root level groups (no parent).
        
        Returns:
            List of root item groups
        """
        return self.model.query.filter_by(parent_id=None, deleted_at=None).all()
    
    def get_children(self, parent_id: int) -> List[ItemGroup]:
        """
        Get all children of a parent group.
        
        Args:
            parent_id: Parent group ID
            
        Returns:
            List of child item groups
        """
        return self.model.query.filter_by(parent_id=parent_id, deleted_at=None).all()
    
    def get_active_groups(self) -> List[ItemGroup]:
        """
        Get all active groups (not deleted).
        
        Returns:
            List of active item groups
        """
        return self.model.query.filter_by(deleted_at=None).order_by(ItemGroup.name).all()

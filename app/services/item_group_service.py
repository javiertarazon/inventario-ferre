"""
Item Group Service - Business logic for item groups/categories.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from app.models import ItemGroup
from app.repositories import ItemGroupRepository
from app.services.validation_service import ValidationService
from app.utils.exceptions import ValidationError, NotFoundError, DatabaseError, BusinessLogicError
from app.extensions import db


class ItemGroupService:
    """Service for managing item group business logic."""
    
    def __init__(self):
        """Initialize item group service with dependencies."""
        self.item_group_repo = ItemGroupRepository()
        self.validation_service = ValidationService()
    
    def create_item_group(self, data: Dict[str, Any], user_id: int) -> ItemGroup:
        """
        Create new item group with validation.
        
        Args:
            data: Item group data dictionary
            user_id: ID of user creating the item group
            
        Returns:
            Created item group instance
            
        Raises:
            ValidationError: If data validation fails
            DatabaseError: If database operation fails
        """
        try:
            # Validate name
            name = data.get('name', '').strip()
            if not name:
                raise ValidationError("El nombre de la categoría es requerido", field='name')
            
            # Check if name already exists
            existing = self.item_group_repo.get_by_name(name)
            if existing:
                raise ValidationError(f"Ya existe una categoría con el nombre '{name}'", field='name')
            
            # Validate parent if provided
            parent_id = data.get('parent_id')
            if parent_id:
                parent = self.item_group_repo.get_by_id(parent_id)
                if not parent or parent.deleted_at is not None:
                    raise ValidationError("La categoría padre no existe", field='parent_id')
            
            # Prepare data
            validated_data = {
                'name': name,
                'description': data.get('description', '').strip() or None,
                'parent_id': parent_id,
                'color': data.get('color', '#007bff'),
                'icon': data.get('icon', 'bi-box'),
                'created_by': user_id,
                'updated_by': user_id,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            # Create item group
            item_group = ItemGroup(**validated_data)
            created_group = self.item_group_repo.create(item_group)
            
            current_app.logger.info(f"Item group created: {created_group.name} by user {user_id}")
            
            return created_group
            
        except ValidationError:
            raise
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error creating item group: {str(e)}")
            raise DatabaseError("Error al crear la categoría", original_error=e)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Unexpected error creating item group: {str(e)}")
            raise BusinessLogicError(f"Error inesperado al crear la categoría: {str(e)}")
    
    def update_item_group(self, group_id: int, data: Dict[str, Any], user_id: int) -> ItemGroup:
        """Update existing item group."""
        try:
            # Get existing group
            group = self.item_group_repo.get_by_id(group_id)
            if not group or group.deleted_at is not None:
                raise NotFoundError("ItemGroup", group_id)
            
            # Validate name if changed
            name = data.get('name', '').strip()
            if name and name != group.name:
                existing = self.item_group_repo.get_by_name(name)
                if existing and existing.id != group_id:
                    raise ValidationError(f"Ya existe una categoría con el nombre '{name}'", field='name')
                group.name = name
            
            # Update fields
            if 'description' in data:
                group.description = data['description'].strip() or None
            if 'parent_id' in data:
                parent_id = data['parent_id']
                if parent_id and parent_id != group_id:  # Prevent self-reference
                    parent = self.item_group_repo.get_by_id(parent_id)
                    if not parent:
                        raise ValidationError("La categoría padre no existe", field='parent_id')
                    group.parent_id = parent_id
                elif parent_id is None:
                    group.parent_id = None
            if 'color' in data:
                group.color = data['color']
            if 'icon' in data:
                group.icon = data['icon']
            
            # Set audit fields
            group.updated_by = user_id
            group.updated_at = datetime.utcnow()
            
            # Save changes
            updated_group = self.item_group_repo.update(group)
            
            current_app.logger.info(f"Item group updated: {updated_group.name} by user {user_id}")
            
            return updated_group
            
        except (NotFoundError, ValidationError):
            raise
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error updating item group: {str(e)}")
            raise DatabaseError("Error al actualizar la categoría", original_error=e)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Unexpected error updating item group: {str(e)}")
            raise BusinessLogicError(f"Error inesperado al actualizar la categoría: {str(e)}")
    
    def delete_item_group(self, group_id: int, user_id: int) -> bool:
        """Soft delete item group."""
        try:
            group = self.item_group_repo.get_by_id(group_id)
            if not group or group.deleted_at is not None:
                raise NotFoundError("ItemGroup", group_id)
            
            # Check if has products
            if group.get_product_count() > 0:
                raise BusinessLogicError(
                    "No se puede eliminar la categoría porque tiene productos asociados"
                )
            
            # Soft delete
            group.deleted_at = datetime.utcnow()
            group.updated_by = user_id
            group.updated_at = datetime.utcnow()
            
            self.item_group_repo.update(group)
            
            current_app.logger.info(f"Item group soft deleted: {group.name} by user {user_id}")
            
            return True
            
        except (NotFoundError, BusinessLogicError):
            raise
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error deleting item group: {str(e)}")
            raise DatabaseError("Error al eliminar la categoría", original_error=e)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Unexpected error deleting item group: {str(e)}")
            raise BusinessLogicError(f"Error inesperado al eliminar la categoría: {str(e)}")
    
    def get_item_group(self, group_id: int) -> Optional[ItemGroup]:
        """Get item group by ID."""
        group = self.item_group_repo.get_by_id(group_id)
        if group and group.deleted_at is None:
            return group
        return None
    
    def get_all_groups(self) -> List[ItemGroup]:
        """Get all active item groups."""
        return self.item_group_repo.get_active_groups()
    
    def get_root_groups(self) -> List[ItemGroup]:
        """Get root level groups."""
        return self.item_group_repo.get_root_groups()
    
    def get_group_tree(self) -> List[Dict[str, Any]]:
        """Get hierarchical tree of all groups."""
        root_groups = self.get_root_groups()
        
        def build_tree(group: ItemGroup) -> Dict[str, Any]:
            return {
                'id': group.id,
                'name': group.name,
                'description': group.description,
                'color': group.color,
                'icon': group.icon,
                'product_count': group.get_product_count(),
                'children': [build_tree(child) for child in group.children if child.deleted_at is None]
            }
        
        return [build_tree(group) for group in root_groups]

    def get_all_groups(self):
        """
        Get all active item groups without pagination.
        
        Returns:
            List of all active item groups
        """
        try:
            return self.item_group_repo.get_all()
        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error getting all item groups: {str(e)}")
            raise DatabaseError(f"Error al obtener categorías: {str(e)}")

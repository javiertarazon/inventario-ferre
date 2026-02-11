"""
Supplier Service - Business logic for supplier management.
"""
from typing import Dict, Any, Optional
from datetime import datetime
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from app.models import Supplier
from app.repositories import SupplierRepository
from app.services.validation_service import ValidationService
from app.utils.exceptions import ValidationError, NotFoundError, DatabaseError, BusinessLogicError
from app.extensions import db


class SupplierService:
    """Service for managing supplier business logic."""
    
    def __init__(self):
        """Initialize supplier service with dependencies."""
        self.supplier_repo = SupplierRepository(Supplier)
        self.validation_service = ValidationService()
    
    def create_supplier(self, data: Dict[str, Any], user_id: int) -> Supplier:
        """
        Create new supplier with validation.
        
        Args:
            data: Supplier data dictionary
            user_id: ID of user creating the supplier
            
        Returns:
            Created supplier instance
            
        Raises:
            ValidationError: If data validation fails
            DatabaseError: If database operation fails
        """
        try:
            # Validate supplier data
            validated_data = self.validation_service.validate_supplier_data(data)
            
            # Check if RIF already exists
            if 'rif' in validated_data:
                existing = self.supplier_repo.get_by_rif(validated_data['rif'])
                if existing and existing.deleted_at is None:
                    raise ValidationError(
                        f"Ya existe un proveedor con el RIF {validated_data['rif']}",
                        field='rif'
                    )
            
            # Set audit fields
            validated_data['created_by'] = user_id
            validated_data['updated_by'] = user_id
            validated_data['created_at'] = datetime.utcnow()
            validated_data['updated_at'] = datetime.utcnow()
            
            # Create supplier
            supplier = Supplier(**validated_data)
            created_supplier = self.supplier_repo.create(supplier)
            
            current_app.logger.info(
                f"Supplier created: {created_supplier.nombre} by user {user_id}"
            )
            
            return created_supplier
            
        except ValidationError:
            raise
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error creating supplier: {str(e)}")
            raise DatabaseError("Error al crear el proveedor", original_error=e)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Unexpected error creating supplier: {str(e)}")
            raise BusinessLogicError(f"Error inesperado al crear el proveedor: {str(e)}")
    
    def update_supplier(self, supplier_id: int, data: Dict[str, Any], user_id: int) -> Supplier:
        """
        Update existing supplier with validation.
        
        Args:
            supplier_id: ID of supplier to update
            data: Updated supplier data
            user_id: ID of user updating the supplier
            
        Returns:
            Updated supplier instance
            
        Raises:
            NotFoundError: If supplier not found
            ValidationError: If data validation fails
            DatabaseError: If database operation fails
        """
        try:
            # Get existing supplier
            supplier = self.supplier_repo.get_by_id(supplier_id)
            if not supplier or supplier.deleted_at is not None:
                raise NotFoundError("Supplier", supplier_id)
            
            # Validate update data
            validated_data = self.validation_service.validate_supplier_data(data, is_update=True)
            
            # Check if RIF is being changed and if new RIF exists
            if 'rif' in validated_data and validated_data['rif'] != supplier.rif:
                existing = self.supplier_repo.get_by_rif(validated_data['rif'])
                if existing and existing.id != supplier_id and existing.deleted_at is None:
                    raise ValidationError(
                        f"Ya existe un proveedor con el RIF {validated_data['rif']}",
                        field='rif'
                    )
            
            # Update fields
            for key, value in validated_data.items():
                if hasattr(supplier, key):
                    setattr(supplier, key, value)
            
            # Set audit fields
            supplier.updated_by = user_id
            supplier.updated_at = datetime.utcnow()
            
            # Save changes
            updated_supplier = self.supplier_repo.update(supplier)
            
            current_app.logger.info(
                f"Supplier updated: {updated_supplier.nombre} by user {user_id}"
            )
            
            return updated_supplier
            
        except (NotFoundError, ValidationError):
            raise
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error updating supplier: {str(e)}")
            raise DatabaseError("Error al actualizar el proveedor", original_error=e)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Unexpected error updating supplier: {str(e)}")
            raise BusinessLogicError(f"Error inesperado al actualizar el proveedor: {str(e)}")
    
    def delete_supplier(self, supplier_id: int, user_id: int) -> bool:
        """
        Soft delete supplier.
        
        Args:
            supplier_id: ID of supplier to delete
            user_id: ID of user deleting the supplier
            
        Returns:
            True if deletion successful
            
        Raises:
            NotFoundError: If supplier not found
            DatabaseError: If database operation fails
        """
        try:
            # Get existing supplier
            supplier = self.supplier_repo.get_by_id(supplier_id)
            if not supplier or supplier.deleted_at is not None:
                raise NotFoundError("Supplier", supplier_id)
            
            # Soft delete
            supplier.deleted_at = datetime.utcnow()
            supplier.updated_by = user_id
            supplier.updated_at = datetime.utcnow()
            
            self.supplier_repo.update(supplier)
            
            current_app.logger.info(
                f"Supplier soft deleted: {supplier.nombre} by user {user_id}"
            )
            
            return True
            
        except NotFoundError:
            raise
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error deleting supplier: {str(e)}")
            raise DatabaseError("Error al eliminar el proveedor", original_error=e)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Unexpected error deleting supplier: {str(e)}")
            raise BusinessLogicError(f"Error inesperado al eliminar el proveedor: {str(e)}")
    
    def get_supplier(self, supplier_id: int) -> Optional[Supplier]:
        """
        Get supplier by ID.
        
        Args:
            supplier_id: ID of supplier to retrieve
            
        Returns:
            Supplier instance or None if not found
        """
        supplier = self.supplier_repo.get_by_id(supplier_id)
        if supplier and supplier.deleted_at is None:
            return supplier
        return None
    
    def get_supplier_by_rif(self, rif: str) -> Optional[Supplier]:
        """
        Get supplier by RIF.
        
        Args:
            rif: Supplier RIF
            
        Returns:
            Supplier instance or None if not found
        """
        supplier = self.supplier_repo.get_by_rif(rif)
        if supplier and supplier.deleted_at is None:
            return supplier
        return None
    
    def list_suppliers(self, page: int = 1, per_page: int = 20):
        """
        List all active suppliers with pagination.
        
        Args:
            page: Page number
            per_page: Items per page
            
        Returns:
            PaginatedResult with suppliers
        """
        try:
            # Validate pagination
            page, per_page = self.validation_service.validate_pagination(page, per_page)
            
            # Get active suppliers
            return self.supplier_repo.get_active_suppliers(page=page, per_page=per_page)
            
        except Exception as e:
            current_app.logger.error(f"Error listing suppliers: {str(e)}")
            raise BusinessLogicError(f"Error al listar proveedores: {str(e)}")
    
    def get_all_suppliers(self):
        """
        Get all active suppliers without pagination.
        
        Returns:
            List of all active suppliers
        """
        try:
            return self.supplier_repo.get_active_suppliers(page=None, per_page=None)
        except Exception as e:
            current_app.logger.error(f"Error getting all suppliers: {str(e)}")
            raise BusinessLogicError(f"Error al obtener proveedores: {str(e)}")

"""
Customer Service - Business logic for customer management.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from app.models import Customer
from app.repositories import CustomerRepository
from app.services.validation_service import ValidationService
from app.utils.exceptions import ValidationError, NotFoundError, DatabaseError, BusinessLogicError
from app.extensions import db


class CustomerService:
    """Service for managing customer business logic."""
    
    def __init__(self):
        """Initialize customer service with dependencies."""
        self.customer_repo = CustomerRepository()
        self.validation_service = ValidationService()
    
    def create_customer(self, data: Dict[str, Any], user_id: int) -> Customer:
        """
        Create new customer with validation.
        
        Args:
            data: Customer data dictionary
            user_id: ID of user creating the customer
            
        Returns:
            Created customer instance
            
        Raises:
            ValidationError: If data validation fails
            DatabaseError: If database operation fails
        """
        try:
            # Validate name
            name = data.get('name', '').strip()
            if not name:
                raise ValidationError("El nombre del cliente es requerido", field='name')
            
            # Validate email if provided
            email = data.get('email', '').strip()
            if email:
                if not self.validation_service._validate_email(email):
                    raise ValidationError("El formato del email es inválido", field='email')
                # Check if email already exists
                existing = self.customer_repo.get_by_email(email)
                if existing:
                    raise ValidationError(f"Ya existe un cliente con el email {email}", field='email')
            
            # Validate tax_id if provided
            tax_id = data.get('tax_id', '').strip()
            if tax_id:
                existing = self.customer_repo.get_by_tax_id(tax_id)
                if existing:
                    raise ValidationError(f"Ya existe un cliente con el RIF/NIT {tax_id}", field='tax_id')
            
            # Prepare data
            validated_data = {
                'name': name,
                'email': email or None,
                'phone': data.get('phone', '').strip() or None,
                'tax_id': tax_id or None,
                'tax_id_type': data.get('tax_id_type', '').strip() or None,
                'address': data.get('address', '').strip() or None,
                'city': data.get('city', '').strip() or None,
                'state': data.get('state', '').strip() or None,
                'country': data.get('country', 'Venezuela'),
                'postal_code': data.get('postal_code', '').strip() or None,
                'company_name': data.get('company_name', '').strip() or None,
                'website': data.get('website', '').strip() or None,
                'notes': data.get('notes', '').strip() or None,
                'customer_type': data.get('customer_type', 'individual'),
                'credit_limit': data.get('credit_limit', 0.0),
                'payment_terms': data.get('payment_terms', 0),
                'is_active': data.get('is_active', True),
                'created_by': user_id,
                'updated_by': user_id,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            # Create customer
            customer = Customer(**validated_data)
            created_customer = self.customer_repo.create(customer)
            
            current_app.logger.info(f"Customer created: {created_customer.name} by user {user_id}")
            
            return created_customer
            
        except ValidationError:
            raise
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error creating customer: {str(e)}")
            raise DatabaseError("Error al crear el cliente", original_error=e)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Unexpected error creating customer: {str(e)}")
            raise BusinessLogicError(f"Error inesperado al crear el cliente: {str(e)}")
    
    def update_customer(self, customer_id: int, data: Dict[str, Any], user_id: int) -> Customer:
        """Update existing customer.
        
        Updates specified customer fields with validation, preventing duplicate
        email and RIF/NIT values across the customer database.
        
        Args:
            customer_id: ID of customer to update
            data: Dictionary of fields to update  
            user_id: ID of user performing the update
            
        Returns:
            Updated Customer instance with all changes persisted
            
        Raises:
            NotFoundError: If customer not found or already deleted
            ValidationError: If data validation fails
            DatabaseError: If database operation fails
        """
        try:
            # Get existing customer
            customer = self.customer_repo.get_by_id(customer_id)
            if not customer or customer.deleted_at is not None:
                raise NotFoundError("Customer", customer_id)
            
            # Validate email if changed
            email = data.get('email', '').strip()
            if email and email != customer.email:
                if not self.validation_service._validate_email(email):
                    raise ValidationError("El formato del email es inválido", field='email')
                existing = self.customer_repo.get_by_email(email)
                if existing and existing.id != customer_id:
                    raise ValidationError(f"Ya existe un cliente con el email {email}", field='email')
                customer.email = email
            
            # Validate tax_id if changed
            tax_id = data.get('tax_id', '').strip()
            if tax_id and tax_id != customer.tax_id:
                existing = self.customer_repo.get_by_tax_id(tax_id)
                if existing and existing.id != customer_id:
                    raise ValidationError(f"Ya existe un cliente con el RIF/NIT {tax_id}", field='tax_id')
                customer.tax_id = tax_id
            
            # Update fields
            if 'name' in data:
                customer.name = data['name'].strip()
            if 'phone' in data:
                customer.phone = data['phone'].strip() or None
            if 'tax_id_type' in data:
                customer.tax_id_type = data['tax_id_type'].strip() or None
            if 'address' in data:
                customer.address = data['address'].strip() or None
            if 'city' in data:
                customer.city = data['city'].strip() or None
            if 'state' in data:
                customer.state = data['state'].strip() or None
            if 'country' in data:
                customer.country = data['country'].strip()
            if 'postal_code' in data:
                customer.postal_code = data['postal_code'].strip() or None
            if 'company_name' in data:
                customer.company_name = data['company_name'].strip() or None
            if 'website' in data:
                customer.website = data['website'].strip() or None
            if 'notes' in data:
                customer.notes = data['notes'].strip() or None
            if 'customer_type' in data:
                customer.customer_type = data['customer_type']
            if 'credit_limit' in data:
                customer.credit_limit = data['credit_limit']
            if 'payment_terms' in data:
                customer.payment_terms = data['payment_terms']
            if 'is_active' in data:
                customer.is_active = data['is_active']
            
            # Set audit fields
            customer.updated_by = user_id
            customer.updated_at = datetime.utcnow()
            
            # Save changes
            updated_customer = self.customer_repo.update(customer)
            
            current_app.logger.info(f"Customer updated: {updated_customer.name} by user {user_id}")
            
            return updated_customer
            
        except (NotFoundError, ValidationError):
            raise
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error updating customer: {str(e)}")
            raise DatabaseError("Error al actualizar el cliente", original_error=e)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Unexpected error updating customer: {str(e)}")
            raise BusinessLogicError(f"Error inesperado al actualizar el cliente: {str(e)}")
    
    def delete_customer(self, customer_id: int, user_id: int) -> bool:
        """Soft delete customer.
        
        Soft-deletes customer record (sets deleted_at timestamp) rather than
        removing the record, preserving referential integrity and audit trail.
        
        Args:
            customer_id: ID of customer to delete
            user_id: ID of user performing the deletion
            
        Returns:
            True if deletion successful
            
        Raises:
            NotFoundError: If customer not found or already deleted
            DatabaseError: If database operation fails
        """
        try:
            customer = self.customer_repo.get_by_id(customer_id)
            if not customer or customer.deleted_at is not None:
                raise NotFoundError("Customer", customer_id)
            
            # Soft delete
            customer.deleted_at = datetime.utcnow()
            customer.updated_by = user_id
            customer.updated_at = datetime.utcnow()
            
            self.customer_repo.update(customer)
            
            current_app.logger.info(f"Customer soft deleted: {customer.name} by user {user_id}")
            
            return True
            
        except NotFoundError:
            raise
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error deleting customer: {str(e)}")
            raise DatabaseError("Error al eliminar el cliente", original_error=e)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Unexpected error deleting customer: {str(e)}")
            raise BusinessLogicError(f"Error inesperado al eliminar el cliente: {str(e)}")
    
    def get_customer(self, customer_id: int) -> Optional[Customer]:
        """Get customer by ID.
        
        Retrieves a customer by their ID, excluding soft-deleted customers.
        
        Args:
            customer_id: ID of customer to retrieve
            
        Returns:
            Customer instance if found and not deleted, None otherwise
        """
        customer = self.customer_repo.get_by_id(customer_id)
        if customer and customer.deleted_at is None:
            return customer
        return None
    
    def list_customers(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """List all active customers with pagination.
        
        Args:
            page: Page number for pagination (starting from 1)
            per_page: Number of items to return per page (default 20)
            
        Returns:
            Dictionary containing:
                - items: List of Customer objects
                - total: Total count of customers
                - pages: Total number of pages
                - current_page: Current page number
                - per_page: Items per page used
                
        Raises:
            BusinessLogicError: If query fails
        """
        try:
            page, per_page = self.validation_service.validate_pagination(page, per_page)
            return self.customer_repo.get_active_customers(page=page, per_page=per_page)
        except Exception as e:
            current_app.logger.error(f"Error listing customers: {str(e)}")
            raise BusinessLogicError(f"Error al listar clientes: {str(e)}")
    
    def search_customers(self, query: str, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Search customers.
        
        Performs full-text search across customer names, emails, tax IDs,
        and company names with pagination support.
        
        Args:
            query: Search query string
            page: Page number for pagination (starting from 1)
            per_page: Number of items to return per page (default 20)
            
        Returns:
            Dictionary containing:
                - items: List of matching Customer objects
                - total: Total count of matches
                - pages: Total number of pages
                - current_page: Current page number
                - per_page: Items per page used
                
        Raises:
            BusinessLogicError: If search operation fails
        """
        try:
            page, per_page = self.validation_service.validate_pagination(page, per_page)
            return self.customer_repo.search_customers(query=query, page=page, per_page=per_page)
        except Exception as e:
            current_app.logger.error(f"Error searching customers: {str(e)}")
            raise BusinessLogicError(f"Error al buscar clientes: {str(e)}")

    def get_all_customers(self) -> List[Customer]:
        """Get all active customers without pagination.
        
        Returns all customers that are not soft-deleted. Use with caution
        on large datasets as no pagination is applied.
        
        Returns:
            List of all active Customer objects
            
        Raises:
            DatabaseError: If database query fails
        """
        try:
            return self.customer_repo.get_all_list()
        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error getting all customers: {str(e)}")
            raise DatabaseError(f"Error al obtener clientes: {str(e)}")

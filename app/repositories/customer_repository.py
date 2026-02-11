"""
Customer Repository - Data access for customers.
"""
from typing import Optional
from app.models.customer import Customer
from app.repositories.base_repository import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    """Repository for customer data access."""
    
    def __init__(self):
        """Initialize repository."""
        super().__init__(Customer)
    
    def get_by_email(self, email: str) -> Optional[Customer]:
        """
        Get customer by email.
        
        Args:
            email: Customer email
            
        Returns:
            Customer instance or None
        """
        return self.model.query.filter_by(email=email, deleted_at=None).first()
    
    def get_by_tax_id(self, tax_id: str) -> Optional[Customer]:
        """
        Get customer by tax ID.
        
        Args:
            tax_id: Customer tax ID (RIF/NIT)
            
        Returns:
            Customer instance or None
        """
        return self.model.query.filter_by(tax_id=tax_id, deleted_at=None).first()
    
    def get_active_customers(self, page: int = 1, per_page: int = 20):
        """
        Get all active customers with pagination.
        
        Args:
            page: Page number
            per_page: Items per page
            
        Returns:
            PaginatedResult with customers
        """
        query = self.model.query.filter_by(is_active=True, deleted_at=None)
        return self._paginate(query, page, per_page)
    
    def search_customers(self, query: str, page: int = 1, per_page: int = 20):
        """
        Search customers by name, email, or tax ID.
        
        Args:
            query: Search query
            page: Page number
            per_page: Items per page
            
        Returns:
            PaginatedResult with customers
        """
        search = f"%{query}%"
        db_query = self.model.query.filter(
            self.model.deleted_at == None,
            (self.model.name.like(search) | 
             self.model.email.like(search) |
             self.model.tax_id.like(search))
        )
        return self._paginate(db_query, page, per_page)

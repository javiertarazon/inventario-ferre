"""
Sales Order Repository - Data access for sales orders.
"""
from typing import Optional, List
from datetime import date
from app.models.sales_order import SalesOrder
from app.repositories.base_repository import BaseRepository


class SalesOrderRepository(BaseRepository[SalesOrder]):
    """Repository for sales order data access."""
    
    def __init__(self):
        """Initialize repository."""
        super().__init__(SalesOrder)
    
    def get_by_order_number(self, order_number: str) -> Optional[SalesOrder]:
        """
        Get sales order by order number.
        
        Args:
            order_number: Order number
            
        Returns:
            SalesOrder instance or None
        """
        return self.model.query.filter_by(order_number=order_number, deleted_at=None).first()
    
    def get_by_customer(self, customer_id: int, page: int = 1, per_page: int = 20):
        """
        Get sales orders by customer.
        
        Args:
            customer_id: Customer ID
            page: Page number
            per_page: Items per page
            
        Returns:
            PaginatedResult with sales orders
        """
        query = self.model.query.filter_by(customer_id=customer_id, deleted_at=None).order_by(
            self.model.order_date.desc()
        )
        return self._paginate(query, page, per_page)
    
    def get_by_status(self, status: str, page: int = 1, per_page: int = 20):
        """
        Get sales orders by status.
        
        Args:
            status: Order status
            page: Page number
            per_page: Items per page
            
        Returns:
            PaginatedResult with sales orders
        """
        query = self.model.query.filter_by(status=status, deleted_at=None).order_by(
            self.model.order_date.desc()
        )
        return self._paginate(query, page, per_page)
    
    def get_by_date_range(self, start_date: date, end_date: date, page: int = 1, per_page: int = 50):
        """
        Get sales orders by date range.
        
        Args:
            start_date: Start date
            end_date: End date
            page: Page number
            per_page: Items per page
            
        Returns:
            PaginatedResult with sales orders
        """
        query = self.model.query.filter(
            self.model.order_date >= start_date,
            self.model.order_date <= end_date,
            self.model.deleted_at == None
        ).order_by(self.model.order_date.desc())
        return self._paginate(query, page, per_page)
    
    def get_pending_orders(self, page: int = 1, per_page: int = 20):
        """
        Get pending orders (draft, confirmed).
        
        Args:
            page: Page number
            per_page: Items per page
            
        Returns:
            PaginatedResult with pending orders
        """
        query = self.model.query.filter(
            self.model.status.in_(['draft', 'confirmed']),
            self.model.deleted_at == None
        ).order_by(self.model.order_date.desc())
        return self._paginate(query, page, per_page)
    
    def generate_order_number(self) -> str:
        """
        Generate next order number.
        
        Returns:
            Order number in format SO-YYYYMMDD-NNNN
        """
        from datetime import datetime
        today = datetime.now()
        prefix = f"SO-{today.strftime('%Y%m%d')}"
        
        # Get last order number for today
        last_order = self.model.query.filter(
            self.model.order_number.like(f"{prefix}%")
        ).order_by(self.model.order_number.desc()).first()
        
        if last_order:
            # Extract sequence number and increment
            try:
                last_seq = int(last_order.order_number.split('-')[-1])
                next_seq = last_seq + 1
            except (ValueError, IndexError):
                next_seq = 1
        else:
            next_seq = 1
        
        return f"{prefix}-{next_seq:04d}"

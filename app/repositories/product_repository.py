"""
Product repository with specialized query methods.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from app.models.product import Product
from app.repositories.base_repository import BaseRepository, PaginatedResult
from app.extensions import db
from app.utils.exceptions import DatabaseError


class ProductRepository(BaseRepository[Product]):
    """Product repository with specialized queries."""
    
    def __init__(self):
        super().__init__(Product)
    
    def search_products(self, query: str, filters: Dict[str, Any] = None, 
                       page: int = 1, per_page: int = 20) -> PaginatedResult[Product]:
        """
        Search products with filters and pagination.
        
        Args:
            query: Search query for codigo or descripcion
            filters: Additional filters (proveedor_id, etc.)
            page: Page number
            per_page: Items per page
            
        Returns:
            Paginated result
        """
        try:
            q = db.session.query(Product).filter(Product.deleted_at.is_(None))
            
            # Search in codigo and descripcion
            if query:
                search_filter = or_(
                    Product.codigo.ilike(f'%{query}%'),
                    Product.descripcion.ilike(f'%{query}%')
                )
                q = q.filter(search_filter)
            
            # Apply additional filters
            if filters:
                if 'proveedor_id' in filters and filters['proveedor_id']:
                    q = q.filter(Product.proveedor_id == filters['proveedor_id'])
                if 'min_stock' in filters:
                    q = q.filter(Product.stock >= filters['min_stock'])
                if 'max_stock' in filters:
                    q = q.filter(Product.stock <= filters['max_stock'])
            
            total = q.count()
            items = q.offset((page - 1) * per_page).limit(per_page).all()
            
            return PaginatedResult(items, total, page, per_page)
        except SQLAlchemyError as e:
            raise DatabaseError("Error searching products", e)
    
    def get_low_stock_products(self, threshold: int = 10, 
                              page: int = 1, per_page: int = 20) -> PaginatedResult[Product]:
        """
        Get products with stock below threshold.
        
        Args:
            threshold: Stock threshold
            page: Page number
            per_page: Items per page
            
        Returns:
            Paginated result
        """
        try:
            q = db.session.query(Product).filter(
                Product.deleted_at.is_(None),
                Product.stock < threshold
            ).order_by(Product.stock.asc())
            
            total = q.count()
            items = q.offset((page - 1) * per_page).limit(per_page).all()
            
            return PaginatedResult(items, total, page, per_page)
        except SQLAlchemyError as e:
            raise DatabaseError("Error retrieving low stock products", e)
    
    def get_by_codigo(self, codigo: str) -> Optional[Product]:
        """
        Get product by codigo.
        
        Args:
            codigo: Product code
            
        Returns:
            Product or None
        """
        try:
            return db.session.query(Product).filter(
                Product.codigo == codigo,
                Product.deleted_at.is_(None)
            ).first()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Error retrieving product by codigo {codigo}", e)
    
    def get_active_products(self, page: int = 1, per_page: int = 20) -> PaginatedResult[Product]:
        """
        Get all active (non-deleted) products.
        
        Args:
            page: Page number
            per_page: Items per page
            
        Returns:
            Paginated result
        """
        try:
            q = db.session.query(Product).filter(Product.deleted_at.is_(None))
            total = q.count()
            items = q.offset((page - 1) * per_page).limit(per_page).all()
            
            return PaginatedResult(items, total, page, per_page)
        except SQLAlchemyError as e:
            raise DatabaseError("Error retrieving active products", e)
    
    def get_by_supplier(self, proveedor_id: int, 
                       page: int = 1, per_page: int = 20) -> PaginatedResult[Product]:
        """
        Get products by supplier.
        
        Args:
            proveedor_id: Supplier ID
            page: Page number
            per_page: Items per page
            
        Returns:
            Paginated result
        """
        try:
            q = db.session.query(Product).filter(
                Product.proveedor_id == proveedor_id,
                Product.deleted_at.is_(None)
            )
            total = q.count()
            items = q.offset((page - 1) * per_page).limit(per_page).all()
            
            return PaginatedResult(items, total, page, per_page)
        except SQLAlchemyError as e:
            raise DatabaseError(f"Error retrieving products for supplier {proveedor_id}", e)

    def get_by_category(self, category_id: int, page: int = 1, per_page: int = 20):
        """
        Get products by category with pagination.
        
        Args:
            category_id: ID of the item group/category
            page: Page number
            per_page: Items per page
            
        Returns:
            Paginated query result
        """
        return self.model.query.filter_by(
            item_group_id=category_id,
            deleted_at=None
        ).order_by(self.model.codigo).paginate(
            page=page, per_page=per_page, error_out=False
        )

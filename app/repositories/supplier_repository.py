"""
Supplier repository.
"""
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError
from app.models.supplier import Proveedor
from app.repositories.base_repository import BaseRepository, PaginatedResult
from app.extensions import db
from app.utils.exceptions import DatabaseError


class SupplierRepository(BaseRepository[Proveedor]):
    """Supplier repository."""
    
    def __init__(self):
        super().__init__(Proveedor)
    
    def get_by_rif(self, rif: str) -> Optional[Proveedor]:
        """Get supplier by RIF."""
        try:
            return db.session.query(Proveedor).filter(
                Proveedor.rif == rif,
                Proveedor.deleted_at.is_(None)
            ).first()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Error retrieving supplier by RIF {rif}", e)
    
    def get_active_suppliers(self, page: int = 1, per_page: int = 20) -> PaginatedResult[Proveedor]:
        """Get all active suppliers."""
        try:
            q = db.session.query(Proveedor).filter(Proveedor.deleted_at.is_(None))
            total = q.count()
            items = q.offset((page - 1) * per_page).limit(per_page).all()
            return PaginatedResult(items, total, page, per_page)
        except SQLAlchemyError as e:
            raise DatabaseError("Error retrieving active suppliers", e)
    
    def get_all_list(self):
        """
        Get all active suppliers as a simple list (no pagination).
        
        Returns:
            List of all active suppliers
        """
        try:
            return db.session.query(Proveedor).filter(Proveedor.deleted_at.is_(None)).all()
        except SQLAlchemyError as e:
            raise DatabaseError("Error retrieving suppliers list", e)

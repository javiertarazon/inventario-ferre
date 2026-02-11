"""
Movement repository.
"""
from datetime import date
from typing import List
from sqlalchemy.exc import SQLAlchemyError
from app.models.movement import Movimiento
from app.repositories.base_repository import BaseRepository, PaginatedResult
from app.extensions import db
from app.utils.exceptions import DatabaseError


class MovementRepository(BaseRepository[Movimiento]):
    """Movement repository."""
    
    def __init__(self):
        super().__init__(Movimiento)
    
    def get_by_date_range(self, start_date: date, end_date: date, 
                         page: int = 1, per_page: int = 50) -> PaginatedResult[Movimiento]:
        """Get movements by date range."""
        try:
            q = db.session.query(Movimiento).filter(
                Movimiento.fecha >= start_date,
                Movimiento.fecha <= end_date
            ).order_by(Movimiento.fecha.desc())
            
            total = q.count()
            items = q.offset((page - 1) * per_page).limit(per_page).all()
            return PaginatedResult(items, total, page, per_page)
        except SQLAlchemyError as e:
            raise DatabaseError("Error retrieving movements by date range", e)
    
    def get_by_product(self, producto_id: int, 
                      page: int = 1, per_page: int = 50) -> PaginatedResult[Movimiento]:
        """Get movements by product."""
        try:
            q = db.session.query(Movimiento).filter(
                Movimiento.producto_id == producto_id
            ).order_by(Movimiento.fecha.desc())
            
            total = q.count()
            items = q.offset((page - 1) * per_page).limit(per_page).all()
            return PaginatedResult(items, total, page, per_page)
        except SQLAlchemyError as e:
            raise DatabaseError(f"Error retrieving movements for product {producto_id}", e)

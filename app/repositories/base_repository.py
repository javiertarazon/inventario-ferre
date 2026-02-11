"""
Base repository with common CRUD operations.
Provides generic data access patterns for all repositories.
"""
from typing import TypeVar, Generic, Type, Optional, List, Dict, Any
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db
from app.utils.exceptions import DatabaseError, NotFoundError

T = TypeVar('T')


class PaginatedResult(Generic[T]):
    """Container for paginated query results."""
    
    def __init__(self, items: List[T], total: int, page: int, per_page: int):
        self.items = items
        self.total = total
        self.page = page
        self.per_page = per_page
        self.pages = (total + per_page - 1) // per_page if per_page > 0 else 0
        self.has_prev = page > 1
        self.has_next = page < self.pages
        self.prev_num = page - 1 if self.has_prev else None
        self.next_num = page + 1 if self.has_next else None
    
    def iter_pages(self, left_edge=2, left_current=2, right_current=3, right_edge=2):
        """
        Iterate over page numbers for pagination.
        Similar to Flask-SQLAlchemy's Pagination.iter_pages()
        
        Args:
            left_edge: Number of pages at the left edge
            left_current: Number of pages left of current page
            right_current: Number of pages right of current page
            right_edge: Number of pages at the right edge
            
        Yields:
            Page numbers or None for gaps
        """
        last = 0
        for num in range(1, self.pages + 1):
            if (num <= left_edge or
                (num > self.page - left_current - 1 and num < self.page + right_current) or
                num > self.pages - right_edge):
                if last + 1 != num:
                    yield None
                yield num
                last = num
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'items': [item.to_dict() if hasattr(item, 'to_dict') else item for item in self.items],
            'total': self.total,
            'page': self.page,
            'per_page': self.per_page,
            'pages': self.pages,
            'has_prev': self.has_prev,
            'has_next': self.has_next
        }


class BaseRepository(Generic[T]):
    """Base repository with common CRUD operations."""
    
    def __init__(self, model: Type[T]):
        """
        Initialize repository with model class.
        
        Args:
            model: SQLAlchemy model class
        """
        self.model = model
    
    def get_by_id(self, id: int) -> Optional[T]:
        """
        Get entity by ID.
        
        Args:
            id: Entity ID
            
        Returns:
            Entity instance or None if not found
        """
        try:
            return db.session.get(self.model, id)
        except SQLAlchemyError as e:
            raise DatabaseError(f"Error retrieving {self.model.__name__}", e)
    
    def get_all(self, page: int = 1, per_page: int = 20) -> PaginatedResult[T]:
        """
        Get all entities with pagination.
        
        Args:
            page: Page number (1-indexed)
            per_page: Items per page
            
        Returns:
            Paginated result
        """
        try:
            query = db.session.query(self.model)
            total = query.count()
            items = query.offset((page - 1) * per_page).limit(per_page).all()
            return PaginatedResult(items, total, page, per_page)
        except SQLAlchemyError as e:
            raise DatabaseError(f"Error retrieving {self.model.__name__} list", e)
    
    def create(self, entity: T) -> T:
        """
        Create new entity.
        
        Args:
            entity: Entity instance to create
            
        Returns:
            Created entity
        """
        try:
            db.session.add(entity)
            db.session.commit()
            return entity
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Error creating {self.model.__name__}", e)
    
    def update(self, entity: T) -> T:
        """
        Update existing entity.
        
        Args:
            entity: Entity instance to update
            
        Returns:
            Updated entity
        """
        try:
            db.session.commit()
            return entity
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Error updating {self.model.__name__}", e)
    
    def delete(self, entity: T) -> bool:
        """
        Delete entity.
        
        Args:
            entity: Entity instance to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            db.session.delete(entity)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Error deleting {self.model.__name__}", e)
    
    def filter_by(self, **kwargs) -> List[T]:
        """
        Filter entities by criteria.
        
        Args:
            **kwargs: Filter criteria
            
        Returns:
            List of matching entities
        """
        try:
            return db.session.query(self.model).filter_by(**kwargs).all()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Error filtering {self.model.__name__}", e)
    
    def exists(self, id: int) -> bool:
        """
        Check if entity exists.
        
        Args:
            id: Entity ID
            
        Returns:
            True if exists, False otherwise
        """
        try:
            return db.session.query(
                db.session.query(self.model).filter_by(id=id).exists()
            ).scalar()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Error checking {self.model.__name__} existence", e)
    
    def count(self, **kwargs) -> int:
        """
        Count entities matching criteria.
        
        Args:
            **kwargs: Filter criteria
            
        Returns:
            Count of matching entities
        """
        try:
            query = db.session.query(self.model)
            if kwargs:
                query = query.filter_by(**kwargs)
            return query.count()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Error counting {self.model.__name__}", e)

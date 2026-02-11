"""
Audit log repository.
"""
from datetime import date
from typing import Dict, Any
from sqlalchemy.exc import SQLAlchemyError
from app.models.audit_log import AuditLog
from app.repositories.base_repository import BaseRepository, PaginatedResult
from app.extensions import db
from app.utils.exceptions import DatabaseError


class AuditRepository(BaseRepository[AuditLog]):
    """Audit log repository."""
    
    def __init__(self):
        super().__init__(AuditLog)
    
    def search_logs(self, filters: Dict[str, Any], 
                   page: int = 1, per_page: int = 50) -> PaginatedResult[AuditLog]:
        """Search audit logs with filters."""
        try:
            q = db.session.query(AuditLog)
            
            if 'user_id' in filters and filters['user_id']:
                q = q.filter(AuditLog.user_id == filters['user_id'])
            if 'action' in filters and filters['action']:
                q = q.filter(AuditLog.action == filters['action'])
            if 'entity_type' in filters and filters['entity_type']:
                q = q.filter(AuditLog.entity_type == filters['entity_type'])
            if 'start_date' in filters and filters['start_date']:
                q = q.filter(AuditLog.timestamp >= filters['start_date'])
            if 'end_date' in filters and filters['end_date']:
                q = q.filter(AuditLog.timestamp <= filters['end_date'])
            
            q = q.order_by(AuditLog.timestamp.desc())
            
            total = q.count()
            items = q.offset((page - 1) * per_page).limit(per_page).all()
            return PaginatedResult(items, total, page, per_page)
        except SQLAlchemyError as e:
            raise DatabaseError("Error searching audit logs", e)

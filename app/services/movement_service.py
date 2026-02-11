"""
Movement Service - Business logic for inventory movement management.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, date
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from app.models import Movement, Product
from app.repositories import MovementRepository, ProductRepository
from app.services.validation_service import ValidationService
from app.utils.exceptions import ValidationError, NotFoundError, DatabaseError, BusinessLogicError
from app.extensions import db


class MovementService:
    """Service for managing inventory movement business logic."""
    
    def __init__(self):
        """Initialize movement service with dependencies."""
        self.movement_repo = MovementRepository()
        self.product_repo = ProductRepository()
        self.validation_service = ValidationService()
    
    def create_movement(self, data: Dict[str, Any], user_id: int) -> Movement:
        """
        Create new movement with stock validation and update.
        
        Args:
            data: Movement data dictionary
            user_id: ID of user creating the movement
            
        Returns:
            Created movement instance
            
        Raises:
            ValidationError: If data validation fails
            NotFoundError: If product not found
            BusinessLogicError: If stock validation fails
            DatabaseError: If database operation fails
        """
        try:
            # Validate movement data
            validated_data = self.validation_service.validate_movement_data(data)
            
            # Get product
            product_id = validated_data['producto_id']
            product = self.product_repo.get_by_id(product_id)
            if not product or product.deleted_at is not None:
                raise NotFoundError("Product", product_id)
            
            # Validate stock for SALIDA movements
            tipo = validated_data['tipo'].upper()
            cantidad = validated_data['cantidad']
            
            if tipo == 'SALIDA':
                if product.stock < cantidad:
                    raise BusinessLogicError(
                        f"Stock insuficiente. Stock actual: {product.stock}, "
                        f"cantidad solicitada: {cantidad}"
                    )
            
            # Calculate new stock
            if tipo == 'ENTRADA':
                new_stock = product.stock + cantidad
            elif tipo == 'SALIDA':
                new_stock = product.stock - cantidad
            elif tipo == 'AJUSTE':
                # For AJUSTE, cantidad is the new stock value
                new_stock = cantidad
            else:
                raise ValidationError(f"Tipo de movimiento inválido: {tipo}", field='tipo')
            
            # Set audit fields
            validated_data['created_by'] = user_id
            validated_data['updated_by'] = user_id
            validated_data['created_at'] = datetime.utcnow()
            validated_data['updated_at'] = datetime.utcnow()
            
            # Set fecha if not provided
            if 'fecha' not in validated_data:
                validated_data['fecha'] = date.today()
            
            # Create movement
            movement = Movement(**validated_data)
            created_movement = self.movement_repo.create(movement)
            
            # Update product stock
            old_stock = product.stock
            product.stock = new_stock
            product.updated_by = user_id
            product.updated_at = datetime.utcnow()
            self.product_repo.update(product)
            
            current_app.logger.info(
                f"Movement created: {tipo} - Product {product.codigo} - "
                f"Cantidad: {cantidad} - Stock: {old_stock} -> {new_stock} by user {user_id}"
            )
            
            return created_movement
            
        except (ValidationError, NotFoundError, BusinessLogicError):
            raise
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error creating movement: {str(e)}")
            raise DatabaseError("Error al crear el movimiento", original_error=e)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Unexpected error creating movement: {str(e)}")
            raise BusinessLogicError(f"Error inesperado al crear el movimiento: {str(e)}")
    
    def get_movement(self, movement_id: int) -> Optional[Movement]:
        """
        Get movement by ID.
        
        Args:
            movement_id: ID of movement to retrieve
            
        Returns:
            Movement instance or None if not found
        """
        movement = self.movement_repo.get_by_id(movement_id)
        if movement and movement.deleted_at is None:
            return movement
        return None
    
    def get_movements_by_date(self, fecha: date, page: int = 1, per_page: int = 50):
        """
        Get movements for specific date with pagination.
        
        Args:
            fecha: Date to filter movements
            page: Page number
            per_page: Items per page
            
        Returns:
            PaginatedResult with movements
        """
        try:
            # Validate pagination
            page, per_page = self.validation_service.validate_pagination(page, per_page)
            
            # Get movements
            return self.movement_repo.get_by_date_range(
                start_date=fecha,
                end_date=fecha,
                page=page,
                per_page=per_page
            )
            
        except Exception as e:
            current_app.logger.error(f"Error getting movements by date: {str(e)}")
            raise BusinessLogicError(f"Error al obtener movimientos: {str(e)}")
    
    def get_movements_by_date_range(self, start_date: date, end_date: date,
                                    page: int = 1, per_page: int = 50):
        """
        Get movements for date range with pagination.
        
        Args:
            start_date: Start date
            end_date: End date
            page: Page number
            per_page: Items per page
            
        Returns:
            PaginatedResult with movements
        """
        try:
            # Validate date range
            self.validation_service.validate_date_range(start_date, end_date)
            
            # Validate pagination
            page, per_page = self.validation_service.validate_pagination(page, per_page)
            
            # Get movements
            return self.movement_repo.get_by_date_range(
                start_date=start_date,
                end_date=end_date,
                page=page,
                per_page=per_page
            )
            
        except Exception as e:
            current_app.logger.error(f"Error getting movements by date range: {str(e)}")
            raise BusinessLogicError(f"Error al obtener movimientos: {str(e)}")
    
    def get_movement_history(self, product_id: int, start_date: Optional[date] = None,
                            end_date: Optional[date] = None) -> List[Movement]:
        """
        Get movement history for a product.
        
        Args:
            product_id: ID of product
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            List of movements
        """
        try:
            # Verify product exists
            product = self.product_repo.get_by_id(product_id)
            if not product or product.deleted_at is not None:
                raise NotFoundError("Product", product_id)
            
            # Get movements
            movements = self.movement_repo.get_by_product(product_id)
            
            # Filter by date range if provided
            if start_date or end_date:
                if start_date and end_date:
                    self.validation_service.validate_date_range(start_date, end_date)
                
                filtered_movements = []
                for movement in movements:
                    if start_date and movement.fecha < start_date:
                        continue
                    if end_date and movement.fecha > end_date:
                        continue
                    filtered_movements.append(movement)
                
                return filtered_movements
            
            return movements
            
        except NotFoundError:
            raise
        except Exception as e:
            current_app.logger.error(f"Error getting movement history: {str(e)}")
            raise BusinessLogicError(f"Error al obtener historial de movimientos: {str(e)}")
    
    def get_today_movements(self, page: int = 1, per_page: int = 50):
        """
        Get today's movements with pagination.
        
        Args:
            page: Page number
            per_page: Items per page
            
        Returns:
            PaginatedResult with movements
        """
        return self.get_movements_by_date(date.today(), page, per_page)

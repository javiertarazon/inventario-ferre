"""
Sales Order Service - Business logic for sales order management.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, date
from decimal import Decimal
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from app.models import SalesOrder, SalesOrderItem, Product, Customer
from app.repositories import SalesOrderRepository, ProductRepository, CustomerRepository
from app.services.validation_service import ValidationService
from app.utils.exceptions import ValidationError, NotFoundError, DatabaseError, BusinessLogicError
from app.extensions import db


class SalesOrderService:
    """Service for managing sales order business logic."""
    
    def __init__(self):
        """Initialize sales order service with dependencies."""
        self.sales_order_repo = SalesOrderRepository()
        self.product_repo = ProductRepository(Product)
        self.customer_repo = CustomerRepository()
        self.validation_service = ValidationService()
    
    def create_sales_order(self, data: Dict[str, Any], user_id: int) -> SalesOrder:
        """
        Create new sales order with items.
        
        Args:
            data: Sales order data dictionary with items
            user_id: ID of user creating the order
            
        Returns:
            Created sales order instance
            
        Raises:
            ValidationError: If data validation fails
            DatabaseError: If database operation fails
        """
        try:
            # Validate customer
            customer_id = data.get('customer_id')
            if not customer_id:
                raise ValidationError("El cliente es requerido", field='customer_id')
            
            customer = self.customer_repo.get_by_id(customer_id)
            if not customer or customer.deleted_at is not None:
                raise ValidationError("El cliente no existe", field='customer_id')
            
            # Validate items
            items_data = data.get('items', [])
            if not items_data:
                raise ValidationError("La orden debe tener al menos un producto", field='items')
            
            # Generate order number
            order_number = self.sales_order_repo.generate_order_number()
            
            # Prepare order data
            order_data = {
                'order_number': order_number,
                'order_date': data.get('order_date', date.today()),
                'expected_delivery_date': data.get('expected_delivery_date'),
                'customer_id': customer_id,
                'status': data.get('status', 'draft'),
                'subtotal': Decimal('0.00'),
                'tax_amount': Decimal(str(data.get('tax_amount', 0))),
                'discount_amount': Decimal(str(data.get('discount_amount', 0))),
                'shipping_cost': Decimal(str(data.get('shipping_cost', 0))),
                'total_amount': Decimal('0.00'),
                'payment_status': 'pending',
                'paid_amount': Decimal('0.00'),
                'shipping_address': data.get('shipping_address', '').strip() or None,
                'shipping_method': data.get('shipping_method', '').strip() or None,
                'notes': data.get('notes', '').strip() or None,
                'internal_notes': data.get('internal_notes', '').strip() or None,
                'created_by': user_id,
                'updated_by': user_id,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            # Create order
            sales_order = SalesOrder(**order_data)
            
            # Add items
            for item_data in items_data:
                item = self._create_order_item(sales_order, item_data)
                sales_order.items.append(item)
            
            # Calculate totals
            sales_order.calculate_totals()
            
            # Save order
            created_order = self.sales_order_repo.create(sales_order)
            
            current_app.logger.info(
                f"Sales order created: {created_order.order_number} by user {user_id}"
            )
            
            return created_order
            
        except ValidationError:
            raise
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error creating sales order: {str(e)}")
            raise DatabaseError("Error al crear la orden de venta", original_error=e)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Unexpected error creating sales order: {str(e)}")
            raise BusinessLogicError(f"Error inesperado al crear la orden: {str(e)}")
    
    def _create_order_item(self, sales_order: SalesOrder, item_data: Dict[str, Any]) -> SalesOrderItem:
        """Create sales order item."""
        # Validate product
        product_id = item_data.get('product_id')
        if not product_id:
            raise ValidationError("El producto es requerido", field='product_id')
        
        product = self.product_repo.get_by_id(product_id)
        if not product or product.deleted_at is not None:
            raise ValidationError(f"El producto {product_id} no existe", field='product_id')
        
        # Validate quantity
        quantity = item_data.get('quantity', 0)
        if quantity <= 0:
            raise ValidationError("La cantidad debe ser mayor a 0", field='quantity')
        
        # Create item
        item = SalesOrderItem(
            product_id=product_id,
            quantity=quantity,
            unit_price=Decimal(str(item_data.get('unit_price', product.precio_dolares))),
            discount_percent=Decimal(str(item_data.get('discount_percent', 0))),
            tax_percent=Decimal(str(item_data.get('tax_percent', 0))),
            notes=item_data.get('notes', '').strip() or None
        )
        
        # Calculate total
        item.calculate_total()
        
        return item
    
    def update_sales_order(self, order_id: int, data: Dict[str, Any], user_id: int) -> SalesOrder:
        """Update existing sales order."""
        try:
            # Get existing order
            order = self.sales_order_repo.get_by_id(order_id)
            if not order or order.deleted_at is not None:
                raise NotFoundError("SalesOrder", order_id)
            
            # Check if order can be modified
            if order.status not in ['draft', 'confirmed']:
                raise BusinessLogicError(
                    f"No se puede modificar una orden en estado '{order.status}'"
                )
            
            # Update fields
            if 'expected_delivery_date' in data:
                order.expected_delivery_date = data['expected_delivery_date']
            if 'tax_amount' in data:
                order.tax_amount = Decimal(str(data['tax_amount']))
            if 'discount_amount' in data:
                order.discount_amount = Decimal(str(data['discount_amount']))
            if 'shipping_cost' in data:
                order.shipping_cost = Decimal(str(data['shipping_cost']))
            if 'shipping_address' in data:
                order.shipping_address = data['shipping_address'].strip() or None
            if 'shipping_method' in data:
                order.shipping_method = data['shipping_method'].strip() or None
            if 'notes' in data:
                order.notes = data['notes'].strip() or None
            if 'internal_notes' in data:
                order.internal_notes = data['internal_notes'].strip() or None
            
            # Recalculate totals
            order.calculate_totals()
            
            # Set audit fields
            order.updated_by = user_id
            order.updated_at = datetime.utcnow()
            
            # Save changes
            updated_order = self.sales_order_repo.update(order)
            
            current_app.logger.info(
                f"Sales order updated: {updated_order.order_number} by user {user_id}"
            )
            
            return updated_order
            
        except (NotFoundError, ValidationError, BusinessLogicError):
            raise
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error updating sales order: {str(e)}")
            raise DatabaseError("Error al actualizar la orden", original_error=e)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Unexpected error updating sales order: {str(e)}")
            raise BusinessLogicError(f"Error inesperado al actualizar la orden: {str(e)}")
    
    def confirm_order(self, order_id: int, user_id: int) -> SalesOrder:
        """
        Confirm order and reduce stock.
        
        Args:
            order_id: Order ID
            user_id: User ID
            
        Returns:
            Updated order
            
        Raises:
            BusinessLogicError: If stock is insufficient
        """
        try:
            order = self.sales_order_repo.get_by_id(order_id)
            if not order or order.deleted_at is not None:
                raise NotFoundError("SalesOrder", order_id)
            
            if not order.can_be_confirmed():
                raise BusinessLogicError("La orden no puede ser confirmada")
            
            # Check stock for all items
            for item in order.items:
                product = item.product
                if product.stock < item.quantity:
                    raise BusinessLogicError(
                        f"Stock insuficiente para {product.descripcion}. "
                        f"Stock actual: {product.stock}, requerido: {item.quantity}"
                    )
            
            # Reduce stock
            for item in order.items:
                product = item.product
                product.stock -= item.quantity
                product.updated_by = user_id
                product.updated_at = datetime.utcnow()
                self.product_repo.update(product)
            
            # Update order status
            order.status = 'confirmed'
            order.updated_by = user_id
            order.updated_at = datetime.utcnow()
            
            updated_order = self.sales_order_repo.update(order)
            
            current_app.logger.info(
                f"Sales order confirmed: {updated_order.order_number} by user {user_id}"
            )
            
            return updated_order
            
        except (NotFoundError, BusinessLogicError):
            raise
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error confirming order: {str(e)}")
            raise DatabaseError("Error al confirmar la orden", original_error=e)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Unexpected error confirming order: {str(e)}")
            raise BusinessLogicError(f"Error inesperado al confirmar la orden: {str(e)}")
    
    def cancel_order(self, order_id: int, user_id: int) -> SalesOrder:
        """Cancel order and restore stock if confirmed."""
        try:
            order = self.sales_order_repo.get_by_id(order_id)
            if not order or order.deleted_at is not None:
                raise NotFoundError("SalesOrder", order_id)
            
            if not order.can_be_cancelled():
                raise BusinessLogicError("La orden no puede ser cancelada")
            
            # Restore stock if order was confirmed
            if order.status == 'confirmed':
                for item in order.items:
                    product = item.product
                    product.stock += item.quantity
                    product.updated_by = user_id
                    product.updated_at = datetime.utcnow()
                    self.product_repo.update(product)
            
            # Update order status
            order.status = 'cancelled'
            order.updated_by = user_id
            order.updated_at = datetime.utcnow()
            
            updated_order = self.sales_order_repo.update(order)
            
            current_app.logger.info(
                f"Sales order cancelled: {updated_order.order_number} by user {user_id}"
            )
            
            return updated_order
            
        except (NotFoundError, BusinessLogicError):
            raise
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error cancelling order: {str(e)}")
            raise DatabaseError("Error al cancelar la orden", original_error=e)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Unexpected error cancelling order: {str(e)}")
            raise BusinessLogicError(f"Error inesperado al cancelar la orden: {str(e)}")
    
    def update_order_status(self, order_id: int, new_status: str, user_id: int) -> SalesOrder:
        """Update order status."""
        try:
            order = self.sales_order_repo.get_by_id(order_id)
            if not order or order.deleted_at is not None:
                raise NotFoundError("SalesOrder", order_id)
            
            valid_statuses = ['draft', 'confirmed', 'packed', 'shipped', 'delivered', 'cancelled']
            if new_status not in valid_statuses:
                raise ValidationError(f"Estado inválido: {new_status}", field='status')
            
            order.status = new_status
            order.updated_by = user_id
            order.updated_at = datetime.utcnow()
            
            updated_order = self.sales_order_repo.update(order)
            
            current_app.logger.info(
                f"Sales order status updated: {updated_order.order_number} -> {new_status} by user {user_id}"
            )
            
            return updated_order
            
        except (NotFoundError, ValidationError):
            raise
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error updating order status: {str(e)}")
            raise DatabaseError("Error al actualizar el estado", original_error=e)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Unexpected error updating order status: {str(e)}")
            raise BusinessLogicError(f"Error inesperado al actualizar el estado: {str(e)}")
    
    def get_sales_order(self, order_id: int) -> Optional[SalesOrder]:
        """Get sales order by ID."""
        order = self.sales_order_repo.get_by_id(order_id)
        if order and order.deleted_at is None:
            return order
        return None
    
    def list_orders(self, page: int = 1, per_page: int = 20):
        """List all orders with pagination."""
        try:
            page, per_page = self.validation_service.validate_pagination(page, per_page)
            return self.sales_order_repo.get_all(page=page, per_page=per_page)
        except Exception as e:
            current_app.logger.error(f"Error listing orders: {str(e)}")
            raise BusinessLogicError(f"Error al listar órdenes: {str(e)}")
    
    def get_orders_by_status(self, status: str, page: int = 1, per_page: int = 20):
        """Get orders by status."""
        try:
            page, per_page = self.validation_service.validate_pagination(page, per_page)
            return self.sales_order_repo.get_by_status(status=status, page=page, per_page=per_page)
        except Exception as e:
            current_app.logger.error(f"Error getting orders by status: {str(e)}")
            raise BusinessLogicError(f"Error al obtener órdenes: {str(e)}")

    def get_customer_orders(self, customer_id: int, page: int = 1, per_page: int = 20):
        """
        Get all orders for a specific customer.
        
        Args:
            customer_id: ID of the customer
            page: Page number for pagination
            per_page: Items per page
            
        Returns:
            Paginated list of orders
        """
        try:
            from app.models import SalesOrder
            return SalesOrder.query.filter_by(
                customer_id=customer_id,
                deleted_at=None
            ).order_by(SalesOrder.order_date.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error getting customer orders: {str(e)}")
            raise DatabaseError(f"Error al obtener órdenes del cliente: {str(e)}")
    
    def get_all_orders(self, page: int = 1, per_page: int = 20):
        """
        Get all sales orders with pagination.
        
        Args:
            page: Page number for pagination
            per_page: Items per page
            
        Returns:
            Paginated list of orders
        """
        try:
            return self.sales_order_repo.get_all(page=page, per_page=per_page)
        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error getting all orders: {str(e)}")
            raise DatabaseError(f"Error al obtener órdenes: {str(e)}")

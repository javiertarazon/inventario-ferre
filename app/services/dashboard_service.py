"""
Dashboard Service - Business logic for dashboard metrics and KPIs.
"""
from typing import Dict, Any
from datetime import datetime, date, timedelta
from flask import current_app
from sqlalchemy import func

from app.models import Product, SalesOrder, Customer, Movement
from app.extensions import db


class DashboardService:
    """Service for dashboard metrics and KPIs."""
    
    def __init__(self):
        """Initialize dashboard service."""
        pass
    
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """
        Get main dashboard metrics.
        
        Returns:
            Dictionary with dashboard metrics
        """
        try:
            metrics = {
                'inventory': self._get_inventory_metrics(),
                'sales': self._get_sales_metrics(),
                'customers': self._get_customer_metrics(),
                'alerts': self._get_alerts(),
                'recent_activity': self._get_recent_activity()
            }
            
            return metrics
            
        except Exception as e:
            current_app.logger.error(f"Error getting dashboard metrics: {str(e)}")
            # Return empty structure to avoid template errors
            return {
                'inventory': {
                    'total_products': 0,
                    'total_value': 0,
                    'low_stock_count': 0,
                    'out_of_stock': 0,
                    'categories': 0
                },
                'sales': {
                    'total_orders': 0,
                    'draft_orders': 0,
                    'confirmed_orders': 0,
                    'delivered_orders': 0,
                    'total_sales': 0,
                    'month_sales': 0,
                    'pending_payment': 0
                },
                'customers': {
                    'total_customers': 0,
                    'active_customers': 0,
                    'new_customers': 0
                },
                'alerts': {
                    'count': 0,
                    'list': []
                },
                'recent_activity': []
            }
    
    def _get_inventory_metrics(self) -> Dict[str, Any]:
        """Get inventory-related metrics."""
        try:
            # Total products
            total_products = Product.query.filter_by(deleted_at=None).count()
            
            # Total stock value
            products = Product.query.filter_by(deleted_at=None).all()
            total_value = sum(
                float(p.stock * p.precio_dolares) for p in products
            )
            
            # Low stock products
            low_stock_count = Product.query.filter(
                Product.deleted_at == None,
                Product.stock <= Product.reorder_point
            ).count()
            
            # Out of stock products
            out_of_stock = Product.query.filter_by(
                stock=0,
                deleted_at=None
            ).count()
            
            # Products by category
            from app.models import ItemGroup
            categories = ItemGroup.query.filter_by(deleted_at=None).count()
            
            return {
                'total_products': total_products,
                'total_value': round(total_value, 2),
                'low_stock_count': low_stock_count,
                'out_of_stock': out_of_stock,
                'categories': categories
            }
        except Exception as e:
            current_app.logger.error(f"Error getting inventory metrics: {str(e)}")
            return {
                'total_products': 0,
                'total_value': 0,
                'low_stock_count': 0,
                'out_of_stock': 0,
                'categories': 0
            }
    
    def _get_sales_metrics(self) -> Dict[str, Any]:
        """Get sales-related metrics."""
        # Total orders
        total_orders = SalesOrder.query.filter_by(deleted_at=None).count()
        
        # Orders by status
        draft_orders = SalesOrder.query.filter_by(
            status='draft',
            deleted_at=None
        ).count()
        
        confirmed_orders = SalesOrder.query.filter_by(
            status='confirmed',
            deleted_at=None
        ).count()
        
        delivered_orders = SalesOrder.query.filter_by(
            status='delivered',
            deleted_at=None
        ).count()
        
        # Total sales amount
        total_sales = db.session.query(
            func.sum(SalesOrder.total_amount)
        ).filter_by(deleted_at=None).scalar() or 0
        
        # This month sales
        today = date.today()
        first_day = date(today.year, today.month, 1)
        month_sales = db.session.query(
            func.sum(SalesOrder.total_amount)
        ).filter(
            SalesOrder.order_date >= first_day,
            SalesOrder.deleted_at == None
        ).scalar() or 0
        
        # Pending payment
        pending_payment = db.session.query(
            func.sum(SalesOrder.total_amount - SalesOrder.paid_amount)
        ).filter(
            SalesOrder.payment_status.in_(['pending', 'partial']),
            SalesOrder.deleted_at == None
        ).scalar() or 0
        
        return {
            'total_orders': total_orders,
            'draft_orders': draft_orders,
            'confirmed_orders': confirmed_orders,
            'delivered_orders': delivered_orders,
            'total_sales': float(total_sales),
            'month_sales': float(month_sales),
            'pending_payment': float(pending_payment)
        }
    
    def _get_customer_metrics(self) -> Dict[str, Any]:
        """Get customer-related metrics."""
        # Total customers
        total_customers = Customer.query.filter_by(deleted_at=None).count()
        
        # Active customers
        active_customers = Customer.query.filter_by(
            is_active=True,
            deleted_at=None
        ).count()
        
        # New customers this month
        today = date.today()
        first_day = datetime(today.year, today.month, 1)
        new_customers = Customer.query.filter(
            Customer.created_at >= first_day,
            Customer.deleted_at == None
        ).count()
        
        return {
            'total_customers': total_customers,
            'active_customers': active_customers,
            'new_customers': new_customers
        }
    
    def _get_alerts(self) -> Dict[str, Any]:
        """Get system alerts."""
        alerts = []
        
        # Low stock alerts
        low_stock_products = Product.query.filter(
            Product.deleted_at == None,
            Product.stock <= Product.reorder_point,
            Product.stock > 0
        ).limit(5).all()
        
        for product in low_stock_products:
            alerts.append({
                'type': 'warning',
                'icon': 'bi-exclamation-triangle',
                'title': 'Stock Bajo',
                'message': f'{product.descripcion} ({product.codigo}) - Stock: {product.stock}',
                'link': f'/products/{product.id}'
            })
        
        # Out of stock alerts
        out_of_stock = Product.query.filter_by(
            stock=0,
            deleted_at=None
        ).limit(3).all()
        
        for product in out_of_stock:
            alerts.append({
                'type': 'danger',
                'icon': 'bi-x-circle',
                'title': 'Sin Stock',
                'message': f'{product.descripcion} ({product.codigo}) - Agotado',
                'link': f'/products/{product.id}'
            })
        
        # Pending orders
        pending_orders = SalesOrder.query.filter_by(
            status='confirmed',
            deleted_at=None
        ).limit(3).all()
        
        for order in pending_orders:
            alerts.append({
                'type': 'info',
                'icon': 'bi-clock',
                'title': 'Orden Pendiente',
                'message': f'Orden {order.order_number} - {order.customer.name}',
                'link': f'/sales-orders/{order.id}'
            })
        
        return {
            'count': len(alerts),
            'list': alerts[:10]  # Limit to 10 alerts
        }
    
    def _get_recent_activity(self) -> list:
        """Get recent activity."""
        activities = []
        
        # Recent movements
        recent_movements = Movement.query.filter_by(
            deleted_at=None
        ).order_by(Movement.created_at.desc()).limit(5).all()
        
        for movement in recent_movements:
            activities.append({
                'type': 'movement',
                'icon': 'bi-arrow-left-right',
                'title': f'Movimiento: {movement.tipo}',
                'description': f'{movement.producto.descripcion} - Cantidad: {movement.cantidad}',
                'timestamp': movement.created_at.isoformat() if movement.created_at else None,
                'timestamp_obj': movement.created_at,  # For sorting
                'user': movement.creator.username if movement.creator else 'Sistema'
            })
        
        # Recent orders
        recent_orders = SalesOrder.query.filter_by(
            deleted_at=None
        ).order_by(SalesOrder.created_at.desc()).limit(5).all()
        
        for order in recent_orders:
            activities.append({
                'type': 'order',
                'icon': 'bi-cart',
                'title': f'Orden: {order.order_number}',
                'description': f'Cliente: {order.customer.name} - Total: ${order.total_amount}',
                'timestamp': order.created_at.isoformat() if order.created_at else None,
                'timestamp_obj': order.created_at,  # For sorting
                'user': order.creator.username if order.creator else 'Sistema'
            })
        
        # Sort by timestamp_obj
        activities.sort(key=lambda x: x['timestamp_obj'] if x['timestamp_obj'] else datetime.min, reverse=True)
        
        # Remove timestamp_obj before returning (not JSON serializable)
        for activity in activities:
            activity.pop('timestamp_obj', None)
        
        return activities[:10]  # Return last 10 activities
    
    def get_sales_chart_data(self, days: int = 30) -> Dict[str, Any]:
        """
        Get sales chart data for the last N days.
        
        Args:
            days: Number of days to include
            
        Returns:
            Chart data with labels and values
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Query sales by date
        sales_by_date = db.session.query(
            SalesOrder.order_date,
            func.sum(SalesOrder.total_amount).label('total')
        ).filter(
            SalesOrder.order_date >= start_date,
            SalesOrder.order_date <= end_date,
            SalesOrder.deleted_at == None
        ).group_by(SalesOrder.order_date).all()
        
        # Create date range
        date_range = [start_date + timedelta(days=x) for x in range(days + 1)]
        
        # Map sales to dates
        sales_map = {sale.order_date: float(sale.total) for sale in sales_by_date}
        
        labels = [d.strftime('%d/%m') for d in date_range]
        values = [sales_map.get(d, 0) for d in date_range]
        
        return {
            'labels': labels,
            'values': values
        }
    
    def get_top_products(self, limit: int = 10) -> list:
        """
        Get top selling products.
        
        Args:
            limit: Number of products to return
            
        Returns:
            List of top products with sales data
        """
        from app.models import SalesOrderItem
        
        top_products = db.session.query(
            Product.id,
            Product.codigo,
            Product.descripcion,
            func.sum(SalesOrderItem.quantity).label('total_quantity'),
            func.sum(SalesOrderItem.total_price).label('total_sales')
        ).join(
            SalesOrderItem, Product.id == SalesOrderItem.product_id
        ).join(
            SalesOrder, SalesOrderItem.sales_order_id == SalesOrder.id
        ).filter(
            Product.deleted_at == None,
            SalesOrder.deleted_at == None
        ).group_by(
            Product.id
        ).order_by(
            func.sum(SalesOrderItem.quantity).desc()
        ).limit(limit).all()
        
        return [
            {
                'id': p.id,
                'codigo': p.codigo,
                'descripcion': p.descripcion,
                'quantity': int(p.total_quantity),
                'sales': float(p.total_sales)
            }
            for p in top_products
        ]

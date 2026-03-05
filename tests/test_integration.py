"""
Integration tests for key workflows - FASE 3 Testing
"""

import pytest
from decimal import Decimal
from datetime import date
from app.utils.exceptions import ValidationError, BusinessLogicError, NotFoundError


class TestProductCreationWorkflow:
    """Test complete product creation workflow."""
    
    def test_create_product_full_workflow(self, app, product_service, test_user, test_supplier, test_item_group):
        """Test creating product from scratch to retrieval."""
        
        user_id, _ = test_user
        supplier_id, _ = test_supplier
        group_id, _ = test_item_group
        
        with app.app_context():
            # Create product
            data = {
                'codigo': 'I-WF-01',
                'descripcion': 'Integration Test Product',
                'stock': 100,
                'precio_dolares': '50.00',
                'factor_ajuste': '1.10',
                'proveedor_id': supplier_id,
                'item_group_id': group_id,
                'reorder_point': 10
            }
            
            created = product_service.create_product(data, user_id)
            assert created is not None
            product_id = created.id
            
            # Retrieve
            retrieved = product_service.get_product(product_id)
            assert retrieved is not None
            assert retrieved.descripcion == 'Integration Test Product'
            
            # Update
            update_data = {'descripcion': 'Updated Description', 'stock': 150}
            updated = product_service.update_product(product_id, update_data, user_id)
            assert updated.stock == 150
            
            # Delete (soft)
            result = product_service.delete_product(product_id, user_id)
            assert result is True
            
            # Verify deleted
            final = product_service.get_product(product_id)
            assert final is None


class TestCustomerOrderWorkflow:
    """Test customer creation and order workflow."""
    
    def test_create_customer_full_workflow(self, app, customer_service, test_user):
        """Test complete customer lifecycle."""
        
        user_id, _ = test_user
        
        with app.app_context():
            # Create
            data = {
                'name': 'Integration Test Customer',
                'email': 'integration@test.com',
                'phone': '02612345678',
                'country': 'Venezuela',
                'credit_limit': '10000.00'
            }
            
            customer = customer_service.create_customer(data, user_id)
            assert customer is not None
            assert customer.name == 'Integration Test Customer'
            customer_id = customer.id
            
            # Retrieve
            retrieved = customer_service.get_customer(customer_id)
            assert retrieved is not None
            assert retrieved.email == 'integration@test.com'
            
            # Update
            update_data = {'name': 'Updated Customer Name', 'credit_limit': '20000.00'}
            updated = customer_service.update_customer(customer_id, update_data, user_id)
            assert updated.name == 'Updated Customer Name'
            assert updated.credit_limit == Decimal('20000.00')
            
            # Delete
            result = customer_service.delete_customer(customer_id, user_id)
            assert result is True
            
            # Verify deleted
            final = customer_service.get_customer(customer_id)
            assert final is None


class TestInventoryMovementWorkflow:
    """Test inventory movement scenarios."""
    
    def test_inventory_entrada(self, app, movement_service, product_service, test_product, test_user):
        """Test incoming inventory movement (ENTRADA)."""
        
        product_id, test_obj = test_product
        user_id, _ = test_user
        
        with app.app_context():
            initial_stock = test_obj.stock
            
            data = {
                'tipo': 'ENTRADA',
                'producto_id': product_id,
                'cantidad': 50,
                'descripcion': 'Stock replenishment',
                'fecha': date.today()
            }
            
            movement = movement_service.create_movement(data, user_id)
            assert movement is not None
            assert movement.tipo == 'ENTRADA'
            
            # Stock should increase
            product = product_service.get_product(product_id)
            assert product.stock == initial_stock + 50
    
    def test_inventory_salida_sufficient_stock(self, app, movement_service, product_service, test_product, test_user):
        """Test outgoing movement (SALIDA) with sufficient stock."""
        
        product_id, test_obj = test_product
        user_id, _ = test_user
        
        with app.app_context():
            initial_stock = test_obj.stock
            
            data = {
                'tipo': 'SALIDA',
                'producto_id': product_id,
                'cantidad': 25,  # Less than available (100)
                'descripcion': 'Sale',
                'fecha': date.today()
            }
            
            movement = movement_service.create_movement(data, user_id)
            assert movement is not None
            
            # Stock should decrease
            product = product_service.get_product(product_id)
            assert product.stock == initial_stock - 25
    
    def test_inventory_salida_insufficient_stock(self, app, movement_service, test_product, test_user):
        """Test outgoing movement (SALIDA) with insufficient stock."""
        
        product_id, _ = test_product
        user_id, _ = test_user
        
        with app.app_context():
            data = {
                'tipo': 'SALIDA',
                'producto_id': product_id,
                'cantidad': 200,  # More than available (100)
                'descripcion': 'Large sale attempt',
                'fecha': date.today()
            }
            
            # Should fail due to insufficient stock
            with pytest.raises(BusinessLogicError) as exc_info:
                movement_service.create_movement(data, user_id)
            
            assert 'stock' in str(exc_info.value).lower() or 'insuficiente' in str(exc_info.value).lower()


class TestDataValidationIntegration:
    """Test validation across services."""
    
    def test_product_validation_prevents_invalid_creation(self, app, product_service, test_user):
        """Test that validation prevents creating invalid products."""
        
        user_id, _ = test_user
        
        with app.app_context():
            invalid_products = [
                {'codigo': 'T-ST-01', 'descripcion': 'Test', 'stock': 'not_a_number'},  # Invalid stock
                {'codigo': 'T-PR-01', 'descripcion': 'Test', 'precio_dolares': 'not_a_decimal'},  # Invalid price
            ]
            
            for invalid_data in invalid_products:
                with pytest.raises((ValidationError, ValueError, TypeError)):
                    product_service.create_product(invalid_data, user_id)




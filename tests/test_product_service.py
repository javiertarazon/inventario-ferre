"""
Unit tests for ProductService - FASE 3 Testing
"""

import pytest
from decimal import Decimal
from datetime import date, datetime
from app.utils.exceptions import ValidationError, NotFoundError, DatabaseError


class TestProductServiceCreate:
    """Test product creation."""
    
    def test_create_product_success(self, app, product_service, test_user, test_supplier, test_item_group):
        """Test successful product creation."""
        user_id, _ = test_user
        supplier_id, _ = test_supplier
        group_id, _ = test_item_group
        
        data = {
            'codigo': 'B-CD-01',
            'descripcion': 'New Product',
            'stock': 50,
            'precio_dolares': '15.50',
            'factor_ajuste': '1.05',
            'proveedor_id': supplier_id,
            'item_group_id': group_id,
            'reorder_point': 5
        }
        
        with app.app_context():
            product = product_service.create_product(data, user_id)
            
            assert product is not None
            assert product.codigo == 'B-CD-01'
            assert product.descripcion == 'New Product'
            assert product.stock == 50
            assert product.created_by == user_id
            assert product.inventory_entry_date == date(2024, 8, 1)

    def test_create_product_allows_custom_inventory_entry_date(self, app, product_service, test_user):
        """Test product creation with explicit inventory entry date."""
        user_id, _ = test_user

        data = {
            'codigo': 'B-CD-02',
            'descripcion': 'Product With Date',
            'stock': 10,
            'inventory_entry_date': '2025-01-15',
        }

        with app.app_context():
            product = product_service.create_product(data, user_id)
            assert product.inventory_entry_date == date(2025, 1, 15)
    
    def test_create_product_duplicate_codigo(self, app, product_service, test_user, test_product):
        """Test product creation with duplicate codigo fails."""
        user_id, _ = test_user
        product_id, existing_product = test_product
        
        data = {
            'codigo': existing_product.codigo,  # Duplicate
            'descripcion': 'Duplicate',
            'stock': 10
        }
        
        with app.app_context():
            with pytest.raises(ValidationError):
                product_service.create_product(data, user_id)
    
    def test_create_product_missing_descripcion(self, app, product_service, test_user):
        """Test product creation without descripcion fails."""
        user_id, _ = test_user
        
        data = {
            'codigo': 'C-TS-01',
            'stock': 10
            # Missing descripcion
        }
        
        with app.app_context():
            with pytest.raises((ValidationError, ValueError)):
                product_service.create_product(data, user_id)
    
    def test_create_product_negative_stock(self, app, product_service, test_user):
        """Test product creation with negative stock fails."""
        user_id, _ = test_user
        
        data = {
            'codigo': 'C-NG-01',
            'descripcion': 'Negative Stock',
            'stock': -10
        }
        
        with app.app_context():
            with pytest.raises(ValidationError):
                product_service.create_product(data, user_id)


class TestProductServiceRead:
    """Test product retrieval."""
    
    def test_get_product_by_id(self, app, product_service, test_product):
        """Test retrieving product by ID."""
        product_id, test_obj = test_product
        
        with app.app_context():
            product = product_service.get_product(product_id)
            
            assert product is not None
            assert product.id == product_id
            assert product.codigo == test_obj.codigo
    
    def test_get_product_not_found(self, app, product_service):
        """Test retrieving non-existent product returns None."""
        with app.app_context():
            product = product_service.get_product(9999)
            
            assert product is None
    
    def test_get_product_by_codigo(self, app, product_service, test_product):
        """Test retrieving product by codigo."""
        product_id, test_obj = test_product
        
        with app.app_context():
            product = product_service.get_product_by_codigo(test_obj.codigo)
            
            assert product is not None
            assert product.codigo == test_obj.codigo


class TestProductServiceUpdate:
    """Test product updates."""
    
    def test_update_product_success(self, app, product_service, test_user, test_product):
        """Test successful product update."""
        user_id, _ = test_user
        product_id, _ = test_product
        
        update_data = {
            'descripcion': 'Updated Description',
            'stock': 200,
            'precio_dolares': '25.00'
        }
        
        with app.app_context():
            updated = product_service.update_product(product_id, update_data, user_id)
            
            assert updated.descripcion == 'Updated Description'
            assert updated.stock == 200
            assert updated.precio_dolares == Decimal('25.00')
            assert updated.updated_by == user_id
    
    def test_update_product_not_found(self, app, product_service, test_user):
        """Test updating non-existent product fails."""
        user_id, _ = test_user
        
        update_data = {'descripcion': 'Test'}
        
        with app.app_context():
            with pytest.raises(NotFoundError):
                product_service.update_product(9999, update_data, user_id)


class TestProductServiceDelete:
    """Test product deletion."""
    
    def test_delete_product_success(self, app, product_service, test_user, test_product):
        """Test successful soft delete of product."""
        user_id, _ = test_user
        product_id, _ = test_product
        
        with app.app_context():
            result = product_service.delete_product(product_id, user_id)
            
            assert result is True
            
            # Verify soft delete (deleted_at set)
            deleted = product_service.get_product(product_id)
            assert deleted is None  # Should return None because it's soft-deleted
    
    def test_delete_product_not_found(self, app, product_service, test_user):
        """Test deleting non-existent product fails."""
        user_id, _ = test_user
        
        with app.app_context():
            with pytest.raises(NotFoundError):
                product_service.delete_product(9999, user_id)


class TestProductServiceSearch:
    """Test product search functionality."""
    
    def test_search_products_empty(self, app, product_service):
        """Test searching with empty query."""
        with app.app_context():
            result = product_service.search_products(query='', page=1, per_page=20)
            
            assert result is not None
    
    def test_get_low_stock_products(self, app, product_service, test_product, test_user):
        """Test getting low stock products."""
        product_id, _ = test_product
        user_id, _ = test_user
        
        with app.app_context():
            # Set stock lower than threshold
            product = product_service.get_product(product_id)
            if product:
                product.stock = 5
                product.updated_by = user_id
                from app.extensions import db
                db.session.commit()
        
        with app.app_context():
            result = product_service.get_low_stock_products(threshold=10)
            
            assert result is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

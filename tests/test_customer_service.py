"""
Unit tests for CustomerService - FASE 3 Testing
"""

import pytest
from decimal import Decimal
from app.utils.exceptions import ValidationError, NotFoundError


class TestCustomerServiceCreate:
    """Test customer creation."""
    
    def test_create_customer_success(self, app, customer_service, test_user):
        """Test successful customer creation."""
        user_id, _ = test_user
        
        data = {
            'name': 'New Customer',
            'email': 'newcustomer@test.com',
            'phone': '02612345678',
            'tax_id': 'J-87654321-0',
            'tax_id_type': 'J',
            'address': 'New Address',
            'city': 'New City',
            'country': 'Venezuela',
            'customer_type': 'business',
            'credit_limit': '5000.00'
        }
        
        with app.app_context():
            customer = customer_service.create_customer(data, user_id)
            
            assert customer is not None
            assert customer.name == 'New Customer'
            assert customer.email == 'newcustomer@test.com'
            assert customer.created_by == user_id
    
    def test_create_customer_missing_name(self, app, customer_service, test_user):
        """Test customer creation without name fails."""
        user_id, _ = test_user
        
        data = {
            'email': 'test@test.com'
            # Missing name
        }
        
        with app.app_context():
            with pytest.raises((ValidationError, ValueError)):
                customer_service.create_customer(data, user_id)
    
    def test_create_customer_invalid_email(self, app, customer_service, test_user):
        """Test customer creation with invalid email fails."""
        user_id, _ = test_user
        
        data = {
            'name': 'Test Customer',
            'email': 'invalid-email'  # Invalid format
        }
        
        with app.app_context():
            with pytest.raises(ValidationError):
                customer_service.create_customer(data, user_id)
    
    def test_create_customer_duplicate_email(self, app, customer_service, test_user, test_customer):
        """Test customer creation with duplicate email fails."""
        user_id, _ = test_user
        _, existing_customer = test_customer
        
        data = {
            'name': 'Another Customer',
            'email': existing_customer.email  # Duplicate
        }
        
        with app.app_context():
            with pytest.raises(ValidationError):
                customer_service.create_customer(data, user_id)


class TestCustomerServiceRead:
    """Test customer retrieval."""
    
    def test_get_customer_by_id(self, app, customer_service, test_customer):
        """Test retrieving customer by ID."""
        customer_id, test_obj = test_customer
        
        with app.app_context():
            customer = customer_service.get_customer(customer_id)
            
            assert customer is not None
            assert customer.id == customer_id
            assert customer.name == test_obj.name
    
    def test_get_customer_not_found(self, app, customer_service):
        """Test retrieving non-existent customer returns None."""
        with app.app_context():
            customer = customer_service.get_customer(9999)
            
            assert customer is None
    
    def test_list_customers(self, app, customer_service):
        """Test listing customers with pagination."""
        with app.app_context():
            result = customer_service.list_customers(page=1, per_page=20)
            
            assert result is not None


class TestCustomerServiceUpdate:
    """Test customer updates."""
    
    def test_update_customer_success(self, app, customer_service, test_user, test_customer):
        """Test successful customer update."""
        user_id, _ = test_user
        customer_id, _ = test_customer
        
        update_data = {
            'name': 'Updated Name',
            'phone': '02698765432',
            'credit_limit': '2000.00'
        }
        
        with app.app_context():
            updated = customer_service.update_customer(customer_id, update_data, user_id)
            
            assert updated.name == 'Updated Name'
            assert updated.phone == '02698765432'
            assert updated.credit_limit == Decimal('2000.00')
            assert updated.updated_by == user_id
    
    def test_update_customer_not_found(self, app, customer_service, test_user):
        """Test updating non-existent customer fails."""
        user_id, _ = test_user
        
        update_data = {'name': 'Test'}
        
        with app.app_context():
            with pytest.raises(NotFoundError):
                customer_service.update_customer(9999, update_data, user_id)


class TestCustomerServiceDelete:
    """Test customer deletion."""
    
    def test_delete_customer_success(self, app, customer_service, test_user, test_customer):
        """Test successful soft delete of customer."""
        user_id, _ = test_user
        customer_id, _ = test_customer
        
        with app.app_context():
            result = customer_service.delete_customer(customer_id, user_id)
            
            assert result is True
            
            # Verify soft delete
            deleted = customer_service.get_customer(customer_id)
            assert deleted is None


class TestCustomerServiceSearch:
    """Test customer search functionality."""
    
    def test_search_customers(self, app, customer_service):
        """Test customer search."""
        with app.app_context():
            result = customer_service.search_customers(query='test', page=1)
            
            assert result is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

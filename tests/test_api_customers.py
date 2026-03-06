"""
Tests for API v1 customer endpoints.
"""

import pytest
from flask_jwt_extended import create_access_token
from app.models.user import User
from app.models.customer import Customer


class TestCustomerAPI:
    """Test customer endpoints."""
    
    @pytest.fixture
    def auth_headers(self, client, app):
        """Create authorization headers with valid token."""
        with app.app_context():
            from app.extensions import db, bcrypt
            
            # Generate password hash
            password_hash = bcrypt.generate_password_hash('password123').decode('utf-8')
            
            user = User(
                email='apitest@example.com',
                username='apitestuser',
                password_hash=password_hash,
                is_active=True
            )
            db.session.add(user)
            db.session.commit()
            user_id = user.id
            
            # JWT identity must be a string
            token = create_access_token(identity=str(user_id))
        
        return {'Authorization': f'Bearer {token}'}
    
    def test_list_customers_requires_auth(self, client):
        """Test that list customers requires authentication."""
        response = client.get('/api/v1/customers')
        assert response.status_code == 401
    
    def test_list_customers_empty(self, client, auth_headers):
        """Test listing customers when none exist."""
        response = client.get('/api/v1/customers', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['items'] == []
        assert data['total'] == 0
        assert data['page'] == 1
    
    def test_list_customers_with_pagination(self, client, app, auth_headers):
        """Test listing customers with pagination."""
        # Create test customers
        with app.app_context():
            from app.extensions import db
            for i in range(25):
                customer = Customer(
                    nombre=f'Customer{i}',
                    apellido=f'Last{i}',
                    email=f'customer{i}@example.com',
                    telefono='555-1234',
                    is_active=True
                )
                db.session.add(customer)
            db.session.commit()
        
        # Test first page
        response = client.get('/api/v1/customers?page=1&per_page=10', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['items']) == 10
        assert data['total'] == 25
        assert data['page'] == 1
        assert data['pages'] == 3
        
        # Test second page
        response = client.get('/api/v1/customers?page=2&per_page=10', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['items']) == 10
        assert data['page'] == 2
    
    def test_get_customer(self, client, app, auth_headers):
        """Test getting a specific customer."""
        # Create test customer
        with app.app_context():
            from app.extensions import db
            customer = Customer(
                nombre='Test',
                apellido='Customer',
                email='test@example.com',
                telefono='555-1234',
                is_active=True
            )
            db.session.add(customer)
            db.session.commit()
            customer_id = customer.id
        
        response = client.get(f'/api/v1/customers/{customer_id}', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['nombre'] == 'Test'
        assert data['apellido'] == 'Customer'
        assert data['email'] == 'test@example.com'
    
    def test_get_customer_not_found(self, client, auth_headers):
        """Test getting non-existent customer."""
        response = client.get('/api/v1/customers/999', headers=auth_headers)
        assert response.status_code == 404
    
    def test_create_customer(self, client, auth_headers):
        """Test creating a new customer."""
        customer_data = {
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'email': 'juan@example.com',
            'telefono': '555-5678'
        }
        
        response = client.post(
            '/api/v1/customers',
            json=customer_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['nombre'] == 'Juan'
        assert data['apellido'] == 'Pérez'
        assert data['email'] == 'juan@example.com'
        assert 'id' in data
    
    def test_create_customer_missing_field(self, client, auth_headers):
        """Test creating customer with missing required field."""
        customer_data = {
            'nombre': 'Juan',
            'apellido': 'Pérez'
            # Missing email
        }
        
        response = client.post(
            '/api/v1/customers',
            json=customer_data,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data or 'errors' in data

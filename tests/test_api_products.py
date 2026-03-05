"""
Tests for API v1 product endpoints.
"""

import pytest
from flask_jwt_extended import create_access_token
from app.models.user import User
from app.models.product import Product


class TestProductAPI:
    """Test product endpoints."""
    
    @pytest.fixture
    def auth_headers(self, client, app):
        """Create authorization headers with valid token."""
        with app.app_context():
            user = User(
                email='apitest@example.com',
                username='apitestuser',
                is_active=True
            )
            from app.extensions import db
            db.session.add(user)
            db.session.commit()
            user_id = user.id
            
            token = create_access_token(identity=user_id)
        
        return {'Authorization': f'Bearer {token}'}
    
    def test_list_products_requires_auth(self, client):
        """Test that list products requires authentication."""
        response = client.get('/api/v1/products')
        assert response.status_code == 401
    
    def test_list_products_empty(self, client, auth_headers):
        """Test listing products when none exist."""
        response = client.get('/api/v1/products', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['items'] == []
        assert data['total'] == 0
        assert data['page'] == 1
    
    def test_list_products_with_pagination(self, client, app, auth_headers):
        """Test listing products with pagination."""
        # Create test products
        with app.app_context():
            from app.extensions import db
            for i in range(25):
                product = Product(
                    codigo=f'A-B{i:02d}-{i:02d}',
                    descripcion=f'Product {i}',
                    stock=10,
                    precio_dolares=100.00
                )
                db.session.add(product)
            db.session.commit()
        
        # List first page
        response = client.get('/api/v1/products?page=1&per_page=10', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['items']) == 10
        assert data['total'] == 25
        assert data['pages'] == 3
    
    def test_get_product(self, client, app, auth_headers):
        """Test getting a single product."""
        # Create test product
        with app.app_context():
            from app.extensions import db
            product = Product(
                codigo='A-BC-01',
                descripcion='Test Product',
                stock=10,
                precio_dolares=50.00
            )
            db.session.add(product)
            db.session.commit()
            product_id = product.id
        
        # Get product
        response = client.get(f'/api/v1/products/{product_id}', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['codigo'] == 'A-BC-01'
        assert data['descripcion'] == 'Test Product'
    
    def test_get_product_not_found(self, client, auth_headers):
        """Test getting non-existent product."""
        response = client.get('/api/v1/products/99999', headers=auth_headers)
        assert response.status_code == 404
    
    def test_create_product_invalid_code(self, client, auth_headers):
        """Test creating product with invalid code format."""
        response = client.post('/api/v1/products', 
            json={
                'codigo': 'INVALID',
                'descripcion': 'Test Product',
                'precio_dolares': '50.00'
            },
            headers=auth_headers)
        
        assert response.status_code == 400
        assert 'errors' in response.get_json()
    
    def test_create_product_missing_field(self, client, auth_headers):
        """Test creating product missing required field."""
        response = client.post('/api/v1/products',
            json={
                'codigo': 'A-BC-01',
                'precio_dolares': '50.00'
                # Missing descripcion
            },
            headers=auth_headers)
        
        assert response.status_code == 400

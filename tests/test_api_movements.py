"""
Tests for API v1 movement endpoints.
"""

import pytest
from datetime import date
from flask_jwt_extended import create_access_token
from app.models.user import User
from app.models.product import Product
from app.models.movement import Movimiento


class TestMovementAPI:
    """Test movement endpoints."""
    
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
    
    @pytest.fixture
    def test_product(self, app):
        """Create a test product for movements."""
        with app.app_context():
            from app.extensions import db
            product = Product(
                codigo='A-AB-01',
                descripcion='Test Product',
                stock=100,
                precio_dolares=10.00
            )
            db.session.add(product)
            db.session.commit()
            product_id = product.id
        return product_id
    
    def test_list_movements_requires_auth(self, client):
        """Test that list movements requires authentication."""
        response = client.get('/api/v1/movements')
        assert response.status_code == 401
    
    def test_list_movements_empty(self, client, auth_headers):
        """Test listing movements when none exist."""
        response = client.get('/api/v1/movements', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['items'] == []
        assert data['total'] == 0
        assert data['page'] == 1
    
    def test_list_movements_with_pagination(self, client, app, auth_headers, test_product):
        """Test listing movements with pagination."""
        # Create test movements
        with app.app_context():
            from app.extensions import db
            for i in range(25):
                movement = Movimiento(
                    producto_id=test_product,
                    tipo='ENTRADA' if i % 2 == 0 else 'SALIDA',
                    cantidad=i + 1,
                    fecha=date.today(),
                    descripcion=f'Movement {i}',
                    created_by=None
                )
                db.session.add(movement)
            db.session.commit()
        
        # Test first page
        response = client.get('/api/v1/movements?page=1&per_page=10', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['items']) == 10
        assert data['total'] == 25
        assert data['page'] == 1
        assert data['pages'] == 3
    
    def test_get_movement(self, client, app, auth_headers, test_product):
        """Test getting a specific movement."""
        # Create test movement
        with app.app_context():
            from app.extensions import db
            movement = Movimiento(
                producto_id=test_product,
                tipo='ENTRADA',
                cantidad=50,
                fecha=date.today(),
                descripcion='Test Movement',
                created_by=None
            )
            db.session.add(movement)
            db.session.commit()
            movement_id = movement.id
        
        response = client.get(f'/api/v1/movements/{movement_id}', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['tipo'] == 'ENTRADA'
        assert data['cantidad'] == 50
    
    def test_get_movement_not_found(self, client, auth_headers):
        """Test getting non-existent movement."""
        response = client.get('/api/v1/movements/999', headers=auth_headers)
        assert response.status_code == 404
    
    def test_create_movement_entrada(self, client, auth_headers, test_product):
        """Test creating an ENTRADA movement."""
        movement_data = {
            'producto_id': test_product,
            'tipo': 'ENTRADA',
            'cantidad': 50,
            'fecha': date.today().isoformat(),
            'descripcion': 'Entrada de stock'
        }
        
        response = client.post(
            '/api/v1/movements',
            json=movement_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['tipo'] == 'ENTRADA'
        assert data['cantidad'] == 50
        assert data['producto_id'] == test_product
    
    def test_create_movement_missing_field(self, client, auth_headers, test_product):
        """Test creating movement with missing required field."""
        movement_data = {
            'producto_id': test_product,
            'tipo': 'ENTRADA',
            # Missing cantidad
            'fecha': date.today().isoformat()
        }
        
        response = client.post(
            '/api/v1/movements',
            json=movement_data,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data or 'errors' in data

"""
Tests for API v1 authentication endpoints.
"""

import pytest
from flask_jwt_extended import create_access_token
from app.models.user import User


class TestAuthAPI:
    """Test authentication endpoints."""
    
    def test_login_success(self, client, app):
        """Test successful login returns tokens."""
        # Create test user
        with app.app_context():
            user = User(
                email='test@example.com',
                username='testuser',
                password_hash='hashed_password',
                is_active=True
            )
            from app.extensions import db, bcrypt
            user.password_hash = bcrypt.generate_password_hash('password123').decode('utf-8')
            db.session.add(user)
            db.session.commit()
        
        # Test login
        response = client.post('/api/v1/auth/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert 'user' in data
        assert data['user']['email'] == 'test@example.com'
    
    def test_login_invalid_credentials(self, client, app):
        """Test login with invalid credentials."""
        response = client.post('/api/v1/auth/login', json={
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
        assert 'error' in response.get_json()
    
    def test_login_missing_email(self, client):
        """Test login without email."""
        response = client.post('/api/v1/auth/login', json={
            'password': 'password123'
        })
        
        assert response.status_code == 400
        assert 'errors' in response.get_json()
    
    def test_get_current_user(self, client, app):
        """Test getting current user info."""
        # Login first to get a valid token
        with app.app_context():
            from app.extensions import db, bcrypt
            user = User(
                email='current@example.com',
                username='currentuser',
                password_hash=bcrypt.generate_password_hash('password123').decode('utf-8'),
                is_active=True
            )
            db.session.add(user)
            db.session.commit()
        
        # Login to get token
        login_response = client.post('/api/v1/auth/login', json={
            'email': 'current@example.com',
            'password': 'password123'
        })
        
        assert login_response.status_code == 200
        token = login_response.get_json()['access_token']
        
        # Test getting current user
        headers = {'Authorization': f'Bearer {token}'}
        response = client.get('/api/v1/auth/me', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['email'] == 'current@example.com'
    
    def test_get_current_user_without_token(self, client):
        """Test getting current user without token."""
        response = client.get('/api/v1/auth/me')
        
        assert response.status_code == 401

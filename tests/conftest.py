import pytest
from app import app, db
from models import Usuario
from werkzeug.security import generate_password_hash
from flask_login import login_user

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False  # Deshabilitar CSRF para tests
    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()
            # Crear usuario de test
            if not Usuario.query.filter_by(username='testuser').first():
                user = Usuario(username='testuser', password='testpass')
                db.session.add(user)
                db.session.commit()
        yield client

@pytest.fixture
def app_context():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield

@pytest.fixture
def logged_in_client(client):
    with client.application.test_request_context():
        user = Usuario.query.filter_by(username='testuser').first()
        login_user(user)
    return client
import pytest
from flask_login import login_user
from models import Usuario
from werkzeug.security import generate_password_hash

def test_index_requires_login(client):
    response = client.get('/')
    assert response.status_code == 302  # Redirect to login

def test_login_success(client):
    response = client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    assert response.status_code == 302  # Redirect after login

def test_logout(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    response = client.get('/logout', follow_redirects=True)
    assert b'Iniciar Sesi' in response.data

def test_productos_get(client):
    response = client.get('/productos')
    assert response.status_code == 302  # Redirect to login

def test_productos_post_valid(client):
    response = client.post('/productos', data={
        'rubro': 'A',
        'iniciales': 'BC',
        'numero': '01',
        'descripcion': 'Producto Test',
        'stock': 10,
        'costo': 100.0,
        'factor_cambiario': 1.0
    })
    assert response.status_code == 302  # Redirect to login

def test_proveedores_post(client):
    response = client.post('/proveedores', data={
        'nombre': 'Proveedor Test',
        'rif': '123456789',
        'rubro_material': 'Material Test'
    })
    assert response.status_code == 302  # Redirect to login

def test_movimientos_post_entrada(client):
    response = client.post('/movimientos', data={
        'tipo': 'entrada',
        'producto_id': 1,
        'cantidad': 5
    })
    assert response.status_code == 302  # Redirect to login

def test_buscar(client):
    response = client.post('/buscar', data={'query': 'Test', 'criterio': 'descripcion'})
    assert response.status_code == 200  # No login required
import pytest
from models import db, Producto, Proveedor, Movimiento, CierreDia, Usuario
from werkzeug.security import generate_password_hash
from werkzeug.security import generate_password_hash

def test_usuario_creation(app_context):
    hashed_password = generate_password_hash('testpass', method='pbkdf2:sha256')
    user = Usuario(username='testuser2', password=hashed_password)
    db.session.add(user)
    db.session.commit()
    assert user.id is not None
    assert user.username == 'testuser2'

def test_producto_creation(app_context):
    producto = Producto(codigo='A-AB-01', descripcion='Producto Test', stock=10, precio_dolares=100.0, factor_ajuste=1.0)
    db.session.add(producto)
    db.session.commit()
    assert producto.id is not None
    assert producto.stock == 10

def test_proveedor_creation(app_context):
    proveedor = Proveedor(nombre='Proveedor Test', rif='123456789', rubro_material='Material Test')
    db.session.add(proveedor)
    db.session.commit()
    assert proveedor.id is not None
    assert proveedor.nombre == 'Proveedor Test'

def test_movimiento_creation(app_context):
    producto = Producto(codigo='A-AB-01', descripcion='Producto Test', stock=10, precio_dolares=100.0, factor_ajuste=1.0)
    db.session.add(producto)
    db.session.commit()
    from datetime import datetime
    movimiento = Movimiento(tipo='entrada', producto_id=producto.id, cantidad=5, fecha=datetime.now())
    db.session.add(movimiento)
    db.session.commit()
    assert movimiento.id is not None
    assert movimiento.tipo == 'entrada'

def test_cierre_dia_creation(app_context):
    from datetime import date, datetime
    cierre = CierreDia(fecha=date.today(), cerrado_en=datetime.now())
    db.session.add(cierre)
    db.session.commit()
    assert cierre.id is not None
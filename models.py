from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False, index=True)
    descripcion = db.Column(db.String(200), nullable=False, index=True)
    stock = db.Column(db.Integer, default=0)
    precio_dolares = db.Column(db.Float, default=0.0)
    factor_ajuste = db.Column(db.Float, default=1.0)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedor.id'), index=True)

    proveedor = db.relationship('Proveedor', backref='productos')

class Proveedor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, index=True)
    rif = db.Column(db.String(30), nullable=False, index=True)
    rubro_material = db.Column(db.String(100), nullable=False, index=True)

class Movimiento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(10), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False, index=True)
    cantidad = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DateTime, nullable=False, index=True)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedor.id'), index=True)
    cerrado = db.Column(db.Boolean, default=False, index=True)

    producto = db.relationship('Producto', backref='movimientos')
    proveedor = db.relationship('Proveedor', backref='movimientos')

class CierreDia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, unique=True, nullable=False, index=True)
    cerrado_en = db.Column(db.DateTime, nullable=False)

class Configuracion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tasa_cambiaria = db.Column(db.Float, default=1.0, nullable=False)  # USD a VES
    factor_ajuste = db.Column(db.Float, default=1.0, nullable=False)
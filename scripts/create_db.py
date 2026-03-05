from app import app, db
from models import Usuario
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()
    # Crear usuario por defecto si no existe
    if not Usuario.query.filter_by(username='admin').first():
        hashed_password = generate_password_hash('admin123', method='pbkdf2:sha256')
        admin = Usuario(username='admin', password=hashed_password)
        db.session.add(admin)
        db.session.commit()
        print("Usuario admin creado con contraseña 'admin123'")
    print("Base de datos creada")
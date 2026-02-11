"""
Script para ejecutar la aplicación Flask con el nuevo sistema
"""

import os
from app import create_app, db
from app.models import User

# Crear la aplicación
app = create_app('development')

# Crear las tablas y usuario admin si no existe
with app.app_context():
    db.create_all()
    
    # Verificar si existe el usuario admin
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@example.com',
            role='admin',
            is_active=True
        )
        admin.set_password('admin')
        db.session.add(admin)
        db.session.commit()
        print("✓ Usuario admin creado (username: admin, password: admin)")
    else:
        print("✓ Usuario admin ya existe")

if __name__ == '__main__':
    print("\n" + "="*60)
    print("SISTEMA DE INVENTARIO - MODO DESARROLLO")
    print("="*60)
    print("\nAccede a la aplicación en: http://127.0.0.1:5000")
    print("\nCredenciales:")
    print("  Usuario: admin")
    print("  Contraseña: admin")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

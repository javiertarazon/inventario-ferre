"""
Script to create admin user for production.
"""
import os
import sys
from getpass import getpass
from app import create_app, db
from app.models import User

def create_admin():
    """Create admin user interactively."""
    print("=" * 60)
    print("CREAR USUARIO ADMINISTRADOR")
    print("=" * 60)
    
    # Get environment
    env = os.environ.get('FLASK_ENV', 'production')
    app = create_app(env)
    
    with app.app_context():
        # Check if admin already exists
        existing_admin = User.query.filter_by(username='admin').first()
        if existing_admin:
            print("\n⚠️  Ya existe un usuario 'admin'")
            response = input("¿Desea reemplazarlo? (s/N): ").lower()
            if response != 's':
                print("Operación cancelada.")
                return
            db.session.delete(existing_admin)
            db.session.commit()
        
        # Get user input
        print("\nIngrese los datos del administrador:")
        username = input("Usuario [admin]: ").strip() or 'admin'
        email = input("Email [admin@ferreteria.local]: ").strip() or 'admin@ferreteria.local'
        
        # Get password with confirmation
        while True:
            password = getpass("Contraseña: ")
            if len(password) < 6:
                print("❌ La contraseña debe tener al menos 6 caracteres")
                continue
            
            password_confirm = getpass("Confirmar contraseña: ")
            if password != password_confirm:
                print("❌ Las contraseñas no coinciden")
                continue
            
            break
        
        # Create admin user
        admin = User(
            username=username,
            email=email,
            role='admin',
            is_active=True
        )
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        
        print("\n" + "=" * 60)
        print("✓ Usuario administrador creado exitosamente")
        print("=" * 60)
        print(f"Usuario: {username}")
        print(f"Email: {email}")
        print(f"Rol: admin")
        print("=" * 60)

if __name__ == '__main__':
    try:
        create_admin()
    except KeyboardInterrupt:
        print("\n\nOperación cancelada por el usuario.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)

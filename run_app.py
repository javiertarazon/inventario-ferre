"""
Script para ejecutar la aplicación Flask con el nuevo sistema
"""

import os
import logging
import secrets
from app import create_app, db
from app.models import User

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear la aplicación
app = create_app('development')

# Crear las tablas y usuario admin solo en el proceso principal (no en el reloader)
if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
    with app.app_context():
        db.create_all()
        
        # Verificar si existe el usuario admin
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Generar contraseña segura aleatoria
            temp_password = secrets.token_urlsafe(12)
            
            admin = User(
                username='admin',
                email=os.environ.get('ADMIN_EMAIL', 'admin@ferreteria.local'),
                role='admin',
                is_active=True
            )
            admin.set_password(temp_password)
            db.session.add(admin)
            db.session.commit()
            
            logger.info("=" * 70)
            logger.info("✅ Usuario admin creado exitosamente")
            logger.info("=" * 70)
            logger.info(f"Usuario: admin")
            logger.info(f"Contraseña temporal: {temp_password}")
            logger.info("⚠️  CAMBIA ESTA CONTRASEÑA EN EL PRIMER LOGIN")
            logger.info("=" * 70)
        else:
            logger.info("✅ Usuario admin ya existe")

if __name__ == '__main__':
    logger.info("\n" + "="*70)
    logger.info("SISTEMA DE INVENTARIO FERRETERÍA - MODO DESARROLLO")
    logger.info("="*70)
    logger.info("\n📱 Accede a la aplicación en: http://127.0.0.1:5000")
    logger.info("\n🔐 Credenciales:")
    logger.info("   Usuario: admin")
    logger.info("   Contraseña: revisa los logs arriba ️⬆️")
    logger.info("\n⚠️  NOTA DE SEGURIDAD:")
    logger.info("   - Cambia SECRET_KEY en .env antes de producción")
    logger.info("   - Cambia la contraseña admin en primer login")
    logger.info("   - Nunca guarde contraseñas en código")
    logger.info("\n" + "="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

# Sistema de Inventario Diario

Este sistema permite gestionar el inventario de una ferretería, registrando entradas y salidas de materiales, creando productos y proveedores, y exportando datos a Excel.

## Instalación

1. Asegúrate de tener Python instalado.
2. Instala las dependencias: `pip install flask sqlalchemy pandas openpyxl flask-wtf flask-login flask-migrate`
3. Configura variables de entorno (opcional): Crea un archivo `.env` con `SECRET_KEY=tu_clave_secreta` y `DATABASE_URL=sqlite:///inventario.db`
4. Ejecuta `python create_db.py` para crear la base de datos y usuario admin (usuario: admin, contraseña: admin123).
5. Ejecuta la aplicación: `python app.py`

## Uso

- Accede a http://localhost:5000/login
- Inicia sesión con admin/admin123
- Crea productos, proveedores, registra movimientos.
- Busca productos por código o descripción.
- Exporta el inventario a Excel.

## Funcionalidades

- Crear códigos de producto únicos.
- Buscar productos.
- Modificar stock mediante movimientos (entradas/salidas).
- Gestionar proveedores.
- Exportar a formato Excel.
- Autenticación de usuarios.
- Paginación en listas.
- Manejo de errores y logging.

## Desarrollo

- Usa Flask-Migrate para migraciones: `flask db init`, `flask db migrate`, `flask db upgrade`
- Tests: Ejecuta `python -m pytest tests/` para correr los tests unitarios.
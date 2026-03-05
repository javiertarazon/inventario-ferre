"""
ARCHIVO LEGACY - NO USAR EN PRODUCCION

Este archivo es un punto de entrada antiguo y ha sido reemplazado por el patron
de Application Factory en app/__init__.py.

Puntos de entrada correctos:
  - Desarrollo:   python run_app.py
  - Produccion:   gunicorn wsgi:app  (via gunicorn_config.py)

El codigo original de este archivo (rutas inline, modelos legacy, etc.) ha sido
migrado a los modulos correspondientes bajo app/:
  - Modelos:      app/models/
  - Rutas:        app/blueprints/
  - Logica:       app/services/
  - Config:       app/config.py
"""
import sys

if __name__ == '__main__':
    print(
        "Este archivo es legacy. Por favor usa:\n"
        "  python run_app.py        (desarrollo)\n"
        "  gunicorn wsgi:app        (produccion)\n"
    )
    sys.exit(1)

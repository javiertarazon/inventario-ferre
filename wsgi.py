"""
WSGI entry point for the inventory management application.
"""
import os
from app import create_app

# Create application instance
app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    app.run()

"""
Script to create database migration.
"""
from app import create_app
from flask_migrate import migrate as flask_migrate, upgrade
from app.extensions import db

app = create_app('development')

with app.app_context():
    # Generate migration
    flask_migrate(message='Add item groups, customers, sales orders, and reorder points')
    print("✓ Migration created successfully")
    
    # Apply migration
    upgrade()
    print("✓ Migration applied successfully")

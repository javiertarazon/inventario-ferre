"""
Create item groups (categories) from Excel data.
"""
from app import create_app
from app.models import ItemGroup
from app.extensions import db
from datetime import datetime

def create_categories():
    """Create categories based on Excel structure."""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("CREANDO CATEGORÍAS")
        print("=" * 60)
        
        # Define categories with their properties
        categories = [
            {
                'name': 'Electricidad',
                'code_prefix': 'E',
                'description': 'Productos eléctricos y de iluminación',
                'color': '#FFC107',  # Amarillo
                'icon': 'lightning-charge'
            },
            {
                'name': 'Plomeria',
                'code_prefix': 'P',
                'description': 'Productos de plomería y tuberías',
                'color': '#2196F3',  # Azul
                'icon': 'droplet'
            },
            {
                'name': 'Albañileria',
                'code_prefix': 'A',
                'description': 'Materiales de construcción y albañilería',
                'color': '#9E9E9E',  # Gris
                'icon': 'bricks'
            },
            {
                'name': 'Carpinteria',
                'code_prefix': 'C',
                'description': 'Herramientas y materiales de carpintería',
                'color': '#795548',  # Marrón
                'icon': 'hammer'
            },
            {
                'name': 'Herreria',
                'code_prefix': 'H',
                'description': 'Productos de herrería y metales',
                'color': '#607D8B',  # Gris azulado
                'icon': 'tools'
            },
            {
                'name': 'Tornilleria',
                'code_prefix': 'T',
                'description': 'Tornillos, tuercas y elementos de fijación',
                'color': '#FF5722',  # Naranja
                'icon': 'nut'
            },
            {
                'name': 'Miselaneos',
                'code_prefix': 'M',
                'description': 'Productos varios y misceláneos',
                'color': '#9C27B0',  # Púrpura
                'icon': 'box-seam'
            }
        ]
        
        created = 0
        updated = 0
        
        for cat_data in categories:
            # Check if category exists
            category = ItemGroup.query.filter_by(name=cat_data['name']).first()
            
            if category:
                # Update existing
                category.description = cat_data['description']
                category.color = cat_data['color']
                category.icon = cat_data['icon']
                category.updated_at = datetime.utcnow()
                category.updated_by = 1
                updated += 1
                print(f"✓ Actualizada: {cat_data['name']} (Prefijo: {cat_data['code_prefix']})")
            else:
                # Create new
                category = ItemGroup(
                    name=cat_data['name'],
                    description=cat_data['description'],
                    color=cat_data['color'],
                    icon=cat_data['icon'],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    created_by=1,
                    updated_by=1
                )
                db.session.add(category)
                created += 1
                print(f"✓ Creada: {cat_data['name']} (Prefijo: {cat_data['code_prefix']})")
        
        db.session.commit()
        
        print("\n" + "=" * 60)
        print(f"✓ Categorías creadas: {created}")
        print(f"✓ Categorías actualizadas: {updated}")
        print(f"✓ Total: {created + updated}")
        print("=" * 60)

if __name__ == '__main__':
    create_categories()

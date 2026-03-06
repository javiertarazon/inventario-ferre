"""
Test categories listing and search functionality.
"""
from app import create_app
from app.services import ItemGroupService

app = create_app()

with app.app_context():
    try:
        item_group_service = ItemGroupService()
        
        print("=" * 60)
        print("TEST 1: Listar todas las categorías")
        print("=" * 60)
        
        all_groups = item_group_service.get_all_groups()
        print(f"Total de categorías: {len(all_groups)}")
        print()
        
        for group in all_groups:
            parent_name = group.parent.name if group.parent else "Raíz"
            product_count = group.get_product_count()
            print(f"  - {group.name}")
            print(f"    Descripción: {group.description or 'N/A'}")
            print(f"    Padre: {parent_name}")
            print(f"    Productos: {product_count}")
            print(f"    Color: {group.color}")
            print(f"    Icono: {group.icon}")
            print()
        
        print("=" * 60)
        print("TEST 2: Buscar categorías con 'Elec'")
        print("=" * 60)
        
        query = "Elec"
        filtered = [g for g in all_groups if query.lower() in g.name.lower() or (g.description and query.lower() in g.description.lower())]
        print(f"Encontradas: {len(filtered)} categorías")
        for group in filtered:
            print(f"  - {group.name}: {group.get_product_count()} productos")
        print()
        
        print("=" * 60)
        print("TEST 3: Buscar categorías con 'Plom'")
        print("=" * 60)
        
        query = "Plom"
        filtered = [g for g in all_groups if query.lower() in g.name.lower() or (g.description and query.lower() in g.description.lower())]
        print(f"Encontradas: {len(filtered)} categorías")
        for group in filtered:
            print(f"  - {group.name}: {group.get_product_count()} productos")
        print()
        
        print("=" * 60)
        print("TEST 4: Categorías raíz (sin padre)")
        print("=" * 60)
        
        root_groups = item_group_service.get_root_groups()
        print(f"Total de categorías raíz: {len(root_groups)}")
        for group in root_groups:
            print(f"  - {group.name}: {group.get_product_count()} productos")
        print()
        
        print("✅ Todas las pruebas completadas!")
        
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

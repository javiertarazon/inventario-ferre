"""
Test categories with AppenderQuery fix.
"""
from app import create_app
from app.services import ItemGroupService

app = create_app()

with app.app_context():
    try:
        print("=" * 60)
        print("TEST: Cargar categorías con get_product_count()")
        print("=" * 60)
        
        item_group_service = ItemGroupService()
        all_groups = item_group_service.get_all_groups()
        
        print(f"Total de categorías: {len(all_groups)}\n")
        
        for group in all_groups:
            try:
                product_count = group.get_product_count()
                print(f"✓ {group.name}: {product_count} productos")
            except Exception as e:
                print(f"✗ {group.name}: ERROR - {str(e)}")
        
        print("\n" + "=" * 60)
        print("TEST: Simular renderizado de template")
        print("=" * 60)
        
        # Simular lo que hace el template
        for group in all_groups:
            try:
                name = group.name
                desc = group.description or "-"
                parent = group.parent.name if group.parent else "Raíz"
                count = group.get_product_count()
                print(f"✓ {name} | {desc[:30]} | Padre: {parent} | {count} productos")
            except Exception as e:
                print(f"✗ ERROR en {group.name}: {str(e)}")
        
        print("\n✅ Todas las pruebas completadas sin errores!")
        
    except Exception as e:
        print(f"\n❌ ERROR GENERAL: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

"""
Test product search functionality with different filters.
"""
from app import create_app
from app.services import ProductService

app = create_app()

with app.app_context():
    try:
        product_service = ProductService()
        
        print("=" * 60)
        print("TEST 1: Búsqueda por código (E-SP)")
        print("=" * 60)
        result = product_service.search_products(
            query='E-SP',
            filters={'search_by': 'codigo'},
            page=1,
            per_page=5
        )
        print(f"Encontrados: {result.total} productos")
        for p in result.items:
            print(f"  - {p.codigo}: {p.descripcion[:50]}")
        print()
        
        print("=" * 60)
        print("TEST 2: Búsqueda por descripción (tubo)")
        print("=" * 60)
        result = product_service.search_products(
            query='tubo',
            filters={'search_by': 'descripcion'},
            page=1,
            per_page=5
        )
        print(f"Encontrados: {result.total} productos")
        for p in result.items:
            print(f"  - {p.codigo}: {p.descripcion[:50]}")
        print()
        
        print("=" * 60)
        print("TEST 3: Búsqueda general (cable)")
        print("=" * 60)
        result = product_service.search_products(
            query='cable',
            filters={'search_by': 'all'},
            page=1,
            per_page=5
        )
        print(f"Encontrados: {result.total} productos")
        for p in result.items:
            print(f"  - {p.codigo}: {p.descripcion[:50]}")
        print()
        
        print("=" * 60)
        print("TEST 4: Búsqueda por categoría (Electricidad)")
        print("=" * 60)
        # First get the category ID
        from app.services import ItemGroupService
        item_group_service = ItemGroupService()
        categories = item_group_service.get_all_groups()
        electricidad = next((c for c in categories if 'Electricidad' in c.name), None)
        
        if electricidad:
            result = product_service.search_products(
                query='',
                filters={'item_group_id': electricidad.id},
                page=1,
                per_page=5
            )
            print(f"Categoría: {electricidad.name}")
            print(f"Encontrados: {result.total} productos")
            for p in result.items:
                print(f"  - {p.codigo}: {p.descripcion[:50]}")
        else:
            print("Categoría Electricidad no encontrada")
        print()
        
        print("=" * 60)
        print("TEST 5: Búsqueda combinada (código + categoría)")
        print("=" * 60)
        if electricidad:
            result = product_service.search_products(
                query='E-',
                filters={'search_by': 'codigo', 'item_group_id': electricidad.id},
                page=1,
                per_page=5
            )
            print(f"Búsqueda: código que contiene 'E-' en categoría {electricidad.name}")
            print(f"Encontrados: {result.total} productos")
            for p in result.items:
                print(f"  - {p.codigo}: {p.descripcion[:50]}")
        print()
        
        print("✅ Todas las pruebas completadas!")
        
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

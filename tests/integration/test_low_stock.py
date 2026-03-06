"""
Test low stock products functionality.
"""
from app import create_app
from app.services import ProductService

app = create_app()

with app.app_context():
    try:
        print("=" * 60)
        print("TEST: Productos con bajo stock")
        print("=" * 60)
        
        product_service = ProductService()
        
        # Test with threshold 10
        threshold = 10
        result = product_service.get_low_stock_products(threshold=threshold, page=1, per_page=20)
        
        print(f"\nUmbral: {threshold} unidades")
        print(f"Productos encontrados: {result.total}")
        print()
        
        if result.items:
            print("Productos con bajo stock:")
            for product in result.items[:10]:
                reorder = f" (Reorden: {product.reorder_point})" if product.reorder_point else ""
                print(f"  - {product.codigo}: {product.descripcion[:40]}")
                print(f"    Stock: {product.stock}{reorder}")
        else:
            print("✓ No hay productos con bajo stock")
        
        # Test with threshold 50
        print("\n" + "=" * 60)
        threshold = 50
        result = product_service.get_low_stock_products(threshold=threshold, page=1, per_page=20)
        
        print(f"\nUmbral: {threshold} unidades")
        print(f"Productos encontrados: {result.total}")
        
        print("\n✅ Test completado!")
        
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

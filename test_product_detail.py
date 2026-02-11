"""
Test product detail view.
"""
from app import create_app
from app.services import ProductService, MovementService

app = create_app()

with app.app_context():
    try:
        print("=" * 60)
        print("TEST: Cargar detalle de producto")
        print("=" * 60)
        
        product_service = ProductService()
        movement_service = MovementService()
        
        # Get first product
        product = product_service.get_product(1)
        
        if not product:
            print("❌ Producto no encontrado")
        else:
            print(f"✓ Producto encontrado: {product.codigo}")
            print(f"  Descripción: {product.descripcion}")
            print(f"  Stock: {product.stock}")
            print(f"  Precio: ${product.precio_dolares}")
            print(f"  Categoría: {product.item_group.name if product.item_group else 'Sin categoría'}")
            print(f"  Proveedor: {product.proveedor.nombre if product.proveedor else 'Sin proveedor'}")
            
            # Get movements
            movements = movement_service.get_movement_history(product.id)
            print(f"\n  Movimientos: {len(movements)}")
            
            if movements:
                print("\n  Últimos 5 movimientos:")
                for mov in movements[:5]:
                    print(f"    - {mov.fecha}: {mov.tipo} - {mov.cantidad} unidades")
        
        print("\n✅ Test completado!")
        
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

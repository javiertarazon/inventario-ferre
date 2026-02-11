"""
Complete test for movement creation with all types.
"""
from datetime import date
from app import create_app
from app.services import MovementService, ProductService
from app.extensions import db

app = create_app()

with app.app_context():
    try:
        movement_service = MovementService()
        product_service = ProductService()
        
        # Get a product
        product = product_service.get_product(1)
        print(f"Testing with product: {product.codigo} - {product.descripcion}")
        print(f"Initial stock: {product.stock}")
        print()
        
        # Test 1: ENTRADA
        print("Test 1: Creating ENTRADA movement...")
        data_entrada = {
            'tipo': 'ENTRADA',
            'producto_id': 1,
            'cantidad': 5,
            'descripcion': 'Entrada de prueba',
            'fecha': date.today()
        }
        movement1 = movement_service.create_movement(data_entrada, user_id=1)
        product = product_service.get_product(1)
        print(f"✓ ENTRADA created - ID: {movement1.id}, New stock: {product.stock}")
        print()
        
        # Test 2: SALIDA
        print("Test 2: Creating SALIDA movement...")
        data_salida = {
            'tipo': 'SALIDA',
            'producto_id': 1,
            'cantidad': 3,
            'descripcion': 'Salida de prueba',
            'fecha': date.today()
        }
        movement2 = movement_service.create_movement(data_salida, user_id=1)
        product = product_service.get_product(1)
        print(f"✓ SALIDA created - ID: {movement2.id}, New stock: {product.stock}")
        print()
        
        # Test 3: AJUSTE
        print("Test 3: Creating AJUSTE movement...")
        data_ajuste = {
            'tipo': 'AJUSTE',
            'producto_id': 1,
            'cantidad': 100,
            'descripcion': 'Ajuste de inventario',
            'fecha': date.today()
        }
        movement3 = movement_service.create_movement(data_ajuste, user_id=1)
        product = product_service.get_product(1)
        print(f"✓ AJUSTE created - ID: {movement3.id}, New stock: {product.stock}")
        print()
        
        # Test 4: Get today's movements
        print("Test 4: Getting today's movements...")
        result = movement_service.get_today_movements()
        print(f"✓ Found {result.total} movements today")
        for mov in result.items[:5]:
            print(f"  - {mov.tipo}: {mov.cantidad} units (Product ID: {mov.producto_id})")
        print()
        
        print("✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

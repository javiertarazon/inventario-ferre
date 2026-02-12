"""
Test script to verify item_group relationship is working.
"""
from app import create_app, db
from app.models import Product, ItemGroup

app = create_app()

with app.app_context():
    # Get a product with item_group_id
    product = Product.query.filter(Product.item_group_id.isnot(None)).first()
    
    if product:
        print(f"\nProducto: {product.codigo} - {product.descripcion}")
        print(f"item_group_id: {product.item_group_id}")
        
        # Try to access item_group relationship
        try:
            if product.item_group:
                print(f"Categoría: {product.item_group.name}")
                print(f"Color: {product.item_group.color}")
                print(f"Icon: {product.item_group.icon}")
                print("\n✓ La relación item_group funciona correctamente!")
            else:
                print("\n✗ item_group es None")
        except Exception as e:
            print(f"\n✗ Error al acceder a item_group: {e}")
    else:
        print("\n✗ No se encontró ningún producto con categoría asignada")
    
    # List all products with their categories
    print("\n" + "="*60)
    print("LISTADO DE PRODUCTOS CON CATEGORÍAS:")
    print("="*60)
    
    products = Product.query.filter(Product.deleted_at.is_(None)).limit(10).all()
    
    for p in products:
        category_name = p.item_group.name if p.item_group else "Sin categoría"
        print(f"{p.codigo:15} | {p.descripcion[:40]:40} | {category_name}")

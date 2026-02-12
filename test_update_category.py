"""
Test para verificar actualización de categoría en productos
"""
from app import create_app, db
from app.models import Product, ItemGroup
from app.services import ProductService

app = create_app()

with app.app_context():
    # Obtener un producto sin categoría
    product = Product.query.filter(Product.item_group_id.is_(None)).first()
    
    if not product:
        print("No hay productos sin categoría. Usando el primero disponible.")
        product = Product.query.first()
    
    print(f"\n{'='*60}")
    print(f"ANTES DE ACTUALIZAR")
    print(f"{'='*60}")
    print(f"Producto ID: {product.id}")
    print(f"Código: {product.codigo}")
    print(f"Descripción: {product.descripcion}")
    print(f"item_group_id: {product.item_group_id}")
    print(f"item_group: {product.item_group}")
    
    # Obtener una categoría
    category = ItemGroup.query.first()
    print(f"\nCategoría a asignar:")
    print(f"ID: {category.id}")
    print(f"Nombre: {category.name}")
    
    # Actualizar usando el servicio
    print(f"\n{'='*60}")
    print(f"ACTUALIZANDO PRODUCTO...")
    print(f"{'='*60}")
    
    product_service = ProductService()
    data = {
        'codigo': product.codigo,
        'descripcion': product.descripcion,
        'stock': product.stock,
        'precio_dolares': float(product.precio_dolares),
        'factor_ajuste': float(product.factor_ajuste),
        'item_group_id': category.id,  # Asignar categoría
        'proveedor_id': product.proveedor_id
    }
    
    try:
        updated_product = product_service.update_product(product.id, data, 1)
        
        print(f"\n{'='*60}")
        print(f"DESPUÉS DE ACTUALIZAR")
        print(f"{'='*60}")
        print(f"Producto ID: {updated_product.id}")
        print(f"Código: {updated_product.codigo}")
        print(f"item_group_id: {updated_product.item_group_id}")
        print(f"item_group: {updated_product.item_group}")
        
        if updated_product.item_group:
            print(f"Categoría nombre: {updated_product.item_group.name}")
            print(f"✅ CATEGORÍA ASIGNADA CORRECTAMENTE")
        else:
            print(f"❌ ERROR: Categoría NO asignada")
        
        # Verificar en base de datos
        db.session.commit()
        
        # Recargar desde BD
        print(f"\n{'='*60}")
        print(f"VERIFICANDO EN BASE DE DATOS")
        print(f"{'='*60}")
        
        product_from_db = Product.query.get(product.id)
        print(f"item_group_id en BD: {product_from_db.item_group_id}")
        print(f"item_group en BD: {product_from_db.item_group}")
        
        if product_from_db.item_group:
            print(f"Categoría en BD: {product_from_db.item_group.name}")
            print(f"✅ CATEGORÍA GUARDADA EN BD CORRECTAMENTE")
        else:
            print(f"❌ ERROR: Categoría NO guardada en BD")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

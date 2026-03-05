"""Verificar la reclasificación de productos."""
from app import create_app
from app.models import Product, ItemGroup

app = create_app()

with app.app_context():
    print("=" * 80)
    print("VERIFICACIÓN DE RECLASIFICACIÓN")
    print("=" * 80)
    
    # Obtener productos reclasificados
    productos = Product.query.filter_by(deleted_at=None).limit(30).all()
    
    print("\nEjemplos de productos reclasificados:\n")
    print(f"{'CÓDIGO':<15} | {'DESCRIPCIÓN':<50} | {'CATEGORÍA':<20}")
    print("-" * 90)
    
    for p in productos:
        categoria = p.item_group.name if p.item_group else "Sin categoría"
        desc = p.descripcion[:50] if len(p.descripcion) <= 50 else p.descripcion[:47] + "..."
        print(f"{p.codigo:<15} | {desc:<50} | {categoria:<20}")
    
    # Estadísticas por categoría
    print("\n" + "=" * 80)
    print("ESTADÍSTICAS POR CATEGORÍA")
    print("=" * 80)
    
    categorias = ItemGroup.query.filter_by(deleted_at=None).all()
    
    for cat in sorted(categorias, key=lambda x: x.name):
        count = Product.query.filter_by(
            item_group_id=cat.id,
            deleted_at=None
        ).count()
        print(f"{cat.name:<30}: {count:>4} productos")
    
    # Total
    total = Product.query.filter_by(deleted_at=None).count()
    con_categoria = Product.query.filter(
        Product.deleted_at == None,
        Product.item_group_id != None
    ).count()
    sin_categoria = total - con_categoria
    
    print("\n" + "=" * 80)
    print(f"Total de productos: {total}")
    print(f"Con categoría: {con_categoria}")
    print(f"Sin categoría: {sin_categoria}")
    print("=" * 80)

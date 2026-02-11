"""
Script para reclasificar productos con categorías y códigos únicos.
Formato: [LETRA_CATEGORIA]-[2_INICIALES]-[NUMERO]
"""
import pandas as pd
from app import create_app
from app.models import Product, ItemGroup
from app.extensions import db
from datetime import datetime
from collections import defaultdict

# Mapeo de categorías a letras
CATEGORY_LETTERS = {
    'Electricidad': 'E',
    'Plomeria': 'P',
    'Ferreteria': 'F',
    'Construccion': 'C',
    'Herramientas': 'H',
    'Pintura': 'T',
    'Jardineria': 'J',
    'Seguridad': 'S',
    'Limpieza': 'L',
    'Automotriz': 'A',
    'Hogar': 'O',
    'Iluminacion': 'I',
    'Cerrajeria': 'R',
    'Vidrieria': 'V',
    'Carpinteria': 'K',
    'Soldadura': 'W',
    'Adhesivos': 'D',
    'Varios': 'X'
}

def get_initials(descripcion):
    """Obtener las iniciales de las primeras dos palabras."""
    palabras = descripcion.strip().split()
    
    if len(palabras) == 0:
        return 'XX'
    elif len(palabras) == 1:
        # Si solo hay una palabra, tomar las primeras 2 letras
        return palabras[0][:2].upper()
    else:
        # Tomar primera letra de cada una de las primeras 2 palabras
        inicial1 = palabras[0][0].upper() if palabras[0] else 'X'
        inicial2 = palabras[1][0].upper() if palabras[1] else 'X'
        return inicial1 + inicial2

def get_or_create_category(nombre_categoria, app_context):
    """Obtener o crear categoría."""
    # Buscar categoría existente
    categoria = ItemGroup.query.filter_by(name=nombre_categoria, deleted_at=None).first()
    
    if not categoria:
        # Crear nueva categoría
        letra = CATEGORY_LETTERS.get(nombre_categoria, 'X')
        categoria = ItemGroup(
            name=nombre_categoria,
            description=f'Categoría de {nombre_categoria}',
            color='#0d6efd',
            icon='bi-box',
            created_by=1,
            updated_by=1,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(categoria)
        db.session.flush()  # Para obtener el ID
        print(f"  ✓ Categoría creada: {nombre_categoria} (Letra: {letra})")
    
    return categoria

def generate_unique_code(categoria_letra, iniciales, existing_codes):
    """Generar código único incremental."""
    prefix = f"{categoria_letra}-{iniciales}"
    
    # Encontrar el número más alto para este prefijo
    max_num = 0
    for code in existing_codes:
        if code.startswith(prefix + "-"):
            try:
                num = int(code.split('-')[2])
                if num > max_num:
                    max_num = num
            except (IndexError, ValueError):
                continue
    
    # Generar siguiente número
    next_num = max_num + 1
    new_code = f"{prefix}-{next_num:02d}"
    existing_codes.add(new_code)
    
    return new_code

def reclassify_products():
    """Reclasificar todos los productos."""
    print("=" * 70)
    print("RECLASIFICACIÓN DE PRODUCTOS")
    print("=" * 70)
    
    # Leer archivo Excel
    print("\n1. Leyendo archivo Excel...")
    df = pd.read_excel('Inventario Ferre-Exito.xlsx', skiprows=2)
    print(f"   Total de filas: {len(df)}")
    
    app = create_app()
    
    with app.app_context():
        # Obtener todos los códigos existentes
        existing_codes = set()
        all_products = Product.query.filter_by(deleted_at=None).all()
        for p in all_products:
            existing_codes.add(p.codigo)
        
        print(f"\n2. Productos existentes en BD: {len(all_products)}")
        
        # Agrupar por categoría
        print("\n3. Analizando categorías...")
        categorias_encontradas = df['Categoria'].dropna().unique()
        print(f"   Categorías encontradas: {len(categorias_encontradas)}")
        for cat in sorted(categorias_encontradas):
            letra = CATEGORY_LETTERS.get(cat, 'X')
            count = len(df[df['Categoria'] == cat])
            print(f"   - {cat} ({letra}): {count} productos")
        
        # Crear categorías
        print("\n4. Creando categorías...")
        categorias_map = {}
        for nombre_cat in categorias_encontradas:
            categoria = get_or_create_category(nombre_cat, app)
            categorias_map[nombre_cat] = categoria
        
        db.session.commit()
        print(f"   Total categorías: {len(categorias_map)}")
        
        # Reclasificar productos
        print("\n5. Reclasificando productos...")
        actualizados = 0
        sin_categoria = 0
        errores = []
        
        # Crear un diccionario de productos por código original
        productos_dict = {}
        for producto in all_products:
            # Intentar encontrar el código original en el Excel
            codigo_original = producto.codigo
            productos_dict[codigo_original] = producto
        
        # Procesar cada fila del Excel
        for idx, row in df.iterrows():
            try:
                codigo_original = str(row.get('Codigo', '')).strip()
                if not codigo_original or codigo_original == 'nan':
                    codigo_original = f"AUTO-{idx+1}"
                
                descripcion = str(row.get('Descripcion del Articulo', '')).strip()
                if not descripcion or descripcion == 'nan':
                    continue
                
                nombre_categoria = row.get('Categoria')
                if pd.isna(nombre_categoria):
                    sin_categoria += 1
                    continue
                
                # Buscar producto por código original o descripción
                producto = productos_dict.get(codigo_original)
                if not producto:
                    # Buscar por descripción
                    producto = Product.query.filter_by(
                        descripcion=descripcion,
                        deleted_at=None
                    ).first()
                
                if not producto:
                    continue
                
                # Obtener categoría
                categoria = categorias_map.get(nombre_categoria)
                if not categoria:
                    continue
                
                # Generar nuevo código
                letra_categoria = CATEGORY_LETTERS.get(nombre_categoria, 'X')
                iniciales = get_initials(descripcion)
                nuevo_codigo = generate_unique_code(letra_categoria, iniciales, existing_codes)
                
                # Actualizar producto
                producto.codigo = nuevo_codigo
                producto.item_group_id = categoria.id
                producto.updated_by = 1
                producto.updated_at = datetime.utcnow()
                
                actualizados += 1
                
                if actualizados % 100 == 0:
                    db.session.commit()
                    print(f"   Procesados: {actualizados} productos...")
                
            except Exception as e:
                errores.append(f"Fila {idx+1}: {str(e)}")
                continue
        
        # Commit final
        db.session.commit()
        
        print("\n" + "=" * 70)
        print("✓ RECLASIFICACIÓN COMPLETADA")
        print("=" * 70)
        print(f"  - Productos actualizados: {actualizados}")
        print(f"  - Sin categoría: {sin_categoria}")
        print(f"  - Errores: {len(errores)}")
        
        if errores and len(errores) <= 10:
            print("\nErrores encontrados:")
            for error in errores:
                print(f"  - {error}")
        
        # Mostrar ejemplos
        print("\n6. Ejemplos de productos reclasificados:")
        ejemplos = Product.query.filter(
            Product.deleted_at == None,
            Product.item_group_id != None
        ).limit(10).all()
        
        for p in ejemplos:
            categoria_nombre = p.item_group.name if p.item_group else "Sin categoría"
            print(f"   {p.codigo} - {p.descripcion[:50]} - [{categoria_nombre}]")
        
        # Estadísticas por categoría
        print("\n7. Estadísticas por categoría:")
        for nombre_cat, categoria in sorted(categorias_map.items()):
            count = Product.query.filter_by(
                item_group_id=categoria.id,
                deleted_at=None
            ).count()
            letra = CATEGORY_LETTERS.get(nombre_cat, 'X')
            print(f"   {letra} - {nombre_cat}: {count} productos")

if __name__ == "__main__":
    try:
        reclassify_products()
    except Exception as e:
        print(f"\n✗ Error fatal: {e}")
        import traceback
        traceback.print_exc()

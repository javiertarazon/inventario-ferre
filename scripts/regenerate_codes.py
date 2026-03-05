"""
Regenerate product codes based on categories and descriptions from Excel.
"""
import pandas as pd
from app import create_app
from app.models import Product, ItemGroup
from app.extensions import db
from app.utils.code_generator import CodeGenerator
from datetime import datetime

def regenerate_codes():
    """Regenerate all product codes from Excel data."""
    print("=" * 60)
    print("REGENERANDO CÓDIGOS DE PRODUCTOS")
    print("=" * 60)
    
    # Read Excel file
    df = pd.read_excel('Inventario Ferre-Exito.xlsx', skiprows=2)
    print(f"\nTotal productos en Excel: {len(df)}")
    
    app = create_app()
    
    with app.app_context():
        # Get all categories
        categories = {cat.name: cat for cat in ItemGroup.query.all()}
        print(f"Categorías disponibles: {list(categories.keys())}")
        
        updated = 0
        created = 0
        errors = []
        
        # Track codes to avoid duplicates
        used_codes = set()
        
        for idx, row in df.iterrows():
            try:
                # Get data from Excel
                old_codigo = str(row.get('Codigo', '')).strip()
                categoria = str(row.get('Categoria', '')).strip()
                descripcion = str(row.get('Descripcion del Articulo', '')).strip()
                
                # Skip if no description
                if not descripcion or descripcion == 'nan':
                    continue
                
                # Skip if no category or invalid category
                if not categoria or categoria == 'nan' or categoria not in categories:
                    errors.append(f"Fila {idx+3}: Categoría inválida '{categoria}' para '{descripcion}'")
                    continue
                
                # Get category
                item_group = categories[categoria]
                
                # Generate new code
                new_codigo = CodeGenerator.generate_code(categoria, descripcion)
                
                # Handle duplicates
                original_code = new_codigo
                counter = 1
                while new_codigo in used_codes:
                    # Extract parts and increment sequence
                    parts = original_code.split('-')
                    if len(parts) >= 4:
                        base_sequence = int(parts[3])
                        new_sequence = base_sequence + counter
                        parts[3] = f"{new_sequence:02d}"
                        new_codigo = '-'.join(parts)
                        counter += 1
                    else:
                        break
                
                used_codes.add(new_codigo)
                
                # Get other data
                stock = row.get('Cantidad Unid/kg', 0)
                if pd.isna(stock):
                    stock = 0
                else:
                    stock = int(float(stock))
                
                precio = row.get('Precio Venta $', 0)
                if pd.isna(precio):
                    precio = 0
                else:
                    precio = float(precio)
                
                # Find existing product by old code or description
                product = None
                if old_codigo and old_codigo != 'nan':
                    product = Product.query.filter_by(codigo=old_codigo, deleted_at=None).first()
                
                if not product:
                    # Try to find by description
                    product = Product.query.filter_by(descripcion=descripcion, deleted_at=None).first()
                
                if product:
                    # Update existing product
                    product.codigo = new_codigo
                    product.descripcion = descripcion
                    product.item_group_id = item_group.id
                    product.stock = stock
                    product.precio_dolares = precio
                    product.updated_at = datetime.utcnow()
                    product.updated_by = 1
                    updated += 1
                    
                    if (updated + created) % 50 == 0:
                        print(f"  Procesados: {updated + created} productos...")
                else:
                    # Create new product
                    product = Product(
                        codigo=new_codigo,
                        descripcion=descripcion,
                        item_group_id=item_group.id,
                        stock=stock,
                        precio_dolares=precio,
                        factor_ajuste=1.0,
                        proveedor_id=3,  # Default supplier
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                        created_by=1,
                        updated_by=1
                    )
                    db.session.add(product)
                    created += 1
                    
                    if (updated + created) % 50 == 0:
                        print(f"  Procesados: {updated + created} productos...")
                
                # Commit every 100 products
                if (updated + created) % 100 == 0:
                    db.session.commit()
                
            except Exception as e:
                errors.append(f"Fila {idx+3}: {str(e)}")
                continue
        
        # Final commit
        db.session.commit()
        
        print("\n" + "=" * 60)
        print("✓ REGENERACIÓN COMPLETADA")
        print("=" * 60)
        print(f"  Productos actualizados: {updated}")
        print(f"  Productos creados: {created}")
        print(f"  Total procesados: {updated + created}")
        print(f"  Errores: {len(errors)}")
        
        if errors and len(errors) <= 20:
            print("\nErrores encontrados:")
            for error in errors:
                print(f"  - {error}")
        elif errors:
            print(f"\nSe encontraron {len(errors)} errores (mostrando primeros 20):")
            for error in errors[:20]:
                print(f"  - {error}")
        
        # Show some examples
        print("\n" + "=" * 60)
        print("EJEMPLOS DE CÓDIGOS GENERADOS:")
        print("=" * 60)
        
        for categoria in ['Electricidad', 'Plomeria', 'Albañileria']:
            products = Product.query.join(ItemGroup).filter(
                ItemGroup.name == categoria,
                Product.deleted_at == None
            ).limit(5).all()
            
            if products:
                print(f"\n{categoria}:")
                for p in products:
                    print(f"  {p.codigo} - {p.descripcion[:50]}")

if __name__ == '__main__':
    try:
        regenerate_codes()
    except Exception as e:
        print(f"\n✗ Error fatal: {e}")
        import traceback
        traceback.print_exc()

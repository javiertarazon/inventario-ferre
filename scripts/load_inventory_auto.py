"""
Script to automatically load inventory from Inventario Ferre-Exito.xlsx
"""
import pandas as pd
from app import create_app
from app.models import Product, Supplier
from app.extensions import db
from datetime import datetime

def load_inventory():
    """Load inventory from Excel file."""
    print("Cargando inventario desde Inventario Ferre-Exito.xlsx...")
    print("=" * 60)
    
    # Read Excel file
    df = pd.read_excel('Inventario Ferre-Exito.xlsx', skiprows=2)
    
    print(f"Total de productos en el archivo: {len(df)}")
    print(f"Columnas: {df.columns.tolist()}")
    
    app = create_app()
    
    with app.app_context():
        # Get or create default supplier
        supplier = Supplier.query.filter_by(nombre='Proveedor General').first()
        if not supplier:
            supplier = Supplier(
                nombre='Proveedor General',
                rif='J-00000000-0',
                telefono='',
                email='',
                direccion='',
                created_by=1,
                updated_by=1,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(supplier)
            db.session.commit()
            print(f"✓ Proveedor creado: {supplier.nombre}")
        
        created = 0
        updated = 0
        errors = []
        
        for idx, row in df.iterrows():
            try:
                # Extract data
                codigo = str(row.get('Codigo', '')).strip()
                if not codigo or codigo == 'nan':
                    codigo = f"AUTO-{idx+1}"
                
                descripcion = str(row.get('Descripcion del Articulo', '')).strip()
                if not descripcion or descripcion == 'nan':
                    descripcion = f"Producto {codigo}"
                
                # Get stock
                stock = row.get('Cantidad Unid/kg', 0)
                if pd.isna(stock):
                    stock = 0
                else:
                    stock = int(float(stock))
                
                # Get price
                precio = row.get('Precio Venta $', 0)
                if pd.isna(precio):
                    precio = 0
                else:
                    precio = float(precio)
                
                # Check if product exists
                product = Product.query.filter_by(codigo=codigo, deleted_at=None).first()
                
                if product:
                    # Update existing product
                    product.descripcion = descripcion
                    product.stock = stock
                    product.precio_dolares = precio
                    product.updated_by = 1
                    product.updated_at = datetime.utcnow()
                    updated += 1
                else:
                    # Create new product
                    product = Product(
                        codigo=codigo,
                        descripcion=descripcion,
                        stock=stock,
                        precio_dolares=precio,
                        factor_ajuste=1.0,
                        proveedor_id=supplier.id,
                        created_by=1,
                        updated_by=1,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    db.session.add(product)
                    created += 1
                
                # Commit every 100 products
                if (created + updated) % 100 == 0:
                    db.session.commit()
                    print(f"  Procesados: {created + updated} productos...")
                
            except Exception as e:
                errors.append(f"Fila {idx+1}: {str(e)}")
                continue
        
        # Final commit
        db.session.commit()
        
        print("\n" + "=" * 60)
        print("✓ Importación completada!")
        print(f"  - Productos creados: {created}")
        print(f"  - Productos actualizados: {updated}")
        print(f"  - Total procesados: {created + updated}")
        print(f"  - Errores: {len(errors)}")
        
        if errors and len(errors) <= 10:
            print("\nErrores encontrados:")
            for error in errors:
                print(f"  - {error}")
        elif errors:
            print(f"\nSe encontraron {len(errors)} errores (mostrando primeros 10):")
            for error in errors[:10]:
                print(f"  - {error}")

if __name__ == "__main__":
    try:
        load_inventory()
    except Exception as e:
        print(f"\n✗ Error fatal: {e}")
        import traceback
        traceback.print_exc()

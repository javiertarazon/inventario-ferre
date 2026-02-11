"""
Script to load inventory from Inventario Ferre-Exito.xlsx
"""
import pandas as pd
from app import create_app
from app.services import ImportService

def analyze_excel():
    """Analyze the Excel file structure."""
    print("Analizando archivo Excel...")
    print("=" * 60)
    
    # Try reading with different skiprows
    for skip in [0, 1, 2]:
        print(f"\nIntentando con skiprows={skip}:")
        try:
            df = pd.read_excel('Inventario Ferre-Exito.xlsx', skiprows=skip)
            print(f"Columnas: {df.columns.tolist()}")
            print(f"Primera fila:\n{df.iloc[0] if len(df) > 0 else 'Sin datos'}")
            print(f"Total filas: {len(df)}")
            
            if skip == 1:
                print("\nPrimeras 5 filas completas:")
                print(df.head())
        except Exception as e:
            print(f"Error: {e}")

def load_inventory():
    """Load inventory from Excel file."""
    print("\n" + "=" * 60)
    print("Cargando inventario...")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        import_service = ImportService()
        
        try:
            # Import from Excel file
            result = import_service.import_from_file(
                'Inventario Ferre-Exito.xlsx',
                user_id=1
            )
            
            print(f"\n✓ Importación exitosa!")
            print(f"  - Productos creados: {result['created']}")
            print(f"  - Productos actualizados: {result['updated']}")
            print(f"  - Errores: {len(result['errors'])}")
            
            if result['errors']:
                print("\nErrores encontrados:")
                for error in result['errors'][:10]:  # Show first 10 errors
                    print(f"  - {error}")
            
        except Exception as e:
            print(f"\n✗ Error al importar: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    # First analyze the file
    analyze_excel()
    
    # Ask user to confirm
    print("\n" + "=" * 60)
    response = input("¿Desea cargar estos datos en la base de datos? (s/n): ")
    
    if response.lower() == 's':
        load_inventory()
    else:
        print("Operación cancelada.")

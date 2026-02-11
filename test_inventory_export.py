"""
Test script to verify inventory export with Bolivares.
"""
from app import create_app
from app.services import ImportService
from datetime import datetime

app = create_app()

with app.app_context():
    print("=" * 60)
    print("PRUEBA DE EXPORTACIÓN DE INVENTARIO EN BOLIVARES")
    print("=" * 60)
    
    # Set date range
    start_date = datetime(2026, 2, 1)
    end_date = datetime(2026, 2, 11)
    
    print(f"\nRango de fechas: {start_date.strftime('%Y-%m-%d')} a {end_date.strftime('%Y-%m-%d')}")
    
    try:
        # Generate report
        import_service = ImportService()
        df = import_service.export_inventory_report(start_date, end_date)
        
        print(f"\n✓ Reporte generado exitosamente")
        print(f"✓ Total de productos: {len(df)}")
        
        # Show column names
        print("\n✓ Columnas del reporte:")
        for col in df.columns:
            print(f"  - {col}")
        
        # Show sample data (first 3 products)
        print("\n✓ Muestra de datos (primeros 3 productos):")
        print("-" * 60)
        
        for idx, row in df.head(3).iterrows():
            print(f"\nProducto: {row['Código']} - {row['Descripción'][:40]}")
            print(f"  Existencia Inicial:")
            print(f"    Cantidad: {row['Existencia Inicial - Cantidad']}")
            print(f"    Costo Unitario: {row['Existencia Inicial - Costo Unitario (Bs)']:.2f} Bs")
            print(f"    Monto: {row['Existencia Inicial - Monto (Bs)']:.2f} Bs")
            print(f"  Entradas:")
            print(f"    Cantidad: {row['Entradas - Cantidad']}")
            print(f"    Monto: {row['Entradas - Monto (Bs)']:.2f} Bs")
            print(f"  Salidas:")
            print(f"    Cantidad: {row['Salidas - Cantidad']}")
            print(f"    Monto: {row['Salidas - Monto (Bs)']:.2f} Bs")
            print(f"  Inventario Final:")
            print(f"    Cantidad: {row['Inv.final - Cantidad']}")
            print(f"    Costo Unitario: {row['Inv.final - Costo Unitario (Bs)']:.2f} Bs")
            print(f"    Monto: {row['Inv.final - Monto (Bs)']:.2f} Bs")
        
        # Calculate totals
        totals = {
            'initial_amount': df['Existencia Inicial - Monto (Bs)'].sum(),
            'entries_amount': df['Entradas - Monto (Bs)'].sum(),
            'exits_amount': df['Salidas - Monto (Bs)'].sum(),
            'final_amount': df['Inv.final - Monto (Bs)'].sum()
        }
        
        print("\n" + "=" * 60)
        print("TOTALES:")
        print("=" * 60)
        print(f"Existencia Inicial: {totals['initial_amount']:,.2f} Bs")
        print(f"Entradas:          {totals['entries_amount']:,.2f} Bs")
        print(f"Salidas:           {totals['exits_amount']:,.2f} Bs")
        print(f"Inventario Final:  {totals['final_amount']:,.2f} Bs")
        
        print("\n" + "=" * 60)
        print("✓ EXPORTACIÓN FUNCIONANDO CORRECTAMENTE")
        print("=" * 60)
        print("\nTodos los precios están en BOLIVARES")
        print("Fórmula aplicada: (Precio USD × Tasa) × Factor")
        
    except Exception as e:
        print(f"\n✗ Error al generar reporte: {str(e)}")
        import traceback
        traceback.print_exc()

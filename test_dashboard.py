"""
Test script to debug dashboard error.
"""
from app import create_app
from app.services import DashboardService

app = create_app()

with app.app_context():
    print("=" * 60)
    print("PRUEBA DEL DASHBOARD")
    print("=" * 60)
    
    try:
        dashboard_service = DashboardService()
        
        print("\n1. Obteniendo métricas...")
        metrics = dashboard_service.get_dashboard_metrics()
        
        print(f"✓ Métricas obtenidas")
        print(f"  - Tipo de metrics: {type(metrics)}")
        print(f"  - Keys: {metrics.keys() if isinstance(metrics, dict) else 'N/A'}")
        
        if 'alerts' in metrics:
            print(f"\n2. Verificando alerts...")
            alerts = metrics['alerts']
            print(f"  - Tipo de alerts: {type(alerts)}")
            print(f"  - Keys: {alerts.keys() if isinstance(alerts, dict) else 'N/A'}")
            
            if 'items' in alerts:
                items = alerts['items']
                print(f"  - Tipo de items: {type(items)}")
                print(f"  - Es iterable: {hasattr(items, '__iter__')}")
                print(f"  - Cantidad de items: {len(items) if hasattr(items, '__len__') else 'N/A'}")
                
                if items:
                    print(f"\n3. Iterando sobre items...")
                    for i, item in enumerate(items):
                        print(f"  Item {i}: {type(item)} - {item.get('title', 'N/A') if isinstance(item, dict) else item}")
        
        print(f"\n4. Verificando recent_activity...")
        if 'recent_activity' in metrics:
            activity = metrics['recent_activity']
            print(f"  - Tipo: {type(activity)}")
            print(f"  - Es iterable: {hasattr(activity, '__iter__')}")
            print(f"  - Cantidad: {len(activity) if hasattr(activity, '__len__') else 'N/A'}")
        
        print("\n5. Obteniendo datos de gráfico...")
        sales_chart = dashboard_service.get_sales_chart_data(days=30)
        print(f"✓ Datos de gráfico obtenidos")
        print(f"  - Tipo: {type(sales_chart)}")
        print(f"  - Keys: {sales_chart.keys() if isinstance(sales_chart, dict) else 'N/A'}")
        
        print("\n6. Obteniendo top productos...")
        top_products = dashboard_service.get_top_products(limit=5)
        print(f"✓ Top productos obtenidos")
        print(f"  - Tipo: {type(top_products)}")
        print(f"  - Cantidad: {len(top_products) if hasattr(top_products, '__len__') else 'N/A'}")
        
        print("\n" + "=" * 60)
        print("✓ TODAS LAS PRUEBAS PASARON")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

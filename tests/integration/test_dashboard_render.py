"""
Test script to simulate dashboard rendering.
"""
from app import create_app
from app.services import DashboardService
from flask import render_template_string

app = create_app()

with app.app_context():
    print("=" * 60)
    print("PRUEBA DE RENDERIZADO DEL DASHBOARD")
    print("=" * 60)
    
    try:
        dashboard_service = DashboardService()
        metrics = dashboard_service.get_dashboard_metrics()
        sales_chart = dashboard_service.get_sales_chart_data(days=30)
        top_products = dashboard_service.get_top_products(limit=5)
        
        print("\n✓ Datos obtenidos correctamente")
        print(f"  - metrics keys: {metrics.keys()}")
        print(f"  - sales_chart keys: {sales_chart.keys()}")
        print(f"  - top_products length: {len(top_products)}")
        
        # Test template iteration
        print("\n✓ Probando iteración de alerts...")
        template = """
        {% if metrics.alerts.list %}
            {% for alert in metrics.alerts.list %}
            Alert {{ loop.index }}: {{ alert.title }}
            {% endfor %}
        {% else %}
            No alerts
        {% endif %}
        """
        
        result = render_template_string(template, metrics=metrics)
        print(result)
        
        print("\n✓ Probando iteración de recent_activity...")
        template2 = """
        {% if metrics.recent_activity %}
            {% for activity in metrics.recent_activity %}
            Activity {{ loop.index }}: {{ activity.title }}
            {% endfor %}
        {% else %}
            No activity
        {% endif %}
        """
        
        result2 = render_template_string(template2, metrics=metrics)
        print(result2)
        
        print("\n✓ Probando iteración de top_products...")
        template3 = """
        {% if top_products %}
            {% for product in top_products %}
            Product {{ loop.index }}: {{ product.codigo }}
            {% endfor %}
        {% else %}
            No products
        {% endif %}
        """
        
        result3 = render_template_string(template3, top_products=top_products)
        print(result3)
        
        print("\n" + "=" * 60)
        print("✓ RENDERIZADO EXITOSO")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

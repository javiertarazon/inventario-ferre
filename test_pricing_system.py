"""
Test script to verify pricing system functionality.
"""
from app import create_app
from app.models import ExchangeRate, Product
from datetime import date
from decimal import Decimal

app = create_app()

with app.app_context():
    print("=" * 60)
    print("PRUEBA DEL SISTEMA DE PRECIOS")
    print("=" * 60)
    
    # 1. Check exchange rate
    current_rate = ExchangeRate.get_current_rate()
    if current_rate:
        print(f"\n✓ Tasa de cambio actual: {current_rate.rate} Bs/$ (Fecha: {current_rate.date})")
    else:
        print("\n✗ No hay tasa de cambio configurada")
    
    # 2. Get sample products
    products = Product.query.filter_by(deleted_at=None).limit(5).all()
    
    if products:
        print(f"\n✓ Productos encontrados: {len(products)}")
        print("\nEjemplos de cálculo de precios:")
        print("-" * 60)
        
        rate_value = float(current_rate.rate) if current_rate else 36.50
        
        for product in products:
            precio_usd = float(product.precio_dolares)
            factor = float(product.factor_ajuste)
            precio_bs = precio_usd * rate_value
            precio_final_bs = precio_bs * factor
            
            print(f"\nProducto: {product.codigo} - {product.descripcion[:40]}")
            print(f"  Precio USD: ${precio_usd:.2f}")
            print(f"  Tasa: {rate_value:.2f} Bs/$")
            print(f"  Precio Bs: {precio_bs:.2f} Bs")
            print(f"  Factor ajuste: {factor:.2f}")
            print(f"  Precio final: {precio_final_bs:.2f} Bs")
            print(f"  Fórmula: ${precio_usd:.2f} × {rate_value:.2f} × {factor:.2f} = {precio_final_bs:.2f} Bs")
    else:
        print("\n✗ No hay productos en la base de datos")
    
    # 3. Check pricing blueprint registration
    print("\n" + "=" * 60)
    print("RUTAS DEL SISTEMA DE PRECIOS:")
    print("=" * 60)
    
    pricing_routes = [rule for rule in app.url_map.iter_rules() if 'pricing' in rule.endpoint]
    
    if pricing_routes:
        print(f"\n✓ Blueprint 'pricing' registrado con {len(pricing_routes)} rutas:")
        for route in pricing_routes:
            print(f"  - {route.rule} [{', '.join(route.methods - {'HEAD', 'OPTIONS'})}]")
    else:
        print("\n✗ Blueprint 'pricing' no está registrado")
    
    print("\n" + "=" * 60)
    print("ACCESO AL SISTEMA:")
    print("=" * 60)
    print("\nURL: http://127.0.0.1:5000/pricing/")
    print("Usuario: admin")
    print("Contraseña: admin")
    print("\n" + "=" * 60)

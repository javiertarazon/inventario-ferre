"""
Test pricing system.
"""
from app import create_app
from app.models import ExchangeRate, Product
from decimal import Decimal

app = create_app()

with app.app_context():
    try:
        print("=" * 60)
        print("TEST: Sistema de Precios")
        print("=" * 60)
        
        # Get current rate
        current_rate = ExchangeRate.get_current_rate()
        print(f"\nTasa actual: {current_rate.rate} Bs/$")
        print(f"Fecha: {current_rate.date}")
        
        # Get a product
        product = Product.query.first()
        print(f"\nProducto de prueba: {product.codigo}")
        print(f"Precio USD: ${product.precio_dolares}")
        print(f"Factor ajuste: {product.factor_ajuste}")
        
        # Calculate prices
        rate = float(current_rate.rate)
        precio_bs = float(product.precio_dolares) * rate
        precio_final = precio_bs * float(product.factor_ajuste)
        
        print(f"\nCálculos:")
        print(f"  Precio en Bs: {precio_bs:.2f} Bs")
        print(f"  Precio final: {precio_final:.2f} Bs")
        print(f"  Fórmula: ({product.precio_dolares} × {rate}) × {product.factor_ajuste} = {precio_final:.2f}")
        
        print("\n✅ Sistema de precios funcionando!")
        
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

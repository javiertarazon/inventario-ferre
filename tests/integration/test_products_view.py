"""
Test script to verify products view with exchange rate calculations.
"""
import sys
from decimal import Decimal
from app import create_app
from app.extensions import db
from app.models import Product, ExchangeRate

def test_products_view():
    """Test that products view handles Decimal/float conversions correctly."""
    app = create_app()
    
    with app.app_context():
        # Get current exchange rate
        current_rate = ExchangeRate.get_current_rate()
        if not current_rate:
            print("❌ No exchange rate found in database")
            return False
        
        print(f"✓ Exchange rate found: {current_rate.rate} Bs/$ (type: {type(current_rate.rate)})")
        
        # Get a sample product
        product = Product.query.first()
        if not product:
            print("❌ No products found in database")
            return False
        
        print(f"✓ Sample product: {product.codigo} - {product.descripcion}")
        print(f"  - precio_dolares: ${product.precio_dolares} (type: {type(product.precio_dolares)})")
        print(f"  - factor_ajuste: {product.factor_ajuste} (type: {type(product.factor_ajuste)})")
        
        # Test calculations
        try:
            # Convert to float for calculations (as done in template)
            exchange_rate = float(current_rate.rate)
            precio_dolares = float(product.precio_dolares or 0)
            factor_ajuste = float(product.factor_ajuste or 1.0)
            
            precio_bs = precio_dolares * exchange_rate
            precio_final_bs = precio_bs * factor_ajuste
            
            print(f"\n✓ Calculations successful:")
            print(f"  - Precio USD: ${precio_dolares:.2f}")
            print(f"  - Tasa de cambio: {exchange_rate:.2f} Bs/$")
            print(f"  - Precio Bs: {precio_bs:.2f} Bs")
            print(f"  - Factor de ajuste: {factor_ajuste:.2f}")
            print(f"  - Precio Final Bs: {precio_final_bs:.2f} Bs")
            
            return True
            
        except Exception as e:
            print(f"❌ Error in calculations: {str(e)}")
            return False

if __name__ == '__main__':
    success = test_products_view()
    sys.exit(0 if success else 1)

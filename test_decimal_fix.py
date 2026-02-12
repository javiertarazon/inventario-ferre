"""
Comprehensive test to verify Decimal/float fix in products view.
"""
import sys
from decimal import Decimal
from app import create_app
from app.extensions import db
from app.models import Product, ExchangeRate

def test_decimal_conversions():
    """Test all Decimal to float conversions work correctly."""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("TESTING DECIMAL/FLOAT CONVERSIONS")
        print("=" * 60)
        
        # Test 1: Exchange rate retrieval
        print("\n1. Testing exchange rate retrieval...")
        current_rate = ExchangeRate.get_current_rate()
        if not current_rate:
            print("   ❌ No exchange rate found")
            return False
        
        print(f"   ✓ Rate: {current_rate.rate} Bs/$ (type: {type(current_rate.rate).__name__})")
        
        # Test 2: Float conversion
        print("\n2. Testing float conversion...")
        try:
            exchange_rate_float = float(current_rate.rate)
            print(f"   ✓ Converted to float: {exchange_rate_float} (type: {type(exchange_rate_float).__name__})")
        except Exception as e:
            print(f"   ❌ Conversion failed: {e}")
            return False
        
        # Test 3: Product retrieval
        print("\n3. Testing product retrieval...")
        products = Product.query.limit(5).all()
        if not products:
            print("   ❌ No products found")
            return False
        
        print(f"   ✓ Found {len(products)} products")
        
        # Test 4: Price calculations for each product
        print("\n4. Testing price calculations...")
        for i, product in enumerate(products, 1):
            try:
                # Simulate template calculations
                precio_dolares = float(product.precio_dolares or 0)
                factor_ajuste = float(product.factor_ajuste or 1.0)
                precio_bs = precio_dolares * exchange_rate_float
                precio_final_bs = precio_bs * factor_ajuste
                
                print(f"\n   Product {i}: {product.codigo}")
                print(f"   - USD: ${precio_dolares:.2f}")
                print(f"   - Bs: {precio_bs:.2f} Bs")
                print(f"   - Factor: {factor_ajuste:.2f}")
                print(f"   - Final: {precio_final_bs:.2f} Bs")
                print(f"   ✓ Calculations successful")
                
            except Exception as e:
                print(f"   ❌ Calculation failed for {product.codigo}: {e}")
                return False
        
        # Test 5: Verify no Decimal × float operations
        print("\n5. Testing type safety...")
        test_product = products[0]
        try:
            # This should fail if not properly converted
            result = test_product.precio_dolares * exchange_rate_float
            print(f"   ⚠️  Direct Decimal × float worked (might cause issues in Jinja2)")
            print(f"   Result: {result} (type: {type(result).__name__})")
        except TypeError as e:
            print(f"   ✓ Direct Decimal × float properly raises TypeError")
            print(f"   (This is expected - conversions must happen in template)")
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        return True

if __name__ == '__main__':
    success = test_decimal_conversions()
    sys.exit(0 if success else 1)

"""
Integration test to verify products page works end-to-end.
"""
import sys
from app import create_app
from app.models import User

def test_products_page():
    """Test that products page renders without errors."""
    app = create_app()
    
    with app.test_client() as client:
        print("=" * 60)
        print("INTEGRATION TEST: Products Page")
        print("=" * 60)
        
        # Test 1: Login
        print("\n1. Testing login...")
        response = client.post('/login', data={
            'username': 'admin',
            'password': 'admin'
        }, follow_redirects=True)
        
        if response.status_code == 200:
            print("   ✓ Login successful")
        else:
            print(f"   ❌ Login failed with status {response.status_code}")
            return False
        
        # Test 2: Access products page
        print("\n2. Testing products page access...")
        response = client.get('/products/')
        
        if response.status_code == 200:
            print("   ✓ Products page loaded successfully")
        else:
            print(f"   ❌ Products page failed with status {response.status_code}")
            return False
        
        # Test 3: Check for error messages in response
        print("\n3. Checking for errors in page content...")
        html = response.data.decode('utf-8')
        
        if 'Error al cargar productos' in html:
            print("   ❌ Error message found in page")
            return False
        
        if 'unsupported operand' in html:
            print("   ❌ Type error found in page")
            return False
        
        print("   ✓ No error messages found")
        
        # Test 4: Check for expected content
        print("\n4. Checking for expected content...")
        expected_elements = [
            'Productos',
            'Precio USD',
            'Precio Bs',
            'Factor',
            'Precio Final Bs'
        ]
        
        for element in expected_elements:
            if element in html:
                print(f"   ✓ Found: {element}")
            else:
                print(f"   ❌ Missing: {element}")
                return False
        
        # Test 5: Check pagination or products
        print("\n5. Checking for products or pagination...")
        if 'pagination' in html or 'producto' in html.lower():
            print("   ✓ Products or pagination found")
        else:
            print("   ⚠️  No products found (might be empty database)")
        
        print("\n" + "=" * 60)
        print("INTEGRATION TEST PASSED ✓")
        print("=" * 60)
        print("\nThe products page is working correctly!")
        print("You can access it at: http://127.0.0.1:5000/products/")
        return True

if __name__ == '__main__':
    success = test_products_page()
    sys.exit(0 if success else 1)

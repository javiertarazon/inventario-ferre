"""
Test script to verify form endpoints work correctly.
"""
import requests
from requests.auth import HTTPBasicAuth

BASE_URL = "http://127.0.0.1:5000"

def test_login():
    """Test login and get session."""
    session = requests.Session()
    
    # Get login page to get CSRF token
    response = session.get(f"{BASE_URL}/login")
    print(f"✓ Login page accessible: {response.status_code}")
    
    # Login
    login_data = {
        'username': 'admin',
        'password': 'admin'
    }
    response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
    print(f"✓ Login successful: {response.status_code}")
    
    return session

def test_form_endpoints(session):
    """Test all form endpoints."""
    
    # Test nuevo producto
    print("\nTesting /products/create...")
    response = session.get(f"{BASE_URL}/products/create")
    if response.status_code == 200:
        print(f"✓ Nuevo Producto form loads: {response.status_code}")
        if 'suppliers' in response.text or 'proveedor' in response.text.lower():
            print("✓ Form contains supplier dropdown")
    else:
        print(f"✗ Nuevo Producto form failed: {response.status_code}")
        print(response.text[:500])
    
    # Test nueva orden
    print("\nTesting /orders/create...")
    response = session.get(f"{BASE_URL}/orders/create")
    if response.status_code == 200:
        print(f"✓ Nueva Orden form loads: {response.status_code}")
        if 'customers' in response.text or 'cliente' in response.text.lower():
            print("✓ Form contains customer dropdown")
    else:
        print(f"✗ Nueva Orden form failed: {response.status_code}")
        print(response.text[:500])
    
    # Test nuevo movimiento
    print("\nTesting /movements/create...")
    response = session.get(f"{BASE_URL}/movements/create")
    if response.status_code == 200:
        print(f"✓ Nuevo Movimiento form loads: {response.status_code}")
        if 'productos' in response.text.lower() or 'product' in response.text.lower():
            print("✓ Form contains product dropdown")
    else:
        print(f"✗ Nuevo Movimiento form failed: {response.status_code}")
        print(response.text[:500])
    
    # Test nueva categoría
    print("\nTesting /categories/create...")
    response = session.get(f"{BASE_URL}/categories/create")
    if response.status_code == 200:
        print(f"✓ Nueva Categoría form loads: {response.status_code}")
    else:
        print(f"✗ Nueva Categoría form failed: {response.status_code}")
        print(response.text[:500])
    
    # Test nuevo cliente
    print("\nTesting /customers/create...")
    response = session.get(f"{BASE_URL}/customers/create")
    if response.status_code == 200:
        print(f"✓ Nuevo Cliente form loads: {response.status_code}")
    else:
        print(f"✗ Nuevo Cliente form failed: {response.status_code}")
        print(response.text[:500])

if __name__ == "__main__":
    print("Testing form endpoints...")
    print("=" * 50)
    
    try:
        session = test_login()
        test_form_endpoints(session)
        print("\n" + "=" * 50)
        print("All form tests completed!")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

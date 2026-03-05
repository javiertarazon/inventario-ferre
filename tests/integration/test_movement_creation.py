"""
Test script to verify movement creation works correctly.
"""
import requests
from datetime import date

BASE_URL = "http://127.0.0.1:5000"

def test_movement_creation():
    """Test creating a movement."""
    session = requests.Session()
    
    # Login
    print("1. Logging in...")
    login_data = {
        'username': 'admin',
        'password': 'admin'
    }
    response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
    print(f"   Login: {response.status_code}")
    
    # Get the form page
    print("\n2. Loading movement form...")
    response = session.get(f"{BASE_URL}/movements/create")
    print(f"   Form page: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   ERROR: Could not load form")
        return
    
    # Try to create a movement
    print("\n3. Creating test movement...")
    movement_data = {
        'tipo': 'ENTRADA',
        'producto_id': '4',  # First product from Excel (Socates Porcelana)
        'cantidad': '5',
        'descripcion': 'Prueba de movimiento desde script',
        'fecha': date.today().isoformat()
    }
    
    response = session.post(f"{BASE_URL}/movements/create", data=movement_data, allow_redirects=False)
    print(f"   Create movement: {response.status_code}")
    
    if response.status_code == 302:
        print("   ✓ Movement created successfully!")
        print(f"   Redirect to: {response.headers.get('Location')}")
    else:
        print(f"   ✗ Failed to create movement")
        print(f"   Response: {response.text[:500]}")
    
    # Check movements list
    print("\n4. Checking movements list...")
    response = session.get(f"{BASE_URL}/movements/")
    print(f"   Movements page: {response.status_code}")
    
    if 'Prueba de movimiento' in response.text:
        print("   ✓ Movement appears in list!")
    else:
        print("   ? Movement not found in list (may be on different page)")

if __name__ == "__main__":
    print("Testing Movement Creation")
    print("=" * 60)
    try:
        test_movement_creation()
        print("\n" + "=" * 60)
        print("Test completed!")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

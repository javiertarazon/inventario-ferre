"""Test script to verify blueprints work correctly."""
from app import create_app
from app.services import ProductService, SupplierService, CustomerService, ItemGroupService

app = create_app()

with app.app_context():
    print("Testing services...")
    
    # Test ProductService
    try:
        ps = ProductService()
        products = ps.get_all_products()
        print(f"✓ ProductService.get_all_products(): {len(products)} products")
    except Exception as e:
        print(f"✗ ProductService.get_all_products(): {e}")
    
    # Test SupplierService
    try:
        ss = SupplierService()
        suppliers = ss.get_all_suppliers()
        print(f"✓ SupplierService.get_all_suppliers(): {len(suppliers)} suppliers")
    except Exception as e:
        print(f"✗ SupplierService.get_all_suppliers(): {e}")
    
    # Test CustomerService
    try:
        cs = CustomerService()
        customers = cs.get_all_customers()
        print(f"✓ CustomerService.get_all_customers(): {len(customers)} customers")
    except Exception as e:
        print(f"✗ CustomerService.get_all_customers(): {e}")
    
    # Test ItemGroupService
    try:
        igs = ItemGroupService()
        groups = igs.get_all_groups()
        print(f"✓ ItemGroupService.get_all_groups(): {len(groups)} groups")
    except Exception as e:
        print(f"✗ ItemGroupService.get_all_groups(): {e}")
    
    # Test search_products
    try:
        ps = ProductService()
        result = ps.search_products(query='', page=1, per_page=10)
        print(f"✓ ProductService.search_products(): {len(result.items)} products")
    except Exception as e:
        print(f"✗ ProductService.search_products(): {e}")
    
    print("\nAll tests completed!")

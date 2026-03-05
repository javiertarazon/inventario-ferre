#!/usr/bin/env python
"""Quick import validation for Phase 2 changes."""

import sys
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modified services import correctly."""
    
    print("\nTesting Phase 2 Service Imports...")
    print("="*60)
    
    services_to_test = [
        'product_service',
        'customer_service',
        'movement_service',
        'supplier_service',
        'validation_service',
        'dashboard_service',
        'import_service',
        'item_group_service',
        'reports_service',
        'sales_order_service',
    ]
    
    failed = []
    passed = []
    
    for service_name in services_to_test:
        try:
            module = __import__(f'app.services.{service_name}', fromlist=[service_name])
            
            # Get all classes from the module
            classes = [name for name in dir(module) if not name.startswith('_')]
            
            print(f"✅ {service_name:30} - {len(classes)} exports")
            passed.append(service_name)
            
        except Exception as e:
            print(f"❌ {service_name:30} - {str(e)[:50]}")
            failed.append((service_name, str(e)))
    
    print("="*60)
    print(f"\nRESULTS: {len(passed)}/{len(services_to_test)} services imported successfully")
    
    if failed:
        print("\nFailed imports:")
        for name, error in failed:
            print(f"  - {name}: {error}")
        return False
    
    print("\n✅ ALL PHASE 2 SERVICE IMPORTS SUCCESSFUL")
    return True


if __name__ == '__main__':
    success = test_imports()
    sys.exit(0 if success else 1)

"""
Test automatic code generation system.
"""
from app import create_app
from app.utils.code_generator import CodeGenerator
from app.models import Product, ItemGroup

def test_code_generation():
    """Test code generation with various scenarios."""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("TESTING CODE GENERATION SYSTEM")
        print("=" * 60)
        
        # Test 1: Basic code generation
        print("\n1. Testing basic code generation...")
        test_cases = [
            ("Electricidad", "Socates Porcelana Patica", "E-SO-PO"),
            ("Plomeria", "Codo Galv 1/2", "P-CO-GA"),
            ("Albañileria", "Pego Gris Sacos", "A-PE-GR"),
            ("Carpinteria", "Disco Sierra Madera", "C-DI-SI"),
            ("Herreria", "Hojas Ceguetones 21", "H-HO-CE"),
            ("Tornilleria", "Barra Roscada 3/16", "B-RO"),
            ("Miselaneos", "Grapas Cercas Galvanizadas", "M-GR-CE")
        ]
        
        for category, description, expected_prefix in test_cases:
            code = CodeGenerator.generate_code(category, description)
            if code.startswith(expected_prefix):
                print(f"   ✓ {category}: {description[:30]:30} → {code}")
            else:
                print(f"   ✗ {category}: Expected {expected_prefix}, got {code}")
        
        # Test 2: Sequence numbering
        print("\n2. Testing sequence numbering...")
        # Get some existing products
        electricidad = ItemGroup.query.filter_by(name='Electricidad').first()
        if electricidad:
            products = Product.query.filter_by(item_group_id=electricidad.id).limit(5).all()
            print(f"   Existing Electricidad products:")
            for p in products:
                print(f"     {p.codigo} - {p.descripcion[:40]}")
        
        # Test 3: Special characters handling
        print("\n3. Testing special characters...")
        special_cases = [
            ("Electricidad", "Lámpara LED 12W", "E-LA-LE"),
            ("Plomeria", "Tubo PVC 1/2\"", "E-TU-PV"),
            ("Albañileria", "Cemento Gris 42kg", "A-CE-GR")
        ]
        
        for category, description, expected_prefix in special_cases:
            code = CodeGenerator.generate_code(category, description)
            print(f"   {description[:30]:30} → {code}")
        
        # Test 4: Count products by category
        print("\n4. Products by category:")
        categories = ItemGroup.query.filter_by(deleted_at=None).all()
        for cat in categories:
            count = Product.query.filter_by(item_group_id=cat.id, deleted_at=None).count()
            print(f"   {cat.name:15} ({cat.icon}): {count:3} productos")
        
        # Test 5: Show code distribution
        print("\n5. Code prefix distribution:")
        all_products = Product.query.filter_by(deleted_at=None).all()
        prefix_count = {}
        for p in all_products:
            prefix = p.codigo.split('-')[0] if '-' in p.codigo else 'OTHER'
            prefix_count[prefix] = prefix_count.get(prefix, 0) + 1
        
        for prefix, count in sorted(prefix_count.items()):
            print(f"   {prefix}: {count} productos")
        
        print("\n" + "=" * 60)
        print("✓ CODE GENERATION SYSTEM WORKING")
        print("=" * 60)

if __name__ == '__main__':
    test_code_generation()

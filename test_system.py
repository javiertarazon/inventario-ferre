"""
Comprehensive system test script.
Tests all implemented functionality.
"""
import sys
from datetime import datetime, date
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.product import Product
from app.models.supplier import Proveedor
from app.models.movement import Movimiento
from app.models.audit_log import AuditLog
from app.repositories.product_repository import ProductRepository
from app.repositories.supplier_repository import SupplierRepository
from app.repositories.movement_repository import MovementRepository
from app.repositories.audit_repository import AuditRepository


def print_section(title):
    """Print section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_configuration():
    """Test configuration loading."""
    print_section("Testing Configuration")
    
    app = create_app('development')
    print(f"✓ Application created successfully")
    print(f"  - App name: {app.name}")
    print(f"  - Debug mode: {app.debug}")
    print(f"  - Database URI: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")
    
    return app


def test_database_models(app):
    """Test database models."""
    print_section("Testing Database Models")
    
    with app.app_context():
        # Drop and recreate tables
        db.drop_all()
        db.create_all()
        print("✓ Database tables created")
        
        # Test User model
        user = User(
            username='admin',
            email='admin@example.com',
            role='admin'
        )
        user.set_password('admin123')
        db.session.add(user)
        db.session.commit()
        print(f"✓ User created: {user.username}")
        
        # Test password verification
        assert user.check_password('admin123'), "Password verification failed"
        print("✓ Password verification works")
        
        # Test Supplier model
        supplier = Proveedor(
            nombre='Proveedor Test',
            rif='J-12345678-9',
            telefono='0212-1234567',
            email='proveedor@test.com',
            created_by=user.id
        )
        db.session.add(supplier)
        db.session.commit()
        print(f"✓ Supplier created: {supplier.nombre}")
        
        # Test Product model
        product = Product(
            codigo='A-01-01',
            descripcion='Producto de Prueba',
            stock=100,
            precio_dolares=10.50,
            factor_ajuste=1.2,
            proveedor_id=supplier.id,
            created_by=user.id
        )
        db.session.add(product)
        db.session.commit()
        print(f"✓ Product created: {product.codigo} - {product.descripcion}")
        
        # Test Movement model
        movement = Movimiento(
            producto_id=product.id,
            tipo='entrada',
            cantidad=50,
            fecha=date.today(),
            descripcion='Entrada inicial',
            created_by=user.id
        )
        db.session.add(movement)
        db.session.commit()
        print(f"✓ Movement created: {movement.tipo} - {movement.cantidad} units")
        
        # Test Audit Log model
        audit = AuditLog(
            user_id=user.id,
            action='CREATE',
            entity_type='Product',
            entity_id=product.id,
            new_values={'codigo': product.codigo, 'descripcion': product.descripcion},
            ip_address='127.0.0.1'
        )
        db.session.add(audit)
        db.session.commit()
        print(f"✓ Audit log created: {audit.action} {audit.entity_type}")
        
        return user, supplier, product, movement


def test_repositories(app):
    """Test repository layer."""
    print_section("Testing Repository Layer")
    
    with app.app_context():
        # Test ProductRepository
        product_repo = ProductRepository()
        
        # Get the first product
        products = product_repo.get_active_products(page=1, per_page=10)
        if products.total > 0:
            product = products.items[0]
            
            # Test get_by_id
            retrieved_product = product_repo.get_by_id(product.id)
            assert retrieved_product is not None, "Product not found"
            print(f"✓ ProductRepository.get_by_id: {retrieved_product.codigo}")
            
            # Test get_by_codigo
            product_by_code = product_repo.get_by_codigo(product.codigo)
            assert product_by_code is not None, "Product not found by codigo"
            print(f"✓ ProductRepository.get_by_codigo: {product_by_code.descripcion}")
            
            # Test search_products
            search_result = product_repo.search_products('Prueba', page=1, per_page=10)
            print(f"✓ ProductRepository.search_products: Found {search_result.total} products")
        
        # Test get_active_products
        active_products = product_repo.get_active_products(page=1, per_page=10)
        print(f"✓ ProductRepository.get_active_products: {active_products.total} active products")
        
        # Test SupplierRepository
        supplier_repo = SupplierRepository()
        
        # Get active suppliers
        active_suppliers = supplier_repo.get_active_suppliers(page=1, per_page=10)
        print(f"✓ SupplierRepository.get_active_suppliers: {active_suppliers.total} suppliers")
        
        if active_suppliers.total > 0:
            supplier = active_suppliers.items[0]
            if supplier.rif:
                # Test get_by_rif
                supplier_by_rif = supplier_repo.get_by_rif(supplier.rif)
                assert supplier_by_rif is not None, "Supplier not found by RIF"
                print(f"✓ SupplierRepository.get_by_rif: {supplier_by_rif.nombre}")
        
        # Test MovementRepository
        movement_repo = MovementRepository()
        
        # Test get_by_date_range
        today = date.today()
        date_movements = movement_repo.get_by_date_range(today, today, page=1, per_page=10)
        print(f"✓ MovementRepository.get_by_date_range: {date_movements.total} movements today")
        
        if products.total > 0:
            # Test get_by_product
            product_movements = movement_repo.get_by_product(products.items[0].id, page=1, per_page=10)
            print(f"✓ MovementRepository.get_by_product: {product_movements.total} movements")
        
        # Test AuditRepository
        audit_repo = AuditRepository()
        
        # Test search_logs
        audit_logs = audit_repo.search_logs({}, page=1, per_page=10)
        print(f"✓ AuditRepository.search_logs: {audit_logs.total} audit logs")


def test_soft_delete(app):
    """Test soft delete functionality."""
    print_section("Testing Soft Delete")
    
    with app.app_context():
        product_repo = ProductRepository()
        
        # Get first product
        products = product_repo.get_active_products()
        if products.total > 0:
            product = products.items[0]
            product_id = product.id
            
            # Soft delete product
            product.soft_delete()
            db.session.commit()
            print(f"✓ Product soft deleted: {product.codigo}")
            
            # Verify it's not in active products
            active_products = product_repo.get_active_products()
            assert product_id not in [p.id for p in active_products.items], "Deleted product still in active list"
            print("✓ Soft deleted product not in active list")
            
            # Restore product
            product.restore()
            db.session.commit()
            print(f"✓ Product restored: {product.codigo}")
            
            # Verify it's back in active products
            active_products = product_repo.get_active_products()
            assert product_id in [p.id for p in active_products.items], "Restored product not in active list"
            print("✓ Restored product back in active list")
        else:
            print("⚠ No products to test soft delete")


def test_user_security(app):
    """Test user security features."""
    print_section("Testing User Security Features")
    
    with app.app_context():
        # Get first user
        user = db.session.query(User).first()
        if not user:
            print("⚠ No users to test")
            return
        
        # Test password hashing
        assert user.check_password('admin123'), "Password check failed"
        assert not user.check_password('wrong_password'), "Wrong password accepted"
        print("✓ Password hashing and verification works")
        
        # Test account locking
        assert not user.is_locked(), "Account should not be locked initially"
        user.lock_account(duration_minutes=30)
        assert user.is_locked(), "Account should be locked"
        print("✓ Account locking works")
        
        # Test account unlocking
        user.unlock_account()
        assert not user.is_locked(), "Account should be unlocked"
        print("✓ Account unlocking works")
        
        # Test failed login tracking
        user.record_failed_login(max_attempts=3)
        assert user.failed_login_attempts == 1, "Failed login not recorded"
        print("✓ Failed login tracking works")
        
        # Test successful login
        user.record_successful_login()
        assert user.failed_login_attempts == 0, "Failed attempts not reset"
        assert user.last_login is not None, "Last login not recorded"
        print("✓ Successful login tracking works")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("  COMPREHENSIVE SYSTEM TEST")
    print("="*60)
    
    try:
        # Test 1: Configuration
        app = test_configuration()
        
        # Test 2: Database Models
        user, supplier, product, movement = test_database_models(app)
        
        # Test 3: Repository Layer
        test_repositories(app)
        
        # Test 4: Soft Delete
        test_soft_delete(app)
        
        # Test 5: User Security
        test_user_security(app)
        
        # Summary
        print_section("TEST SUMMARY")
        print("✓ All tests passed successfully!")
        print("\nImplemented Features:")
        print("  • Configuration management (development, testing, production)")
        print("  • Enhanced database models with audit fields")
        print("  • User model with security features (password hashing, account locking)")
        print("  • Repository layer with CRUD operations")
        print("  • Soft delete functionality")
        print("  • Audit logging")
        print("  • Error handling and logging infrastructure")
        print("  • Database migrations")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())

"""
Pytest configuration and fixtures for Phase 3 testing.
"""

import pytest
from decimal import Decimal
from datetime import datetime, date
from app import create_app
from app.extensions import db
from app.models import Product, Customer, Supplier, Movement, ItemGroup, User
from app.services import (
    ProductService, CustomerService, SupplierService,
    MovementService, ValidationService
)


@pytest.fixture(scope='function')
def app():
    """Create application for testing with in-memory database."""
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client for making HTTP requests."""
    return app.test_client()


@pytest.fixture
def app_context(app):
    """Application context for manual testing."""
    ctx = app.app_context()
    ctx.push()
    yield ctx
    ctx.pop()


@pytest.fixture
def test_user(app):
    """Create test user - returns (user_id, user_obj) tuple."""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            is_active=True
        )
        user.set_password('testpass123')
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        return (user_id, user)


@pytest.fixture
def test_supplier(app):
    """Create test supplier returns (supplier_id, supplier_obj) tuple."""
    with app.app_context():
        supplier = Supplier(
            nombre='Test Supplier',
            rif='J-12345678-9',
            email='supplier@test.com',
            telefono='02612345678',
            direccion='Test Address 123',
            created_by=1,
            updated_by=1
        )
        db.session.add(supplier)
        db.session.commit()
        supplier_id = supplier.id
        return (supplier_id, supplier)


@pytest.fixture
def test_item_group(app):
    """Create test item group/category - returns (group_id, group_obj) tuple."""
    with app.app_context():
        group = ItemGroup(
            name='Test Category',
            description='Test category description',
            color='#007bff',
            icon='bi-box',
            created_by=1,
            updated_by=1
        )
        db.session.add(group)
        db.session.commit()
        group_id = group.id
        return (group_id, group)


@pytest.fixture
def test_product(app, test_supplier, test_item_group):
    """Create test product - returns (product_id, product_obj) tuple."""
    with app.app_context():
        supplier_id, _ = test_supplier
        group_id, _ = test_item_group
        
        product = Product(
            codigo='A-TEST-01',
            descripcion='Test Product',
            stock=100,
            precio_dolares=Decimal('10.00'),
            factor_ajuste=Decimal('1.00'),
            proveedor_id=supplier_id,
            item_group_id=group_id,
            reorder_point=10,
            created_by=1,
            updated_by=1
        )
        db.session.add(product)
        db.session.commit()
        product_id = product.id
        return (product_id, product)


@pytest.fixture
def test_customer(app):
    """Create test customer - returns (customer_id, customer_obj) tuple."""
    with app.app_context():
        customer = Customer(
            name='Test Customer',
            email='customer@test.com',
            phone='02612345678',
            tax_id='J-12345678-9',
            tax_id_type='J',
            address='Test Address 123',
            city='Test City',
            country='Venezuela',
            is_active=True,
            credit_limit=Decimal('1000.00'),
            created_by=1,
            updated_by=1
        )
        db.session.add(customer)
        db.session.commit()
        customer_id = customer.id
        return (customer_id, customer)


@pytest.fixture
def product_service(app):
    """Create ProductService instance."""
    with app.app_context():
        return ProductService()


@pytest.fixture
def customer_service(app):
    """Create CustomerService instance."""
    with app.app_context():
        return CustomerService()


@pytest.fixture
def supplier_service(app):
    """Create SupplierService instance."""
    with app.app_context():
        return SupplierService()


@pytest.fixture
def movement_service(app):
    """Create MovementService instance."""
    with app.app_context():
        return MovementService()


@pytest.fixture
def validation_service(app):
    """Create ValidationService instance."""
    with app.app_context():
        return ValidationService()

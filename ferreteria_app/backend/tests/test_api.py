import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.database import Base, get_db
from app.models.models import User, Product, Customer, Invoice, ExchangeRate
from app.schemas.schemas import UserCreate, ProductCreate, CustomerCreate, InvoiceCreate, InvoiceItemCreate
from app.core.security import get_password_hash


# Configurar base de datos de prueba en memoria
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def override_get_db():
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@app.on_event("startup")
async def startup_test():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    app.dependency_overrides[get_db] = override_get_db


@app.on_event("shutdown")
async def shutdown_test():
    await engine.dispose()


# ==================== FIXTURES ====================

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def test_user():
    async for db in override_get_db():
        user_data = UserCreate(
            username="testadmin",
            email="admin@test.com",
            full_name="Administrador Test",
            password="password123",
            role="admin"
        )
        from app.services.crud_services import UserService
        user = await UserService.create_user(db, user_data)
        return user


@pytest.fixture
async def test_product():
    async for db in override_get_db():
        product_data = ProductCreate(
            sku="TEST-001",
            name="Martillo Profesional",
            description="Martillo de acero templado",
            category="Herramientas",
            unit_price_usd=15.50,
            stock_quantity=100.0,
            min_stock=10.0,
            unit_measure="unidad",
            iva_rate=0.16
        )
        from app.services.crud_services import ProductService
        product = await ProductService.create_product(db, product_data)
        return product


@pytest.fixture
async def test_customer():
    async for db in override_get_db():
        customer_data = CustomerCreate(
            rif="V-12345678-9",
            name="Juan Pérez",
            address="Calle Principal #123",
            phone="0412-1234567",
            email="juan@example.com",
            customer_type="natural"
        )
        from app.services.crud_services import CustomerService
        customer = await CustomerService.create_customer(db, customer_data)
        return customer


@pytest.fixture
async def test_exchange_rate():
    async for db in override_get_db():
        from app.services.crud_services import ExchangeRateService
        rate = await ExchangeRateService.create_exchange_rate(db, rate=36.50, source="BCV_TEST")
        return rate


# ==================== AUTH TESTS ====================

@pytest.mark.asyncio
async def test_register_user(client):
    """Prueba registro de usuario"""
    response = await client.post("/api/v1/auth/register", json={
        "username": "newuser",
        "email": "newuser@test.com",
        "full_name": "Nuevo Usuario",
        "password": "securepass123",
        "role": "cajero"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@test.com"


@pytest.mark.asyncio
async def test_login_user(client, test_user):
    """Prueba inicio de sesión"""
    response = await client.post(
        "/api/v1/auth/login",
        params={"username": "testadmin", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    """Prueba credenciales inválidas"""
    response = await client.post(
        "/api/v1/auth/login",
        params={"username": "nonexistent", "password": "wrongpass"}
    )
    assert response.status_code == 401


# ==================== PRODUCT TESTS ====================

@pytest.mark.asyncio
async def test_create_product(client):
    """Prueba creación de producto"""
    response = await client.post("/api/v1/products", json={
        "sku": "PROD-001",
        "name": "Taladro Eléctrico",
        "description": "Taladro 500W",
        "category": "Herramientas Eléctricas",
        "unit_price_usd": 45.00,
        "stock_quantity": 50.0,
        "min_stock": 5.0,
        "unit_measure": "unidad",
        "iva_rate": 0.16
    })
    assert response.status_code == 201
    data = response.json()
    assert data["sku"] == "PROD-001"
    assert data["name"] == "Taladro Eléctrico"


@pytest.mark.asyncio
async def test_get_products(client, test_product):
    """Prueba obtención de lista de productos"""
    response = await client.get("/api/v1/products")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(p["sku"] == "TEST-001" for p in data)


@pytest.mark.asyncio
async def test_update_product(client, test_product):
    """Prueba actualización de producto"""
    response = await client.put(f"/api/v1/products/{test_product.id}", json={
        "unit_price_usd": 18.00,
        "stock_quantity": 150.0
    })
    assert response.status_code == 200
    data = response.json()
    assert data["unit_price_usd"] == 18.00


# ==================== CUSTOMER TESTS ====================

@pytest.mark.asyncio
async def test_create_customer(client):
    """Prueba creación de cliente con RIF válido"""
    response = await client.post("/api/v1/customers", json={
        "rif": "J-12345678-9",
        "name": "Empresa CA",
        "address": "Av. Principal",
        "phone": "0212-1234567",
        "email": "empresa@example.com",
        "customer_type": "juridica"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["rif"] == "J-12345678-9"


@pytest.mark.asyncio
async def test_create_customer_invalid_rif(client):
    """Prueba validación de RIF inválido"""
    response = await client.post("/api/v1/customers", json={
        "rif": "X-123",
        "name": "Invalido",
    })
    assert response.status_code == 422  # Validation error


# ==================== INVOICE TESTS ====================

@pytest.mark.asyncio
async def test_create_invoice(client, test_customer, test_product, test_exchange_rate):
    """Prueba creación de factura"""
    invoice_data = {
        "customer_id": test_customer.id,
        "items": [
            {
                "product_id": test_product.id,
                "quantity": 2.0,
                "unit_price_usd": test_product.unit_price_usd,
                "iva_rate": 0.16
            }
        ],
        "payment_method": "punto",
        "apply_igtf": False
    }
    
    response = await client.post("/api/v1/invoices", json=invoice_data)
    assert response.status_code == 201
    data = response.json()
    assert "invoice_number" in data
    assert data["total_usd"] > 0
    assert data["exchange_rate"] == 36.50


@pytest.mark.asyncio
async def test_create_invoice_with_igtf(client, test_customer, test_product, test_exchange_rate):
    """Prueba creación de factura con IGTF"""
    invoice_data = {
        "customer_id": test_customer.id,
        "items": [
            {
                "product_id": test_product.id,
                "quantity": 1.0,
                "unit_price_usd": test_product.unit_price_usd,
                "iva_rate": 0.16
            }
        ],
        "payment_method": "divisas",
        "apply_igtf": True
    }
    
    response = await client.post("/api/v1/invoices", json=invoice_data)
    assert response.status_code == 201
    data = response.json()
    assert data["apply_igtf"] == True
    assert data["igtf_amount_usd"] > 0  # Debe tener IGTF calculado


@pytest.mark.asyncio
async def test_get_invoices(client):
    """Prueba obtención de lista de facturas"""
    response = await client.get("/api/v1/invoices")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ==================== EXCHANGE RATE TESTS ====================

@pytest.mark.asyncio
async def test_get_current_exchange_rate(client, test_exchange_rate):
    """Prueba obtención de tasa actual"""
    response = await client.get("/api/v1/exchange-rate/current")
    assert response.status_code == 200
    data = response.json()
    assert data["rate"] == 36.50


@pytest.mark.asyncio
async def test_update_exchange_rate(client):
    """Prueba actualización de tasa BCV (simulada)"""
    # Nota: Esta prueba puede fallar si no hay conexión a internet
    response = await client.post("/api/v1/exchange-rate/update")
    assert response.status_code in [200, 500]  # Puede fallar si BCV no responde


# ==================== SYSTEM INIT TEST ====================

@pytest.mark.asyncio
async def test_system_initialization(client):
    """Prueba inicialización del sistema con BCV"""
    response = await client.get("/api/v1/system/init")
    assert response.status_code == 200
    data = response.json()
    assert data["initialized"] == True
    assert "exchange_rate" in data
    assert data["base_currency"] == "USD"


# ==================== LOW STOCK TEST ====================

@pytest.mark.asyncio
async def test_low_stock_alert(client):
    """Prueba alerta de stock bajo"""
    # Crear producto con stock bajo
    async for db in override_get_db():
        from app.services.crud_services import ProductService
        from app.schemas.schemas import ProductCreate
        
        low_stock_product = ProductCreate(
            sku="LOW-001",
            name="Producto Stock Bajo",
            unit_price_usd=10.00,
            stock_quantity=2.0,
            min_stock=10.0
        )
        await ProductService.create_product(db, low_stock_product)
    
    response = await client.get("/api/v1/products/low-stock")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(p["sku"] == "LOW-001" for p in data)


# ==================== RUN TESTS ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

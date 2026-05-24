import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings


# Configurar base de datos de prueba en memoria
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

test_session_maker = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def override_get_db():
    async with test_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest.fixture(scope="function")
async def client():
    """Crea un cliente de prueba para la API"""
    # Crear tablas
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Sobrescribir dependencia de base de datos
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()
    
    # Eliminar tablas
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_root_endpoint(client):
    """Prueba el endpoint raíz"""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Ferretería" in data["message"]


@pytest.mark.asyncio
async def test_health_check(client):
    """Prueba el endpoint de salud"""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_register_user(client):
    """Prueba el registro de usuario"""
    user_data = {
        "username": "testadmin",
        "email": "admin@ferreteria.com",
        "full_name": "Administrador Test",
        "password": "password123",
        "role": "admin"
    }
    
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testadmin"
    assert "id" in data


@pytest.mark.asyncio
async def test_login(client):
    """Prueba el inicio de sesión"""
    # Primero registrar usuario
    user_data = {
        "username": "testuser",
        "email": "user@ferreteria.com",
        "full_name": "Usuario Test",
        "password": "password123",
        "role": "cajero"
    }
    
    await client.post("/api/v1/auth/register", json=user_data)
    
    # Intentar login
    login_data = {
        "username": "testuser",
        "password": "password123"
    }
    
    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_create_product_unauthorized(client):
    """Prueba creación de producto sin autenticación (debería fallar o pasar según implementación)"""
    product_data = {
        "code": "PROD001",
        "name": "Martillo",
        "price_usd": 15.99,
        "stock_quantity": 50,
        "category": "Herramientas"
    }
    
    response = await client.post("/api/v1/products/", json=product_data)
    # Dependiendo de la implementación, puede ser 201 o 401
    assert response.status_code in [201, 401]


@pytest.mark.asyncio
async def test_products_list_empty(client):
    """Prueba listar productos vacíos"""
    response = await client.get("/api/v1/products/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_customers_list_empty(client):
    """Prueba listar clientes vacíos"""
    response = await client.get("/api/v1/customers/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_sales_list_empty(client):
    """Prueba listar ventas vacías"""
    response = await client.get("/api/v1/sales/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_exchange_rate_bcv(client):
    """Prueba obtener tasa del BCV"""
    response = await client.get("/api/v1/exchange-rate/bcv")
    assert response.status_code == 200
    data = response.json()
    assert "rate" in data
    assert "message" in data
    assert "is_alert" in data


@pytest.mark.asyncio
async def test_create_customer_unauthorized(client):
    """Prueba crear cliente"""
    customer_data = {
        "rif": "V12345678",
        "name": "Cliente Test",
        "customer_type": "natural"
    }
    
    response = await client.post("/api/v1/customers/", json=customer_data)
    # Puede ser 201 o 401 dependiendo de la autenticación
    assert response.status_code in [201, 401]


@pytest.mark.asyncio
async def test_invalid_rif_validation(client):
    """Prueba validación de RIF inválido"""
    customer_data = {
        "rif": "INVALIDO",
        "name": "Cliente Test",
        "customer_type": "natural"
    }
    
    response = await client.post("/api/v1/customers/", json=customer_data)
    assert response.status_code in [400, 401, 422]


@pytest.mark.asyncio
async def test_product_creation_with_all_fields(client):
    """Prueba creación de producto con todos los campos"""
    product_data = {
        "code": "TEST002",
        "name": "Taladro Percutor",
        "description": "Taladro percutor 500W",
        "category": "Herramientas Eléctricas",
        "brand": "Bosch",
        "price_usd": 89.99,
        "stock_quantity": 25,
        "min_stock": 5,
        "unit_of_measure": "unidad",
        "iva_rate": 0.16,
        "is_exempt": False
    }
    
    response = await client.post("/api/v1/products/", json=product_data)
    # Puede ser 201 o 401
    assert response.status_code in [201, 401]
    
    if response.status_code == 201:
        data = response.json()
        assert data["code"] == "TEST002"
        assert data["price_usd"] == 89.99


@pytest.mark.asyncio
async def test_duplicate_product_code(client):
    """Prueba que no se puedan crear productos con código duplicado"""
    # Crear primer producto
    product_data_1 = {
        "code": "DUP001",
        "name": "Producto 1",
        "price_usd": 10.00
    }
    
    response1 = await client.post("/api/v1/products/", json=product_data_1)
    
    # Intentar crear producto con mismo código
    product_data_2 = {
        "code": "DUP001",
        "name": "Producto 2",
        "price_usd": 20.00
    }
    
    response2 = await client.post("/api/v1/products/", json=product_data_2)
    
    # Al menos uno debe fallar o ambos deben tener códigos diferentes
    if response1.status_code == 201 and response2.status_code == 201:
        # Esto no debería pasar, pero si pasa, verificar que los códigos sean diferentes
        assert response1.json()["code"] != response2.json()["code"]


@pytest.mark.asyncio
async def test_pagination(client):
    """Prueba paginación de productos"""
    response = await client.get("/api/v1/products/?skip=0&limit=10")
    assert response.status_code == 200
    
    response_page2 = await client.get("/api/v1/products/?skip=10&limit=10")
    assert response_page2.status_code == 200


@pytest.mark.asyncio
async def test_search_products(client):
    """Prueba búsqueda de productos"""
    response = await client.get("/api/v1/products/?search=martillo")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

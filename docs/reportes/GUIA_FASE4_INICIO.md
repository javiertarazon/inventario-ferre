# Fase 4: API REST - Guía de Inicio

**Pre-requisitos Cumplidos**: ✅ Fase 3 (100% tests pasando)  
**Próximo Paso**: Implementar endpoints REST  
**Estimado**: 8-10 horas  

---

## Arquitectura Propuesta para Fase 4

### 1. Estructura de Blueprints (Flask)

```
app/
├── blueprints/
│   ├── __init__.py
│   ├── products_bp.py          # GET /products, POST, PUT, DELETE
│   ├── customers_bp.py         # GET /customers, POST, PUT, DELETE
│   ├── suppliers_bp.py         # GET /suppliers, POST, PUT, DELETE
│   ├── movements_bp.py         # POST /movements (ENTRADA/SALIDA)
│   └── auth_bp.py              # POST /auth/login (JWT)
├── schemas/
│   ├── product_schema.py       # Request/Response validation
│   ├── customer_schema.py
│   ├── supplier_schema.py
│   └── movement_schema.py
└── decorators/
    ├── auth.py                 # @jwt_required, @admin_required
    └── validation.py           # @validate_json
```

### 2. Stack Tecnológico

```python
# requirements.txt additions:
Flask-JWT-Extended>=4.4.0      # JWT authentication
marshmallow>=3.13.0            # Request/Response schemas
python-dateutil>=2.8.0         # Date handling
python-dotenv>=0.21.0          # Environment variables
```

### 3. Patrón de Endpoint (Ejemplo)

```python
# app/blueprints/products_bp.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.schemas import ProductSchema
from app.services import ProductService

products_bp = Blueprint('products', __name__, url_prefix='/api/v1/products')
product_schema = ProductSchema()

@products_bp.route('', methods=['GET'])
@jwt_required()
def list_products():
    """GET /api/v1/products - List all products with pagination"""
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    with db.app.app_context():  # Reutilizar patrón Fase 3
        service = ProductService(db)
        result = service.get_all_products(page, per_page)
        return jsonify({
            'items': product_schema.dump(result.items, many=True),
            'total': result.total,
            'page': result.page,
            'per_page': result.per_page
        })

@products_bp.route('', methods=['POST'])
@jwt_required()
def create_product():
    """POST /api/v1/products - Create new product"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validar con Marshmallow
    errors = product_schema.validate(data)
    if errors:
        return jsonify({'errors': errors}), 400
    
    with db.app.app_context():
        service = ProductService(db)
        try:
            product = service.create_product(
                codigo=data['codigo'],
                descripcion=data['descripcion'],
                precio=data['precio'],
                stock=data.get('stock', 0)
            )
            return jsonify(product_schema.dump(product)), 201
        except ValidationError as e:
            return jsonify({'error': str(e)}), 400
```

### 4. Schemas Marshmallow (Ejemplo)

```python
# app/schemas/product_schema.py
from marshmallow import Schema, fields, validate

class ProductSchema(Schema):
    id = fields.Int(dump_only=True)
    codigo = fields.Str(required=True, validate=validate.Regexp(r'^[A-Z]{1}-[A-Z]{2}-\d{2}$'))
    descripcion = fields.Str(required=True, validate=validate.Length(min=3, max=200))
    precio = fields.Decimal(required=True, places=2, as_string=False)
    stock = fields.Int(validate=validate.Range(min=0))
    created_at = fields.DateTime(dump_only=True)
    
    class Meta:
        fields = ('id', 'codigo', 'descripcion', 'precio', 'stock', 'created_at')
```

### 5. JWT Authentication

```python
# app/auth.py
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from datetime import timedelta

jwt = JWTManager()

def init_jwt(app):
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'change-me-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    jwt.init_app(app)

# En blueprints:
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = validate_credentials(data['email'], data['password'])  # Implement this
    if user:
        expires = timedelta(hours=24)
        access_token = create_access_token(identity=user.id, expires_delta=expires)
        return jsonify({'access_token': access_token}), 200
    return jsonify({'error': 'Invalid credentials'}), 401
```

---

## Plan de Implementación (8-10 horas)

### Phase 4.1: Setup Base (1 hora)
- [ ] Instalar dependencias (`Flask-JWT-Extended`, `marshmallow`)
- [ ] Crear estructura de carpetas (blueprints/, schemas/, decorators/)
- [ ] Configurar Blueprint registration en `app/__init__.py`
- [ ] Crear archivo base auth.py con JWT config

### Phase 4.2: Schemas & Validation (1.5 horas)
- [ ] Implementar ProductSchema (Marshmallow)
- [ ] Implementar CustomerSchema
- [ ] Implementar SupplierSchema
- [ ] Implementar MovementSchema
- [ ] Tests para validación (marshmallow tests)

### Phase 4.3: Auth Blueprint (1.5 horas)
- [ ] POST /auth/login (email + password)
- [ ] POST /auth/refresh (refresh token)
- [ ] Implementar decorators @jwt_required, @admin_required
- [ ] Tests para auth endpoints (5+ tests)

### Phase 4.4: Products Endpoints (2 horas)
- [ ] GET /api/v1/products (list con paginación)
- [ ] GET /api/v1/products/:id
- [ ] POST /api/v1/products (create)
- [ ] PUT /api/v1/products/:id (update)
- [ ] DELETE /api/v1/products/:id
- [ ] Tests para endpoints (10+ tests)

### Phase 4.5: Customers Endpoints (2 horas)
- [ ] GET /api/v1/customers (list)
- [ ] GET /api/v1/customers/:id
- [ ] POST /api/v1/customers (create)
- [ ] PUT /api/v1/customers/:id (update)
- [ ] DELETE /api/v1/customers/:id
- [ ] Tests para endpoints (10+ tests)

### Phase 4.6: Movements & Final (2 horas)
- [ ] POST /api/v1/movements (ENTRADA/SALIDA)
- [ ] GET /api/v1/movements (historial)
- [ ] Integration tests (10+ tests)
- [ ] Coverage report

---

## Reutilizar desde Fase 3

### ✅ Fixtures para API Tests
```python
# tests/conftest.py ya tiene:
@pytest.fixture
def client(app):  # ← USA ESTO para tests HTTP
    return app.test_client()

@pytest.fixture
def auth_headers(app, client):
    """Retorna headers con JWT válido"""
    response = client.post('/api/v1/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    token = response.json['access_token']
    return {'Authorization': f'Bearer {token}'}
```

### ✅ App Context Pattern
```python
# REUTILIZAR en tests HTTP:
def test_list_products(client):
    response = client.get('/api/v1/products', headers=auth_headers)
    assert response.status_code == 200
    assert 'items' in response.json
```

### ✅ Service Layer
Ya testeado en Fase 3, solo agregar lógica HTTP:
```python
# Existing:
service = ProductService(db)
products = service.get_all_products(page=1, per_page=20)

# Wrap en endpoint:
return jsonify(product_schema.dump(products.items, many=True))
```

---

## Checklist de Implementación

### Setup
- [ ] Instalar dependencias adicionales
- [ ] Crear estructura de carpetas
- [ ] Registrar blueprints en app/__init__.py
- [ ] Configurar JWT en app/config.py

### Auth
- [ ] JWT configuration
- [ ] Login endpoint
- [ ] Token validation decorators
- [ ] Auth tests (5+)

### Schemas
- [ ] ProductSchema
- [ ] CustomerSchema
- [ ] SupplierSchema
- [ ] Marshmallow tests (20+)

### Endpoints
- [ ] Products CRUD (5 endpoints)
- [ ] Customers CRUD (5 endpoints)
- [ ] Suppliers CRUD (5 endpoints)
- [ ] Movements POST (1 endpoint)
- [ ] API tests (50+)

### Final
- [ ] Integration tests (10+)
- [ ] Error handling
- [ ] Coverage report (target 70%+)
- [ ] Documentation/README API

---

## Testing Strategy para Fase 4

### Test Structure Propuesto
```
tests/
├── test_api_auth.py            # Auth endpoints (5 tests)
├── test_api_products.py        # Product endpoints (10 tests)
├── test_api_customers.py       # Customer endpoints (10 tests)
├── test_api_suppliers.py       # Supplier endpoints (10 tests)
├── test_api_movements.py       # Movement endpoints (10 tests)
├── test_schemas_validation.py  # Marshmallow validation (10 tests)
└── test_api_integration.py     # Full workflows (10+ tests)
```

### Patrón de Test API
```python
def test_list_products_requires_auth(client):
    """Test endpoint without JWT returns 401"""
    response = client.get('/api/v1/products')
    assert response.status_code == 401

def test_list_products_success(client, auth_headers):
    """Test endpoint with JWT returns products"""
    response = client.get('/api/v1/products', headers=auth_headers)
    assert response.status_code == 200
    assert 'items' in response.json

def test_create_product_validation(client, auth_headers):
    """Test invalid product data returns 400"""
    response = client.post('/api/v1/products', 
        json={'codigo': 'invalid', 'descripcion': ''},
        headers=auth_headers)
    assert response.status_code == 400
    assert 'errors' in response.json
```

---

## Inicio Rápido (Primeras 30 minutos)

```bash
# 1. Instalar dependencias
pip install Flask-JWT-Extended marshmallow

# 2. Crear estructura base
mkdir -p app/blueprints app/schemas app/decorators

# 3. Crear auth.py básico
# Copiar template de abajo

# 4. Correr ejemplo
pytest tests/test_api_auth.py

# 5. Validar setup
flask --app run
```

---

## Conclusión Fase 3 → Inicio Fase 4

**Fase 3**: ✅ COMPLETADA (42/42 tests)  
**Prerequisitos**: ✅ LISTOS  
**Dependencias**: ⏳ POR INSTALAR  
**Blueprints**: ⏳ POR CREAR  

**Próximo paso**: Instalar dependencias y crear estructura base de Fase 4

---

*Guía preparada para iniciar Fase 4*  
*Siguiendo patrones validados en Fase 3*  
*Estimado: 8-10 horas*

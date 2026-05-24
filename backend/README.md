# Sistema de Inventario y Facturación para Ferretería

Sistema profesional para gestión de inventario y facturación de ferreterías, cumpliendo con las normativas del SENIAT (Venezuela).

## Características Principales

### ✅ Cumplimiento Fiscal Venezolano
- **IVA**: Cálculo automático de IVA (16%, 8% reducido, exento)
- **IGTF**: Impuesto a las Grandes Transacciones Financieras (3%) para pagos en divisas
- **Tasa BCV**: Integración automática con tasa del Banco Central de Venezuela
- **RIF**: Validación de formato de RIF venezolano para clientes
- **Facturas PDF**: Generación de facturas con código QR fiscal

### 📦 Gestión de Inventario
- Productos con múltiples unidades de medida (unidad, kg, m, litro)
- Control de stock mínimo con alertas
- Categorías y marcas
- Precios en USD y VES (conversión automática)
- Movimientos de inventario auditados

### 💰 Facturación
- Facturas con numeración correlativa
- Múltiples métodos de pago (efectivo, punto, transferencia, divisa)
- Cálculo automático de impuestos
- Soporte bimonetario (USD/VES)
- Historial de ventas

### 👥 Usuarios y Seguridad
- Roles: Administrador, Cajero, Almacénista
- Autenticación JWT
- Auditoría de acciones
- Contraseñas encriptadas con bcrypt

### 🔄 Tasa de Cambio BCV
- Obtención automática al iniciar el sistema
- Reintentos automáticos (3 intentos)
- Alertas si falla la conexión
- Actualización manual disponible
- Histórico de tasas

## Arquitectura Técnica

### Backend
- **Framework**: FastAPI (Python 3.12+)
- **Base de Datos**: SQLite (portable) / PostgreSQL (producción)
- **ORM**: SQLAlchemy (asíncrono)
- **Autenticación**: JWT con python-jose
- **PDF**: ReportLab
- **QR**: qrcode

### Frontend (Pendiente)
- React + TailwindCSS (recomendado)
- Responsive (PC, tablet, móvil)

## Estructura del Proyecto

```
backend/
├── app/
│   ├── api/              # Endpoints REST
│   │   ├── auth.py       # Autenticación
│   │   ├── products.py   # Productos
│   │   ├── customers.py  # Clientes
│   │   ├── sales.py      # Ventas/Facturación
│   │   └── exchange_rate.py  # Tasa de cambio
│   ├── core/             # Configuración central
│   │   ├── config.py     # Variables de entorno
│   │   ├── database.py   # Conexión DB
│   │   ├── security.py   # Encriptación
│   │   └── jwt.py        # Tokens JWT
│   ├── models/           # Modelos de base de datos
│   ├── schemas/          # Validación Pydantic
│   ├── services/         # Lógica de negocio
│   │   ├── bcv_service.py    # Servicio BCV
│   │   └── services.py       # Servicios CRUD
│   ├── utils/            # Utilidades
│   │   └── invoice_pdf.py    # Generador PDF
│   └── main.py           # Aplicación principal
├── tests/                # Pruebas unitarias
├── requirements.txt      # Dependencias
└── pytest.ini           # Configuración tests
```

## Instalación

### Requisitos Previos
- Python 3.12 o superior
- pip

### Pasos de Instalación

1. **Clonar o navegar al directorio**
```bash
cd backend
```

2. **Crear entorno virtual (recomendado)**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Ejecutar la aplicación**
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. **Acceder a la API**
- Documentación interactiva: http://localhost:8000/docs
- Alternativa: http://localhost:8000/redoc

## Endpoints de la API

### Autenticación
- `POST /api/v1/auth/register` - Registrar usuario
- `POST /api/v1/auth/login` - Iniciar sesión

### Productos
- `GET /api/v1/products/` - Listar productos
- `POST /api/v1/products/` - Crear producto
- `GET /api/v1/products/{id}` - Obtener producto
- `PUT /api/v1/products/{id}` - Actualizar producto
- `DELETE /api/v1/products/{id}` - Eliminar producto

### Clientes
- `GET /api/v1/customers/` - Listar clientes
- `POST /api/v1/customers/` - Crear cliente
- `GET /api/v1/customers/{id}` - Obtener cliente
- `PUT /api/v1/customers/{id}` - Actualizar cliente
- `DELETE /api/v1/customers/{id}` - Eliminar cliente

### Ventas/Facturación
- `GET /api/v1/sales/` - Listar ventas
- `POST /api/v1/sales/` - Crear venta/factura
- `GET /api/v1/sales/{id}` - Obtener factura

### Tasa de Cambio
- `GET /api/v1/exchange-rate/` - Tasa actual
- `GET /api/v1/exchange-rate/bcv` - Obtener del BCV
- `POST /api/v1/exchange-rate/` - Establecer tasa manual
- `POST /api/v1/exchange-rate/refresh-bcv` - Refrescar del BCV

## Ejemplos de Uso

### Crear Usuario Administrador
```json
POST /api/v1/auth/register
{
  "username": "admin",
  "email": "admin@ferreteria.com",
  "full_name": "Administrador",
  "password": "secure_password",
  "role": "admin"
}
```

### Crear Producto
```json
POST /api/v1/products/
{
  "code": "MART-001",
  "name": "Martillo Acero 500g",
  "description": "Martillo de acero forjado",
  "category": "Herramientas Manuales",
  "brand": "Truper",
  "price_usd": 12.99,
  "stock_quantity": 50,
  "min_stock": 10,
  "unit_of_measure": "unidad",
  "iva_rate": 0.16,
  "is_exempt": false
}
```

### Crear Cliente
```json
POST /api/v1/customers/
{
  "rif": "V12345678",
  "name": "Juan Pérez",
  "email": "juan@email.com",
  "phone": "0412-1234567",
  "address": "Calle Principal #123",
  "customer_type": "natural"
}
```

### Crear Venta/Factura
```json
POST /api/v1/sales/
{
  "customer_id": 1,
  "payment_method": "punto",
  "payment_currency": "USD",
  "notes": "Venta mostrador",
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    },
    {
      "product_id": 2,
      "quantity": 1
    }
  ]
}
```

## Pruebas Unitarias

Ejecutar todas las pruebas:
```bash
pytest tests/ -v
```

Ejecutar con cobertura:
```bash
pytest tests/ -v --cov=app
```

## Configuración

Las variables de entorno se pueden configurar en un archivo `.env`:

```env
# App
APP_NAME="Ferretería Inventario & Facturación"
DEBUG=True

# Database
DATABASE_URL="sqlite+aiosqlite:///./ferreteria.db"

# Security
SECRET_KEY="tu_clave_secreta_muy_segura"
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# BCV
BCV_MAX_RETRIES=3
DEFAULT_RATE=36.5

# Currency
BASE_CURRENCY="USD"

# Impuestos
IGTF_RATE=0.03
IVA_GENERAL=0.16
```

## Consideraciones Fiscales (SENIAT)

### Providencia Administrativa SNAT/2015/0049
- Las facturas deben incluir código QR
- Numeración correlativa obligatoria
- Conservación de registros por 5 años

### IGTF (Impuesto a las Grandes Transacciones Financieras)
- Aplica 3% para pagos en moneda extranjera
- Calculado automáticamente cuando `payment_currency = "USD"`

### IVA
- General: 16%
- Reducido: 8% (alimentos, medicinas)
- Exento: 0% (productos básicos)

## Roadmap

### Fase 1 (Completada) ✅
- [x] Backend API REST
- [x] Modelos de base de datos
- [x] Autenticación JWT
- [x] CRUD completo
- [x] Integración BCV
- [x] Cálculo de impuestos
- [x] Pruebas unitarias

### Fase 2 (Pendiente)
- [ ] Frontend React
- [ ] Dashboard de estadísticas
- [ ] Reportes imprimibles
- [ ] Exportación Excel/PDF
- [ ] Backup automático

### Fase 3 (Futura)
- [ ] Multiusuario en red
- [ ] PostgreSQL para producción
- [ ] Módulo de compras
- [ ] Proveedores
- [ ] Códigos de barra

## Soporte

Para problemas o sugerencias, contactar al equipo de desarrollo.

## Licencia

Uso comercial restringido. Todos los derechos reservados.

---

**Versión**: 1.0.0  
**Última actualización**: 2025  
**Desarrollado para**: Ferreterías de Venezuela

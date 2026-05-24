# Sistema de Inventario y Facturación para Ferretería - Venezuela

Sistema profesional para la gestión de inventario y facturación de ferreterías, cumpliendo con las normativas fiscales venezolanas (SENIAT).

## 🚀 Características Principales

### ✅ Normativa Fiscal Venezolana
- **IVA**: Cálculo automático (16%, 8%, exento)
- **IGTF**: 3% para pagos en divisas
- **RIF**: Validación automática de clientes
- **Facturas**: Formato fiscal con código QR
- **Tasa BCV**: Actualización automática desde el Banco Central de Venezuela

### 💰 Sistema Bimonetario
- Precios base en USD
- Conversión automática a VES según tasa BCV
- Historial de tasas
- Alertas cuando falla la conexión al BCV (3 reintentos)

### 📦 Gestión de Inventario
- Múltiples unidades de medida
- Alertas de stock mínimo
- Movimientos auditados
- Categorización de productos

### 👥 Usuarios y Seguridad
- Roles: Administrador, Cajero, Almacénista
- Autenticación JWT
- Auditoría de acciones
- Contraseñas encriptadas

### 📱 Responsive Design
- Funciona en PC, tablet y móvil
- PWA (Progressive Web App)
- Interfaz moderna con TailwindCSS

## 🛠️ Stack Tecnológico

### Backend
- **Python 3.9+**
- **FastAPI** - API REST asíncrona
- **SQLAlchemy** - ORM asíncrono
- **SQLite** - Base de datos ( PostgreSQL/MySQL en producción)
- **PyJWT** - Autenticación
- **Bcrypt** - Encriptación de contraseñas

### Frontend
- **React 18**
- **Vite** - Build tool
- **TailwindCSS** - Estilos
- **React Router** - Navegación
- **Axios** - Cliente HTTP
- **Lucide React** - Iconos

## 📋 Instalación

### Requisitos Previos
- Python 3.9 o superior
- Node.js 18 o superior
- npm o yarn

### Backend

```bash
cd /workspace

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Iniciar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Copiar variables de entorno
cp src/.env.example src/.env

# Iniciar servidor de desarrollo
npm run dev

# Build para producción
npm run build
```

## 🔐 Credenciales por Defecto

```
Email: admin@ferreteria.com
Password: admin123
```

## 📡 Endpoints de la API

### Autenticación
- `POST /api/auth/register` - Registrar usuario
- `POST /api/auth/login` - Iniciar sesión
- `GET /api/auth/me` - Obtener usuario actual

### Productos
- `GET /api/products` - Listar productos
- `POST /api/products` - Crear producto
- `PUT /api/products/{id}` - Actualizar producto
- `DELETE /api/products/{id}` - Eliminar producto

### Clientes
- `GET /api/customers` - Listar clientes
- `POST /api/customers` - Crear cliente
- `GET /api/customers/validate-rif/{rif}` - Validar RIF

### Ventas
- `GET /api/sales` - Listar ventas
- `POST /api/sales` - Registrar venta
- `GET /api/sales/{id}/pdf` - Descargar factura PDF

### Tasa de Cambio
- `GET /api/exchange-rate/current` - Tasa actual
- `POST /api/exchange-rate/update-bcv` - Actualizar desde BCV
- `POST /api/exchange-rate/update` - Actualización manual
- `GET /api/exchange-rate/history` - Historial

## 🧪 Pruebas Unitarias

```bash
# Ejecutar pruebas del backend
pytest tests/ -v

# Con cobertura
pytest tests/ --cov=app --cov-report=html
```

## 📄 Estructura del Proyecto

```
/workspace
├── app/                      # Backend Python
│   ├── api/                  # Endpoints REST
│   ├── core/                 # Configuración y seguridad
│   ├── models/               # Modelos de datos
│   ├── services/             # Lógica de negocio
│   └── utils/                # Utilidades
├── frontend/                 # Frontend React
│   ├── src/
│   │   ├── components/       # Componentes UI
│   │   ├── context/          # Contextos React
│   │   ├── hooks/            # Hooks personalizados
│   │   ├── pages/            # Páginas
│   │   └── services/         # Servicios API
│   └── package.json
├── tests/                    # Pruebas unitarias
└── README.md
```

## ⚠️ Consideraciones Fiscales

### IVA (Impuesto al Valor Agregado)
- **General**: 16%
- **Reducida**: 8% (alimentos, medicinas)
- **Exento**: 0% (productos de primera necesidad)

### IGTF (Impuesto a las Grandes Transacciones Financieras)
- **3%** sobre el total cuando el pago se realiza en divisas

### Facturación
- Numeración correlativa obligatoria
- Código QR para validación fiscal
- Datos completos del emisor y receptor
- Desglose de impuestos

## 🔧 Configuración de Producción

### Variables de Entorno (Backend)
```bash
DATABASE_URL=sqlite:///./ferreteria.db
SECRET_KEY=tu_clave_secreta_muy_segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEFAULT_EXCHANGE_RATE=36.5
BCV_URL=https://www.bcv.org.ve
```

### Base de Datos
Para producción se recomienda:
- **PostgreSQL** para entornos multiusuario
- Configurar backups automáticos
- Índices en campos de búsqueda frecuente

## 📞 Soporte

Para soporte técnico o consultas sobre la implementación:
- Revisar la documentación de la API en `/docs` (Swagger UI)
- Verificar logs del sistema
- Contactar al administrador

## 📝 Licencia

Este software está diseñado para uso comercial en ferreterías venezolanas.
Cumple con las normativas del SENIAT vigentes en 2024.

---

**Desarrollado con ❤️ para las ferreterías de Venezuela**

# Ferretería Venezuela - Sistema de Inventario y Facturación

Sistema profesional para la gestión de inventario y facturación de ferreterías, cumpliendo con las normativas del SENIAT en Venezuela.

## 🚀 Características Principales

### Backend (Python/FastAPI)
- ✅ API RESTful asíncrona con FastAPI
- ✅ Base de datos SQLite con SQLAlchemy (async)
- ✅ Autenticación JWT con roles (Admin, Cajero, Inventario)
- ✅ Integración con tasa BCV (3 reintentos automáticos)
- ✅ Cálculo automático de IVA (16%) e IGTF (3%)
- ✅ Generación de facturas en PDF con código QR
- ✅ Auditoría completa de operaciones
- ✅ Alertas de stock bajo

### Frontend (React + Vite + TailwindCSS)
- ✅ Interfaz responsive (PC, tablet, móvil)
- ✅ Dashboard con estadísticas en tiempo real
- ✅ Punto de venta (POS) intuitivo
- ✅ Gestión de productos, clientes y facturas
- ✅ Notificaciones de alertas BCV
- ✅ Diseño moderno con TailwindCSS

## 📋 Requisitos Fiscales SENIAT

- ✅ Validación de RIF venezolano (V, E, J, G, P)
- ✅ Múltiples alícuotas de IVA (16%, reducidas, exentas)
- ✅ IGTF 3% para pagos en divisas
- ✅ Tasa de cambio BCV actualizada
- ✅ Facturas con formato fiscal y QR
- ✅ Numeración correlativa de facturas
- ✅ Registro de auditoría

## 🛠️ Instalación

### Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Ejecutar en desarrollo
npm run dev

# Construir para producción
npm run build
```

## 📁 Estructura del Proyecto

```
ferreteria_app/
├── backend/
│   ├── app/
│   │   ├── api/          # Rutas de la API
│   │   ├── core/         # Configuración y seguridad
│   │   ├── db/           # Configuración de base de datos
│   │   ├── models/       # Modelos SQLAlchemy
│   │   ├── schemas/      # Esquemas Pydantic
│   │   ├── services/     # Lógica de negocio
│   │   ├── utils/        # Utilidades (PDF, QR)
│   │   └── main.py       # Punto de entrada
│   ├── tests/            # Pruebas unitarias
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── components/   # Componentes React
    │   ├── pages/        # Páginas de la aplicación
    │   ├── store/        # Estado global (Zustand)
    │   └── App.jsx
    └── package.json
```

## 🔑 Endpoints Principales

### Autenticación
- `POST /api/v1/auth/register` - Registrar usuario
- `POST /api/v1/auth/login` - Iniciar sesión

### Productos
- `GET /api/v1/products` - Listar productos
- `POST /api/v1/products` - Crear producto
- `GET /api/v1/products/low-stock` - Alerta stock bajo

### Clientes
- `GET /api/v1/customers` - Listar clientes
- `POST /api/v1/customers` - Crear cliente (valida RIF)

### Facturas
- `POST /api/v1/invoices` - Crear factura
- `GET /api/v1/invoices` - Listar facturas

### Tasas de Cambio
- `GET /api/v1/exchange-rate/current` - Tasa actual
- `POST /api/v1/exchange-rate/update` - Actualizar desde BCV
- `GET /api/v1/system/init` - Inicializar sistema

## 🧪 Pruebas Unitarias

```bash
cd backend
pytest tests/test_api.py -v
```

Las pruebas incluyen:
- ✅ Registro y autenticación de usuarios
- ✅ CRUD de productos
- ✅ Validación de RIF
- ✅ Creación de facturas con IVA e IGTF
- ✅ Actualización de tasa BCV
- ✅ Alertas de stock bajo

## 💡 Uso del Sistema

1. **Inicialización**: Al iniciar, el sistema obtiene automáticamente la tasa del BCV con 3 reintentos. Si falla, usa una tasa de respaldo y muestra alerta.

2. **Moneda Base**: Todos los precios se manejan en USD. El sistema convierte a Bolívares usando la tasa BCV del día.

3. **Facturación**: 
   - Seleccione cliente (valida RIF)
   - Agregue productos
   - El sistema calcula automáticamente IVA (16%)
   - Si paga en divisas, aplica IGTF (3%)
   - Genere PDF con QR fiscal

4. **Inventario**: 
   - Configure stock mínimo por producto
   - Reciba alertas de productos bajos
   - Actualice stock automáticamente con cada venta

## 📄 Licencia

Este proyecto es de uso exclusivo para la ferretería especificada.

## 👨‍💻 Soporte

Para soporte técnico o personalizaciones, contacte al desarrollador.

---

**Nota**: Este sistema cumple con las normativas fiscales venezolanas vigentes. Mantenga siempre actualizada la tasa del BCV para garantizar la correcta facturación.

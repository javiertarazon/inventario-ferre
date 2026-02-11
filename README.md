# Sistema de Inventario Ferre-Exito

Sistema de gestión de inventario desarrollado con Flask, inspirado en Zoho Inventory, para INVERSIONES FERRE-EXITO, C.A.

## 🚀 Características Principales

### Fase 1 - Implementado ✅

- **Gestión de Productos**
  - CRUD completo de productos
  - Categorización jerárquica (Item Groups)
  - Puntos de reorden con alertas automáticas
  - Importación masiva desde Excel/CSV
  - Códigos de producto auto-generados

- **Gestión de Clientes**
  - Información completa de clientes
  - Límites de crédito
  - Direcciones de facturación y envío
  - Términos de pago personalizables

- **Órdenes de Venta**
  - Creación de órdenes con múltiples productos
  - Workflow de estados (Borrador → Confirmada → Enviada → Entregada)
  - Validación automática de stock
  - Reducción/restauración de inventario

- **Dashboard con Métricas**
  - KPIs de inventario en tiempo real
  - Métricas de ventas y clientes
  - Alertas de bajo stock
  - Gráficos de ventas (últimos 30 días)
  - Top productos más vendidos

- **Libro de Inventario Art 177**
  - Reporte completo según normativa venezolana
  - Exportación a Excel con formato oficial
  - Filtros por rango de fechas
  - Cálculo automático de entradas/salidas

- **Importación de Inventario**
  - Soporte para archivos XLSX, XLS y CSV
  - Detección automática de columnas
  - Creación y actualización masiva de productos
  - Reporte detallado de resultados

## 📋 Requisitos

- Python 3.8+
- SQLite (incluido)
- Navegador web moderno

## 🔧 Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/javiertarazon/inventario-ferre.git
cd inventario-ferre
```

2. Crear entorno virtual:
```bash
python -m venv .venv
```

3. Activar entorno virtual:
- Windows:
```bash
.venv\Scripts\activate
```
- Linux/Mac:
```bash
source .venv/bin/activate
```

4. Instalar dependencias:
```bash
pip install -r requirements.txt
```

5. Configurar variables de entorno:
```bash
copy .env.example .env
# Editar .env con tus configuraciones
```

6. Inicializar base de datos:
```bash
flask db upgrade
python create_db.py
```

7. Ejecutar aplicación:
```bash
python run_app.py
```

8. Acceder a: `http://127.0.0.1:5000`

**Credenciales por defecto:**
- Usuario: `admin`
- Contraseña: `admin`

## 📁 Estructura del Proyecto

```
inventario-ferre/
├── app/
│   ├── blueprints/          # Rutas y controladores
│   │   ├── main.py          # Rutas principales
│   │   ├── products.py      # Gestión de productos
│   │   ├── customers.py     # Gestión de clientes
│   │   ├── sales_orders.py  # Órdenes de venta
│   │   ├── item_groups.py   # Categorías
│   │   ├── suppliers.py     # Proveedores
│   │   └── movements.py     # Movimientos de inventario
│   ├── models/              # Modelos de datos
│   ├── repositories/        # Capa de acceso a datos
│   ├── services/            # Lógica de negocio
│   ├── templates/           # Plantillas HTML
│   ├── middleware/          # Middleware y manejo de errores
│   └── utils/               # Utilidades
├── migrations/              # Migraciones de base de datos
├── uploads/                 # Archivos cargados
├── backups/                 # Respaldos de base de datos
├── logs/                    # Archivos de log
└── requirements.txt         # Dependencias Python
```

## 🎯 Uso

### Importar Inventario

1. Ir a **Inventario → Importar Inventario**
2. Seleccionar archivo Excel o CSV
3. El archivo debe contener al menos:
   - Columna "Código" o "Code"
   - Columna "Descripción" o "Description"
4. Columnas opcionales: Stock, Precio
5. Click en "Importar Archivo"

### Generar Libro de Inventario

1. Ir a **Inventario → Libro de Inventario**
2. Seleccionar rango de fechas
3. Ver reporte en pantalla o exportar a Excel
4. El reporte cumple con Art 177 de la ley I.S.L.R

### Crear Orden de Venta

1. Ir a **Órdenes → Nueva Orden**
2. Seleccionar cliente
3. Agregar productos (múltiples)
4. Los precios se cargan automáticamente
5. Confirmar orden para reducir stock

### Configurar Puntos de Reorden

1. Ir a **Productos → Editar Producto**
2. Establecer "Punto de Reorden"
3. Establecer "Cantidad a Reordenar"
4. El sistema alertará cuando stock ≤ punto de reorden

## 🗺️ Roadmap

### Fase 2 - En Planificación
- Gestión de compras y órdenes de compra
- Múltiples almacenes
- Transferencias entre almacenes
- Ajustes de inventario

### Fase 3 - Futuro
- Integración con envíos
- Reportes avanzados
- API REST completa
- Aplicación móvil

Ver [ZOHO_INVENTORY_ROADMAP.md](ZOHO_INVENTORY_ROADMAP.md) para más detalles.

## 🛠️ Tecnologías

- **Backend:** Flask 3.0+
- **Base de Datos:** SQLite con SQLAlchemy
- **Frontend:** Bootstrap 5, Bootstrap Icons
- **Autenticación:** Flask-Login
- **Migraciones:** Flask-Migrate (Alembic)
- **Importación:** Pandas, OpenPyXL
- **Validación:** WTForms

## 📊 Arquitectura

El sistema sigue una arquitectura en capas:

1. **Presentación:** Templates Jinja2 + Bootstrap
2. **Controladores:** Flask Blueprints
3. **Servicios:** Lógica de negocio
4. **Repositorios:** Acceso a datos
5. **Modelos:** SQLAlchemy ORM

Patrones implementados:
- Repository Pattern
- Service Layer Pattern
- Soft Delete Pattern
- Blueprint Pattern

## 🔒 Seguridad

- Autenticación requerida en todas las rutas
- Bloqueo de cuenta tras intentos fallidos
- Soft delete para integridad referencial
- Validación de datos en múltiples capas
- Logs de auditoría

## 📝 Licencia

Este proyecto es privado y propiedad de INVERSIONES FERRE-EXITO, C.A.

## 👥 Autor

Desarrollado por Javier Tarazon para INVERSIONES FERRE-EXITO, C.A.

## 📞 Contacto

- **Empresa:** INVERSIONES FERRE-EXITO, C.A
- **RIF:** J31764195-7
- **Dirección:** Calle Bolívar. Palo Negro, Municipio Libertador. Estado Aragua
- **Teléfono:** 0412-7434522

## 🐛 Reportar Problemas

Para reportar problemas o sugerencias, crear un issue en GitHub.

## 📚 Documentación Adicional

- [FASE1_IMPLEMENTACION.md](FASE1_IMPLEMENTACION.md) - Detalles de implementación Fase 1
- [FASE1_BLUEPRINTS_TEMPLATES.md](FASE1_BLUEPRINTS_TEMPLATES.md) - Documentación de blueprints y templates
- [SISTEMA_FUNCIONAL.md](SISTEMA_FUNCIONAL.md) - Estado funcional del sistema
- [ZOHO_INVENTORY_ROADMAP.md](ZOHO_INVENTORY_ROADMAP.md) - Roadmap completo

---

**Versión:** 1.0.0  
**Última actualización:** Febrero 2026

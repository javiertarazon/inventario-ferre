# Changelog - Sistema de Inventario Ferre-Exito

Todos los cambios notables en este proyecto serán documentados en este archivo.

## [1.3.0] - 2026-03-07

### ✨ Nuevas Funcionalidades

- **Carga histórica de tasa BCV**
  - Nuevo proceso de backfill desde archivos históricos XLS publicados por el BCV.
  - Cobertura automática de sábados, domingos y feriados usando la fecha valor publicada por BCV.
  - Nuevo script operativo `scripts/backfill_bcv_history.py`.

- **Historial de tasa cambiaria con búsqueda y paginación**
  - El módulo de precios ahora permite buscar tasas por fecha exacta.
  - Se agregó paginación del historial para facilitar revisión de grandes volúmenes de tasas.

### 🐛 Correcciones

- **Histórico BCV utilizable en operación real**
  - El servicio de tasas ahora soporta reconstrucción histórica persistente en la base local.
  - Se verificó la cobertura completa del rango solicitado desde `2025-08-01` hasta `2026-03-06`.

### 🧪 Tests Agregados o Actualizados

- `tests/test_exchange_rate_service.py`
  - Parser histórico BCV
  - Cobertura de sábados, domingos y feriados
- `tests/test_pricing_blueprint.py`
  - Buscador por fecha del historial
  - Paginación del historial de tasas

### 📚 Documentación

- Documento de release agregado en `docs/reportes/RELEASE_1.3.0.md`.
- README actualizado con capacidades nuevas del histórico BCV y consulta del historial.

## [1.2.0] - 2026-03-07

### ✨ Nuevas Funcionalidades

- **Configuración editable de empresa**
  - Nuevo módulo para administrar razón social, RIF, dirección fiscal, teléfono y correo.
  - Contexto global de empresa disponible en reportes y plantillas.

- **Automatización diaria de tasa BCV**
  - Servicio dedicado para sincronizar tasa USD del BCV.
  - Integración desde interfaz web, comando CLI y script programable para Windows.
  - Soporte para fallback SSL controlado por configuración del entorno.

- **Historial de compras por factura y proveedor**
  - Nuevos modelos de facturas de compra y líneas históricas por producto.
  - Registro manual e importación CSV/XLSX desde el nuevo módulo de compras.
  - Actualización automática de stock con movimientos de entrada al registrar compras.

- **Fecha inicial de inventario por producto**
  - Campo persistente de fecha de entrada inicial con valor de arranque `2024-08-01`.
  - Integración en validación, formularios web, esquemas y servicios.

- **Cierres diarios con reconstrucción de salidas 60/40**
  - Nuevo módulo para registrar o importar cierres diarios de ventas.
  - Reconstrucción estimada de salidas por producto usando peso del inventario disponible.
  - Trazabilidad entre cierre diario, asignaciones reconstruidas y movimientos `SALIDA` generados.

- **Búsqueda global API v1**
  - Endpoint adicional de búsqueda para apoyar navegación y localización rápida de entidades.

### 🐛 Correcciones

- **Buscador de precios estabilizado**
  - Se eliminó conflicto entre el contenedor del buscador global y el buscador del módulo de precios.
  - Se reforzó la autenticación del endpoint JSON de búsqueda.

- **Sincronización BCV adaptada al entorno real**
  - Ajuste del parser al HTML actual del BCV.
  - Corrección del entry point para ejecución externa en scripts programados.

- **Importación y normalización de inventario**
  - Mejoras en generación de códigos válidos.
  - Evitada recreación de duplicados por descripciones equivalentes.
  - Scripts de deduplicación y normalización para productos afectados por factor `1.25`.

### 🧪 Tests Agregados

- `tests/test_company_settings.py`
- `tests/test_exchange_rate_service.py`
- `tests/test_pricing_blueprint.py`
- `tests/test_purchase_invoice_service.py`
- `tests/test_purchase_invoice_blueprint.py`

### 🗃️ Migraciones

- `6d5f1c8a2e71_add_company_settings_table_and_rate_precision.py`
- `9c0d1f4a7b22_add_inventory_entry_date_and_purchase_history.py`
- `b17f2c6d91aa_add_daily_sales_closures.py`

### 📚 Documentación

- Documento de release agregado en `docs/reportes/RELEASE_1.2.0.md`.
- README actualizado con resumen de capacidades nuevas del sistema.

### 📊 Estado de la Entrega

- ✅ Módulo de empresa operativo
- ✅ Sincronización BCV automatizable
- ✅ Compras históricas por factura/proveedor
- ✅ Cierres diarios con reconstrucción 60/40
- ✅ Versión preparada para commit y publicación remota

## [1.1] - 2026-02-11

### 🐛 Correcciones

- **Fix crítico**: Las categorías ahora se muestran correctamente en el listado de productos después de editar
  - Agregado eager loading con `joinedload` para relaciones `item_group` y `proveedor`
  - Agregado `db.session.refresh()` después de actualizar productos
  - Documentado en `FIX_CATEGORIA_PRODUCTOS.md`

- **Fix crítico**: Corregido error "unsupported operand type(s) for *: 'decimal.Decimal' and 'float'"
  - Agregado filtro `|float` en templates Jinja2 para conversión de Decimal
  - Documentado en `FIX_DECIMAL_FLOAT_ERROR.md`

### ✨ Nuevas Funcionalidades

- **Sistema de generación automática de códigos de productos**
  - Formato: `{CATEGORIA}-{PALABRA1}-{PALABRA2}-{SECUENCIA}`
  - Ejemplo: `E-SO-PO-01` (Electricidad - Socates Porcelana)
  - Implementado en `app/utils/code_generator.py`
  - 793 productos con códigos regenerados automáticamente

- **Sistema de categorías mejorado**
  - 7 categorías creadas: Electricidad, Plomería, Albañilería, Carpintería, Herrería, Tornillería, Misceláneos
  - Cada categoría con color e icono personalizado
  - Badges visuales en listado de productos

### 📚 Documentación

- **INFORME_PRODUCCION.md** (40+ páginas)
  - Arquitectura completa del sistema
  - Requisitos de hardware y software
  - 3 opciones de despliegue (local, nube, híbrido)
  - Guía de instalación paso a paso
  - Configuración de seguridad
  - Sistema de respaldos
  - Estimación de costos

- **RESUMEN_EJECUTIVO_PRODUCCION.md**
  - Resumen ejecutivo para toma de decisiones
  - Comparativa de opciones de despliegue
  - Costos detallados

- **CHECKLIST_INSTALACION.md**
  - Lista de verificación de 10 fases
  - Checklist de seguridad

- **README_PRODUCCION.md**
  - Guía rápida de instalación
  - Comandos esenciales

- **SISTEMA_CODIGOS_AUTOMATICOS.md**
  - Documentación del sistema de códigos
  - Ejemplos y casos de uso

### 🔧 Scripts de Producción

- **gunicorn_config.py** - Configuración del servidor WSGI
- **create_admin.py** - Script interactivo para crear usuario administrador
- **backup.sh** - Script de respaldo automático para Linux
- **backup.bat** - Script de respaldo automático para Windows
- **create_categories.py** - Script para crear categorías iniciales
- **regenerate_codes.py** - Script para regenerar códigos de productos existentes

### 🚀 Mejoras de Rendimiento

- Eager loading para evitar problema N+1 de consultas
- Optimización de consultas en `ProductRepository`
- Carga anticipada de relaciones `item_group` y `proveedor`

### 🧪 Tests Agregados

- `test_products_view.py` - Tests de vista de productos
- `test_decimal_fix.py` - Tests de corrección Decimal
- `test_products_integration.py` - Tests de integración
- `test_code_generation.py` - Tests de generación de códigos
- `test_item_group_relation.py` - Tests de relación con categorías

### 📊 Estado del Sistema

- ✅ **LISTO PARA PRODUCCIÓN**
- 793 productos cargados con códigos regenerados
- 7 categorías configuradas
- Tasa de cambio actual: 388.74 Bs/$
- Base de datos: SQLite en `instance/inventario.db`
- Servidor: http://127.0.0.1:5000
- Credenciales: admin/admin

### 🔐 Seguridad

- Autenticación de usuarios implementada
- Protección CSRF habilitada
- Contraseñas encriptadas con bcrypt
- Soft deletes para auditoría
- Campos de auditoría (created_by, updated_by, created_at, updated_at)

### 📦 Archivos Modificados

**Modelos:**
- `app/models/product.py` - Relaciones mejoradas

**Repositorios:**
- `app/repositories/product_repository.py` - Eager loading agregado

**Servicios:**
- `app/services/product_service.py` - Refresh después de actualizar
- `app/services/import_service.py` - Generación automática de códigos

**Blueprints:**
- `app/blueprints/products.py` - Manejo mejorado de categorías

**Templates:**
- `app/templates/productos.html` - Filtro |float para Decimal

**Utilidades:**
- `app/utils/code_generator.py` - Nuevo módulo

### 🎯 Próximos Pasos Sugeridos

1. Configurar servidor de producción
2. Implementar respaldos automáticos
3. Configurar SSL/HTTPS
4. Capacitar usuarios
5. Migrar datos de producción

---

## [1.0] - 2026-02-10

### Versión Inicial

- Sistema básico de inventario funcional
- CRUD de productos, proveedores, clientes
- Sistema de movimientos
- Órdenes de venta
- Sistema de precios con tasa de cambio
- Reportes básicos
- Importación desde Excel

---

**Formato del Changelog basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/)**

**Versionado basado en [Semantic Versioning](https://semver.org/lang/es/)**

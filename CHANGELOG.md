# Changelog - Sistema de Inventario Ferre-Exito

Todos los cambios notables en este proyecto serán documentados en este archivo.

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

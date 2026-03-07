# Release 1.2.0

Fecha: 2026-03-07

## Resumen Ejecutivo

La versión 1.2.0 consolida la transición del sistema desde un inventario base hacia una operación diaria más cercana al negocio real de la ferretería. Esta entrega incorpora configuración fiscal de empresa, automatización de tasa BCV, historial de compras por factura/proveedor y cierres diarios con reconstrucción estimada de salidas bajo la regla 60/40.

## Mejoras Incluidas

### 1. Configuración de empresa

- Módulo administrativo para editar nombre, RIF, dirección fiscal, teléfono y correo.
- Reutilización automática de estos datos en reportes y plantillas.

### 2. Tasa BCV automatizada

- Servicio de sincronización BCV desde interfaz, CLI y script programable.
- Wrapper para Windows Task Scheduler.
- Manejo de compatibilidad SSL y parser adaptado al HTML real del BCV.

### 3. Historial de compras

- Nuevos modelos para facturas de compra y líneas históricas.
- Registro manual de facturas desde la web.
- Importación de facturas CSV/XLSX.
- Generación automática de movimientos de entrada y actualización de stock.

### 4. Fecha inicial de inventario

- Campo persistente por producto con fecha de arranque predeterminada `2024-08-01`.

### 5. Cierres diarios y reconstrucción 60/40

- Nuevo módulo de cierres diarios con registro manual e importación.
- Reconstrucción estimada de salidas por producto basada en el inventario disponible.
- Trazabilidad entre cierre, asignaciones y movimientos de salida generados.

### 6. Estabilización técnica adicional

- Corrección del buscador del módulo de precios.
- Normalización y deduplicación de productos afectados por reglas previas de factor de ajuste.
- Endpoints API de búsqueda integrados al paquete v1.

## Archivos Clave de la Entrega

- `app/services/exchange_rate_service.py`
- `app/services/company_settings_service.py`
- `app/services/purchase_invoice_service.py`
- `app/services/daily_sales_closure_service.py`
- `app/blueprints/settings.py`
- `app/blueprints/purchases.py`
- `app/blueprints/daily_closures.py`
- `migrations/versions/6d5f1c8a2e71_add_company_settings_table_and_rate_precision.py`
- `migrations/versions/9c0d1f4a7b22_add_inventory_entry_date_and_purchase_history.py`
- `migrations/versions/b17f2c6d91aa_add_daily_sales_closures.py`

## Impacto Operativo

- Mejora el control administrativo y fiscal del sistema.
- Reduce trabajo manual en actualización de tasa BCV.
- Conserva historial real de costos por proveedor y factura.
- Permite aproximar salidas diarias aunque no exista desglose detallado por producto en el cierre de ventas.

## Pendientes Recomendados

1. Ejecutar pruebas funcionales completas de compras y cierres diarios con datos reales.
2. Publicar reportes fiscales enriquecidos tipo SENIAT sobre compras y cierres.
3. Evaluar futura carga desde imágenes/OCR de facturas.
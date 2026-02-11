# Instrucciones para agentes IA (ferreteria inventario)

## Visión general del proyecto
- App web Flask monolítica: rutas en [app.py](app.py), modelos SQLAlchemy en [models.py](models.py), vistas en templates/.
- Persistencia con SQLite en una ruta fija de Windows: d:/javie/ferreteria inventario/inventario.db (config en [app.py](app.py)).
- Flujos principales:
  - CRUD de productos/proveedores y movimientos de inventario (entradas/salidas) via rutas Flask.
  - Cierres diarios con `CierreDia` y marca `Movimiento.cerrado`.
  - Exportación a Excel con pandas/openpyxl.

## Estructura y patrones clave
- Código de producto:
  - Validación manual por formulario (rubro 1 letra, iniciales 2 letras, número 2 dígitos) con `generar_codigo()`.
  - Generación automática desde categoría + descripción con `generar_codigo_auto()` y prefijo `R-XX-##`.
- Modelos y relaciones:
  - `Producto` ↔ `Proveedor` (FK) y `Producto` ↔ `Movimiento` (backref). Ver [models.py](models.py).
- Inventario diario:
  - Filtro por fecha con `db.func.date(Movimiento.fecha)` y vista combinada en `inventario_diario.html`.

## Workflows útiles
- Instalar dependencias: `pip install flask sqlalchemy pandas openpyxl` (ver [README.md](README.md)).
- Ejecutar app: `python app.py` (inicializa tablas con `db.create_all()` y usa `debug=True`).
- Crear BD explícita: `python create_db.py`.
- Migraciones manuales SQLite:
  - `python update_db.py` agrega columnas/cierre_dia.
  - `python fix_proveedor_cols.py` corrige columnas en dos rutas posibles de DB.
  - Al cambiar modelos SQLAlchemy (agregar/renombrar columnas), actualizar [update_db.py](update_db.py) para renombrar o agregar columnas en SQLite usando ALTER TABLE RENAME COLUMN o ADD COLUMN. Ejecutar `python update_db.py` antes de reiniciar la app para evitar errores de metadatos SQLAlchemy. No cambiar nombres de columnas sin migrar la DB.

## Integraciones y archivos relevantes
- Excel:
  - Importación fija desde `Inventario Ferre-Exito.xlsx` en `importar_excel`.
  - Exportación diaria/completa genera .xlsx en el cwd.
- Plantillas HTML: ver templates/ (base + páginas específicas como productos, movimientos, inventario).

## Convenciones locales a respetar
- Mantener mensajes `flash()` en español y rutas/nombres de vistas en español.
- Evitar cambiar la ruta del SQLite sin revisar scripts auxiliares ([update_db.py](update_db.py), [fix_proveedor_cols.py](fix_proveedor_cols.py)).
- La lógica de stock se ajusta en la ruta `/movimientos` (entrada suma, salida resta).

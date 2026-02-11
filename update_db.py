import sqlite3

DB_PATH = "d:/javie/ferreteria inventario/inventario.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("PRAGMA table_info(producto)")
columns = {row[1] for row in cur.fetchall()}

if "costo" in columns and "precio_dolares" not in columns:
    cur.execute("ALTER TABLE producto RENAME COLUMN costo TO precio_dolares")

if "factor_cambiario" in columns and "factor_ajuste" not in columns:
    cur.execute("ALTER TABLE producto RENAME COLUMN factor_cambiario TO factor_ajuste")

# Si no existen, agregar con defaults
if "precio_dolares" not in columns:
    cur.execute("ALTER TABLE producto ADD COLUMN precio_dolares REAL DEFAULT 0.0")

if "factor_ajuste" not in columns:
    cur.execute("ALTER TABLE producto ADD COLUMN factor_ajuste REAL DEFAULT 1.0")

cur.execute("PRAGMA table_info(movimiento)")
mov_columns = {row[1] for row in cur.fetchall()}
if "cerrado" not in mov_columns:
    cur.execute("ALTER TABLE movimiento ADD COLUMN cerrado INTEGER DEFAULT 0")

cur.execute("PRAGMA table_info(proveedor)")
prov_columns = {row[1] for row in cur.fetchall()}
if "rif" not in prov_columns:
    cur.execute("ALTER TABLE proveedor ADD COLUMN rif TEXT DEFAULT ''")
if "rubro_material" not in prov_columns:
    cur.execute("ALTER TABLE proveedor ADD COLUMN rubro_material TEXT DEFAULT ''")

cur.execute(
    "CREATE TABLE IF NOT EXISTS configuracion ("
    "id INTEGER PRIMARY KEY, "
    "tasa_cambiaria REAL NOT NULL DEFAULT 1.0, "
    "factor_ajuste REAL NOT NULL DEFAULT 1.0"
    ")"
)

conn.commit()
conn.close()

print("Migración completada")

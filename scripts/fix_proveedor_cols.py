import sqlite3

paths = [
    "d:/javie/ferreteria inventario/inventario.db",
    "d:/javie/ferreteria inventario/instance/inventario.db",
]

for p in paths:
    conn = sqlite3.connect(p)
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(proveedor)")
    cols = {c[1] for c in cur.fetchall()}
    if "rif" not in cols:
        cur.execute("ALTER TABLE proveedor ADD COLUMN rif TEXT DEFAULT ''")
    if "rubro_material" not in cols:
        cur.execute("ALTER TABLE proveedor ADD COLUMN rubro_material TEXT DEFAULT ''")
    conn.commit()
    conn.close()
    print("updated", p)

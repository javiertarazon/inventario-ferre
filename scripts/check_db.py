import sqlite3

DB_PATH = "d:/javie/ferreteria inventario/inventario.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("PRAGMA table_info(producto)")
print(cur.fetchall())
conn.close()

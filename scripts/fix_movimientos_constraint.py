"""
Fix movimientos table constraint to accept uppercase and AJUSTE type.
"""
from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    try:
        print("Fixing movimientos table constraint...")
        
        # SQLite doesn't support ALTER TABLE to modify constraints
        # We need to recreate the table
        
        # 1. Create new table with correct constraint
        db.session.execute(db.text("""
            CREATE TABLE movimientos_new (
                id INTEGER NOT NULL,
                producto_id INTEGER NOT NULL,
                tipo VARCHAR(20) NOT NULL,
                cantidad INTEGER NOT NULL,
                fecha DATE NOT NULL,
                descripcion TEXT,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                created_by INTEGER,
                updated_by INTEGER,
                deleted_at DATETIME,
                PRIMARY KEY (id),
                CONSTRAINT check_cantidad_positive CHECK (cantidad > 0),
                CONSTRAINT check_tipo_valid CHECK (tipo IN ('ENTRADA', 'SALIDA', 'AJUSTE', 'entrada', 'salida', 'ajuste')),
                FOREIGN KEY(producto_id) REFERENCES products (id),
                FOREIGN KEY(created_by) REFERENCES users (id),
                FOREIGN KEY(updated_by) REFERENCES users (id)
            )
        """))
        print("✓ Created new table with correct constraint")
        
        # 2. Copy data from old table
        db.session.execute(db.text("""
            INSERT INTO movimientos_new 
            SELECT * FROM movimientos
        """))
        print("✓ Copied data from old table")
        
        # 3. Drop old table
        db.session.execute(db.text("DROP TABLE movimientos"))
        print("✓ Dropped old table")
        
        # 4. Rename new table
        db.session.execute(db.text("ALTER TABLE movimientos_new RENAME TO movimientos"))
        print("✓ Renamed new table")
        
        # 5. Recreate indexes
        db.session.execute(db.text("""
            CREATE INDEX idx_movimientos_producto_id ON movimientos (producto_id)
        """))
        db.session.execute(db.text("""
            CREATE INDEX idx_movimientos_tipo ON movimientos (tipo)
        """))
        db.session.execute(db.text("""
            CREATE INDEX idx_movimientos_fecha ON movimientos (fecha)
        """))
        db.session.execute(db.text("""
            CREATE INDEX idx_movement_product_date ON movimientos (producto_id, fecha)
        """))
        print("✓ Recreated indexes")
        
        # Commit changes
        db.session.commit()
        print("\n✅ Movimientos table constraint fixed successfully!")
        
        # Verify
        result = db.session.execute(db.text("SELECT sql FROM sqlite_master WHERE type='table' AND name='movimientos'"))
        schema = result.fetchone()[0]
        print("\nNew schema:")
        print(schema)
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

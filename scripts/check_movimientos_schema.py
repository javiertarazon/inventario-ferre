"""Check movimientos table schema."""
from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    result = db.session.execute(db.text("SELECT sql FROM sqlite_master WHERE type='table' AND name='movimientos'"))
    schema = result.fetchone()[0]
    print("Movimientos table schema:")
    print(schema)

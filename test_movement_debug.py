"""
Debug script to test movement creation and see exact error.
"""
import sys
from datetime import date
from app import create_app
from app.services import MovementService
from app.extensions import db

app = create_app()

with app.app_context():
    try:
        # Test data
        data = {
            'tipo': 'ENTRADA',
            'producto_id': 1,
            'cantidad': 10,
            'descripcion': 'Test movement',
            'fecha': date.today()
        }
        
        print("Creating movement with data:")
        print(data)
        print()
        
        movement_service = MovementService()
        movement = movement_service.create_movement(data, user_id=1)
        
        print("Movement created successfully!")
        print(f"ID: {movement.id}")
        print(f"Tipo: {movement.tipo}")
        print(f"Cantidad: {movement.cantidad}")
        print(f"Producto ID: {movement.producto_id}")
        
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

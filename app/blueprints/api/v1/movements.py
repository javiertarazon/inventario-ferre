"""
API v1 movements routes.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from datetime import date
from app.extensions import db
from app.models import Movimiento, Product
from app.services.movement_service import MovementService
from app.schemas.movement_api_schema import (
    MovementCreateSchema, MovementResponseSchema, MovementListSchema
)
from app.utils.exceptions import ValidationError as AppValidationError, NotFoundError

movements_bp = Blueprint('api_movements', __name__, url_prefix='/api/v1/movements')

# Initialize schemas and services
movement_create_schema = MovementCreateSchema()
movement_response_schema = MovementResponseSchema()
movement_list_schema = MovementListSchema()
movement_service = MovementService()


@movements_bp.route('', methods=['GET'])
@jwt_required()
def list_movements():
    """
    List all inventory movements with pagination.
    
    Query Parameters:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 20, max: 100)
        - tipo: Filter by movement type (ENTRADA, SALIDA, AJUSTE, DEVOLUCION)
        - producto_id: Filter by product ID
        - sort: Field to sort by (default: fecha)
        - order: asc or desc (default: desc)
    
    ---
    get:
      tags:
        - Movements
      summary: List inventory movements
      security:
        - bearerAuth: []
      responses:
        200:
          description: List of movements
        401:
          description: Unauthorized
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        tipo = request.args.get('tipo', '', type=str).upper()
        producto_id = request.args.get('producto_id', None, type=int)
        
        # Validate pagination
        if per_page > 100:
            per_page = 100
        if page < 1:
            page = 1
        
        # Build query
        query = db.session.query(Movimiento)
        
        # Apply filters
        if tipo:
            query = query.filter(Movimiento.tipo == tipo)
        if producto_id:
            query = query.filter(Movimiento.producto_id == producto_id)
        
        # Get total and paginate
        total = query.count()
        movements = query.order_by(Movimiento.fecha.desc()).offset((page - 1) * per_page).limit(per_page).all()
        
        # Prepare response
        items = movement_response_schema.dump(movements, many=True)
        response = {
            'items': items,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@movements_bp.route('/<int:movement_id>', methods=['GET'])
@jwt_required()
def get_movement(movement_id):
    """
    Get a specific movement by ID.
    
    ---
    get:
      tags:
        - Movements
      summary: Get movement by ID
      security:
        - bearerAuth: []
      parameters:
        - in: path
          name: movement_id
          schema:
            type: integer
      responses:
        200:
          description: Movement details
        404:
          description: Movement not found
    """
    try:
        movement = Movimiento.query.get(movement_id)
        
        if not movement:
            return jsonify({'error': 'Movimiento no encontrado'}), 404
        
        return jsonify(movement_response_schema.dump(movement)), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@movements_bp.route('', methods=['POST'])
@jwt_required()
def create_movement():
    """
    Create a new inventory movement.
    
    ---
    post:
      tags:
        - Movements
      summary: Create movement
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                producto_id:
                  type: integer
                tipo:
                  type: string
                  enum: [ENTRADA, SALIDA, AJUSTE, DEVOLUCION]
                cantidad:
                  type: integer
                referencia:
                  type: string
                razon:
                  type: string
      responses:
        201:
          description: Movement created
        400:
          description: Validation error
    """
    try:
        data = movement_create_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'errors': err.messages}), 400
    
    try:
        user_id = get_jwt_identity()
        
        # Verify product exists
        product = Product.query.get(data.get('producto_id'))
        if not product:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        # Create movement
        movement = Movimiento(
            producto_id=data.get('producto_id'),
            tipo=data.get('tipo').upper(),
            cantidad=data.get('cantidad'),
            fecha=date.today(),
            descripcion=data.get('razon'),
            created_by=int(user_id)
        )
        
        db.session.add(movement)
        db.session.commit()
        
        return jsonify(movement_response_schema.dump(movement)), 201
        
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'errors': err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@movements_bp.route('/<int:movement_id>', methods=['PUT'])
@jwt_required()
def update_movement(movement_id):
    """
    Update an existing movement.
    
    ---
    put:
      tags:
        - Movements
      summary: Update movement
      security:
        - bearerAuth: []
      parameters:
        - in: path
          name: movement_id
          schema:
            type: integer
      responses:
        200:
          description: Movement updated
        404:
          description: Movement not found
    """
    try:
        movement = Movimiento.query.get(movement_id)
        
        if not movement:
            return jsonify({'error': 'Movimiento no encontrado'}), 404
        
        data = movement_create_schema.load(request.get_json(), partial=True)
        
        # Update fields
        if 'tipo' in data:
            movement.tipo = data['tipo'].upper()
        if 'cantidad' in data:
            movement.cantidad = data['cantidad']
        if 'razon' in data:
            movement.descripcion = data['razon']
        
        user_id = get_jwt_identity()
        movement.updated_by = int(user_id)
        
        db.session.commit()
        
        return jsonify(movement_response_schema.dump(movement)), 200
        
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'errors': err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@movements_bp.route('/<int:movement_id>', methods=['DELETE'])
@jwt_required()
def delete_movement(movement_id):
    """
    Delete a movement (soft delete).
    
    ---
    delete:
      tags:
        - Movements
      summary: Delete movement
      security:
        - bearerAuth: []
      parameters:
        - in: path
          name: movement_id
          schema:
            type: integer
      responses:
        204:
          description: Movement deleted
        404:
          description: Movement not found
    """
    try:
        movement = Movimiento.query.get(movement_id)
        
        if not movement:
            return jsonify({'error': 'Movimiento no encontrado'}), 404
        
        # Soft delete
        from datetime import datetime
        movement.deleted_at = datetime.utcnow()
        db.session.commit()
        
        return '', 204
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

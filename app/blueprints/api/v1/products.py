"""
API v1 products routes.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from app.extensions import db
from app.models import Product
from app.repositories import ProductRepository
from app.services.product_service import ProductService
from app.schemas.product_api_schema import (
    ProductCreateSchema, ProductUpdateSchema, ProductResponseSchema, ProductListSchema
)
from app.utils.exceptions import ValidationError as AppValidationError, NotFoundError

products_bp = Blueprint('api_products', __name__, url_prefix='/api/v1/products')

# Initialize schemas and services
product_create_schema = ProductCreateSchema()
product_update_schema = ProductUpdateSchema()
product_response_schema = ProductResponseSchema()
product_list_schema = ProductListSchema()
product_service = ProductService()


@products_bp.route('', methods=['GET'])
@jwt_required()
def list_products():
    """
    List all products with pagination.
    
    Query Parameters:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 20, max: 100)
        - search: Search term for code or description
        - sort: Field to sort by (default: codigo)
        - order: asc or desc (default: asc)
    
    ---
    get:
      tags:
        - Products
      summary: List products
      security:
        - bearerAuth: []
      parameters:
        - in: query
          name: page
          schema:
            type: integer
            default: 1
        - in: query
          name: per_page
          schema:
            type: integer
            default: 20
        - in: query
          name: search
          schema:
            type: string
      responses:
        200:
          description: List of products
        401:
          description: Unauthorized
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '', type=str)
        
        # Validate pagination
        if per_page > 100:
            per_page = 100
        if page < 1:
            page = 1
        
        # Get products from repository
        repo = ProductRepository()
        
        if search:
            # Search products by code or description
            query = db.session.query(Product).filter(
                (Product.codigo.ilike(f'%{search}%')) |
                (Product.descripcion.ilike(f'%{search}%'))
            )
        else:
            query = db.session.query(Product)
        
        # Paginate
        total = query.count()
        products = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # Prepare response
        items = product_response_schema.dump(products, many=True)
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


@products_bp.route('/<int:product_id>', methods=['GET'])
@jwt_required()
def get_product(product_id):
    """
    Get a specific product by ID.
    
    ---
    get:
      tags:
        - Products
      summary: Get product by ID
      security:
        - bearerAuth: []
      parameters:
        - in: path
          name: product_id
          required: true
          schema:
            type: integer
      responses:
        200:
          description: Product details
        404:
          description: Product not found
        401:
          description: Unauthorized
    """
    try:
        product = Product.query.get(product_id)
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        return jsonify(product_response_schema.dump(product)), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@products_bp.route('', methods=['POST'])
@jwt_required()
def create_product():
    """
    Create a new product.
    
    ---
    post:
      tags:
        - Products
      summary: Create product
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                codigo:
                  type: string
                  example: "A-BC-01"
                descripcion:
                  type: string
                  example: "Taladro eléctrico"
                stock:
                  type: integer
                  default: 0
                precio_dolares:
                  type: number
                  example: 25.50
      responses:
        201:
          description: Product created
        400:
          description: Validation error
        401:
          description: Unauthorized
    """
    try:
        # Validate request data
        data = product_create_schema.load(request.get_json())
        user_id = get_jwt_identity()
        
        # Create product using service
        product = product_service.create_product(data, user_id)
        
        return jsonify(product_response_schema.dump(product)), 201
        
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    except AppValidationError as err:
        return jsonify({'error': str(err)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@products_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    """
    Update a product.
    
    ---
    put:
      tags:
        - Products
      summary: Update product
      security:
        - bearerAuth: []
      parameters:
        - in: path
          name: product_id
          required: true
          schema:
            type: integer
      responses:
        200:
          description: Product updated
        404:
          description: Product not found
        401:
          description: Unauthorized
    """
    try:
        product = Product.query.get(product_id)
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Validate request data
        data = product_update_schema.load(request.get_json())
        user_id = get_jwt_identity()
        
        # Update product
        updated_product = product_service.update_product(product_id, data, user_id)
        
        return jsonify(product_response_schema.dump(updated_product)), 200
        
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    except AppValidationError as err:
        return jsonify({'error': str(err)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@products_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    """
    Delete a product.
    
    ---
    delete:
      tags:
        - Products
      summary: Delete product
      security:
        - bearerAuth: []
      parameters:
        - in: path
          name: product_id
          required: true
          schema:
            type: integer
      responses:
        204:
          description: Product deleted
        404:
          description: Product not found
        401:
          description: Unauthorized
    """
    try:
        product = Product.query.get(product_id)
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        user_id = get_jwt_identity()
        product_service.delete_product(product_id, user_id)
        
        return '', 204
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

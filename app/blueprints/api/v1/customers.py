"""
API v1 customers routes.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from app.extensions import db
from app.models import Customer
from app.services.customer_service import CustomerService
from app.schemas.customer_api_schema import (
    CustomerCreateSchema, CustomerUpdateSchema, CustomerResponseSchema, CustomerListSchema
)
from app.utils.exceptions import ValidationError as AppValidationError, NotFoundError

customers_bp = Blueprint('api_customers', __name__, url_prefix='/api/v1/customers')

# Initialize schemas and services
customer_create_schema = CustomerCreateSchema()
customer_update_schema = CustomerUpdateSchema()
customer_response_schema = CustomerResponseSchema()
customer_list_schema = CustomerListSchema()
customer_service = CustomerService()


@customers_bp.route('', methods=['GET'])
@jwt_required()
def list_customers():
    """
    List all customers with pagination.
    
    Query Parameters:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 20, max: 100)
        - search: Search term for name or email
        - sort: Field to sort by (default: nombre)
        - order: asc or desc (default: asc)
    
    ---
    get:
      tags:
        - Customers
      summary: List customers
      security:
        - bearerAuth: []
      responses:
        200:
          description: List of customers
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
        
        # Build query
        query = db.session.query(Customer).filter(Customer.is_active == True)
        
        if search:
            query = query.filter(
                (Customer.nombre.ilike(f'%{search}%')) |
                (Customer.apellido.ilike(f'%{search}%')) |
                (Customer.email.ilike(f'%{search}%'))
            )
        
        # Get total and paginate
        total = query.count()
        customers = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # Prepare response
        items = customer_response_schema.dump(customers, many=True)
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


@customers_bp.route('/<int:customer_id>', methods=['GET'])
@jwt_required()
def get_customer(customer_id):
    """
    Get a specific customer by ID.
    
    ---
    get:
      tags:
        - Customers
      summary: Get customer by ID
      security:
        - bearerAuth: []
      responses:
        200:
          description: Customer details
        404:
          description: Customer not found
    """
    try:
        customer = Customer.query.filter_by(id=customer_id, is_active=True).first()
        
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        return jsonify(customer_response_schema.dump(customer)), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@customers_bp.route('', methods=['POST'])
@jwt_required()
def create_customer():
    """
    Create a new customer.
    
    ---
    post:
      tags:
        - Customers
      summary: Create customer
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                nombre:
                  type: string
                apellido:
                  type: string
                email:
                  type: string
                  format: email
                telefono:
                  type: string
                direccion:
                  type: string
    """
    try:
        # Validate request data
        data = customer_create_schema.load(request.get_json())
        user_id = get_jwt_identity()
        
        # Create customer using service
        customer = customer_service.create_customer(data, user_id)
        
        return jsonify(customer_response_schema.dump(customer)), 201
        
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    except AppValidationError as err:
        return jsonify({'error': str(err)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@customers_bp.route('/<int:customer_id>', methods=['PUT'])
@jwt_required()
def update_customer(customer_id):
    """
    Update a customer.
    
    ---
    put:
      tags:
        - Customers
      summary: Update customer
      security:
        - bearerAuth: []
    """
    try:
        customer = Customer.query.filter_by(id=customer_id, is_active=True).first()
        
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        # Validate request data
        data = customer_update_schema.load(request.get_json())
        user_id = get_jwt_identity()
        
        # Update customer
        updated_customer = customer_service.update_customer(customer_id, data, user_id)
        
        return jsonify(customer_response_schema.dump(updated_customer)), 200
        
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    except AppValidationError as err:
        return jsonify({'error': str(err)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@customers_bp.route('/<int:customer_id>', methods=['DELETE'])
@jwt_required()
def delete_customer(customer_id):
    """
    Delete (soft-delete) a customer.
    
    ---
    delete:
      tags:
        - Customers
      summary: Delete customer
      security:
        - bearerAuth: []
    """
    try:
        customer = Customer.query.filter_by(id=customer_id, is_active=True).first()
        
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        user_id = get_jwt_identity()
        customer_service.delete_customer(customer_id, user_id)
        
        return '', 204
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

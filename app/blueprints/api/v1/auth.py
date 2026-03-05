"""
API v1 authentication routes.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from marshmallow import ValidationError
from datetime import timedelta
from app.extensions import db, bcrypt
from app.models.user import User
from app.schemas.user_schema import UserLoginSchema, TokenResponseSchema, UserResponseSchema

auth_bp = Blueprint('api_auth', __name__, url_prefix='/api/v1/auth')


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User login endpoint.
    
    Returns JWT access and refresh tokens.
    ---
    post:
      tags:
        - Authentication
      summary: User login
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                email:
                  type: string
                  example: "user@example.com"
                password:
                  type: string
                  example: "password123"
      responses:
        200:
          description: Login successful
          content:
            application/json:
              schema:
                type: object
                properties:
                  access_token:
                    type: string
                  refresh_token:
                    type: string
                  user:
                    type: object
        401:
          description: Invalid credentials
        400:
          description: Validation error
    """
    schema = UserLoginSchema()
    
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    
    # Find user by email
    user = User.query.filter_by(email=data['email'], is_active=True).first()
    
    if not user or not bcrypt.check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Create tokens
    access_token = create_access_token(
        identity=user.id,
        expires_delta=timedelta(hours=24)
    )
    refresh_token = create_refresh_token(
        identity=user.id
    )
    
    # Prepare response
    user_schema = UserResponseSchema()
    response = TokenResponseSchema().dump({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'expires_in': 86400,  # 24 hours in seconds
        'user': user
    })
    
    return jsonify(response), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token using refresh token.
    
    ---
    post:
      tags:
        - Authentication
      summary: Refresh access token
      security:
        - bearerAuth: []
      responses:
        200:
          description: Token refreshed successfully
        401:
          description: Invalid or expired refresh token
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not user.is_active:
        return jsonify({'error': 'User not found or inactive'}), 401
    
    # Create new access token
    access_token = create_access_token(
        identity=user_id,
        expires_delta=timedelta(hours=24)
    )
    
    response = {
        'access_token': access_token,
        'expires_in': 86400,
        'token_type': 'Bearer'
    }
    
    return jsonify(response), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get current authenticated user information.
    
    ---
    get:
      tags:
        - Authentication
      summary: Get current user info
      security:
        - bearerAuth: []
      responses:
        200:
          description: User information
        401:
          description: Unauthorized
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    schema = UserResponseSchema()
    return jsonify(schema.dump(user)), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout endpoint.
    
    Note: Token is not invalidated on server. 
    Client should discard the token.
    
    ---
    post:
      tags:
        - Authentication
      summary: User logout
      security:
        - bearerAuth: []
      responses:
        200:
          description: Logout successful
    """
    # In a real application, you might want to blacklist the token
    # For now, client just discards it
    return jsonify({'message': 'Logout successful'}), 200

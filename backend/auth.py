from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from backend.models import db, User
from backend.utils import validate_email
from backend.notifications import send_registration_confirmation
from backend.security import validate_and_sanitize_json, rate_limit
import re

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['POST'])
@validate_and_sanitize_json()
@rate_limit(max_requests=5, window=300)  # 5 requests per 5 minutes
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        required_fields = ['name', 'email', 'password', 'role']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        name = data['name'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        role = data['role'].strip().lower()
        
        # Validate email format
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate role
        if role not in ['admin', 'fan']:
            return jsonify({'error': 'Role must be either "admin" or "fan"'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'User with this email already exists'}), 409
        
        # Validate password strength
        from backend.security import validate_password
        if not validate_password(password):
            return jsonify({'error': 'Password does not meet security requirements'}), 400
        
        # Create new user
        user = User(
            name=name,
            email=email,
            role=role
        )
        user.set_password(password)
        
        # Add user to database
        db.session.add(user)
        db.session.commit()
        
        # Send registration confirmation email
        send_registration_confirmation(user, current_app)
        
        # Create tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500

@bp.route('/login', methods=['POST'])
@validate_and_sanitize_json()
@rate_limit(max_requests=10, window=300)  # 10 requests per 5 minutes
def login():
    """Authenticate user and return JWT tokens"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        if 'email' not in data or not data['email']:
            return jsonify({'error': 'Email is required'}), 400
        
        if 'password' not in data or not data['password']:
            return jsonify({'error': 'Password is required'}), 400
        
        email = data['email'].strip().lower()
        password = data['password']
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        # Check if user exists and password is correct
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Create tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500

@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        current_user_id = get_jwt_identity()
        access_token = create_access_token(identity=current_user_id)
        
        return jsonify({
            'access_token': access_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Token refresh failed', 'details': str(e)}), 500

@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (invalidate refresh token)"""
    # In a real application, you would add the refresh token to a blacklist
    # For now, we'll just return a success message
    return jsonify({'message': 'Logout successful'}), 200
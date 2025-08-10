from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import db, User
from backend.utils import validate_email
from backend.notifications import send_password_reset
from backend.security import validate_and_sanitize_json, rate_limit
import secrets
import datetime

bp = Blueprint('users', __name__)

# In a real application, you would store these tokens in a database
# For simplicity, we'll use an in-memory store
password_reset_tokens = {}

@bp.route('/profile', methods=['GET'])
@jwt_required()
@rate_limit(max_requests=120, window=3600)  # 120 requests per hour
def get_profile():
    """Get authenticated user's profile information"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify(user.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve profile', 'details': str(e)}), 500

@bp.route('/profile', methods=['PUT'])
@jwt_required()
@validate_and_sanitize_json()
@rate_limit(max_requests=30, window=3600)  # 30 requests per hour
def update_profile():
    """Update authenticated user's profile information"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update name if provided
        if 'name' in data and data['name']:
            name = data['name'].strip()
            # Validate name length
            if len(name) < 2 or len(name) > 100:
                return jsonify({'error': 'Name must be between 2 and 100 characters'}), 400
            user.name = name
        
        # Update email if provided
        if 'email' in data and data['email']:
            email = data['email'].strip().lower()
            
            # Validate email format
            if not validate_email(email):
                return jsonify({'error': 'Invalid email format'}), 400
            
            # Check if email is already taken by another user
            existing_user = User.query.filter_by(email=email).first()
            if existing_user and existing_user.id != current_user_id:
                return jsonify({'error': 'Email already taken'}), 409
            
            user.email = email
        
        # Update user in database
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update profile', 'details': str(e)}), 500

@bp.route('/password', methods=['PUT'])
@jwt_required()
@validate_and_sanitize_json()
@rate_limit(max_requests=5, window=3600)  # 5 requests per hour
def change_password():
    """Change authenticated user's password"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        if 'current_password' not in data or not data['current_password']:
            return jsonify({'error': 'Current password is required'}), 400
        
        if 'new_password' not in data or not data['new_password']:
            return jsonify({'error': 'New password is required'}), 400
        
        current_password = data['current_password']
        new_password = data['new_password']
        
        # Check if current password is correct
        if not user.check_password(current_password):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Validate new password strength
        from backend.security import validate_password
        if not validate_password(new_password):
            return jsonify({'error': 'New password does not meet security requirements'}), 400
        
        # Update password
        user.set_password(new_password)
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to change password', 'details': str(e)}), 500

@bp.route('/password-reset', methods=['POST'])
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from backend.models import User
import re
import html

def sanitize_input(data):
    """Sanitize user input to prevent XSS attacks"""
    if isinstance(data, str):
        # Escape HTML characters
        data = html.escape(data)
        # Remove any script tags
        data = re.sub(r'<script.*?>.*?</script>', '', data, flags=re.IGNORECASE | re.DOTALL)
        # Remove any javascript: links
        data = re.sub(r'javascript:', '', data, flags=re.IGNORECASE)
    elif isinstance(data, dict):
        for key, value in data.items():
            data[key] = sanitize_input(value)
    elif isinstance(data, list):
        for i, value in enumerate(data):
            data[i] = sanitize_input(value)
    return data

def validate_and_sanitize_json():
    """Decorator to validate and sanitize JSON input"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if request has JSON data
            if request.is_json:
                data = request.get_json()
                if data:
                    # Sanitize the data
                    sanitized_data = sanitize_input(data)
                    # Replace the request data with sanitized data
                    request._cached_json = (sanitized_data, sanitized_data)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def rate_limit(max_requests=100, window=3600):
    """Decorator to implement rate limiting"""
    # In a real application, you would use Redis or a database to store request counts
    # For simplicity, we'll use an in-memory store
    request_counts = {}
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client IP
            client_ip = request.remote_addr
            
            # Get current time
            import time
            current_time = time.time()
            
            # Initialize or update request count for this IP
            if client_ip not in request_counts:
                request_counts[client_ip] = {
                    'count': 1,
                    'start_time': current_time
                }
            else:
                # Check if the window has expired
                if current_time - request_counts[client_ip]['start_time'] > window:
                    # Reset the count
                    request_counts[client_ip] = {
                        'count': 1,
                        'start_time': current_time
                    }
                else:
                    # Increment the count
                    request_counts[client_ip]['count'] += 1
            
            # Check if the limit has been exceeded
            if request_counts[client_ip]['count'] > max_requests:
                return jsonify({'error': 'Rate limit exceeded'}), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_auth(f):
    """Decorator to require authentication for an endpoint"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Authentication required'}), 401
    return decorated_function

def require_admin(f):
    """Decorator to require admin role for an endpoint"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user or not user.is_admin():
                return jsonify({'error': 'Admin access required'}), 403
            
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Authentication required'}), 401
    return decorated_function

def require_fan(f):
    """Decorator to require fan role for an endpoint"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user or not user.is_fan():
                return jsonify({'error': 'Fan access required'}), 403
            
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Authentication required'}), 401
    return decorated_function

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    # Check if password is at least 8 characters long
    if len(password) < 8:
        return False
    
    # Check if password contains at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False
    
    # Check if password contains at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False
    
    # Check if password contains at least one digit
    if not re.search(r'[0-9]', password):
        return False
    
    # Check if password contains at least one special character
    if not re.search(r'[^a-zA-Z0-9]', password):
        return False
    
    return True

def generate_csrf_token():
    """Generate a CSRF token"""
    import secrets
    return secrets.token_urlsafe(32)

def validate_csrf_token(token, expected_token):
    """Validate a CSRF token"""
    return token == expected_token
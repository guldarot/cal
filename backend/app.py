from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_cors import CORS
from backend.config import Config
from backend.models import db, bcrypt
import os
import redis

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)
    mail = Mail(app)
    
    # Initialize Redis
    app.redis = redis.from_url(app.config['REDIS_URL'])
    
    # Enable CORS for all routes
    CORS(app)
    
    # Register blueprints
    from backend.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    from backend.users import bp as users_bp
    app.register_blueprint(users_bp, url_prefix='/api/users')
    
    from backend.events import bp as events_bp
    app.register_blueprint(events_bp, url_prefix='/api/events')
    
    from backend.bookings import bp as bookings_bp
    app.register_blueprint(bookings_bp, url_prefix='/api/bookings')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}, 200
    
    # Security headers middleware
    @app.after_request
    def after_request(response):
        # Add security headers
        for header, value in app.config.get('SECURITY_HEADERS', {}).items():
            response.headers[header] = value
        return response
    
    return app

# For running the app directly
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
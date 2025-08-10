#!/usr/bin/env python3
"""
Script to generate initial database migration files.
This script should be run once to create the initial migration files.
"""

import os
import sys
from flask import Flask
from flask_migrate import Migrate, upgrade
from backend.app import create_app
from backend.models import db

def main():
    # Create the Flask app
    app = create_app()
    
    # Initialize Flask-Migrate with the app and db
    migrate = Migrate(app, db)
    
    # Create the migrations directory if it doesn't exist
    migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
    if not os.path.exists(migrations_dir):
        os.makedirs(migrations_dir)
    
    with app.app_context():
        # Import the models to register them with SQLAlchemy
        from backend import models
        
        # Initialize the migration repository
        if not os.path.exists(os.path.join(migrations_dir, 'alembic.ini')):
            from flask_migrate import init
            init()
        
        # Generate the initial migration
        from flask_migrate import migrate
        migrate(message='Initial migration')

if __name__ == '__main__':
    main()
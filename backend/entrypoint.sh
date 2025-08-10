#!/bin/bash
# Entrypoint script for the backend service

# Exit on any error
set -e

# Parse DATABASE_URL to extract components for pg_isready
# DATABASE_URL format: postgresql://user:password@host:port/database
DB_USER=$(echo $DATABASE_URL | cut -d: -f2 | cut -d/ -f3)
DB_HOST=$(echo $DATABASE_URL | cut -d@ -f2 | cut -d: -f1)
DB_PORT=$(echo $DATABASE_URL | cut -d: -f4 | cut -d/ -f1)
DB_NAME=$(echo $DATABASE_URL | cut -d/ -f4)

# Wait for database to be ready
echo "Waiting for database to be ready..."
while ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME 2>/dev/null; do
  sleep 1
done

echo "Database is ready!"

# Check if migrations directory exists and has migrations
if [ ! -d "backend/migrations/versions" ] || [ -z "$(ls -A backend/migrations/versions)" ]; then
  echo "No migrations found. Generating initial migrations..."
  python backend/generate_migrations.py
fi

# Run database migrations
echo "Running database migrations..."
flask db upgrade

# Start the application
echo "Starting the application..."
exec gunicorn --bind 0.0.0.0:5000 --workers 4 run:app
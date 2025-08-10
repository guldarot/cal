# Deployment Guide

## Overview

This document provides detailed instructions for deploying the Appointment Booking System in various environments.

## Prerequisites

- Docker and Docker Compose installed
- Git installed
- At least 2GB of available RAM
- PostgreSQL 13+ (if deploying without Docker)

## Production Deployment with Docker Compose

### 1. Environment Configuration

Before deploying, ensure your `.env` file is properly configured with production values:

```env
# Database configuration
DATABASE_URL=postgresql://username:password@host:port/database_name

# Redis configuration
REDIS_URL=redis://redis:6379/0

# Secret keys (change these for production)
SECRET_KEY=your-very-secure-secret-key-here
JWT_SECRET_KEY=your-very-secure-jwt-secret-key-here

# Mail configuration
MAIL_SERVER=smtp.your-email-provider.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@domain.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@domain.com

# Frontend URL (for email links)
FRONTEND_URL=https://yourdomain.com

# Debug mode (should be False in production)
DEBUG=False

# Host and Port
HOST=0.0.0.0
PORT=5000
```

### 2. Deploying the Application

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd appointment-booking-system
   ```

2. Configure your environment variables in the `.env` file

3. Build and start the services:
   ```bash
   docker-compose up --build -d
   ```

4. The application will be available at `http://localhost` (or your configured domain)

### 3. Automatic Database Initialization

The database migrations are automatically applied when the application starts through the entrypoint script. No manual intervention is required.

## Manual Deployment (Without Docker)

### 1. Backend Setup

1. Install Python 3.9+ and create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables as described in the Docker section

4. Initialize the database:
   ```bash
   flask db upgrade
   ```

5. Start the backend:
   ```bash
   python run.py
   ```

### 2. Frontend Setup

1. Install Node.js 14+ and npm

2. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```

3. Build the frontend:
   ```bash
   npm run build
   ```

4. Serve the built files using a web server like Nginx or Apache

## Scaling and Performance

### Horizontal Scaling

To scale the application horizontally:

1. Use a load balancer to distribute traffic across multiple backend instances
2. Use a shared database (not SQLite) for all instances
3. Use a shared Redis instance for all instances

### Database Optimization

1. Use connection pooling
2. Implement proper indexing on frequently queried columns
3. Regularly run `VACUUM` and `ANALYZE` on PostgreSQL

## Monitoring and Logging

### Health Checks

The application provides health check endpoints:

- Backend: `http://localhost:5000/health`
- Docker Compose: `docker-compose exec app curl http://localhost:5000/health`

### Log Monitoring

Logs are output to stdout/stderr and can be collected by Docker logging drivers or external services like ELK stack or Datadog.

## Security Considerations

### SSL/TLS

For production deployments, always use SSL/TLS. This can be achieved by:

1. Adding SSL termination to the Nginx configuration
2. Using a reverse proxy like Cloudflare or AWS ELB with SSL
3. Using Let's Encrypt certificates with automated renewal

### Secret Management

Never commit secrets to version control. Use:
1. Environment variables
2. Secret management services (HashiCorp Vault, AWS Secrets Manager, etc.)
3. Kubernetes secrets (for Kubernetes deployments)

## Backup and Disaster Recovery

### Database Backups

1. Implement regular automated backups of the PostgreSQL database
2. Test backup restoration procedures regularly
3. Store backups in multiple geographic locations

### Application Backups

1. Keep the application code in version control
2. Backup configuration files separately from code
3. Document the deployment process

## Troubleshooting

### Common Issues

1. **Database Connection Issues**: Check DATABASE_URL configuration and database service status
2. **Redis Connection Issues**: Check REDIS_URL configuration and Redis service status
3. **Mail Delivery Issues**: Verify mail server configuration and credentials
4. **Permission Issues**: Ensure proper file permissions, especially for Docker volumes

### Debugging

1. Check container logs: `docker-compose logs`
2. Check individual service logs: `docker-compose logs <service-name>`
3. Access containers for debugging: `docker-compose exec <service-name> sh`

## Updating the Application

### With Docker Compose

1. Pull the latest code:
   ```bash
   git pull origin main
   ```

2. Rebuild and restart services:
   ```bash
   docker-compose down
   docker-compose up --build -d
   ```

### Manual Updates

1. Pull the latest code:
   ```bash
   git pull origin main
   ```

2. Update Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Update Node dependencies:
   ```bash
   cd frontend
   npm install
   ```

4. Run database migrations:
   ```bash
   flask db upgrade
   ```

5. Restart services
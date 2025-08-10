# Appointment Booking System

A comprehensive web application for handling appointments with user authentication, event management, and booking system.

## Features

### User Authentication and Authorization
- Users can register and log in using email and password
- Two roles: admins and fans
- Admins can create and manage events
- Fans can view events and book time slots

### Event Creation
- Admins can create events with a title, description, date, and predefined time slots
- Each event has its own unique URL that can be shared
- Events can be published or kept as drafts

### Booking System
- Fans can view available time slots for an event and book a slot
- Booking requires fan information (name, email, phone number)
- System prevents double-booking with concurrency handling
- Fans can view and cancel their bookings

### User Information Management
- Users can update their profiles (name, email, password)
- Admins can view all bookings for their events

### Notifications
- Email notifications to fans when they book a slot
- Email notifications to admins when a booking is made

### Security
- HTTPS for secure communication
- Protection against common web vulnerabilities (SQL injection, XSS, CSRF)
- Secure password hashing with bcrypt
- JWT-based authentication

## Technology Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT (JSON Web Tokens)
- **Password Security**: Bcrypt
- **Email Service**: Flask-Mail
- **API Documentation**: Swagger/OpenAPI

### Frontend
- **Framework**: React.js with Vite
- **State Management**: React Context API
- **Routing**: React Router
- **UI Components**: Material-UI
- **HTTP Client**: Axios

### Deployment
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Reverse Proxy**: Nginx

## Prerequisites

- Docker and Docker Compose
- Git

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd appointment-booking-system
   ```

2. Configure environment variables:
   Create a `.env` file in the root directory based on `.env.example` or use the provided `.env` file.
   Make sure to update the secret keys and mail configuration for production use.

3. Build and run the application:
   ```bash
   docker-compose up --build
   ```

The application will be available at `http://localhost`.

## Development Setup

### Backend Development

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment variables as described above

3. Initialize the database:
   ```bash
   flask db upgrade
   ```

4. Run the backend:
   ```bash
   python run.py
   ```

The backend will be available at `http://localhost:5000`.

### Frontend Development

1. Install Node dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Run the frontend:
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:3000`.

## API Documentation

The API documentation is available at `http://localhost:5000/api/docs` when the backend is running.

## Testing

To run the test suite:

```bash
# Backend tests
python -m pytest

# Frontend tests
cd frontend
npm run test
```

## Deployment

### Docker Deployment

1. Build and run with Docker Compose:
   ```bash
   docker-compose up --build
   ```

The database migrations will be automatically applied when the application starts.

### Manual Deployment

Follow the instructions in [DEPLOYMENT.md](DEPLOYMENT.md) for manual deployment options.

## Project Structure

```
appointment-booking-system/
├── backend/                 # Flask backend application
│   ├── __init__.py          # Package initialization
│   ├── app.py              # Flask application factory
│   ├── models.py           # Database models
│   ├── auth.py             # Authentication routes
│   ├── users.py            # User management routes
│   ├── events.py           # Event management routes
│   ├── bookings.py         # Booking management routes
│   ├── notifications.py    # Notification system
│   ├── security.py         # Security utilities
│   ├── utils.py            # Utility functions
│   ├── config.py           # Configuration
│   ├── entrypoint.sh      # Docker entrypoint script
│   ├── generate_migrations.py # Migration generation script
│   └── migrations/         # Database migrations
├── frontend/               # React frontend application
│   ├── src/                # Source code
│   │   ├── components/     # Reusable components
│   │   ├── pages/          # Page components
│   │   ├── context/        # React context providers
│   │   ├── services/       # API service functions
│   │   └── App.jsx         # Main application component
│   ├── Dockerfile          # Frontend Docker configuration
│   └── nginx.conf          # Frontend Nginx configuration
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile              # Backend Docker configuration
├── nginx.conf              # Nginx configuration
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── .env                    # Environment variables
└── DEPLOYMENT.md           # Deployment guide
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions, please file an issue on the GitHub repository.
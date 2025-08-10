# Backend API Design

## Overview
This document outlines the RESTful API design for the appointment booking system. The API will be implemented using Flask and will follow REST principles with proper HTTP methods, status codes, and error handling.

## Authentication & Authorization

### Authentication Method
- **JWT (JSON Web Tokens)** for stateless authentication
- Tokens will be sent in the `Authorization` header as `Bearer <token>`
- Tokens will have a short expiration time (e.g., 15 minutes) with refresh tokens

### Roles
- **Admin**: Can create and manage events, view all bookings
- **Fan**: Can view events and book time slots

### Protected Routes
All routes except authentication routes will require a valid JWT token. Routes will be protected based on user roles:

- Admin-only routes will check for `admin` role
- Fan-only routes will check for `fan` role
- Public routes (event viewing) will not require authentication

## API Endpoints

### Authentication Routes

#### User Registration
- **URL**: `POST /api/auth/register`
- **Description**: Register a new user
- **Request Body**:
  ```json
  {
    "name": "string",
    "email": "string",
    "password": "string",
    "role": "admin|fan"
  }
  ```
- **Success Response**: `201 Created`
  ```json
  {
    "message": "User registered successfully",
    "user": {
      "id": "integer",
      "name": "string",
      "email": "string",
      "role": "admin|fan"
    }
  }
  ```
- **Error Responses**:
  - `400 Bad Request`: Invalid input data
  - `409 Conflict`: Email already exists

#### User Login
- **URL**: `POST /api/auth/login`
- **Description**: Authenticate user and return JWT token
- **Request Body**:
  ```json
  {
    "email": "string",
    "password": "string"
  }
  ```
- **Success Response**: `200 OK`
  ```json
  {
    "access_token": "string",
    "refresh_token": "string",
    "user": {
      "id": "integer",
      "name": "string",
      "email": "string",
      "role": "admin|fan"
    }
  }
  ```
- **Error Responses**:
  - `400 Bad Request`: Missing credentials
  - `401 Unauthorized`: Invalid credentials

#### Refresh Token
- **URL**: `POST /api/auth/refresh`
- **Description**: Refresh JWT access token
- **Request Body**:
  ```json
  {
    "refresh_token": "string"
  }
  ```
- **Success Response**: `200 OK`
  ```json
  {
    "access_token": "string"
  }
  ```
- **Error Responses**:
  - `401 Unauthorized`: Invalid or expired refresh token

#### User Logout
- **URL**: `POST /api/auth/logout`
- **Description**: Invalidate refresh token
- **Request Body**:
  ```json
  {
    "refresh_token": "string"
  }
  ```
- **Success Response**: `200 OK`
  ```json
  {
    "message": "Logged out successfully"
  }
  ```
- **Error Responses**:
  - `400 Bad Request`: Missing refresh token
  - `401 Unauthorized`: Invalid refresh token

### User Management Routes

#### Get User Profile
- **URL**: `GET /api/users/profile`
- **Description**: Get authenticated user's profile information
- **Headers**: `Authorization: Bearer <token>`
- **Success Response**: `200 OK`
  ```json
  {
    "id": "integer",
    "name": "string",
    "email": "string",
    "role": "admin|fan",
    "created_at": "datetime"
  }
  ```
- **Error Responses**:
  - `401 Unauthorized`: Missing or invalid token

#### Update User Profile
- **URL**: `PUT /api/users/profile`
- **Description**: Update authenticated user's profile information
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "name": "string",
    "email": "string"
  }
  ```
- **Success Response**: `200 OK`
  ```json
  {
    "message": "Profile updated successfully",
    "user": {
      "id": "integer",
      "name": "string",
      "email": "string",
      "role": "admin|fan"
    }
  }
  ```
- **Error Responses**:
  - `400 Bad Request`: Invalid input data
  - `401 Unauthorized`: Missing or invalid token
  - `409 Conflict`: Email already exists

#### Change Password
- **URL**: `PUT /api/users/password`
- **Description**: Change authenticated user's password
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "current_password": "string",
    "new_password": "string"
  }
  ```
- **Success Response**: `200 OK`
  ```json
  {
    "message": "Password changed successfully"
  }
  ```
- **Error Responses**:
  - `400 Bad Request`: Invalid input data
  - `401 Unauthorized`: Missing or invalid token
  - `401 Unauthorized`: Current password is incorrect

### Event Management Routes (Admin Only)

#### Create Event
- **URL**: `POST /api/events`
- **Description**: Create a new event
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "title": "string",
    "description": "string",
    "event_date": "date",
    "time_slots": [
      {
        "start_time": "time",
        "end_time": "time"
      }
    ]
  }
  ```
- **Success Response**: `201 Created`
  ```json
  {
    "id": "integer",
    "admin_id": "integer",
    "title": "string",
    "description": "string",
    "event_date": "date",
    "unique_url": "string",
    "is_published": "boolean",
    "created_at": "datetime",
    "time_slots": [
      {
        "id": "integer",
        "start_time": "time",
        "end_time": "time",
        "is_booked": "boolean"
      }
    ]
  }
  ```
- **Error Responses**:
  - `400 Bad Request`: Invalid input data
  - `401 Unauthorized`: Missing or invalid token
  - `403 Forbidden`: User is not an admin

#### List Admin's Events
- **URL**: `GET /api/events`
- **Description**: Get all events created by the authenticated admin
- **Headers**: `Authorization: Bearer <token>`
- **Query Parameters**:
  - `page`: integer (default: 1)
  - `per_page`: integer (default: 10, max: 100)
- **Success Response**: `200 OK`
  ```json
  {
    "events": [
      {
        "id": "integer",
        "title": "string",
        "description": "string",
        "event_date": "date",
        "unique_url": "string",
        "is_published": "boolean",
        "created_at": "datetime",
        "bookings_count": "integer"
      }
    ],
    "pagination": {
      "page": "integer",
      "per_page": "integer",
      "total": "integer",
      "pages": "integer"
    }
  }
  ```
- **Error Responses**:
  - `401 Unauthorized`: Missing or invalid token
  - `403 Forbidden`: User is not an admin

#### Get Event Details
- **URL**: `GET /api/events/{id}`
- **Description**: Get detailed information about a specific event
- **Headers**: `Authorization: Bearer <token>`
- **Success Response**: `200 OK`
  ```json
  {
    "id": "integer",
    "title": "string",
    "description": "string",
    "event_date": "date",
    "unique_url": "string",
    "is_published": "boolean",
    "created_at": "datetime",
    "time_slots": [
      {
        "id": "integer",
        "start_time": "time",
        "end_time": "time",
        "is_booked": "boolean"
      }
    ]
  }
  ```
- **Error Responses**:
  - `401 Unauthorized`: Missing or invalid token
  - `403 Forbidden`: User is not the event owner
  - `404 Not Found`: Event not found

#### Update Event
- **URL**: `PUT /api/events/{id}`
- **Description**: Update an existing event
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "title": "string",
    "description": "string",
    "event_date": "date"
  }
  ```
- **Success Response**: `200 OK`
  ```json
  {
    "id": "integer",
    "title": "string",
    "description": "string",
    "event_date": "date",
    "unique_url": "string",
    "is_published": "boolean",
    "updated_at": "datetime"
  }
  ```
- **Error Responses**:
  - `400 Bad Request`: Invalid input data
  - `401 Unauthorized`: Missing or invalid token
  - `403 Forbidden`: User is not the event owner
  - `404 Not Found`: Event not found

#### Delete Event
- **URL**: `DELETE /api/events/{id}`
- **Description**: Delete an event and all associated time slots and bookings
- **Headers**: `Authorization: Bearer <token>`
- **Success Response**: `200 OK`
  ```json
  {
    "message": "Event deleted successfully"
  }
  ```
- **Error Responses**:
  - `401 Unauthorized`: Missing or invalid token
  - `403 Forbidden`: User is not the event owner
  - `404 Not Found`: Event not found

#### Publish Event
- **URL**: `POST /api/events/{id}/publish`
- **Description**: Publish or unpublish an event
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "is_published": "boolean"
  }
  ```
- **Success Response**: `200 OK`
  ```json
  {
    "id": "integer",
    "is_published": "boolean",
    "message": "Event published/unpublished successfully"
  }
  ```
- **Error Responses**:
  - `400 Bad Request`: Invalid input data
  - `401 Unauthorized`: Missing or invalid token
  - `403 Forbidden`: User is not the event owner
  - `404 Not Found`: Event not found

#### Get Event Bookings
- **URL**: `GET /api/events/{id}/bookings`
- **Description**: Get all bookings for a specific event
- **Headers**: `Authorization: Bearer <token>`
- **Query Parameters**:
  - `page`: integer (default: 1)
  - `per_page`: integer (default: 10, max: 100)
- **Success Response**: `200 OK`
  ```json
  {
    "bookings": [
      {
        "id": "integer",
        "fan_name": "string",
        "fan_email": "string",
        "fan_phone": "string",
        "created_at": "datetime",
        "time_slot": {
          "start_time": "time",
          "end_time": "time"
        }
      }
    ],
    "pagination": {
      "page": "integer",
      "per_page": "integer",
      "total": "integer",
      "pages": "integer"
    }
  }
  ```
- **Error Responses**:
  - `401 Unauthorized`: Missing or invalid token
  - `403 Forbidden`: User is not the event owner
  - `404 Not Found`: Event not found

### Public Event Routes

#### List Published Events
- **URL**: `GET /api/events/public`
- **Description**: Get all published events
- **Query Parameters**:
  - `page`: integer (default: 1)
  - `per_page`: integer (default: 10, max: 100)
  - `date`: date (filter by event date)
- **Success Response**: `200 OK`
  ```json
  {
    "events": [
      {
        "id": "integer",
        "title": "string",
        "description": "string",
        "event_date": "date",
        "unique_url": "string"
      }
    ],
    "pagination": {
      "page": "integer",
      "per_page": "integer",
      "total": "integer",
      "pages": "integer"
    }
  }
  ```

#### Get Event by URL
- **URL**: `GET /api/events/public/{url}`
- **Description**: Get event details by unique URL
- **Success Response**: `200 OK`
  ```json
  {
    "id": "integer",
    "title": "string",
    "description": "string",
    "event_date": "date",
    "unique_url": "string"
  }
  ```
- **Error Responses**:
  - `404 Not Found`: Event not found or not published

#### Get Available Time Slots
- **URL**: `GET /api/events/public/{url}/slots`
- **Description**: Get available time slots for an event
- **Success Response**: `200 OK`
  ```json
  {
    "time_slots": [
      {
        "id": "integer",
        "start_time": "time",
        "end_time": "time"
      }
    ]
  }
  ```
- **Error Responses**:
  - `404 Not Found`: Event not found or not published

### Booking Routes (Fan Only)

#### Create Booking
- **URL**: `POST /api/bookings`
- **Description**: Book a time slot for an event
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "time_slot_id": "integer",
    "fan_name": "string",
    "fan_email": "string",
    "fan_phone": "string"
  }
  ```
- **Success Response**: `201 Created`
  ```json
  {
    "id": "integer",
    "time_slot_id": "integer",
    "fan_name": "string",
    "fan_email": "string",
    "fan_phone": "string",
    "created_at": "datetime",
    "event": {
      "id": "integer",
      "title": "string",
      "event_date": "date"
    },
    "time_slot": {
      "start_time": "time",
      "end_time": "time"
    }
  }
  ```
- **Error Responses**:
  - `400 Bad Request`: Invalid input data
  - `401 Unauthorized`: Missing or invalid token
  - `403 Forbidden`: User is not a fan
  - `404 Not Found`: Time slot not found
  - `409 Conflict`: Time slot already booked

#### List User's Bookings
- **URL**: `GET /api/bookings`
- **Description**: Get all bookings made by the authenticated fan
- **Headers**: `Authorization: Bearer <token>`
- **Query Parameters**:
  - `page": integer (default: 1)
  - `per_page`: integer (default: 10, max: 100)
- **Success Response**: `200 OK`
  ```json
  {
    "bookings": [
      {
        "id": "integer",
        "fan_name": "string",
        "fan_email": "string",
        "fan_phone": "string",
        "created_at": "datetime",
        "event": {
          "id": "integer",
          "title": "string",
          "event_date": "date"
        },
        "time_slot": {
          "start_time": "time",
          "end_time": "time"
        }
      }
    ],
    "pagination": {
      "page": "integer",
      "per_page": "integer",
      "total": "integer",
      "pages": "integer"
    }
  }
  ```
- **Error Responses**:
  - `401 Unauthorized`: Missing or invalid token
  - `403 Forbidden`: User is not a fan

#### Get Booking Details
- **URL**: `GET /api/bookings/{id}`
- **Description**: Get detailed information about a specific booking
- **Headers**: `Authorization: Bearer <token>`
- **Success Response**: `200 OK`
  ```json
  {
    "id": "integer",
    "fan_name": "string",
    "fan_email": "string",
    "fan_phone": "string",
    "created_at": "datetime",
    "event": {
      "id": "integer",
      "title": "string",
      "description": "string",
      "event_date": "date",
      "unique_url": "string"
    },
    "time_slot": {
      "start_time": "time",
      "end_time": "time"
    }
  }
  ```
- **Error Responses**:
  - `401 Unauthorized`: Missing or invalid token
  - `403 Forbidden`: User is not the booking owner
  - `404 Not Found`: Booking not found

#### Cancel Booking
- **URL**: `DELETE /api/bookings/{id}`
- **Description**: Cancel a booking
- **Headers**: `Authorization: Bearer <token>`
- **Success Response**: `200 OK`
  ```json
  {
    "message": "Booking cancelled successfully"
  }
  ```
- **Error Responses**:
  - `401 Unauthorized`: Missing or invalid token
  - `403 Forbidden`: User is not the booking owner
  - `404 Not Found`: Booking not found

## Error Response Format

All error responses will follow this format:
```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": "object|null"
  }
}
```

## Status Codes

- `200 OK`: Successful GET, PUT, PATCH, or DELETE request
- `201 Created`: Successful POST request
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Authenticated user does not have permission
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict (e.g., duplicate email)
- `500 Internal Server Error`: Unexpected server error

## Rate Limiting

To prevent abuse, the API will implement rate limiting:
- 100 requests per hour for authenticated users
- 10 requests per hour for unauthenticated users

Rate limit responses will return `429 Too Many Requests` with a `Retry-After` header.

## CORS Policy

The API will allow CORS requests from the frontend domain with the following configuration:
- Allow credentials: true
- Allow methods: GET, POST, PUT, DELETE, OPTIONS
- Allow headers: Authorization, Content-Type, X-Requested-With
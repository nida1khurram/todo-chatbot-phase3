# API Documentation

This document provides detailed information about the API endpoints available in the Todo Full-Stack Application.

## Authentication Endpoints

### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "created_at": "2023-12-01T10:00:00Z"
}
```

**Validation:**
- Email must be a valid email format
- Password must be at least 6 characters long
- Email must be unique

**Errors:**
- 400: Invalid input data
- 409: Email already exists

### POST /auth/login
Authenticate a user and return JWT tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Validation:**
- Email must be a valid email format
- Password must match the stored hash

**Errors:**
- 401: Invalid credentials
- 400: Invalid input data

## Task Management Endpoints

All task endpoints require authentication via JWT token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### GET /tasks
Retrieve all tasks for the authenticated user.

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Complete project",
    "description": "Finish the todo app project",
    "completed": false,
    "user_id": 1,
    "created_at": "2023-12-01T10:00:00Z",
    "updated_at": "2023-12-01T10:00:00Z",
    "due_date": "2023-12-15T00:00:00Z"
  },
  {
    "id": 2,
    "title": "Write documentation",
    "description": "Create API documentation",
    "completed": true,
    "user_id": 1,
    "created_at": "2023-12-01T11:00:00Z",
    "updated_at": "2023-12-01T12:00:00Z",
    "due_date": null
  }
]
```

**Errors:**
- 401: Unauthorized (invalid or missing token)

### POST /tasks
Create a new task for the authenticated user.

**Request Body:**
```json
{
  "title": "New task",
  "description": "Task description (optional)",
  "due_date": "2023-12-31T23:59:59Z"  // optional
}
```

**Response (201 Created):**
```json
{
  "id": 3,
  "title": "New task",
  "description": "Task description (optional)",
  "completed": false,
  "user_id": 1,
  "created_at": "2023-12-01T13:00:00Z",
  "updated_at": "2023-12-01T13:00:00Z",
  "due_date": "2023-12-31T23:59:59Z"
}
```

**Validation:**
- Title is required and must be at least 1 character
- Description is optional
- Due date must be in ISO 8601 format if provided

**Errors:**
- 401: Unauthorized
- 400: Invalid input data

### GET /tasks/{task_id}
Retrieve a specific task for the authenticated user.

**Path Parameters:**
- `task_id`: The ID of the task to retrieve

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Complete project",
  "description": "Finish the todo app project",
  "completed": false,
  "user_id": 1,
  "created_at": "2023-12-01T10:00:00Z",
  "updated_at": "2023-12-01T10:00:00Z",
  "due_date": "2023-12-15T00:00:00Z"
}
```

**Errors:**
- 401: Unauthorized
- 404: Task not found (or doesn't belong to user)

### PUT /tasks/{task_id}
Update a specific task for the authenticated user.

**Path Parameters:**
- `task_id`: The ID of the task to update

**Request Body (all fields optional):**
```json
{
  "title": "Updated task title",
  "description": "Updated description",
  "completed": true,
  "due_date": "2023-12-31T23:59:59Z"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Updated task title",
  "description": "Updated description",
  "completed": true,
  "user_id": 1,
  "created_at": "2023-12-01T10:00:00Z",
  "updated_at": "2023-12-01T14:00:00Z",
  "due_date": "2023-12-31T23:59:59Z"
}
```

**Errors:**
- 401: Unauthorized
- 404: Task not found (or doesn't belong to user)
- 400: Invalid input data

### DELETE /tasks/{task_id}
Delete a specific task for the authenticated user.

**Path Parameters:**
- `task_id`: The ID of the task to delete

**Response (204 No Content):**
No response body.

**Errors:**
- 401: Unauthorized
- 404: Task not found (or doesn't belong to user)

## Health Check Endpoint

### GET /health
Check the health status of the application.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2023-12-01T10:00:00Z"
}
```

## Error Response Format

All error responses follow this format:

```json
{
  "detail": "Error message explaining what went wrong"
}
```

## Authentication and Security

- All task endpoints require a valid JWT token in the Authorization header
- Tokens expire after 30 minutes by default (configurable via ACCESS_TOKEN_EXPIRE_MINUTES)
- Users can only access their own tasks (user_id isolation)
- All inputs are validated to prevent injection attacks
- Passwords are hashed using bcrypt before storage

## Rate Limiting

The API implements rate limiting to prevent abuse:
- Authentication endpoints: 5 requests per minute per IP
- Task endpoints: 100 requests per minute per authenticated user

## Pagination

For endpoints that return multiple items (like GET /tasks), pagination may be implemented in future versions. Currently, all items are returned in a single response.
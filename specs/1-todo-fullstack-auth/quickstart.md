# Quickstart Guide: Todo Full-Stack Web Application

## Prerequisites

- Python 3.11+ installed
- Node.js 18+ installed
- PostgreSQL (or access to Neon PostgreSQL)
- Docker (optional, for containerized development)

## Setup Instructions

### 1. Clone and Initialize Repository

```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install uv  # if not already installed
   uv sync
   # Or with pip: pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your database URL and Better Auth secret
   ```

5. Run database migrations:
   ```bash
   python -m src.db.init  # or equivalent migration command
   ```

6. Start the backend server:
   ```bash
   uv run python -m src.main
   # Or: uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

### 3. Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend  # from repository root
   ```

2. Install dependencies:
   ```bash
   npm install
   # Or with yarn: yarn install
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your backend API URL and other configuration
   ```

4. Start the development server:
   ```bash
   npm run dev
   # Or with yarn: yarn dev
   ```

5. Open your browser to `http://localhost:3000`

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://username:password@localhost:5432/todoapp
BETTER_AUTH_SECRET=your-super-secret-jwt-key-here
BETTER_AUTH_URL=http://localhost:3000
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
```

## Running Tests

### Backend Tests
```bash
# Run all backend tests
cd backend
python -m pytest

# Run tests with coverage
python -m pytest --cov=src
```

### Frontend Tests
```bash
# Run all frontend tests
cd frontend
npm run test

# Run tests in watch mode
npm run test:watch
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get JWT token
- `POST /auth/logout` - Logout user

### Tasks
- `GET /tasks` - Get all tasks for authenticated user
- `POST /tasks` - Create a new task
- `GET /tasks/{task_id}` - Get a specific task
- `PUT /tasks/{task_id}` - Update a specific task
- `DELETE /tasks/{task_id}` - Delete a specific task

## Database Models

### User
- id (Integer, Primary Key)
- email (String, Unique)
- password_hash (String)
- created_at (DateTime)
- updated_at (DateTime)

### Task
- id (Integer, Primary Key)
- user_id (Integer, Foreign Key to User)
- title (String)
- description (String, Optional)
- completed (Boolean)
- created_at (DateTime)
- updated_at (DateTime)
- due_date (DateTime, Optional)

## Development Workflow

1. Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes in both frontend and backend as needed

3. Run tests to ensure everything works:
   ```bash
   # Backend
   cd backend && python -m pytest
   # Frontend
   cd frontend && npm run test
   ```

4. Commit your changes:
   ```bash
   git add .
   git commit -m "Description of changes"
   ```

5. Push your branch and create a pull request

## Common Tasks

### Adding a New API Endpoint
1. Define the endpoint in the appropriate router file in `backend/src/api/`
2. Create Pydantic schemas in `backend/src/models/` if needed
3. Implement the logic in `backend/src/services/`
4. Add tests in `backend/tests/`
5. Update the frontend API client in `frontend/src/services/`

### Adding a New Frontend Page
1. Create a new page file in `frontend/src/app/`
2. Use server components for data fetching with authentication
3. Use client components for interactive elements
4. Add navigation links as needed
5. Write tests for new components

## Troubleshooting

### Common Issues
- **Database connection errors**: Check that PostgreSQL is running and credentials are correct
- **Authentication not working**: Verify that JWT secret is set correctly in both backend and frontend
- **Frontend can't connect to backend**: Check that both services are running and URLs are configured correctly
- **Migration errors**: Run migrations from the backend directory with the virtual environment activated

### Development Tips
- Use `--reload` flag when running the backend for automatic reloading
- Frontend changes are automatically reflected in development mode
- Check logs in both terminal windows for error messages
- Use the API documentation to understand available endpoints
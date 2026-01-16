# Quickstart Guide

Get the Todo Full-Stack Application up and running in minutes.

## Prerequisites

- Python 3.9+ (Python 3.13+ recommended)
- Node.js 18+
- PostgreSQL (or a Neon account for cloud PostgreSQL)
- pip/uv for Python package management
- npm for Node.js package management

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd todo-fullstack-app
```

### 2. Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Install dependencies using your preferred Python package manager:

```bash
# Using pip
pip install -r requirements.txt

# Or if using uv (recommended)
uv pip install -r requirements.txt

# Or if using poetry (if pyproject.toml contains poetry configuration)
poetry install
```

Set up environment variables in `.env` (create this file based on `.env.example`):

```env
DATABASE_URL=postgresql://username:password@localhost:5432/todo_db
SECRET_KEY=your-super-secret-key-here-32-characters-min
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

> **Note**: Generate a secure secret key for production:
> ```bash
> python -c "import secrets; print(secrets.token_urlsafe(32))"
> ```

Run database migrations using Alembic:

```bash
# Upgrade database to latest version
alembic upgrade head

# Or if you need to initialize the database first
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

Start the backend server:

```bash
# Using uvicorn directly
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Or using the run script if available
python -m src.main
```

The backend API will be available at `http://localhost:8000`.

### 3. Frontend Setup

Open a new terminal window and navigate to the frontend directory:

```bash
cd frontend  # From the project root
```

Install dependencies:

```bash
npm install
```

Set up environment variables in `.env.local` (create this file based on `.env.local.example`):

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Start the frontend development server:

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`.

### 4. Access the Application

1. Open your browser and go to `http://localhost:3000`
2. Click "Sign up" to create a new account
3. After registration, you'll be redirected to the login page
4. Log in with your credentials
5. Start adding and managing your tasks!

### 5. API Documentation

View the API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- Redoc: `http://localhost:8000/redoc`

## Troubleshooting

### Common Issues

**Database Connection Issues:**
- Ensure PostgreSQL is running and accessible
- Verify your `DATABASE_URL` is correct (format: `postgresql://username:password@host:port/database_name`)
- Check that the database exists (create it if needed)
- Ensure your PostgreSQL server allows connections on the specified port

**Backend Server Won't Start:**
- Check that the required Python packages are installed
- Verify that the port 8000 is not already in use
- Ensure all environment variables are properly set

**Frontend Can't Connect to Backend:**
- Ensure the backend server is running on port 8000
- Check that `NEXT_PUBLIC_API_URL` is set correctly in `.env.local`
- Verify CORS settings if accessing from a different domain
- Make sure both servers are running simultaneously

**Authentication Issues:**
- Make sure you're registering before trying to log in
- Check that your password meets the minimum requirements (6+ characters)
- Verify that JWT tokens are properly configured

**Migration Issues:**
- If getting Alembic errors, try running `alembic upgrade head` from the backend directory
- Ensure you have the correct database URL in your environment variables

## Development Commands

### Backend
```bash
# Run tests
python -m pytest

# Run tests with coverage
python -m pytest --cov=src

# Format code with black
python -m black src/

# Check code with ruff
python -m ruff check src/

# Run with auto-reload
uvicorn src.main:app --reload

# Run with custom host/port
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
# Run development server
npm run dev

# Build for production
npm run build

# Run linting
npm run lint

# Run tests
npm run test

# Run tests in watch mode
npm run test -- --watch

# Run production build locally
npm run start
```

## Production Deployment Notes

For production deployment, ensure you have:

1. **Environment Variables**: Set secure values for SECRET_KEY and use a production database
2. **HTTPS**: Use HTTPS in production for security
3. **Database**: Use a managed PostgreSQL service (like Neon, AWS RDS, etc.)
4. **Secrets**: Never commit secrets to version control
5. **Monitoring**: Set up proper logging and monitoring for your deployed application
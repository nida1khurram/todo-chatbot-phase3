# FastAPI Project Setup Skill

## Description
Set up FastAPI project with main.py entry point, create routes/ directory structure, configure CORS, set up async endpoints, install dependencies including SQLModel and uvicorn, and create proper Python package structure.

## When to Use
- Setting up a new FastAPI backend from scratch
- Initializing the backend portion of a monorepo
- Creating API server for Next.js frontend
- Configuring async Python web application
- Setting up proper Python package structure with dependencies

## Prerequisites
- Python 3.13+ installed
- pip or uv package manager
- Backend directory prepared
- Understanding of async/await in Python
- Database connection string (Neon PostgreSQL)

## Core Concepts

### FastAPI Fundamentals
- ASGI framework for building APIs
- Automatic OpenAPI documentation
- Type hints for request/response validation
- Async/await for high performance
- Dependency injection system
- Automatic JSON serialization

### Project Structure
- `main.py` - Application entry point
- `routes/` - API route handlers
- `models/` - SQLModel database models
- `core/` - Configuration and utilities
- `middleware/` - CORS and authentication
- `schemas/` - Pydantic request/response models

## Skill Steps

### 1. Create Backend Directory Structure

```bash
# Navigate to backend directory
cd backend

# Create directory structure
mkdir -p routes models core middleware schemas tests
mkdir -p core/config
touch main.py
touch routes/__init__.py routes/auth.py routes/tasks.py routes/tags.py
touch models/__init__.py models/task.py models/tag.py models/user.py
touch core/__init__.py core/config/__init__.py core/config/settings.py
touch core/database.py core/security.py
touch middleware/__init__.py middleware/auth.py middleware/cors.py
touch schemas/__init__.py schemas/task.py schemas/tag.py schemas/user.py
touch .env .env.example requirements.txt
```

**Directory Structure**:
```
backend/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (git-ignored)
├── .env.example              # Environment variable template
├── core/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py       # Configuration settings
│   ├── database.py           # Database connection
│   └── security.py           # JWT utilities
├── models/
│   ├── __init__.py
│   ├── task.py               # Task model
│   ├── tag.py                # Tag model
│   └── user.py               # User model
├── routes/
│   ├── __init__.py
│   ├── auth.py               # Authentication routes
│   ├── tasks.py              # Task CRUD routes
│   └── tags.py               # Tag routes
├── middleware/
│   ├── __init__.py
│   ├── auth.py               # JWT verification
│   └── cors.py               # CORS configuration
├── schemas/
│   ├── __init__.py
│   ├── task.py               # Task schemas
│   ├── tag.py                # Tag schemas
│   └── user.py               # User schemas
└── tests/
    └── __init__.py
```

### 2. Install Dependencies

**requirements.txt**:

```txt
# FastAPI and server
fastapi==0.115.0
uvicorn[standard]==0.32.0
python-multipart==0.0.12

# Database and ORM
sqlmodel==0.0.22
psycopg2-binary==2.9.10
asyncpg==0.30.0

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.1

# CORS
fastapi-cors==0.0.6

# Validation
pydantic==2.9.2
pydantic-settings==2.6.0

# Testing (optional)
pytest==8.3.3
pytest-asyncio==0.24.0
httpx==0.27.2
```

**Install dependencies**:

```bash
# Using pip
pip install -r requirements.txt

# Or using uv (faster)
uv pip install -r requirements.txt
```

### 3. Create Configuration Settings

**core/config/settings.py**:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    app_name: str = "Todo API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database
    database_url: str
    database_echo: bool = False  # Log SQL queries

    # JWT Authentication
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 10080  # 7 days

    # CORS
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
    ]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Global settings instance
settings = Settings()
```

**.env.example**:

```bash
# Application
APP_NAME=Todo API
APP_VERSION=1.0.0
DEBUG=false

# Database (Neon PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:password@host/database

# JWT Authentication
JWT_SECRET_KEY=your-secret-key-min-32-chars-long-change-this
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=10080

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Server
HOST=0.0.0.0
PORT=8000
RELOAD=true
```

**.env** (create this file, add to .gitignore):

```bash
# Copy from .env.example and fill in real values
DATABASE_URL=postgresql+asyncpg://your-neon-connection-string
JWT_SECRET_KEY=generate-a-secure-random-key-here
```

### 4. Set Up Database Connection

**core/database.py**:

```python
from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from .config.settings import settings


# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.database_echo,
    future=True,
)

# Async session factory
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Initialize database tables"""
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database session.
    Usage: session: AsyncSession = Depends(get_session)
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

### 5. Create Main Application Entry Point

**main.py**:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from core.config.settings import settings
from core.database import init_db
from routes import auth, tasks, tags


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Runs on startup and shutdown.
    """
    # Startup: Initialize database
    print("🚀 Starting up...")
    await init_db()
    print("✅ Database initialized")

    yield

    # Shutdown
    print("👋 Shutting down...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/docs",  # Swagger UI at /docs
    redoc_url="/redoc",  # ReDoc at /redoc
    openapi_url="/openapi.json",
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(tasks.router, prefix="/api/{user_id}/tasks", tags=["Tasks"])
app.include_router(tags.router, prefix="/api/{user_id}/tags", tags=["Tags"])


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API health check"""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc",
    }


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )
```

### 6. Create Basic Route Structure

**routes/__init__.py**:

```python
"""API routes package"""
from . import auth, tasks, tags

__all__ = ["auth", "tasks", "tags"]
```

**routes/auth.py** (skeleton):

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_session
from schemas.user import UserCreate, UserResponse, SignInRequest, AuthResponse

router = APIRouter()


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session),
):
    """Register a new user"""
    # TODO: Implement user registration
    return {"user": {}, "token": ""}


@router.post("/signin", response_model=AuthResponse)
async def signin(
    credentials: SignInRequest,
    session: AsyncSession = Depends(get_session),
):
    """Authenticate user and return JWT token"""
    # TODO: Implement user authentication
    return {"user": {}, "token": ""}
```

**routes/tasks.py** (skeleton):

```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from core.database import get_session
from schemas.task import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter()


@router.get("/", response_model=list[TaskResponse])
async def get_tasks(
    user_id: str,
    status: Optional[str] = Query(None, description="Filter by status: all, pending, completed"),
    priority: Optional[str] = Query(None, description="Filter by priority: high,medium,low"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    sort_by: Optional[str] = Query("created_at", description="Sort by: created_at, priority, title"),
    sort_order: Optional[str] = Query("desc", description="Sort order: asc, desc"),
    session: AsyncSession = Depends(get_session),
):
    """Get all tasks for user with optional filters"""
    # TODO: Implement task listing with filters
    return []


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: str,
    task_data: TaskCreate,
    session: AsyncSession = Depends(get_session),
):
    """Create a new task"""
    # TODO: Implement task creation
    return {}


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    user_id: str,
    task_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get a single task by ID"""
    # TODO: Implement task retrieval
    return {}


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    user_id: str,
    task_id: int,
    task_data: TaskUpdate,
    session: AsyncSession = Depends(get_session),
):
    """Update an existing task"""
    # TODO: Implement task update
    return {}


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: str,
    task_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Delete a task"""
    # TODO: Implement task deletion
    pass


@router.patch("/{task_id}/complete", response_model=TaskResponse)
async def toggle_complete(
    user_id: str,
    task_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Toggle task completion status"""
    # TODO: Implement toggle completion
    return {}
```

**routes/tags.py** (skeleton):

```python
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_session
from schemas.tag import TagCreate, TagResponse

router = APIRouter()


@router.get("/", response_model=list[TagResponse])
async def get_tags(
    user_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Get all tags for user"""
    # TODO: Implement tag listing
    return []


@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    user_id: str,
    tag_data: TagCreate,
    session: AsyncSession = Depends(get_session),
):
    """Create a new tag"""
    # TODO: Implement tag creation
    return {}


@router.get("/autocomplete", response_model=list[TagResponse])
async def autocomplete_tags(
    user_id: str,
    query: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Max results"),
    session: AsyncSession = Depends(get_session),
):
    """Get tag autocomplete suggestions"""
    # TODO: Implement tag autocomplete
    return []


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    user_id: str,
    tag_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Delete a tag"""
    # TODO: Implement tag deletion
    pass
```

### 7. Create Pydantic Schemas

**schemas/user.py** (skeleton):

```python
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)


class UserResponse(UserBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    user: UserResponse
    token: str
```

**schemas/task.py** (skeleton):

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: str = Field(..., pattern="^(high|medium|low)$")


class TaskCreate(TaskBase):
    tag_ids: Optional[list[int]] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[str] = Field(None, pattern="^(high|medium|low)$")
    completed: Optional[bool] = None
    tag_ids: Optional[list[int]] = None


class TaskResponse(TaskBase):
    id: int
    user_id: str
    completed: bool
    created_at: datetime
    updated_at: datetime
    tags: list[dict] = []

    class Config:
        from_attributes = True
```

**schemas/tag.py** (skeleton):

```python
from pydantic import BaseModel, Field
from datetime import datetime


class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)


class TagCreate(TagBase):
    pass


class TagResponse(TagBase):
    id: int
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True
```

### 8. Create Security Utilities

**core/security.py**:

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from .config.settings import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token

    Args:
        data: Dictionary with user information (typically {"sub": user_id})
        expires_delta: Optional custom expiration time

    Returns:
        JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify JWT token

    Args:
        token: JWT token string

    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError:
        return None
```

### 9. Run the Application

**Development Mode**:

```bash
# Method 1: Using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Method 2: Using Python
python main.py

# Method 3: Using uvicorn with custom options
uvicorn main:app --reload --host 0.0.0.0 --port 8000 --log-level info
```

**Production Mode**:

```bash
# Without reload
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 10. Verify Installation

**Check API Documentation**:

After starting the server, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

**Test Endpoints**:

```bash
# Health check
curl http://localhost:8000/health

# Root endpoint
curl http://localhost:8000/

# Expected response:
# {
#   "message": "Welcome to Todo API",
#   "version": "1.0.0",
#   "docs": "/docs",
#   "redoc": "/redoc"
# }
```

### 11. Add .gitignore

**backend/.gitignore**:

```txt
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment variables
.env
.env.local

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Testing
.pytest_cache/
.coverage
htmlcov/

# Logs
*.log
```

### 12. Create Development Scripts

**scripts/dev.sh** (optional):

```bash
#!/bin/bash
# Development server startup script

echo "🚀 Starting FastAPI development server..."

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Run with uvicorn
uvicorn main:app --reload --host ${HOST:-0.0.0.0} --port ${PORT:-8000}
```

Make it executable:

```bash
chmod +x scripts/dev.sh
./scripts/dev.sh
```

## Testing the Setup

### Manual Testing

**Test CORS**:

```bash
# From frontend (Next.js)
curl -X GET http://localhost:8000/health \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET"
```

**Test Async Endpoint**:

```python
# Add to routes/tasks.py for testing
@router.get("/test-async")
async def test_async():
    """Test async endpoint"""
    import asyncio
    await asyncio.sleep(1)  # Simulate async operation
    return {"message": "Async working!"}
```

## Best Practices

1. **Async All the Way**: Use async/await for all route handlers and database operations
2. **Type Hints**: Add type hints to all functions for better IDE support
3. **Dependency Injection**: Use FastAPI's `Depends()` for database sessions and auth
4. **Pydantic Models**: Use Pydantic for request validation and response serialization
5. **Error Handling**: Use HTTPException for proper error responses
6. **Environment Variables**: Never hardcode secrets, use .env files
7. **CORS Configuration**: Restrict origins in production
8. **Documentation**: FastAPI auto-generates docs, but add docstrings for clarity
9. **Database Sessions**: Always use dependency injection for sessions
10. **Lifespan Events**: Use lifespan for startup/shutdown tasks

## Common Patterns

### Async Route with Database
```python
@router.get("/tasks", response_model=list[TaskResponse])
async def get_tasks(
    user_id: str,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(Task).where(Task.user_id == user_id)
    )
    tasks = result.scalars().all()
    return tasks
```

### Error Handling
```python
if not task:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Task not found"
    )
```

### JWT Protected Route
```python
from middleware.auth import get_current_user

@router.get("/protected")
async def protected_route(
    current_user: User = Depends(get_current_user),
):
    return {"user_id": current_user.id}
```

## Success Criteria

- ✅ FastAPI application runs on port 8000
- ✅ All dependencies installed correctly
- ✅ CORS configured for frontend origins
- ✅ Database connection established
- ✅ OpenAPI docs accessible at /docs
- ✅ Health check endpoint responds
- ✅ Environment variables loaded from .env
- ✅ Async endpoints working correctly
- ✅ Route structure organized by resource
- ✅ Proper Python package structure with __init__.py

## Troubleshooting

### Issue: ModuleNotFoundError
**Solution**: Ensure all directories have `__init__.py` files

### Issue: Database connection failed
**Solution**: Check DATABASE_URL in .env, ensure Neon database is accessible

### Issue: CORS errors from frontend
**Solution**: Add frontend URL to CORS_ORIGINS in .env

### Issue: JWT secret key error
**Solution**: Generate a secure key: `openssl rand -hex 32`

## Related Skills

- `sqlmodel_models`: Create database models
- `jwt_authentication`: Implement JWT verification
- `async_route_handlers`: Build async API endpoints

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

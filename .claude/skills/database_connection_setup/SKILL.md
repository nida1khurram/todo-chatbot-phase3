# Database Connection Setup Skill

## Description
Set up Neon Serverless PostgreSQL connection using SQLModel create_engine, implement dependency injection for session management with proper cleanup, handle connection errors, and configure connection pooling.

## When to Use
- Setting up PostgreSQL connection for FastAPI application
- Configuring Neon Serverless PostgreSQL
- Implementing async database session management
- Adding dependency injection for database sessions
- Configuring connection pooling for production

## Prerequisites
- FastAPI project set up
- SQLModel and asyncpg installed
- Neon PostgreSQL database created
- Database connection string available
- Understanding of async/await in Python

## Core Concepts

### Neon Serverless PostgreSQL
- Serverless PostgreSQL with autoscaling
- Automatic connection pooling
- Pay-per-use pricing model
- Free tier: 0.5GB storage, 190 compute hours/month
- Connection via asyncpg driver

### SQLModel + AsyncPG
- SQLModel: ORM built on SQLAlchemy + Pydantic
- AsyncPG: Async PostgreSQL driver
- create_async_engine: Async engine for SQLModel
- AsyncSession: Async database session
- Connection pooling built-in

### Dependency Injection
- FastAPI's `Depends()` for session management
- Automatic session lifecycle (create, commit, rollback, close)
- Generator pattern with `yield`
- Exception handling for transactions

## Skill Steps

### 1. Install Required Dependencies

**requirements.txt** (add these if not present):

```txt
# Database
sqlmodel==0.0.22
asyncpg==0.30.0
psycopg2-binary==2.9.10  # For migrations/tools

# Environment variables
python-dotenv==1.0.1
```

**Install**:

```bash
pip install sqlmodel asyncpg psycopg2-binary python-dotenv
```

### 2. Get Neon Connection String

**From Neon Dashboard**:

1. Go to https://console.neon.tech/
2. Select your project
3. Navigate to "Connection Details"
4. Copy the connection string

**Format**:
```
postgresql://username:password@ep-xxx-xxx.region.aws.neon.tech/dbname?sslmode=require
```

**Convert to Async Format**:
```
postgresql+asyncpg://username:password@ep-xxx-xxx.region.aws.neon.tech/dbname?sslmode=require
```

### 3. Configure Environment Variables

**.env**:

```bash
# Neon PostgreSQL Connection
DATABASE_URL=postgresql+asyncpg://username:password@ep-xxx-xxx.region.aws.neon.tech/dbname?sslmode=require

# Database Settings
DATABASE_ECHO=false  # Set to true to log SQL queries
DATABASE_POOL_SIZE=10  # Max connections in pool
DATABASE_MAX_OVERFLOW=20  # Additional connections if pool is full
DATABASE_POOL_TIMEOUT=30  # Seconds to wait for connection
DATABASE_POOL_RECYCLE=3600  # Recycle connections after 1 hour
```

**.env.example**:

```bash
# Neon PostgreSQL Connection
DATABASE_URL=postgresql+asyncpg://username:password@ep-xxx-xxx.region.aws.neon.tech/dbname?sslmode=require

# Database Settings
DATABASE_ECHO=false
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=3600
```

### 4. Update Settings Configuration

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

    # Database - Primary connection
    database_url: str

    # Database - Connection pool settings
    database_echo: bool = False  # Log SQL queries
    database_pool_size: int = 10  # Max connections in pool
    database_max_overflow: int = 20  # Additional connections beyond pool_size
    database_pool_timeout: int = 30  # Seconds to wait for connection
    database_pool_recycle: int = 3600  # Recycle connections after N seconds
    database_pool_pre_ping: bool = True  # Verify connections before using

    # Database - Connection retry settings
    database_connect_retry_count: int = 3
    database_connect_retry_delay: int = 2  # Seconds between retries

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

### 5. Create Database Connection Module

**core/database.py**:

```python
from sqlmodel import SQLModel, select
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.pool import NullPool, QueuePool
from typing import AsyncGenerator, Optional
import logging
import asyncio
from contextlib import asynccontextmanager

from .config.settings import settings

# Configure logging
logger = logging.getLogger(__name__)

# Global engine instance
engine: Optional[AsyncEngine] = None


def create_engine_with_config() -> AsyncEngine:
    """
    Create async engine with connection pooling configuration.

    Connection Pool Parameters:
    - pool_size: Number of connections maintained in the pool
    - max_overflow: Additional connections beyond pool_size
    - pool_timeout: Seconds to wait for an available connection
    - pool_recycle: Recycle connections after N seconds
    - pool_pre_ping: Test connections before using them

    For Neon Serverless PostgreSQL:
    - Use QueuePool for connection pooling
    - Configure appropriate pool size based on workload
    - Enable pool_pre_ping to handle Neon's auto-pause
    """

    # Create engine with connection pooling
    engine = create_async_engine(
        settings.database_url,
        echo=settings.database_echo,  # Log SQL queries if True
        future=True,
        poolclass=QueuePool,  # Use connection pooling
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        pool_timeout=settings.database_pool_timeout,
        pool_recycle=settings.database_pool_recycle,
        pool_pre_ping=settings.database_pool_pre_ping,
        # Additional connection arguments for asyncpg
        connect_args={
            "server_settings": {
                "application_name": settings.app_name,
                "jit": "off",  # Disable JIT for better performance with short-lived connections
            },
            "command_timeout": 60,  # Command timeout in seconds
            "timeout": 10,  # Connection timeout in seconds
        },
    )

    logger.info(
        f"Database engine created with pool_size={settings.database_pool_size}, "
        f"max_overflow={settings.database_max_overflow}"
    )

    return engine


async def init_engine() -> None:
    """
    Initialize the global database engine.
    Called on application startup.
    """
    global engine

    if engine is not None:
        logger.warning("Database engine already initialized")
        return

    logger.info("Initializing database engine...")

    try:
        engine = create_engine_with_config()

        # Test connection with retry logic
        await test_connection_with_retry()

        logger.info("✅ Database engine initialized successfully")

    except Exception as e:
        logger.error(f"❌ Failed to initialize database engine: {e}")
        raise


async def close_engine() -> None:
    """
    Close the global database engine.
    Called on application shutdown.
    """
    global engine

    if engine is None:
        logger.warning("Database engine not initialized")
        return

    logger.info("Closing database engine...")

    try:
        await engine.dispose()
        engine = None
        logger.info("✅ Database engine closed successfully")

    except Exception as e:
        logger.error(f"❌ Error closing database engine: {e}")
        raise


async def test_connection() -> bool:
    """
    Test database connection.

    Returns:
        True if connection successful, False otherwise
    """
    global engine

    if engine is None:
        logger.error("Database engine not initialized")
        return False

    try:
        async with engine.connect() as conn:
            await conn.execute(select(1))
        logger.info("✅ Database connection test successful")
        return True

    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")
        return False


async def test_connection_with_retry() -> None:
    """
    Test database connection with retry logic.

    Raises:
        Exception if all retry attempts fail
    """
    retry_count = settings.database_connect_retry_count
    retry_delay = settings.database_connect_retry_delay

    for attempt in range(1, retry_count + 1):
        logger.info(f"Testing database connection (attempt {attempt}/{retry_count})...")

        if await test_connection():
            return

        if attempt < retry_count:
            logger.warning(f"Retrying in {retry_delay} seconds...")
            await asyncio.sleep(retry_delay)

    raise Exception(
        f"Failed to connect to database after {retry_count} attempts"
    )


async def init_db() -> None:
    """
    Initialize database tables.
    Creates all tables defined in SQLModel.metadata
    """
    global engine

    if engine is None:
        raise Exception("Database engine not initialized")

    # Import all models to register them with SQLModel
    from models import User, Task, Tag, TaskTag

    logger.info("Creating database tables...")

    try:
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(SQLModel.metadata.create_all)

        logger.info("✅ All database tables created successfully")

    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")
        raise


async def drop_db() -> None:
    """
    Drop all database tables.
    ⚠️ WARNING: This will delete all data!
    """
    global engine

    if engine is None:
        raise Exception("Database engine not initialized")

    from models import User, Task, Tag, TaskTag

    logger.warning("⚠️ Dropping all database tables...")

    try:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)

        logger.info("✅ All database tables dropped")

    except Exception as e:
        logger.error(f"❌ Failed to drop database tables: {e}")
        raise


# Async session factory
async_session_maker = async_sessionmaker(
    bind=lambda: engine,  # Lazy binding to global engine
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database session.

    Usage in FastAPI routes:
        @app.get("/items")
        async def get_items(session: AsyncSession = Depends(get_session)):
            result = await session.execute(select(Item))
            items = result.scalars().all()
            return items

    Session Lifecycle:
    1. Create new session
    2. Yield session to route handler
    3. Commit transaction if no errors
    4. Rollback transaction if error occurs
    5. Close session (cleanup)

    Raises:
        Exception: If database engine not initialized
    """
    global engine

    if engine is None:
        raise Exception("Database engine not initialized. Call init_engine() first.")

    # Create new session
    async with async_session_maker() as session:
        try:
            # Yield session to route handler
            yield session

            # Commit transaction if no errors
            await session.commit()

        except Exception as e:
            # Rollback transaction on error
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise

        finally:
            # Close session (cleanup)
            await session.close()


@asynccontextmanager
async def get_session_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for getting database session outside of FastAPI routes.

    Usage:
        async with get_session_context() as session:
            result = await session.execute(select(Item))
            items = result.scalars().all()
    """
    async for session in get_session():
        yield session


async def get_db_info() -> dict:
    """
    Get database connection information.

    Returns:
        Dictionary with connection pool statistics
    """
    global engine

    if engine is None:
        return {"status": "not_initialized"}

    pool = engine.pool

    return {
        "status": "initialized",
        "pool_size": pool.size(),
        "checked_in_connections": pool.checkedin(),
        "checked_out_connections": pool.checkedout(),
        "overflow_connections": pool.overflow(),
        "total_connections": pool.size() + pool.overflow(),
    }
```

### 6. Update Application Lifespan

**main.py** (updated lifespan):

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from core.config.settings import settings
from core.database import init_engine, close_engine, init_db, get_db_info
from routes import auth, tasks, tags

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Runs on startup and shutdown.
    """
    # Startup
    logger.info("🚀 Starting up...")

    try:
        # Initialize database engine with connection pooling
        await init_engine()

        # Create database tables
        await init_db()

        logger.info("✅ Application startup complete")

    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

    yield

    # Shutdown
    logger.info("👋 Shutting down...")

    try:
        # Close database engine and cleanup connections
        await close_engine()

        logger.info("✅ Application shutdown complete")

    except Exception as e:
        logger.error(f"❌ Shutdown error: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
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


# Health check endpoint with database status
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint with database connection status"""
    db_info = await get_db_info()

    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "database": db_info,
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

### 7. Using Database Session in Routes

**routes/tasks.py** (example):

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from core.database import get_session
from models import Task
from schemas.task import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter()


@router.get("/", response_model=list[TaskResponse])
async def get_tasks(
    user_id: str,
    session: AsyncSession = Depends(get_session),  # Dependency injection
):
    """
    Get all tasks for user.

    Database session is automatically:
    1. Created
    2. Injected into this function
    3. Committed on success
    4. Rolled back on error
    5. Closed after request
    """
    try:
        # Query database
        result = await session.execute(
            select(Task).where(Task.user_id == user_id)
        )
        tasks = result.scalars().all()

        return tasks

    except Exception as e:
        # Session is automatically rolled back
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: str,
    task_data: TaskCreate,
    session: AsyncSession = Depends(get_session),
):
    """Create a new task"""

    try:
        # Create task
        task = Task(
            user_id=user_id,
            title=task_data.title,
            description=task_data.description,
            priority=task_data.priority,
        )

        # Add to session
        session.add(task)

        # Flush to get task.id without committing
        await session.flush()

        # Refresh to load relationships
        await session.refresh(task)

        # Session automatically commits after this function returns
        return task

    except Exception as e:
        # Session is automatically rolled back
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}",
        )
```

### 8. Manual Session Management (Outside Routes)

**Example: Background Task or Script**:

```python
from core.database import get_session_context
from sqlalchemy import select
from models import Task


async def cleanup_old_tasks():
    """Example background task using manual session management"""

    async with get_session_context() as session:
        # Query tasks
        result = await session.execute(
            select(Task).where(Task.completed == True)
        )
        tasks = result.scalars().all()

        # Delete tasks
        for task in tasks:
            await session.delete(task)

        # Session automatically commits on exit
```

### 9. Connection Pool Monitoring

**Add endpoint to monitor pool**:

```python
@app.get("/db/pool-status", tags=["Database"])
async def get_pool_status():
    """Get database connection pool statistics"""
    db_info = await get_db_info()

    if db_info["status"] != "initialized":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not initialized",
        )

    return {
        "pool_size": db_info["pool_size"],
        "checked_in": db_info["checked_in_connections"],
        "checked_out": db_info["checked_out_connections"],
        "overflow": db_info["overflow_connections"],
        "total": db_info["total_connections"],
        "utilization": (
            db_info["checked_out_connections"] / db_info["pool_size"] * 100
            if db_info["pool_size"] > 0 else 0
        ),
    }
```

### 10. Error Handling Best Practices

**Custom Exception Handler**:

```python
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, OperationalError
import logging

logger = logging.getLogger(__name__)


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Handle database integrity errors (unique constraints, foreign keys)"""
    logger.error(f"Database integrity error: {exc}")

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "success": False,
            "message": "Database constraint violation",
            "detail": "The operation conflicts with existing data",
        },
    )


@app.exception_handler(OperationalError)
async def operational_error_handler(request: Request, exc: OperationalError):
    """Handle database operational errors (connection issues)"""
    logger.error(f"Database operational error: {exc}")

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "success": False,
            "message": "Database temporarily unavailable",
            "detail": "Please try again in a few moments",
        },
    )
```

## Connection Pool Configuration Guide

### Development Settings
```python
# Low traffic, local development
pool_size=5
max_overflow=10
pool_timeout=30
pool_recycle=3600
```

### Production Settings (Small App)
```python
# Up to 100 concurrent users
pool_size=10
max_overflow=20
pool_timeout=30
pool_recycle=3600
pool_pre_ping=True
```

### Production Settings (Large App)
```python
# High traffic application
pool_size=20
max_overflow=40
pool_timeout=30
pool_recycle=1800  # 30 minutes
pool_pre_ping=True
```

### Neon Serverless Specific
```python
# Optimize for Neon's auto-pause behavior
pool_size=5  # Smaller pool for serverless
max_overflow=15
pool_timeout=30
pool_recycle=600  # 10 minutes (shorter for serverless)
pool_pre_ping=True  # Critical for auto-pause handling
```

## Best Practices

1. **Always Use Dependency Injection**: Use `Depends(get_session)` in routes
2. **Never Store Sessions**: Create new session for each request
3. **Enable pool_pre_ping**: Handles Neon's auto-pause gracefully
4. **Configure Timeouts**: Set connection and command timeouts
5. **Monitor Pool Usage**: Track connection pool utilization
6. **Handle Errors**: Add exception handlers for database errors
7. **Test Connection**: Verify connection on startup with retry logic
8. **Cleanup Properly**: Close engine on shutdown
9. **Use Context Managers**: For manual session management
10. **Log Appropriately**: Log connection events and errors

## Common Patterns

### Dependency Injection Pattern
```python
@router.get("/items")
async def get_items(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Item))
    return result.scalars().all()
```

### Transaction Pattern
```python
async with get_session_context() as session:
    # Multiple operations in single transaction
    item1 = Item(name="Item 1")
    item2 = Item(name="Item 2")
    session.add_all([item1, item2])
    # Commits automatically on exit
```

### Nested Transaction Pattern
```python
async with session.begin_nested():
    # Savepoint for partial rollback
    item = Item(name="Test")
    session.add(item)
    # Rollback to savepoint if needed
```

## Success Criteria

- ✅ Neon PostgreSQL connection string configured
- ✅ Async engine created with connection pooling
- ✅ Dependency injection for session management
- ✅ Proper session lifecycle (create, commit, rollback, close)
- ✅ Connection retry logic implemented
- ✅ Error handling for database exceptions
- ✅ Connection pool monitoring available
- ✅ Cleanup on application shutdown
- ✅ pool_pre_ping enabled for Neon
- ✅ Logging configured for database events

## Troubleshooting

### Issue: Connection timeout errors
**Solution**: Increase `pool_timeout` or `pool_size`, check network connectivity

### Issue: Too many connections error
**Solution**: Reduce `pool_size` + `max_overflow`, check for connection leaks

### Issue: Neon database auto-pauses
**Solution**: Enable `pool_pre_ping=True` to wake database automatically

### Issue: Stale connections
**Solution**: Reduce `pool_recycle` value, enable `pool_pre_ping`

### Issue: Slow queries
**Solution**: Enable `echo=True` to log SQL, analyze queries, add indexes

## Related Skills

- `fastapi_project_setup`: FastAPI application setup
- `sqlmodel_schema_design`: Database models
- `async_route_handlers`: Using sessions in routes

## References

- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Neon Documentation](https://neon.tech/docs/introduction)
- [AsyncPG Documentation](https://magicstack.github.io/asyncpg/)
- [Connection Pooling Guide](https://docs.sqlalchemy.org/en/20/core/pooling.html)

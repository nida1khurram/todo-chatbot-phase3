import logging
from sqlmodel import create_engine, Session
from .settings import settings
import os

# Set up logging
logger = logging.getLogger(__name__)

# Database URL construction
if settings.database_url:
    DATABASE_URL = settings.database_url
    logger.info("Using database URL from settings")
else:
    DATABASE_URL = f"postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"
    logger.info(f"Using constructed database URL with host: {settings.db_host}")

# Create the database engine
if DATABASE_URL.startswith("sqlite"):
    # SQLite-specific engine configuration
    engine = create_engine(
        DATABASE_URL,
        echo=settings.db_echo,
        connect_args={"check_same_thread": False}  # Required for SQLite with threading
    )
else:
    # PostgreSQL-specific engine configuration
    engine = create_engine(
        DATABASE_URL,
        echo=settings.db_echo,  # Set to True to see SQL queries in logs
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=300,  # Recycle connections after 5 minutes
    )
logger.info("Database engine created successfully")

def get_session():
    """Dependency to get database session"""
    logger.debug("Creating database session")
    with Session(engine) as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            logger.debug("Database session closed")
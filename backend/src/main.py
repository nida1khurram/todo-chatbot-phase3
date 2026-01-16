import logging
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .api import auth, tasks, chat
from .database import engine
from .models import Base
from .middleware.validation import ValidationMiddleware
from .middleware.security import SecurityHeadersMiddleware
from .logging_config import setup_logging

# Set up centralized logging
setup_logging(log_level="INFO")
logger = logging.getLogger(__name__)

# Set up rate limiter
limiter = Limiter(key_func=get_remote_address)
logger.info("Rate limiter initialized")

# Create database tables
Base.metadata.create_all(bind=engine)
logger.info("Database tables created successfully")

app = FastAPI(title="Todo API", version="1.0.0")

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


from fastapi.middleware.cors import CORSMiddleware

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Add exposed headers to ensure authorization headers are accessible
    expose_headers=["Access-Control-Allow-Origin", "Access-Control-Allow-Credentials"]
)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Add validation middleware - temporarily disabled due to request body consumption issue
# app.add_middleware(ValidationMiddleware)

# Include API routes
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
app.include_router(chat.router, prefix="/api", tags=["chat"])

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Todo API is running!"}

@app.get("/health")
def health_check():
    logger.info("Health check endpoint accessed")
    return {"status": "healthy"}
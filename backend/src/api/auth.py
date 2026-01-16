import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from datetime import timedelta
from pydantic import EmailStr
from ..database import get_session
from ..models.user import User
from ..schemas.user import UserCreate, UserRead
from ..middleware.auth import verify_password, get_password_hash, create_access_token, get_current_user
from ..services.user_service import create_user, authenticate_user

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/register", response_model=UserRead)
def register(user: UserCreate, session: Session = Depends(get_session)):
    """
    Register a new user
    """
    logger.info(f"Registration attempt for email: {user.email}")
    try:
        # Validate email format
        if "@" not in user.email:
            logger.warning(f"Invalid email format attempted: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )

        # Check if user already exists
        db_user = session.query(User).filter(User.email == user.email).first()
        if db_user:
            logger.warning(f"Registration attempted for existing email: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Validate password strength (minimum length)
        if len(user.password) < 6:
            logger.warning(f"Password too short for email: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters long"
            )

        hashed_password = get_password_hash(user.password)
        db_user = create_user(session, user.email, hashed_password)
        logger.info(f"Successfully registered user: {db_user.email}")
        return db_user
    except HTTPException:
        # Re-raise HTTP exceptions
        logger.warning(f"Registration failed for email: {user.email}")
        raise
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error during registration for {user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during registration"
        )

@router.post("/login")
def login(user: UserCreate, session: Session = Depends(get_session)):
    """
    Login and return access token
    """
    logger.info(f"Login attempt for email: {user.email}")
    try:
        # Validate email format
        if "@" not in user.email:
            logger.warning(f"Invalid email format attempted for login: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )

        authenticated_user = authenticate_user(session, user.email, user.password)
        if not authenticated_user:
            logger.warning(f"Failed login attempt for email: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not authenticated_user.is_active:
            logger.warning(f"Login attempt for inactive account: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive account",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=30)  # Use settings from config
        access_token = create_access_token(
            data={"sub": str(authenticated_user.id)}, expires_delta=access_token_expires
        )

        logger.info(f"Successful login for user: {authenticated_user.email}")
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": authenticated_user.id,
                "email": authenticated_user.email
            }
        }
    except HTTPException:
        # Re-raise HTTP exceptions
        logger.warning(f"Login failed for email: {user.email}")
        raise
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error during login for {user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login"
        )


@router.post("/logout")
def logout():
    """
    Logout user (currently just a success response since JWTs are stateless)
    In a production system, you might implement token blacklisting
    """
    logger.info("Logout request received")
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserRead)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's information
    """
    logger.info(f"Retrieving user information for user ID: {current_user.id}")
    return current_user
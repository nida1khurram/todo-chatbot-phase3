import logging
from sqlmodel import Session
from typing import Optional
from ..models.user import User
from ..middleware.auth import verify_password

# Set up logging
logger = logging.getLogger(__name__)

def create_user(session: Session, email: str, hashed_password: str) -> User:
    """
    Create a new user with the given email and hashed password
    """
    logger.info(f"Creating new user with email: {email}")
    try:
        user = User(email=email, password_hash=hashed_password)
        session.add(user)
        session.commit()
        session.refresh(user)
        logger.info(f"Successfully created user with ID: {user.id}")
        return user
    except Exception as e:
        logger.error(f"Error creating user with email {email}: {str(e)}")
        raise

def authenticate_user(session: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user by email and password
    """
    logger.info(f"Authenticating user with email: {email}")
    try:
        user = session.query(User).filter(User.email == email).first()
        if not user:
            logger.info(f"Authentication failed - user with email {email} not found")
            return None
        if not verify_password(password, user.password_hash):
            logger.info(f"Authentication failed - invalid password for email {email}")
            return None
        logger.info(f"Successfully authenticated user with ID: {user.id}")
        return user
    except Exception as e:
        logger.error(f"Error authenticating user with email {email}: {str(e)}")
        raise

def get_user_by_email(session: Session, email: str) -> Optional[User]:
    """
    Get a user by their email address
    """
    logger.info(f"Retrieving user by email: {email}")
    try:
        user = session.query(User).filter(User.email == email).first()
        if user:
            logger.info(f"Found user with ID: {user.id}")
        else:
            logger.info(f"No user found with email: {email}")
        return user
    except Exception as e:
        logger.error(f"Error retrieving user by email {email}: {str(e)}")
        raise

def get_user_by_id(session: Session, user_id: int) -> Optional[User]:
    """
    Get a user by their ID
    """
    logger.info(f"Retrieving user by ID: {user_id}")
    try:
        user = session.get(User, user_id)
        if user:
            logger.info(f"Found user with email: {user.email}")
        else:
            logger.info(f"No user found with ID: {user_id}")
        return user
    except Exception as e:
        logger.error(f"Error retrieving user by ID {user_id}: {str(e)}")
        raise
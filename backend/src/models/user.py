from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, Optional, List
from datetime import datetime
from pydantic import validator
from sqlalchemy import Index

if TYPE_CHECKING:
    from .task import Task
    from .conversation import Conversation
    from .message import Message

class UserBase(SQLModel):
    email: str = Field(unique=True, nullable=False, index=True)  # Index for email lookups
    is_active: bool = Field(default=True, index=True)  # Index for filtering active users

class User(SQLModel, table=True):
    """
    User model representing a registered user in the system with authentication credentials
    """
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, nullable=False, index=True)  # Index for email lookups
    is_active: bool = Field(default=True, index=True)  # Index for filtering active users
    password_hash: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)  # Index for time-based queries
    updated_at: datetime = Field(default_factory=datetime.utcnow, index=True)  # Index for time-based queries

    # Relationships to other models
    tasks: List["Task"] = Relationship(back_populates="user")
    conversations: List["Conversation"] = Relationship(back_populates="user")
    messages: List["Message"] = Relationship(back_populates="user")

    # Add composite index for common query patterns
    __table_args__ = (Index('idx_email_active', 'email', 'is_active'),)

    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email address')
        return v

    class Config:
        arbitrary_types_allowed = True
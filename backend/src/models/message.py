"""
Message Model for Todo AI Chatbot
This module defines the Message entity for storing chat messages
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, Optional
from datetime import datetime
import sqlalchemy as sa

if TYPE_CHECKING:
    from .user import User
    from .conversation import Conversation


class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    conversation_id: int = Field(foreign_key="conversations.id")
    role: str = Field(sa_column_kwargs={"name": "role"})  # Will store "user" or "assistant"
    content: str = Field(sa_column=sa.TEXT)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship(back_populates="messages")
    conversation: "Conversation" = Relationship(back_populates="messages")
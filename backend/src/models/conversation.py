"""
Conversation Model for Todo AI Chatbot
This module defines the Conversation entity for storing chat conversations
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, List, Optional
from datetime import datetime

if TYPE_CHECKING:
    from .user import User
    from .message import Message


class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation")
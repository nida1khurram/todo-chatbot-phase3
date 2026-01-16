"""
Message Service for Todo AI Chatbot
This module provides business logic for message management
"""

from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
from backend.src.models.message import Message
from backend.src.models.user import User


class MessageService:
    def __init__(self, session: Session):
        self.session = session

    def add_message(self, conversation_id: int, user_id: int, role: str, content: str) -> Message:
        """Add a message to a conversation"""
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content
        )
        self.session.add(message)
        self.session.commit()
        self.session.refresh(message)
        return message

    def get_messages(self, conversation_id: int, user_id: int, limit: int = 50) -> List[Message]:
        """Get messages from a conversation"""
        statement = select(Message).where(
            Message.conversation_id == conversation_id,
            Message.user_id == user_id
        ).order_by(Message.created_at.asc()).limit(limit)

        messages = self.session.exec(statement).all()
        return messages

    def get_message(self, message_id: int, user_id: int) -> Optional[Message]:
        """Get a specific message for a user"""
        statement = select(Message).where(
            Message.id == message_id,
            Message.user_id == user_id
        )
        return self.session.exec(statement).first()
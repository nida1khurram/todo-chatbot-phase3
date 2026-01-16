"""
Chat Service for Todo AI Chatbot
This module provides business logic for chat operations and conversation management
"""

from sqlmodel import Session, select
from typing import List, Optional
from ..models.conversation import Conversation
from ..models.message import Message
from ..models.user import User
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self, session: Session):
        self.session = session

    def create_conversation(self, user_id) -> Conversation:
        """Create a new conversation for a user"""
        # Handle both integer user IDs and guest identifiers
        conversation = Conversation(user_id=user_id if isinstance(user_id, int) else -1)  # Use -1 for guest users
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)
        logger.info(f"Created new conversation {conversation.id} for user {user_id}")
        return conversation

    def get_conversation(self, conversation_id: int, user_id) -> Optional[Conversation]:
        """Get a specific conversation for a user"""
        # Handle both integer user IDs and guest identifiers
        user_filter = user_id if isinstance(user_id, int) else -1
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_filter
        )
        return self.session.exec(statement).first()

    def get_or_create_conversation(self, conversation_id: Optional[int], user_id) -> Conversation:
        """Get existing conversation or create new one"""
        if conversation_id:
            conversation = self.get_conversation(conversation_id, user_id)
            if conversation:
                return conversation

        # Create new conversation if none found
        return self.create_conversation(user_id)

    def add_message(self, conversation_id: int, user_id, role: str, content: str) -> Message:
        """Add a message to a conversation"""
        # Handle both integer user IDs and guest identifiers
        message_user_id = user_id if isinstance(user_id, int) else -1
        message = Message(
            conversation_id=conversation_id,
            user_id=message_user_id,
            role=role,
            content=content
        )
        self.session.add(message)
        self.session.commit()
        self.session.refresh(message)
        logger.info(f"Added {role} message to conversation {conversation_id}")
        return message

    def get_conversation_history(self, conversation_id: int, user_id, limit: int = 50) -> List[Message]:
        """Get conversation history with message limit"""
        # Handle both integer user IDs and guest identifiers
        user_filter = user_id if isinstance(user_id, int) else -1
        statement = select(Message).where(
            Message.conversation_id == conversation_id,
            Message.user_id == user_filter
        ).order_by(Message.created_at.asc()).limit(limit)

        messages = self.session.exec(statement).all()
        logger.info(f"Retrieved {len(messages)} messages from conversation {conversation_id}")
        return messages

    def update_conversation_timestamp(self, conversation_id: int):
        """Update the updated_at timestamp for a conversation"""
        conversation = self.session.get(Conversation, conversation_id)
        if conversation:
            conversation.updated_at = datetime.utcnow()
            self.session.add(conversation)
            self.session.commit()
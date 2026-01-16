"""
Conversation Service for Todo AI Chatbot
This module provides business logic for conversation management
"""

from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
from backend.src.models.conversation import Conversation
from backend.src.models.message import Message
from backend.src.models.user import User


class ConversationService:
    def __init__(self, session: Session):
        self.session = session

    def create_conversation(self, user_id: int) -> Conversation:
        """Create a new conversation for a user"""
        conversation = Conversation(user_id=user_id)
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)
        return conversation

    def get_conversation(self, conversation_id: int, user_id: int) -> Optional[Conversation]:
        """Get a specific conversation for a user"""
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        return self.session.exec(statement).first()

    def get_or_create_conversation(self, conversation_id: Optional[int], user_id: int) -> Conversation:
        """Get existing conversation or create new one"""
        if conversation_id:
            conversation = self.get_conversation(conversation_id, user_id)
            if conversation:
                return conversation

        # Create new conversation if none found
        return self.create_conversation(user_id)

    def get_conversation_history(self, conversation_id: int, user_id: int, limit: int = 50) -> List[Message]:
        """Get conversation history with message limit"""
        statement = select(Message).where(
            Message.conversation_id == conversation_id,
            Message.user_id == user_id
        ).order_by(Message.created_at.asc()).limit(limit)

        messages = self.session.exec(statement).all()
        return messages

    def update_conversation_timestamp(self, conversation_id: int):
        """Update the updated_at timestamp for a conversation"""
        conversation = self.session.get(Conversation, conversation_id)
        if conversation:
            conversation.updated_at = datetime.utcnow()
            self.session.add(conversation)
            self.session.commit()
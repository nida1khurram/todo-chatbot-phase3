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
import re

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self, session: Session):
        self.session = session

    def _ensure_guest_user_exists(self, user_id_str: str) -> int:
        """Ensure a guest user exists in the database, creating one if needed"""
        from ..middleware.auth import get_password_hash
        
        # Check if this is a guest user identifier (contains 'guest')
        if 'guest' in user_id_str.lower():
            # Try to find an existing guest user with this identifier
            # We'll use a deterministic approach to map guest IDs to user records
            # Create a hash-like value for the guest ID
            guest_hash = abs(hash(user_id_str)) % 1000000  # Keep it within reasonable range
            
            # Look for existing guest user with this hash
            statement = select(User).where(User.email == f"guest_{guest_hash}@example.com")
            existing_user = self.session.exec(statement).first()
            
            if existing_user:
                return existing_user.id
            else:
                # Create a new guest user with a dummy password hash
                dummy_password_hash = get_password_hash("guest_default_password")
                
                guest_user = User(
                    email=f"guest_{guest_hash}@example.com",
                    username=f"guest_{guest_hash}",
                    password_hash=dummy_password_hash,  # Properly hashed password
                    is_active=True
                )
                self.session.add(guest_user)
                self.session.commit()
                self.session.refresh(guest_user)
                return guest_user.id
        else:
            # For numeric user IDs, return as-is
            try:
                return int(user_id_str)
            except ValueError:
                # If it's not a number and not a guest ID, treat as guest
                guest_hash = abs(hash(str(user_id_str))) % 1000000
                statement = select(User).where(User.email == f"guest_{guest_hash}@example.com")
                existing_user = self.session.exec(statement).first()
                
                if existing_user:
                    return existing_user.id
                else:
                    dummy_password_hash = get_password_hash("guest_default_password")
                    
                    guest_user = User(
                        email=f"guest_{guest_hash}@example.com",
                        username=f"user_{guest_hash}",
                        password_hash=dummy_password_hash,
                        is_active=True
                    )
                    self.session.add(guest_user)
                    self.session.commit()
                    self.session.refresh(guest_user)
                    return guest_user.id

    def create_conversation(self, user_id) -> Conversation:
        """Create a new conversation for a user"""
        # Handle both registered users and guest users
        actual_user_id = self._ensure_guest_user_exists(str(user_id))
        
        conversation = Conversation(user_id=actual_user_id)
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)
        logger.info(f"Created new conversation {conversation.id} for user {actual_user_id} (original: {user_id})")
        return conversation

    def get_conversation(self, conversation_id: int, user_id) -> Optional[Conversation]:
        """Get a specific conversation for a user"""
        # Handle both registered users and guest users
        actual_user_id = self._ensure_guest_user_exists(str(user_id))
        
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == actual_user_id
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
        # Handle both registered users and guest users
        actual_user_id = self._ensure_guest_user_exists(str(user_id))
        
        message = Message(
            conversation_id=conversation_id,
            user_id=actual_user_id,
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
        # Handle both registered users and guest users
        actual_user_id = self._ensure_guest_user_exists(str(user_id))
        
        statement = select(Message).where(
            Message.conversation_id == conversation_id,
            Message.user_id == actual_user_id
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
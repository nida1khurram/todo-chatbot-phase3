# Stateless Chat Endpoint Skill

## Description
Create a stateless chat endpoint that persists conversation state to the database while maintaining server scalability. Implements proper conversation flow with database-backed persistence and integrates with AI agents and existing authentication.

## When to Use This Skill
- Creating scalable chat endpoints that don't store state in memory
- Building persistent conversation history
- Ensuring horizontal scalability for chat services
- Integrating AI agents with database persistence
- Maintaining conversation context across server restarts

## Prerequisites
- Database models for Conversation and Message entities
- Existing authentication system with JWT validation
- AI agent service ready to process messages
- MCP tools available for task operations
- Proper error handling and validation in place

## Implementation Steps

### 1. Define Database Models for Chat
```python
# backend/src/models/chat.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import TYPE_CHECKING
from .base import Base  # Assuming you have a base model

if TYPE_CHECKING:
    from .user import User
    from .task import Task

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="messages")
    conversation = relationship("Conversation", back_populates="messages")
```

### 2. Create Chat Schemas
```python
# backend/src/schemas/chat.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class MessageBase(BaseModel):
    role: str
    content: str

class MessageCreate(MessageBase):
    pass

class MessageRead(MessageBase):
    id: int
    user_id: int
    conversation_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationBase(BaseModel):
    pass

class ConversationCreate(ConversationBase):
    pass

class ConversationRead(ConversationBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None

class ChatResponse(BaseModel):
    conversation_id: int
    response: str
    tool_calls: Optional[List[dict]] = []

class ChatHistoryResponse(BaseModel):
    messages: List[MessageRead]
    conversation_id: int
```

### 3. Create Chat Service
```python
# backend/src/services/chat_service.py
from sqlmodel import Session, select
from typing import List, Optional
from ..models.chat import Conversation, Message
from ..models.user import User
from ..schemas.chat import MessageCreate, ConversationCreate
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, session: Session):
        self.session = session

    def create_conversation(self, user_id: int) -> Conversation:
        """Create a new conversation for a user"""
        conversation = Conversation(user_id=user_id)
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)
        logger.info(f"Created new conversation {conversation.id} for user {user_id}")
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
        logger.info(f"Added {role} message to conversation {conversation_id}")
        return message

    def get_conversation_history(self, conversation_id: int, user_id: int, limit: int = 50) -> List[Message]:
        """Get conversation history with message limit"""
        statement = select(Message).where(
            Message.conversation_id == conversation_id,
            Message.user_id == user_id
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
```

### 4. Create Chat API Routes
```python
# backend/src/api/chat.py
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List, Optional
from ..database import get_session
from ..models.user import User
from ..middleware.auth import get_current_user
from ..schemas.chat import ChatRequest, ChatResponse, ChatHistoryResponse
from ..services.chat_service import ChatService
from ..services.ai_agent_manager import AIAgentManager
import json

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat_endpoint(
    user_id: str,
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Chat endpoint that processes user messages and returns AI responses.
    This endpoint is stateless - all conversation state is persisted to the database.
    """
    logger.info(f"User {current_user.id} sending chat message")

    # Verify that the user_id in the path matches the authenticated user
    if str(current_user.id) != user_id:
        logger.warning(f"User {current_user.id} attempted to access chat for user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    try:
        # Initialize services
        chat_service = ChatService(session)
        ai_agent_manager = AIAgentManager()

        # Get or create conversation
        conversation = chat_service.get_or_create_conversation(chat_request.conversation_id, current_user.id)

        # Add user message to conversation
        user_message = chat_service.add_message(
            conversation_id=conversation.id,
            user_id=current_user.id,
            role="user",
            content=chat_request.message
        )

        # Get conversation history for context
        history_messages = chat_service.get_conversation_history(conversation.id, current_user.id)

        # Format history for AI agent (convert to the format expected by the AI)
        formatted_history = []
        for msg in history_messages:
            formatted_history.append({
                "role": msg.role,
                "content": msg.content
            })

        # Process message with AI agent
        ai_result = await ai_agent_manager.process_message(
            user_id=str(current_user.id),
            message=chat_request.message,
            conversation_history=formatted_history[:-1]  # Exclude the current message we just added
        )

        # Extract AI response
        if ai_result["type"] == "tool_calls":
            response_content = ai_result.get("content", "Processing your request...")
            tool_calls = ai_result.get("tool_calls", [])
        else:
            response_content = ai_result.get("content", "I'm here to help with your tasks!")
            tool_calls = []

        # Add AI response to conversation
        ai_message = chat_service.add_message(
            conversation_id=conversation.id,
            user_id=current_user.id,  # This represents the assistant's user context
            role="assistant",
            content=response_content
        )

        # Update conversation timestamp
        chat_service.update_conversation_timestamp(conversation.id)

        logger.info(f"Chat response generated for conversation {conversation.id}")

        return ChatResponse(
            conversation_id=conversation.id,
            response=response_content,
            tool_calls=tool_calls
        )

    except Exception as e:
        logger.error(f"Error processing chat request for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        )

@router.get("/{user_id}/conversations/{conversation_id}/history", response_model=ChatHistoryResponse)
def get_conversation_history(
    user_id: str,
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get the history of a specific conversation.
    """
    logger.info(f"User {current_user.id} requesting conversation history {conversation_id}")

    # Verify that the user_id in the path matches the authenticated user
    if str(current_user.id) != user_id:
        logger.warning(f"User {current_user.id} attempted to access history for user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    try:
        chat_service = ChatService(session)

        # Verify conversation belongs to user
        conversation = chat_service.get_conversation(conversation_id, current_user.id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Get messages
        messages = chat_service.get_conversation_history(conversation_id, current_user.id)

        return ChatHistoryResponse(
            messages=messages,
            conversation_id=conversation_id
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving conversation history {conversation_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the conversation history"
        )
```

### 5. Update Main Application to Include Chat Routes
```python
# Update backend/src/main.py to include chat routes
# Add this line to the imports:
# from .api import auth, tasks, chat

# Add this line to include the chat router:
# app.include_router(chat.router, prefix="/api", tags=["chat"])
```

### 6. Create Database Migration
```python
# backend/src/database/migrations/chat_tables.py
from sqlmodel import Session, create_engine
from ..models.chat import Conversation, Message
from ..models.base import Base

def create_chat_tables(engine):
    """Create chat-related database tables"""
    Base.metadata.create_all(bind=engine)
    print("Chat tables created successfully")
```

## Key Implementation Notes

### Stateless Architecture
- Server holds no in-memory state
- All conversation data persisted to database
- Server restarts don't affect conversation continuity
- Horizontal scalability supported

### Data Isolation
- User ID validation in all endpoints
- Conversation access limited to owning user
- Message retrieval filtered by user ID
- Proper foreign key relationships

### Error Handling
- Comprehensive error handling for all operations
- Proper HTTP status codes
- Detailed logging for debugging
- Graceful degradation for AI service failures

### Performance Considerations
- Message history limits to prevent excessive loading
- Proper indexing on database tables
- Efficient querying with joins
- Connection pooling for database access

## Testing Strategy
```python
# backend/tests/test_chat_endpoint.py
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from unittest.mock import AsyncMock, patch
from backend.src.main import app
from backend.src.models.chat import Conversation, Message

client = TestClient(app)

@pytest.fixture
def mock_ai_agent():
    with patch('backend.src.services.ai_agent_manager.AIAgentManager') as mock:
        mock_instance = AsyncMock()
        mock_instance.process_message.return_value = {
            "type": "message",
            "content": "I've processed your request"
        }
        mock.return_value = mock_instance
        yield mock_instance

def test_chat_endpoint_success(client, db_session, authenticated_headers, mock_ai_agent):
    # Create a conversation
    response = client.post(
        "/api/1/chat",
        json={"message": "Hello", "conversation_id": None},
        headers=authenticated_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert "response" in data

    # Verify conversation was created
    conversation = db_session.get(Conversation, data["conversation_id"])
    assert conversation is not None
    assert conversation.user_id == 1

def test_chat_endpoint_invalid_user(client, authenticated_headers, mock_ai_agent):
    # Try to access another user's chat endpoint
    response = client.post(
        "/api/999/chat",  # Different user ID
        json={"message": "Hello", "conversation_id": None},
        headers=authenticated_headers
    )

    assert response.status_code == 403  # Forbidden

def test_conversation_history(client, db_session, authenticated_headers, mock_ai_agent):
    # First create a conversation
    response = client.post(
        "/api/1/chat",
        json={"message": "Hello", "conversation_id": None},
        headers=authenticated_headers
    )

    conversation_id = response.json()["conversation_id"]

    # Get conversation history
    response = client.get(
        f"/api/1/conversations/{conversation_id}/history",
        headers=authenticated_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert "messages" in data
    assert len(data["messages"]) >= 2  # User message + AI response
```

## Common Issues and Solutions

### Issue: Database Transaction Management
**Problem**: Messages not properly saved due to transaction issues
**Solution**: Ensure proper session management and commit/rollback handling

### Issue: Authentication Mismatch
**Problem**: User ID in path doesn't match authenticated user
**Solution**: Always validate that path user_id matches current_user.id

### Issue: Conversation Continuity
**Problem**: New conversation created on each request instead of continuing
**Solution**: Properly handle conversation_id parameter and retrieve existing conversations

### Issue: AI Response Processing
**Problem**: AI responses not properly formatted for frontend
**Solution**: Ensure consistent response format with tool_calls and content

## Success Criteria
- [ ] Stateless architecture with no server-side state
- [ ] Conversation state persisted to database
- [ ] Proper user isolation maintained
- [ ] Authentication enforced on all endpoints
- [ ] Conversation history retrievable
- [ ] AI integration working properly
- [ ] Error handling implemented comprehensively
- [ ] Database migrations created for chat models

## Files Created
- `backend/src/models/chat.py` - Database models for conversations and messages
- `backend/src/schemas/chat.py` - Pydantic schemas for chat data
- `backend/src/services/chat_service.py` - Business logic for chat operations
- `backend/src/api/chat.py` - API endpoints for chat functionality
- `backend/src/database/migrations/chat_tables.py` - Database migration helper
- `backend/tests/test_chat_endpoint.py` - Tests (optional)
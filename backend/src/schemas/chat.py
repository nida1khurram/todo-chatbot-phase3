"""
Chat Schemas for Todo AI Chatbot
This module defines Pydantic schemas for chat-related data structures
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from .user import UserRead
from .task import TaskRead


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
    tool_calls: Optional[List[Dict[str, Any]]] = []


class ChatHistoryResponse(BaseModel):
    messages: List[MessageRead]
    conversation_id: int


class ToolCall(BaseModel):
    id: str
    function: Dict[str, Any]
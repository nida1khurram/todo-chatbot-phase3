from sqlmodel import SQLModel

# Export Base as SQLModel for compatibility
Base = SQLModel

# Import all models to register them
from .user import User
from .task import Task
from .conversation import Conversation
from .message import Message

# Make them available when importing from .models
__all__ = ["Base", "User", "Task", "Conversation", "Message"]
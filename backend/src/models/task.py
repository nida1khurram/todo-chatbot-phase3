from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, Optional
from datetime import datetime
from sqlalchemy import Index

if TYPE_CHECKING:
    from .user import User

class TaskBase(SQLModel):
    title: str = Field(nullable=False, min_length=1)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False, index=True)  # Index for filtering completed tasks
    user_id: int = Field(foreign_key="users.id", nullable=False, index=True)  # Index for user-based queries
    due_date: Optional[datetime] = Field(default=None, index=True)  # Index for date-based queries
    priority: str = Field(default="medium", index=True)  # low, medium, high
    tags: Optional[str] = Field(default=None, index=True)  # Comma-separated tags
    recurrence_rule: Optional[str] = Field(default=None)  # Rule for recurring tasks (e.g., daily, weekly, monthly)
    recurrence_end_date: Optional[datetime] = Field(default=None)  # End date for recurring tasks

class Task(TaskBase, table=True):
    """
    Task model representing a todo item created by a specific user
    """
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)  # Index for time-based queries
    updated_at: datetime = Field(default_factory=datetime.utcnow, index=True)  # Index for time-based queries

    # Relationship to User
    user: Optional["User"] = Relationship(back_populates="tasks")

    # Add composite index for common query patterns (user_id + completed)
    __table_args__ = (Index('idx_user_completed', 'user_id', 'completed'),
                      Index('idx_user_created', 'user_id', 'created_at'),
                      Index('idx_user_due_date', 'user_id', 'due_date'))

    class Config:
        arbitrary_types_allowed = True
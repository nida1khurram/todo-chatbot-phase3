from sqlmodel import SQLModel
from typing import Optional
from datetime import datetime
from pydantic import field_validator

class TaskBase(SQLModel):
    title: str
    description: Optional[str] = None
    completed: bool = False
    due_date: Optional[datetime] = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Title cannot be empty')
        if len(v) > 200:
            raise ValueError('Title must be less than 200 characters')
        return v.strip()

    @field_validator('description', mode='before')
    @classmethod
    def validate_description(cls, v):
        if v and len(v) > 1000:
            raise ValueError('Description must be less than 1000 characters')
        return v

class TaskCreate(TaskBase):
    pass

class TaskRead(TaskBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    due_date: Optional[datetime] = None

    @field_validator('title', mode='before')
    @classmethod
    def validate_title(cls, v):
        if v is not None:  # Only validate if the field is provided
            if not v or len(v.strip()) == 0:
                raise ValueError('Title cannot be empty')
            if len(v) > 200:
                raise ValueError('Title must be less than 200 characters')
            return v.strip()
        return v

    @field_validator('description', mode='before')
    @classmethod
    def validate_description(cls, v):
        if v is not None:  # Only validate if the field is provided
            if len(v) > 1000:
                raise ValueError('Description must be less than 1000 characters')
        return v
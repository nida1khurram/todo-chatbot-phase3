from sqlmodel import SQLModel
from typing import Optional
from datetime import datetime
from pydantic import field_validator

class TaskBase(SQLModel):
    title: str
    description: Optional[str] = None
    completed: bool = False
    due_date: Optional[datetime] = None
    priority: str = "medium"  # low, medium, high
    tags: Optional[str] = None  # Comma-separated tags
    recurrence_rule: Optional[str] = None  # Rule for recurring tasks (e.g., daily, weekly, monthly)
    recurrence_end_date: Optional[datetime] = None  # End date for recurring tasks

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

    @field_validator('priority', mode='before')
    @classmethod
    def validate_priority(cls, v):
        if v and v not in ['low', 'medium', 'high']:
            raise ValueError('Priority must be low, medium, or high')
        return v

    @field_validator('recurrence_rule', mode='before')
    @classmethod
    def validate_recurrence_rule(cls, v):
        valid_rules = [None, 'daily', 'weekly', 'monthly', 'yearly']
        if v not in valid_rules:
            raise ValueError('Recurrence rule must be daily, weekly, monthly, or yearly')
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
    priority: Optional[str] = None
    tags: Optional[str] = None
    recurrence_rule: Optional[str] = None
    recurrence_end_date: Optional[datetime] = None

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

    @field_validator('priority', mode='before')
    @classmethod
    def validate_priority(cls, v):
        if v is not None:  # Only validate if the field is provided
            if v not in ['low', 'medium', 'high']:
                raise ValueError('Priority must be low, medium, or high')
        return v

    @field_validator('recurrence_rule', mode='before')
    @classmethod
    def validate_recurrence_rule(cls, v):
        if v is not None:  # Only validate if the field is provided
            valid_rules = [None, 'daily', 'weekly', 'monthly', 'yearly']
            if v not in valid_rules:
                raise ValueError('Recurrence rule must be daily, weekly, monthly, or yearly')
        return v
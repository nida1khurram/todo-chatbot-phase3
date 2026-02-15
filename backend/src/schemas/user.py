from sqlmodel import SQLModel
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator

class UserBase(SQLModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v

class UserRead(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class UserUpdate(SQLModel):
    email: Optional[str] = None
    is_active: Optional[bool] = None
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.user import UserRole

# TODO: Create pydantic schemas for User

class UserBase(BaseModel):
    """
    Base User schema with common attributes
    """
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    """
    Schema for creating a new user (includes password)
    """
    password: str = Field(..., min_length=8)
    role: Optional[UserRole] = UserRole.USER

class UserUpdate(BaseModel):
    """
    Schema for updating user information
    """
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None

class UserInDB(UserBase):
    """
    Schema for user stored in database (includes password_hash)
    """
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    password_hash: str

    class Config:
        from_attributes = True  # Enable ORM mode

class UserResponse(UserBase):
    """
    Schema for API responses (excludes password_hash)
    """
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
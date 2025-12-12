from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from app.db.session import Base
import enum

class UserRole(str, enum.Enum):
    """
    User roles for RBAC (Role-Based Access Control).
    """
    ADMIN = "admin"
    AGENT = "agent"
    USER = "user"

class User(Base):
    """
    User model for authentication and authorization.

    Roles:
    - ADMIN: Full access to all resources
    - AGENT: Can view and manage tickets to them
    - USER: Can only create and view their own tickets
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<User{self.email}>"
    
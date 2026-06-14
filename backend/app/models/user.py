import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlmodel import Field, Relationship, SQLModel


class UserRole(str, Enum):
    LEARNER = "learner"
    INSTRUCTOR = "instructor"
    COORDINATOR = "coordinator"
    PARENT = "parent"
    ADMIN = "admin"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(index=True, unique=True)
    role: UserRole = Field(default=UserRole.LEARNER)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    profile: "StudentProfile" = Relationship(back_populates="user")
    consents: list["ConsentGrant"] = Relationship(back_populates="user")

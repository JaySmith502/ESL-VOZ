import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON
from sqlmodel import Column, Field, Relationship, SQLModel


class Attempt(SQLModel, table=True):
    __tablename__ = "attempts"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    student_id: uuid.UUID = Field(foreign_key="student_profiles.id")
    activity_type: str
    lesson_id: str | None = Field(default=None)
    step_id: str | None = Field(default=None)
    mode: str | None = Field(default=None)
    cefr_band: str | None = Field(default=None)
    domain: str | None = Field(default=None)
    score: float = Field(ge=0.0, le=1.0)
    raw_json: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    student: "StudentProfile" = Relationship(back_populates="attempts")

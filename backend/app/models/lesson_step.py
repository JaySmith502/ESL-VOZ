import uuid
from typing import Any

from sqlalchemy import JSON
from sqlmodel import Column, Field, Relationship, SQLModel


class LessonStep(SQLModel, table=True):
    __tablename__ = "lesson_steps"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    lesson_id: str = Field(foreign_key="lessons.lesson_id")
    step_idx: int
    step_type: str
    config: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))

    lesson: "Lesson" = Relationship(back_populates="steps")

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON
from sqlmodel import Column, Field, Relationship, SQLModel


class Lesson(SQLModel, table=True):
    __tablename__ = "lessons"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    lesson_id: str = Field(index=True, unique=True)
    title_en: str
    title_es: str
    template_pattern: str
    cefr_band: str
    domain: str
    modes: list[str] | None = Field(default=None, sa_column=Column(JSON))
    components: list[str] | None = Field(default=None, sa_column=Column(JSON))
    estimated_minutes: int
    yaml_path: str
    license: str
    origin: str = Field(default="authored")
    target_descriptors: list[str] | None = Field(default=None, sa_column=Column(JSON))
    prerequisites: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    steps: list["LessonStep"] = Relationship(back_populates="lesson")

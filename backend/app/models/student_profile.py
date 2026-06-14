import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from sqlalchemy import JSON
from sqlmodel import Column, Field, Relationship, SQLModel


class LanguagePreference(str, Enum):
    SPANISH_FIRST = "spanish_first"
    BILINGUAL = "bilingual"
    ENGLISH_ONLY = "english_only"


class StudentProfile(SQLModel, table=True):
    __tablename__ = "student_profiles"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", unique=True)
    cohort_id: uuid.UUID | None = Field(foreign_key="cohorts.id", nullable=True)
    language_preference: LanguagePreference = Field(default=LanguagePreference.BILINGUAL)
    l1: str = Field(default="es")
    cefr_band: str | None = Field(default=None)
    intake_answers: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: "User" = Relationship(back_populates="profile")
    cohort: "Cohort" = Relationship(back_populates="students")
    mastery_cells: list["MasteryCell"] = Relationship(back_populates="student")
    attempts: list["Attempt"] = Relationship(back_populates="student")

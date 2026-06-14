import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON
from sqlmodel import Column, Field, Relationship, SQLModel


class MasteryCell(SQLModel, table=True):
    __tablename__ = "mastery_cells"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    student_id: uuid.UUID = Field(foreign_key="student_profiles.id")
    mode: str  # Listening, Speaking, Reading, Writing, Mediation
    cefr_band: str  # A1.1, A1.2, A2.1, A2.2, B1.1, B1.2, B2
    domain: str  # Survival, School, Academic, Workplace
    mastery_score: float = Field(default=0.0, ge=0.0, le=1.0)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    descriptors_demonstrated: list[str] | None = Field(default=None, sa_column=Column(JSON))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    student: "StudentProfile" = Relationship(back_populates="mastery_cells")

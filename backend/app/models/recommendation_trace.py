import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON
from sqlmodel import Column, Field, SQLModel


class RecommendationTrace(SQLModel, table=True):
    __tablename__ = "recommendation_traces"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    student_id: uuid.UUID = Field(foreign_key="student_profiles.id")
    bucket_fired: str
    rationale: str
    candidates_considered: list[dict[str, Any]] | None = Field(default=None, sa_column=Column(JSON))
    selected_activity: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    graph_evidence: list[dict[str, Any]] | None = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

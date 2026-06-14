import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON
from sqlmodel import Column, Field, SQLModel


class CostEvent(SQLModel, table=True):
    __tablename__ = "cost_events"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    student_id: uuid.UUID | None = Field(default=None, foreign_key="student_profiles.id")
    vendor: str
    operation: str
    cost_usd: float
    meta: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

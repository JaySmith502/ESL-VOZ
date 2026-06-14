import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlmodel import Field, Relationship, SQLModel


class CohortStatus(str, Enum):
    PRE_ENROLLED = "pre_enrolled"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Cohort(SQLModel, table=True):
    __tablename__ = "cohorts"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    status: CohortStatus = Field(default=CohortStatus.ACTIVE)
    coordinator_id: uuid.UUID | None = Field(foreign_key="users.id", nullable=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    students: list["StudentProfile"] = Relationship(back_populates="cohort")

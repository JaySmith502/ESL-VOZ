import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlmodel import Field, Relationship, SQLModel


class ConsentLayer(str, Enum):
    PLATFORM_TERMS = "platform_terms"
    VOICE_AUDIO = "voice_audio"
    ANONYMIZED_SHARING = "anonymized_sharing"


class ConsentGrant(SQLModel, table=True):
    __tablename__ = "consent_grants"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    layer: ConsentLayer
    version: str
    granted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    withdrawn_at: datetime | None = Field(default=None)

    user: "User" = Relationship(back_populates="consents")

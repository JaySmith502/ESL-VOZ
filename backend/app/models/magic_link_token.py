import uuid
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class MagicLinkToken(SQLModel, table=True):
    __tablename__ = "magic_link_tokens"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    token_hash: str = Field(index=True, unique=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    expires_at: datetime
    used_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

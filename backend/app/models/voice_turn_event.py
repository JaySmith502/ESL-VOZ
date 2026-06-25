import uuid
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class VoiceTurnEvent(SQLModel, table=True):
    """One row per voice-pipeline segment timing.

    Audio turns write asr_ms + llm_ms (+ total_ms = sum). TTS calls write tts_ms.
    p95 over `total_ms` answers M1 acceptance #6 ("p95 voice turn ≤ 2.5s").
    """

    __tablename__ = "voice_turn_events"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    student_id: uuid.UUID | None = Field(default=None, foreign_key="student_profiles.id")
    asr_ms: int | None = None
    llm_ms: int | None = None
    tts_ms: int | None = None
    total_ms: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

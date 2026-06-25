import time
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.core.config import settings
from app.db import get_db
from app.models import ConsentLayer, StudentProfile, User, VoiceTurnEvent
from app.services.auth import has_consent, require_user
from app.services.cost_tracker import record_cost
from app.services.tts import (
    MAX_TTS_INPUT_CHARS,
    OPENAI_TTS_MODEL,
    OpenAITTSError,
    synthesize_openai,
)
from app.services.tutor import tutor_subdialog

router = APIRouter()


class TutorTextRequest(BaseModel):
    target: str
    acceptable_variants: list[str] | None = None
    transcript: str


@router.post("/subdialog")
async def subdialog(
    request: TutorTextRequest,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    profile = db.exec(select(StudentProfile).where(StudentProfile.user_id == user.id)).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Complete intake first")

    result = await tutor_subdialog(
        target=request.target,
        variants=request.acceptable_variants or [],
        transcript=request.transcript,
        l1=profile.l1,
    )
    if result.get("llm_cost_usd"):
        record_cost(
            db=db,
            vendor="anthropic",
            operation="correction",
            cost_usd=result["llm_cost_usd"],
            student_id=profile.id,
            meta={"model": "claude-haiku-4-5"},
        )
    return result


@router.post("/subdialog/audio")
async def subdialog_audio(
    target: str,
    audio: UploadFile,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    profile = db.exec(select(StudentProfile).where(StudentProfile.user_id == user.id)).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Complete intake first")

    # Voice consent is a hard gate — recording audio without it is not allowed,
    # even if the recorder UI happens to fire. Three-layer consent is M1
    # acceptance criterion #9.
    if not has_consent(db, user.id, ConsentLayer.VOICE_AUDIO):
        raise HTTPException(
            status_code=403,
            detail="Voice consent required. Enable voice recording in your settings to use the microphone.",
        )

    audio_bytes = await audio.read()
    result = await tutor_subdialog(
        target=target,
        audio_bytes=audio_bytes,
        mimetype=audio.content_type or "audio/webm",
        l1=profile.l1,
    )
    # Split the rolled-up cost into its real vendors for the rollup query.
    asr_cost = round((result.get("cost_usd") or 0) - (result.get("llm_cost_usd") or 0), 6)
    if asr_cost > 0:
        record_cost(
            db=db,
            vendor="deepgram",
            operation="transcribe",
            cost_usd=asr_cost,
            student_id=profile.id,
            meta={"duration_s": result.get("asr_duration_s")},
        )
    if result.get("llm_cost_usd"):
        record_cost(
            db=db,
            vendor="anthropic",
            operation="correction",
            cost_usd=result["llm_cost_usd"],
            student_id=profile.id,
            meta={"model": "claude-haiku-4-5"},
        )
    asr_ms = result.get("asr_ms")
    llm_ms = result.get("llm_ms")
    if asr_ms is not None or llm_ms is not None:
        total = (asr_ms or 0) + (llm_ms or 0)
        db.add(VoiceTurnEvent(
            student_id=profile.id, asr_ms=asr_ms, llm_ms=llm_ms, total_ms=total,
        ))
        db.commit()
    return result


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=MAX_TTS_INPUT_CHARS)
    # Voice picker stays server-side for M1 — see roadmap §M4 persona library.
    voice: str | None = None


# OpenAI tts-1 list price ($15 / 1M chars); cost_tracker has it at $0.015/1k chars.
_TTS_USD_PER_CHAR = 0.015 / 1000


@router.post("/tts")
async def tts(
    request: TTSRequest,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
) -> Response:
    """Synthesize one short utterance and return mp3 bytes.

    Returns 503 if the OpenAI key is unset so the frontend can degrade
    silently (the lesson text is already on screen).
    """
    if not settings.openai_api_key:
        raise HTTPException(status_code=503, detail="Text-to-speech is not configured")

    profile = db.exec(
        select(StudentProfile).where(StudentProfile.user_id == user.id)
    ).first()
    t0 = time.perf_counter()
    try:
        audio_bytes = await synthesize_openai(
            request.text, settings.openai_api_key, voice=request.voice or "nova"
        )
    except OpenAITTSError as e:
        raise HTTPException(status_code=502, detail=f"TTS failed: {e}") from e
    tts_ms = int((time.perf_counter() - t0) * 1000)

    cost_usd = round(len(request.text) * _TTS_USD_PER_CHAR, 6)
    record_cost(
        db=db,
        vendor="openai",
        operation="tts",
        cost_usd=cost_usd,
        student_id=profile.id if profile else None,
        meta={"model": OPENAI_TTS_MODEL, "chars": len(request.text)},
    )
    db.add(VoiceTurnEvent(
        student_id=profile.id if profile else None, tts_ms=tts_ms, total_ms=tts_ms,
    ))
    db.commit()
    return Response(
        content=audio_bytes,
        media_type="audio/mpeg",
        headers={"Cache-Control": "no-store"},
    )

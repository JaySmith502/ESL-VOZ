from typing import Any

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from pydantic import BaseModel
from sqlmodel import Session, select

from app.db import get_db
from app.models import StudentProfile, User
from app.services.auth import require_user
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

    return await tutor_subdialog(
        target=request.target,
        variants=request.acceptable_variants or [],
        transcript=request.transcript,
        l1=profile.l1,
    )


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

    audio_bytes = await audio.read()
    return await tutor_subdialog(
        target=target,
        audio_bytes=audio_bytes,
        l1=profile.l1,
    )

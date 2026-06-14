from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.db import get_db
from app.models import Attempt, Lesson, StudentProfile, User
from app.services.auth import require_user
from app.services.mastery import update_mastery_from_attempt

router = APIRouter()


class AttemptPayload(BaseModel):
    step_id: str
    score: float
    mode: str | None = None
    cefr_band: str | None = None
    domain: str | None = None
    response: dict[str, Any] | None = None


@router.get("")
def list_lessons(db: Session = Depends(get_db)):
    lessons = db.exec(select(Lesson)).all()
    return [{"lesson_id": l.lesson_id, "title_en": l.title_en, "title_es": l.title_es, "cefr_band": l.cefr_band} for l in lessons]


@router.get("/{lesson_id}")
def get_lesson(lesson_id: str, db: Session = Depends(get_db)):
    lesson = db.exec(select(Lesson).where(Lesson.lesson_id == lesson_id)).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    steps = sorted(lesson.steps, key=lambda s: s.step_idx)
    return {
        "lesson_id": lesson.lesson_id,
        "title_en": lesson.title_en,
        "title_es": lesson.title_es,
        "cefr_band": lesson.cefr_band,
        "domain": lesson.domain,
        "modes": lesson.modes,
        "components": lesson.components,
        "estimated_minutes": lesson.estimated_minutes,
        "steps": [
            {
                "step_id": str(s.id),
                "step_idx": s.step_idx,
                "step_type": s.step_type,
                "config": s.config,
            }
            for s in steps
        ],
    }


@router.post("/{lesson_id}/attempt")
def record_attempt(
    lesson_id: str,
    payload: AttemptPayload,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    profile = db.exec(select(StudentProfile).where(StudentProfile.user_id == user.id)).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Complete intake first")

    lesson = db.exec(select(Lesson).where(Lesson.lesson_id == lesson_id)).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    attempt = Attempt(
        student_id=profile.id,
        activity_type="lesson",
        lesson_id=lesson_id,
        step_id=payload.step_id,
        mode=payload.mode or (lesson.modes[0] if lesson.modes else None),
        cefr_band=payload.cefr_band or lesson.cefr_band,
        domain=payload.domain or lesson.domain,
        score=payload.score,
        raw_json={"response": payload.response},
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    cell = update_mastery_from_attempt(db, profile, attempt)
    return {
        "attempt_id": str(attempt.id),
        "mastery_cell": {
            "mode": cell.mode,
            "cefr_band": cell.cefr_band,
            "domain": cell.domain,
            "mastery_score": cell.mastery_score,
            "confidence": cell.confidence,
        }
        if cell
        else None,
    }

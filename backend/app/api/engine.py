from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import get_db
from app.models import StudentProfile, User
from app.services.auth import require_user
from app.services.engine import recommend_next_activity

router = APIRouter()


@router.get("/next-activity")
def next_activity(user: User = Depends(require_user), db: Session = Depends(get_db)):
    profile = db.exec(select(StudentProfile).where(StudentProfile.user_id == user.id)).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Complete intake first")
    return recommend_next_activity(db, profile)

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select

import resend

from app.core.config import settings
from app.db import get_db
from app.models import MasteryCell, StudentProfile, UserRole
from app.services.auth import (
    create_access_token,
    create_magic_link,
    create_or_get_user,
    require_user,
    verify_magic_link,
)

router = APIRouter()


def _send_magic_link_email(to: str, link: str) -> None:
    if not settings.resend_api_key:
        return
    resend.api_key = settings.resend_api_key
    resend.Emails.send(
        {
            "from": settings.resend_from_email,
            "to": to,
            "subject": "Your ESL-voice login link",
            "html": f"<p>Click the link below to log in:</p><a href=\"{link}\">{link}</a>",
        }
    )



class MagicLinkRequest(BaseModel):
    email: EmailStr


class MagicLinkVerifyRequest(BaseModel):
    token: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/magic-link", status_code=status.HTTP_202_ACCEPTED)
def request_magic_link(payload: MagicLinkRequest, db: Session = Depends(get_db)):
    user = create_or_get_user(db, payload.email, role=UserRole.LEARNER)
    raw_token = create_magic_link(db, user)
    link = f"{settings.frontend_url}/login/verify?token={raw_token}"
    _send_magic_link_email(payload.email, link)
    print(f"[MAGIC LINK] {link}")
    if settings.environment == "development":
        return {"detail": "Magic link sent", "token": raw_token, "link": link}
    return {"detail": "Magic link sent"}


@router.post("/magic-link/verify", response_model=TokenResponse)
def exchange_magic_link(payload: MagicLinkVerifyRequest, db: Session = Depends(get_db)):
    user = verify_magic_link(db, payload.token)
    access_token = create_access_token(user.id)
    return TokenResponse(access_token=access_token)


@router.get("/me")
def me(user=Depends(require_user)):
    return {"id": str(user.id), "email": user.email, "role": user.role}


@router.get("/me/profile")
def me_profile(user=Depends(require_user), db: Session = Depends(get_db)):
    profile = db.exec(select(StudentProfile).where(StudentProfile.user_id == user.id)).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Complete intake first")
    cells = db.exec(select(MasteryCell).where(MasteryCell.student_id == profile.id)).all()
    return {
        "profile_id": str(profile.id),
        "cefr_band": profile.cefr_band,
        "language_preference": profile.language_preference,
        "l1": profile.l1,
        "mastery_cells": [
            {
                "mode": c.mode,
                "cefr_band": c.cefr_band,
                "domain": c.domain,
                "mastery_score": c.mastery_score,
                "confidence": c.confidence,
            }
            for c in cells
        ],
    }

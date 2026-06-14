from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select

from app.db import get_db
from app.models import (
    ConsentGrant,
    ConsentLayer,
    LanguagePreference,
    StudentProfile,
    User,
    UserRole,
)
from app.services.auth import (
    create_access_token,
    create_magic_link,
    create_or_get_user,
    record_consent,
    require_user,
)
from app.services.placement import get_placement_items, run_placement

router = APIRouter()


class IntakeRequest(BaseModel):
    email: EmailStr
    native_language: str
    years_in_us: int
    prior_english_study: str
    highest_education: str
    primary_goal: str
    age_band: str
    language_preference: LanguagePreference = LanguagePreference.BILINGUAL


class ConsentRequest(BaseModel):
    platform_terms: bool
    voice_audio: bool = False
    anonymized_sharing: bool = False


class PlacementRequest(BaseModel):
    answers: dict[str, Any]


@router.post("/intake")
def submit_intake(payload: IntakeRequest, db: Session = Depends(get_db)):
    user = create_or_get_user(db, payload.email, role=UserRole.LEARNER)
    profile = db.exec(select(StudentProfile).where(StudentProfile.user_id == user.id)).first()
    if not profile:
        profile = StudentProfile(
            user_id=user.id,
            language_preference=payload.language_preference,
            l1=payload.native_language,
            intake_answers={
                "native_language": payload.native_language,
                "years_in_us": payload.years_in_us,
                "prior_english_study": payload.prior_english_study,
                "highest_education": payload.highest_education,
                "primary_goal": payload.primary_goal,
                "age_band": payload.age_band,
            },
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    # Auto-issue access token so the learner can continue onboarding
    access_token = create_access_token(user.id)
    return {
        "user_id": str(user.id),
        "profile_id": str(profile.id),
        "access_token": access_token,
    }


@router.post("/consent")
def submit_consent(payload: ConsentRequest, user: User = Depends(require_user), db: Session = Depends(get_db)):
    if not payload.platform_terms:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Platform terms required")
    record_consent(db, user.id, ConsentLayer.PLATFORM_TERMS)
    if payload.voice_audio:
        record_consent(db, user.id, ConsentLayer.VOICE_AUDIO)
    if payload.anonymized_sharing:
        record_consent(db, user.id, ConsentLayer.ANONYMIZED_SHARING)
    return {"detail": "Consent recorded"}


@router.get("/placement-items")
def list_placement_items():
    return {"items": get_placement_items()}


@router.post("/placement")
def submit_placement(payload: PlacementRequest, user: User = Depends(require_user), db: Session = Depends(get_db)):
    profile = db.exec(select(StudentProfile).where(StudentProfile.user_id == user.id)).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Complete intake first")
    result = run_placement(db, profile, payload.answers)
    return result

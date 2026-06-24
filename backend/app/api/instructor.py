from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from app.db import get_db
from app.models import Cohort, CostEvent, MasteryCell, RecommendationTrace, StudentProfile, User, UserRole
from app.services.auth import require_user

router = APIRouter()


def require_instructor(user: User = Depends(require_user)):
    if user.role not in (UserRole.INSTRUCTOR, UserRole.COORDINATOR, UserRole.ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Instructors only")
    return user


@router.get("/cohorts")
def list_cohorts(user: User = Depends(require_instructor), db: Session = Depends(get_db)):
    stmt = select(Cohort)
    if user.role == UserRole.INSTRUCTOR:
        stmt = stmt.where(Cohort.coordinator_id == user.id)
    cohorts = db.exec(stmt).all()
    return [
        {
            "id": str(c.id),
            "name": c.name,
            "status": c.status,
            "student_count": len(c.students),
        }
        for c in cohorts
    ]


@router.get("/cohorts/{cohort_id}")
def get_cohort(
    cohort_id: UUID,
    user: User = Depends(require_instructor),
    db: Session = Depends(get_db),
):
    cohort = db.exec(select(Cohort).where(Cohort.id == cohort_id)).first()
    if not cohort:
        raise HTTPException(status_code=404, detail="Cohort not found")
    if user.role == UserRole.INSTRUCTOR and cohort.coordinator_id != user.id:
        raise HTTPException(status_code=403, detail="Not your cohort")

    students = []
    for s in cohort.students:
        cells = db.exec(select(MasteryCell).where(MasteryCell.student_id == s.id)).all()
        attempts = s.attempts if hasattr(s, "attempts") else []
        students.append({
            "id": str(s.id),
            "email": s.user.email,
            "cefr_band": s.cefr_band,
            "language_preference": s.language_preference,
            "avg_mastery": round(sum(c.mastery_score for c in cells) / len(cells), 2) if cells else 0,
            "last_active": max((a.created_at for a in attempts), default=None),
        })
    return {
        "id": str(cohort.id),
        "name": cohort.name,
        "students": students,
    }


@router.get("/students/{student_id}")
def get_student(
    student_id: UUID,
    user: User = Depends(require_instructor),
    db: Session = Depends(get_db),
):
    student = db.exec(select(StudentProfile).where(StudentProfile.id == student_id)).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    cells = db.exec(select(MasteryCell).where(MasteryCell.student_id == student.id)).all()
    traces = db.exec(
        select(RecommendationTrace)
        .where(RecommendationTrace.student_id == student.id)
        # Exclude intervention rows — they live in /interventions, not here.
        .where(RecommendationTrace.bucket_fired != "intervention")
        .order_by(RecommendationTrace.created_at.desc())
    ).all()

    return {
        "id": str(student.id),
        "email": student.user.email,
        "cefr_band": student.cefr_band,
        "language_preference": student.language_preference,
        "l1": student.l1,
        "cells": [
            {
                "mode": c.mode,
                "cefr_band": c.cefr_band,
                "domain": c.domain,
                "mastery_score": c.mastery_score,
                "confidence": c.confidence,
            }
            for c in cells
        ],
        "recent_recommendations": [
            {
                "lesson_id": (t.selected_activity or {}).get("lesson_id"),
                "bucket": t.bucket_fired,
                "rationale": t.rationale,
                "created_at": t.created_at,
            }
            for t in traces[:10]
        ],
    }


class InterventionPayload(BaseModel):
    student_id: UUID
    note: str
    action: str = "review"


@router.post("/intervention")
def create_intervention(
    payload: InterventionPayload,
    user: User = Depends(require_instructor),
    db: Session = Depends(get_db),
):
    student = db.exec(select(StudentProfile).where(StudentProfile.id == payload.student_id)).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Store intervention as a special recommendation trace for now.
    # ponytail: shared table with recommendations; split into its own model
    # when audit volume justifies it.
    trace = RecommendationTrace(
        student_id=student.id,
        bucket_fired="intervention",
        rationale=f"[INTERVENTION by {user.email}] {payload.action}: {payload.note}",
        selected_activity={"type": "intervention", "lesson_id": "__intervention__"},
    )
    db.add(trace)
    db.commit()
    return {"status": "recorded"}


@router.get("/students/{student_id}/interventions")
def list_interventions(
    student_id: UUID,
    user: User = Depends(require_instructor),
    db: Session = Depends(get_db),
):
    """Audit trail of Flag/Note actions for one student.

    Roadmap §M1 calls for an "audit table" — this is it, sourced from the same
    rows the create endpoint writes.
    """
    student = db.exec(select(StudentProfile).where(StudentProfile.id == student_id)).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    rows = db.exec(
        select(RecommendationTrace)
        .where(RecommendationTrace.student_id == student.id)
        .where(RecommendationTrace.bucket_fired == "intervention")
        .order_by(RecommendationTrace.created_at.desc())
    ).all()
    return [
        {
            "id": str(r.id),
            "rationale": r.rationale,
            "created_at": r.created_at,
        }
        for r in rows
    ]


@router.get("/costs")
def get_costs(
    user: User = Depends(require_instructor),
    db: Session = Depends(get_db),
):
    events = db.exec(select(CostEvent).order_by(CostEvent.created_at.desc())).all()
    total = sum(e.cost_usd for e in events)
    by_vendor: dict[str, float] = {}
    for e in events:
        by_vendor[e.vendor] = by_vendor.get(e.vendor, 0.0) + e.cost_usd
    return {
        "total_usd": round(total, 4),
        "count": len(events),
        "by_vendor": {k: round(v, 4) for k, v in by_vendor.items()},
        "recent": [
            {
                "vendor": e.vendor,
                "operation": e.operation,
                "cost_usd": e.cost_usd,
                "created_at": e.created_at,
            }
            for e in events[:20]
        ],
    }

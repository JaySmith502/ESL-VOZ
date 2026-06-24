"""Instructor intervention audit trail.

Covers the new GET /instructor/students/{id}/interventions endpoint and the
invariant that recommendation listings exclude intervention rows.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from app.db import get_db
from app.main import app
from app.models import StudentProfile, User, UserRole
from app.services.auth import create_access_token, create_or_get_user


@pytest.fixture(name="engine")
def engine_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        from app.services.lesson_ingest import ingest_lessons

        ingest_lessons(session)
    return engine


@pytest.fixture(name="client")
def client_fixture(engine):
    def _get_db():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = _get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _bootstrap_learner_and_instructor(client: TestClient, engine):
    """Sign up a learner who has run one engine recommendation, plus an
    instructor token. Returns (student_id, instructor_token, learner_token)."""
    r = client.post(
        "/onboarding/intake",
        json={
            "email": "audit-learner@example.com",
            "native_language": "es",
            "years_in_us": 1,
            "prior_english_study": "none",
            "highest_education": "high_school",
            "primary_goal": "work",
            "age_band": "25-34",
            "language_preference": "bilingual",
        },
    )
    learner_token = r.json()["access_token"]
    client.post(
        "/onboarding/consent",
        headers={"Authorization": f"Bearer {learner_token}"},
        json={"platform_terms": True, "voice_audio": False, "anonymized_sharing": False},
    )
    # Generate a real (non-intervention) recommendation trace.
    client.get("/engine/next-activity", headers={"Authorization": f"Bearer {learner_token}"})

    with Session(engine) as s:
        inst = create_or_get_user(s, "inst-audit@example.com", role=UserRole.INSTRUCTOR)
        inst.role = UserRole.INSTRUCTOR
        s.add(inst); s.commit(); s.refresh(inst)
        inst_token = create_access_token(inst.id)
        student = s.exec(
            select(StudentProfile).join(User).where(User.email == "audit-learner@example.com")
        ).first()
        student_id = str(student.id)
    return student_id, inst_token, learner_token


def test_intervention_history_empty_by_default(client: TestClient, engine):
    student_id, inst_token, _ = _bootstrap_learner_and_instructor(client, engine)
    r = client.get(
        f"/instructor/students/{student_id}/interventions",
        headers={"Authorization": f"Bearer {inst_token}"},
    )
    assert r.status_code == 200
    assert r.json() == []


def test_intervention_history_returns_recorded_actions(client: TestClient, engine):
    student_id, inst_token, _ = _bootstrap_learner_and_instructor(client, engine)
    # Record two interventions.
    for note in ["Missed two sessions", "Struggling with pronunciation"]:
        r = client.post(
            "/instructor/intervention",
            headers={"Authorization": f"Bearer {inst_token}"},
            json={"student_id": student_id, "note": note, "action": "flag"},
        )
        assert r.status_code == 200

    r = client.get(
        f"/instructor/students/{student_id}/interventions",
        headers={"Authorization": f"Bearer {inst_token}"},
    )
    assert r.status_code == 200
    rows = r.json()
    assert len(rows) == 2
    # Newest first
    assert "Struggling with pronunciation" in rows[0]["rationale"]
    assert "Missed two sessions" in rows[1]["rationale"]


def test_recommendations_view_excludes_intervention_rows(client: TestClient, engine):
    """The student detail's recent_recommendations must NOT mix audit rows in."""
    student_id, inst_token, _ = _bootstrap_learner_and_instructor(client, engine)
    client.post(
        "/instructor/intervention",
        headers={"Authorization": f"Bearer {inst_token}"},
        json={"student_id": student_id, "note": "see me", "action": "flag"},
    )
    r = client.get(
        f"/instructor/students/{student_id}",
        headers={"Authorization": f"Bearer {inst_token}"},
    )
    assert r.status_code == 200
    recs = r.json()["recent_recommendations"]
    assert all(rec["bucket"] != "intervention" for rec in recs)


def test_intervention_history_requires_instructor(client: TestClient, engine):
    student_id, _, learner_token = _bootstrap_learner_and_instructor(client, engine)
    r = client.get(
        f"/instructor/students/{student_id}/interventions",
        headers={"Authorization": f"Bearer {learner_token}"},
    )
    assert r.status_code == 403

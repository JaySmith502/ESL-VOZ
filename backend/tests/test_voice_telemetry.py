"""Voice-turn p95 telemetry — M1 acceptance #6."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.db import get_db
from app.main import app
from app.models import StudentProfile, User, UserRole, VoiceTurnEvent
from app.services.auth import create_access_token, create_or_get_user


@pytest.fixture(name="engine")
def engine_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
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


def _instructor_token(engine) -> str:
    with Session(engine) as s:
        inst = create_or_get_user(s, "inst-telem@example.com", role=UserRole.INSTRUCTOR)
        inst.role = UserRole.INSTRUCTOR
        s.add(inst); s.commit(); s.refresh(inst)
        return create_access_token(inst.id)


def _learner_token(client: TestClient, email: str = "telem-learner@example.com") -> str:
    r = client.post(
        "/onboarding/intake",
        json={
            "email": email,
            "native_language": "es",
            "years_in_us": 1,
            "prior_english_study": "none",
            "highest_education": "high_school",
            "primary_goal": "work",
            "age_band": "25-34",
            "language_preference": "bilingual",
        },
    )
    return r.json()["access_token"]


def test_p95_empty(client: TestClient, engine):
    tok = _instructor_token(engine)
    r = client.get("/instructor/telemetry/voice-p95", headers={"Authorization": f"Bearer {tok}"})
    assert r.status_code == 200
    body = r.json()
    assert body["sample_size"] == 0
    assert body["p95_ms"]["voice_turn_total"] == 0
    assert body["meets_target"] is None


def test_p95_meets_target(client: TestClient, engine):
    _learner_token(client)  # creates a profile so we can attach events
    tok = _instructor_token(engine)
    with Session(engine) as s:
        sid = s.exec(__import__("sqlmodel").select(StudentProfile)).first().id
        # 100 fast turns + 5 slow ones — p95 should land around the slow tail.
        for _ in range(100):
            s.add(VoiceTurnEvent(student_id=sid, asr_ms=300, llm_ms=400, total_ms=700))
        for _ in range(5):
            s.add(VoiceTurnEvent(student_id=sid, asr_ms=1200, llm_ms=1100, total_ms=2300))
        s.commit()
    r = client.get("/instructor/telemetry/voice-p95", headers={"Authorization": f"Bearer {tok}"})
    body = r.json()
    assert body["sample_size"] == 105
    assert body["voice_turn_count"] == 105
    assert body["p95_ms"]["voice_turn_total"] >= 700
    assert body["meets_target"] is True


def test_p95_window_excludes_old_rows(client: TestClient, engine):
    _learner_token(client)
    tok = _instructor_token(engine)
    old = datetime.now(timezone.utc) - timedelta(days=30)
    with Session(engine) as s:
        sid = s.exec(__import__("sqlmodel").select(StudentProfile)).first().id
        s.add(VoiceTurnEvent(student_id=sid, asr_ms=9000, llm_ms=9000, total_ms=18000, created_at=old))
        s.add(VoiceTurnEvent(student_id=sid, asr_ms=500, llm_ms=500, total_ms=1000))
        s.commit()
    r = client.get("/instructor/telemetry/voice-p95?days=7", headers={"Authorization": f"Bearer {tok}"})
    body = r.json()
    assert body["sample_size"] == 1
    assert body["p95_ms"]["voice_turn_total"] == 1000


def test_p95_requires_instructor(client: TestClient):
    learner_tok = _learner_token(client)
    r = client.get("/instructor/telemetry/voice-p95", headers={"Authorization": f"Bearer {learner_tok}"})
    assert r.status_code == 403

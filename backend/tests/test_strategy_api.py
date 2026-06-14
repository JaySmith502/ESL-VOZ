"""Strategy pass — FastAPI contract tests for auth, lessons, onboarding,
instructor (role gating), and tutor.

Uses an in-memory SQLite engine seeded with the YAML lesson catalog, mirroring
test_acceptance.py's fixture.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from app.db import get_db
from app.main import app
from app.models import User, UserRole
from app.services.auth import create_access_token


@pytest.fixture(name="engine")
def engine_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
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


def _intake(client: TestClient, email: str = "api@example.com") -> str:
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
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


# ---------------------------------------------------------------------------
# auth
# ---------------------------------------------------------------------------


class TestAuthAPI:
    def test_health(self, client: TestClient):
        assert client.get("/health").json() == {"status": "ok"}

    def test_magic_link_request_returns_token_in_dev(self, client: TestClient):
        r = client.post("/auth/magic-link", json={"email": "ml@example.com"})
        assert r.status_code == 202
        body = r.json()
        assert "token" in body
        # Exchange
        r2 = client.post("/auth/magic-link/verify", json={"token": body["token"]})
        assert r2.status_code == 200
        assert r2.json()["token_type"] == "bearer"

    def test_magic_link_reuse_is_rejected(self, client: TestClient):
        r = client.post("/auth/magic-link", json={"email": "reuse@example.com"}).json()
        client.post("/auth/magic-link/verify", json={"token": r["token"]})
        r2 = client.post("/auth/magic-link/verify", json={"token": r["token"]})
        assert r2.status_code == 400

    def test_me_requires_bearer(self, client: TestClient):
        assert client.get("/auth/me").status_code == 401

    def test_me_profile_400_before_intake(self, client: TestClient):
        # Create a user but no profile, then hit profile endpoint
        r = client.post("/auth/magic-link", json={"email": "noprof@example.com"}).json()
        tok = client.post("/auth/magic-link/verify", json={"token": r["token"]}).json()["access_token"]
        r2 = client.get("/auth/me/profile", headers={"Authorization": f"Bearer {tok}"})
        assert r2.status_code == 400


# ---------------------------------------------------------------------------
# onboarding
# ---------------------------------------------------------------------------


class TestOnboardingAPI:
    def test_consent_without_platform_terms_is_400(self, client: TestClient):
        token = _intake(client, "consent@example.com")
        r = client.post(
            "/onboarding/consent",
            headers={"Authorization": f"Bearer {token}"},
            json={"platform_terms": False, "voice_audio": False, "anonymized_sharing": False},
        )
        assert r.status_code == 400

    def test_placement_before_intake_is_400(self, client: TestClient):
        # Issue a token for a user who has no StudentProfile.
        r = client.post("/auth/magic-link", json={"email": "skip-intake@example.com"}).json()
        tok = client.post("/auth/magic-link/verify", json={"token": r["token"]}).json()["access_token"]
        r2 = client.post(
            "/onboarding/placement",
            headers={"Authorization": f"Bearer {tok}"},
            json={"answers": {}},
        )
        assert r2.status_code == 400

    def test_placement_items_returns_nonempty_sanitized(self, client: TestClient):
        items = client.get("/onboarding/placement-items").json()["items"]
        assert items
        assert all("answer" not in it for it in items)


# ---------------------------------------------------------------------------
# lessons
# ---------------------------------------------------------------------------


class TestLessonsAPI:
    def test_list_lessons_returns_seeded_catalog(self, client: TestClient):
        lessons = client.get("/lessons").json()
        assert len(lessons) >= 1
        assert {"lesson_id", "title_en", "title_es", "cefr_band"} <= lessons[0].keys()

    def test_get_unknown_lesson_404(self, client: TestClient):
        assert client.get("/lessons/does-not-exist").status_code == 404

    def test_attempt_requires_auth(self, client: TestClient):
        # First find any lesson id
        lid = client.get("/lessons").json()[0]["lesson_id"]
        r = client.post(f"/lessons/{lid}/attempt", json={"step_id": "x", "score": 1.0})
        assert r.status_code == 401

    def test_attempt_without_profile_is_400(self, client: TestClient):
        # User authed but no intake.
        ml = client.post("/auth/magic-link", json={"email": "no-profile@example.com"}).json()
        tok = client.post("/auth/magic-link/verify", json={"token": ml["token"]}).json()["access_token"]
        lid = client.get("/lessons").json()[0]["lesson_id"]
        r = client.post(
            f"/lessons/{lid}/attempt",
            headers={"Authorization": f"Bearer {tok}"},
            json={"step_id": "x", "score": 1.0},
        )
        assert r.status_code == 400


# ---------------------------------------------------------------------------
# engine
# ---------------------------------------------------------------------------


class TestEngineAPI:
    def test_next_activity_requires_auth(self, client: TestClient):
        assert client.get("/engine/next-activity").status_code == 401


# ---------------------------------------------------------------------------
# instructor — role gating
# ---------------------------------------------------------------------------


class TestInstructorAPI:
    def test_learner_token_is_forbidden(self, client: TestClient):
        token = _intake(client, "learner@example.com")
        r = client.get("/instructor/cohorts", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 403

    def test_instructor_student_detail_reads_traces(self, client: TestClient, engine):
        # Set up a learner, run them through intake + an engine recommendation
        # so a RecommendationTrace exists, then have an instructor fetch detail.
        token = _intake(client, "traced@example.com")
        client.post(
            "/onboarding/consent",
            headers={"Authorization": f"Bearer {token}"},
            json={"platform_terms": True, "voice_audio": False, "anonymized_sharing": False},
        )
        # Drive a recommendation to write a trace row
        client.get("/engine/next-activity", headers={"Authorization": f"Bearer {token}"})

        with Session(engine) as s:
            from app.models import StudentProfile
            from app.services.auth import create_or_get_user

            inst = create_or_get_user(s, "inst-detail@example.com", role=UserRole.INSTRUCTOR)
            inst.role = UserRole.INSTRUCTOR
            s.add(inst); s.commit(); s.refresh(inst)
            inst_tok = create_access_token(inst.id)
            student = s.exec(select(StudentProfile).join(User).where(User.email == "traced@example.com")).first()
            student_id = student.id

        r = client.get(
            f"/instructor/students/{student_id}",
            headers={"Authorization": f"Bearer {inst_tok}"},
        )
        assert r.status_code == 200

    def test_instructor_can_list_empty_cohorts(self, client: TestClient, engine):
        with Session(engine) as s:
            from app.services.auth import create_or_get_user

            inst = create_or_get_user(s, "inst@example.com", role=UserRole.INSTRUCTOR)
            inst.role = UserRole.INSTRUCTOR
            s.add(inst)
            s.commit()
            s.refresh(inst)
            token = create_access_token(inst.id)
        r = client.get("/instructor/cohorts", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        assert r.json() == []


# ---------------------------------------------------------------------------
# tutor
# ---------------------------------------------------------------------------


class TestTutorAPI:
    def test_subdialog_deterministic_stub(self, client: TestClient):
        token = _intake(client, "tutor-api@example.com")
        r = client.post(
            "/tutor/subdialog",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "target": "I would like water, please.",
                "acceptable_variants": ["water please"],
                "transcript": "I would like water, please.",
            },
        )
        assert r.status_code == 200
        body = r.json()
        assert body["score"] == 1.0
        assert body["used_live_ai"] is False
        assert body["audio_url"] is None

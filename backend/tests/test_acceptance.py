"""End-to-end walking skeleton acceptance test.

Covers: intake → consent → placement → recommendation → lesson attempt → next recommendation.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.db import get_db
from app.main import app


@pytest.fixture(name="client")
def client_fixture():
    from sqlmodel import Session

    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)

    # Seed a minimal lesson catalog for the walking skeleton test.
    with Session(engine) as session:
        from app.services.lesson_ingest import ingest_lessons

        ingest_lessons(session)

    def _get_db():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = _get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_walking_skeleton(client: TestClient):
    # Intake creates a new learner and returns a token
    r = client.post("/onboarding/intake", json={
        "email": "student@example.com",
        "native_language": "es",
        "years_in_us": 2,
        "prior_english_study": "none",
        "highest_education": "high_school",
        "primary_goal": "work",
        "age_band": "25-34",
        "language_preference": "bilingual",
    })
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Consent
    r = client.post("/onboarding/consent", headers=headers, json={
        "platform_terms": True,
        "voice_audio": False,
        "anonymized_sharing": False,
    })
    assert r.status_code == 200, r.text

    # Placement
    items = client.get("/onboarding/placement-items", headers=headers).json()
    assert items["items"]
    answers = {item["id"]: "test" for item in items["items"][:4]}
    r = client.post("/onboarding/placement", headers=headers, json={"answers": answers})
    assert r.status_code == 200, r.text
    placement = r.json()
    assert placement["overall_band"]

    # Profile reflects band
    me = client.get("/auth/me/profile", headers=headers).json()
    assert me["cefr_band"] == placement["overall_band"]

    # Recommendation
    rec = client.get("/engine/next-activity", headers=headers).json()
    assert rec["activity"]["lesson_id"]
    assert rec["rationale"]

    # Lesson fetch
    lesson_id = rec["activity"]["lesson_id"]
    lesson = client.get(f"/lessons/{lesson_id}", headers=headers).json()
    assert lesson["steps"]

    # Attempt each step
    for step in lesson["steps"]:
        r = client.post(f"/lessons/{lesson_id}/attempt", headers=headers, json={
            "step_id": step["step_id"],
            "score": 1.0,
            "response": {},
        })
        assert r.status_code == 200, r.text

    # Next recommendation changes or repeats with reason
    rec2 = client.get("/engine/next-activity", headers=headers).json()
    assert rec2["activity"]["lesson_id"]

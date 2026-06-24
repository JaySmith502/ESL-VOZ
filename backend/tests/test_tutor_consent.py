"""Voice consent is a hard gate on the audio subdialog endpoint.

M1 acceptance criterion #9 requires that voice recording cannot happen
without an explicit, recorded consent grant.
"""

import io

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.db import get_db
from app.main import app


@pytest.fixture(name="client")
def client_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)

    def _get_db():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = _get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _bootstrap(client: TestClient, voice_consent: bool) -> dict:
    """Sign up a learner, optionally granting voice consent."""
    r = client.post(
        "/onboarding/intake",
        json={
            "email": "voice@example.com",
            "native_language": "es",
            "years_in_us": 1,
            "prior_english_study": "none",
            "highest_education": "high_school",
            "primary_goal": "work",
            "age_band": "25-34",
            "language_preference": "bilingual",
        },
    )
    assert r.status_code == 200
    headers = {"Authorization": f"Bearer {r.json()['access_token']}"}

    r = client.post(
        "/onboarding/consent",
        headers=headers,
        json={
            "platform_terms": True,
            "voice_audio": voice_consent,
            "anonymized_sharing": False,
        },
    )
    assert r.status_code == 200
    return headers


def test_audio_endpoint_rejects_without_voice_consent(client: TestClient):
    headers = _bootstrap(client, voice_consent=False)
    files = {"audio": ("rec.webm", io.BytesIO(b"\x00\x01"), "audio/webm")}
    r = client.post(
        "/tutor/subdialog/audio?target=Hello", headers=headers, files=files
    )
    assert r.status_code == 403
    assert "consent" in r.json()["detail"].lower()


def test_audio_endpoint_allows_with_voice_consent(client: TestClient, monkeypatch):
    headers = _bootstrap(client, voice_consent=True)

    # No real Deepgram call — service short-circuits when key is missing.
    files = {"audio": ("rec.webm", io.BytesIO(b"\x00\x01"), "audio/webm")}
    r = client.post(
        "/tutor/subdialog/audio?target=Hello", headers=headers, files=files
    )
    # With voice consent granted but no ASR key, the service returns a
    # learner-friendly 200 with score 0 (not the consent 403).
    assert r.status_code == 200
    body = r.json()
    assert body["score"] == 0.0
    assert "unavailable" in body["feedback_en"].lower()


def test_text_subdialog_does_not_require_voice_consent(client: TestClient):
    """The /tutor/subdialog text endpoint is fine without voice consent —
    consent gates audio capture specifically, not text input."""
    headers = _bootstrap(client, voice_consent=False)
    r = client.post(
        "/tutor/subdialog",
        headers=headers,
        json={
            "target": "Hello",
            "acceptable_variants": [],
            "transcript": "hello",
        },
    )
    assert r.status_code == 200
    assert r.json()["score"] == 1.0

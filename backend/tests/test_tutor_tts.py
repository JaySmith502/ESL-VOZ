"""OpenAI TTS endpoint: gating, success, cost record, failure modes."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from app.db import get_db
from app.main import app
from app.models import CostEvent


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


def _auth(client: TestClient) -> dict:
    r = client.post(
        "/onboarding/intake",
        json={
            "email": "tts@example.com",
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
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_tts_503_when_no_openai_key(client: TestClient, monkeypatch):
    from app.api import tutor as tutor_api

    monkeypatch.setattr(tutor_api.settings, "openai_api_key", None)
    headers = _auth(client)
    r = client.post("/tutor/tts", headers=headers, json={"text": "Hello"})
    assert r.status_code == 503


def test_tts_returns_audio_and_records_cost(client: TestClient, engine, monkeypatch):
    from app.api import tutor as tutor_api

    monkeypatch.setattr(tutor_api.settings, "openai_api_key", "test-key")
    fake_audio = b"ID3\x03" + b"\x00" * 128  # mp3-shaped bytes

    async def fake_synth(*args, **kwargs):
        return fake_audio

    headers = _auth(client)
    with patch.object(tutor_api, "synthesize_openai", AsyncMock(side_effect=fake_synth)):
        r = client.post(
            "/tutor/tts", headers=headers, json={"text": "Hello there"}
        )
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("audio/mpeg")
    assert r.content == fake_audio

    with Session(engine) as session:
        events = session.exec(
            select(CostEvent).where(CostEvent.vendor == "openai")
        ).all()
    assert len(events) == 1
    assert events[0].operation == "tts"
    assert events[0].cost_usd > 0


def test_tts_502_on_upstream_failure(client: TestClient, monkeypatch):
    from app.api import tutor as tutor_api
    from app.services.tts import OpenAITTSError

    monkeypatch.setattr(tutor_api.settings, "openai_api_key", "test-key")
    headers = _auth(client)

    async def boom(*args, **kwargs):
        raise OpenAITTSError("simulated 500")

    with patch.object(tutor_api, "synthesize_openai", AsyncMock(side_effect=boom)):
        r = client.post("/tutor/tts", headers=headers, json={"text": "Hi"})
    assert r.status_code == 502


def test_tts_rejects_empty_input(client: TestClient, monkeypatch):
    from app.api import tutor as tutor_api

    monkeypatch.setattr(tutor_api.settings, "openai_api_key", "test-key")
    headers = _auth(client)
    r = client.post("/tutor/tts", headers=headers, json={"text": ""})
    assert r.status_code == 422  # pydantic min_length


def test_tts_rejects_overlong_input(client: TestClient, monkeypatch):
    from app.api import tutor as tutor_api

    monkeypatch.setattr(tutor_api.settings, "openai_api_key", "test-key")
    headers = _auth(client)
    r = client.post(
        "/tutor/tts", headers=headers, json={"text": "x" * 5000}
    )
    assert r.status_code == 422  # pydantic max_length


def test_tts_requires_auth(client: TestClient):
    r = client.post("/tutor/tts", json={"text": "Hello"})
    assert r.status_code == 401

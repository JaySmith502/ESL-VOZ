"""Voice tutor subdialog: ASR + scoring + confidence gate."""

from unittest.mock import patch

import pytest

from app.services import tutor as tutor_module
from app.services.tutor import tutor_subdialog


def _deepgram_response(transcript: str, confidence: float, duration: float = 1.0) -> dict:
    return {
        "metadata": {"duration": duration},
        "results": {
            "channels": [
                {"alternatives": [{"transcript": transcript, "confidence": confidence}]}
            ]
        },
    }


@pytest.fixture
def with_deepgram_key(monkeypatch):
    monkeypatch.setattr(tutor_module.settings, "deepgram_api_key", "test-key")


@pytest.fixture
def without_deepgram_key(monkeypatch):
    monkeypatch.setattr(tutor_module.settings, "deepgram_api_key", None)


async def test_empty_audio_blob_returns_zero(without_deepgram_key):
    result = await tutor_subdialog(target="Hello", audio_bytes=b"")
    assert result["score"] == 0.0
    assert "didn't hear" in result["feedback_en"]
    assert result["used_live_ai"] is False


async def test_audio_without_key_returns_zero(without_deepgram_key):
    result = await tutor_subdialog(target="Hello", audio_bytes=b"\x00\x01\x02")
    assert result["score"] == 0.0
    assert "unavailable" in result["feedback_en"]


async def test_audio_with_good_transcript_scores_full(with_deepgram_key):
    async def fake_transcribe(*args, **kwargs):
        return {"transcript": "hello", "confidence": 0.95, "duration_s": 1.2}

    with patch.object(tutor_module, "transcribe_deepgram", fake_transcribe):
        result = await tutor_subdialog(target="Hello", audio_bytes=b"\x00\x01")
    assert result["score"] == 1.0
    assert result["transcript"] == "hello"
    assert result["asr_confidence"] == 0.95
    assert result["cost_usd"] > 0  # billed for transcription
    assert result["used_live_ai"] is True


async def test_low_confidence_does_not_score(with_deepgram_key):
    async def fake_transcribe(*args, **kwargs):
        return {"transcript": "garbled noise", "confidence": 0.2, "duration_s": 1.0}

    with patch.object(tutor_module, "transcribe_deepgram", fake_transcribe):
        result = await tutor_subdialog(target="Hello", audio_bytes=b"\x00\x01")
    # Below confidence gate: refuse to grade — no false success, no false failure.
    assert result["score"] == 0.0
    assert "clearly" in result["feedback_en"]
    assert result["cost_usd"] > 0  # cost still incurred


async def test_empty_transcript_does_not_score(with_deepgram_key):
    async def fake_transcribe(*args, **kwargs):
        return {"transcript": "", "confidence": 0.0, "duration_s": 0.8}

    with patch.object(tutor_module, "transcribe_deepgram", fake_transcribe):
        result = await tutor_subdialog(target="Hello", audio_bytes=b"\x00\x01")
    assert result["score"] == 0.0
    assert "didn't catch" in result["feedback_en"]


async def test_deepgram_error_returns_zero(with_deepgram_key):
    from app.services.asr import DeepgramError

    async def fake_transcribe(*args, **kwargs):
        raise DeepgramError("simulated 500")

    with patch.object(tutor_module, "transcribe_deepgram", fake_transcribe):
        result = await tutor_subdialog(target="Hello", audio_bytes=b"\x00\x01")
    assert result["score"] == 0.0
    assert "couldn't transcribe" in result["feedback_en"]


async def test_text_path_unchanged():
    result = await tutor_subdialog(target="Hello there", transcript="hello there")
    assert result["score"] == 1.0


async def test_partial_overlap_scores_fraction():
    result = await tutor_subdialog(target="I would like water please", transcript="water please")
    assert result["score"] == pytest.approx(0.4)


async def test_no_input_at_all_returns_zero():
    result = await tutor_subdialog(target="Hello")
    assert result["score"] == 0.0
    assert "record or type" in result["feedback_en"]


async def test_critical_bug_fix_target_not_used_as_transcript(with_deepgram_key):
    """Regression guard: prior bug let `final_transcript = transcript or target`
    fall back to the target, returning score 1.0 for silence. Make sure that
    can never come back."""

    async def fake_transcribe(*args, **kwargs):
        return {"transcript": "", "confidence": 0.99, "duration_s": 0.5}

    with patch.object(tutor_module, "transcribe_deepgram", fake_transcribe):
        result = await tutor_subdialog(target="Hello", audio_bytes=b"\x00\x01")
    assert result["score"] == 0.0
    assert result["transcript"] != "Hello"

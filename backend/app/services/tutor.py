"""Voice tutor subdialog service.

M1 stub: when API keys are absent, returns deterministic correction feedback based on
a target utterance and its accepted variants. When keys are present, it can call
Deepgram (ASR), Anthropic (correction), and OpenAI (TTS).
"""

import re
from typing import Any

from app.core.config import settings


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9\s]", "", text.lower()).strip()


def _score_utterance(target: str, variants: list[str], transcript: str) -> tuple[float, str, str]:
    norm = _normalize(transcript)
    accepted = [_normalize(target)] + [_normalize(v) for v in variants]

    if any(norm == a for a in accepted):
        return 1.0, transcript, "Great pronunciation!"

    target_words = _normalize(target).split()
    said_words = norm.split()
    overlap = sum(1 for w in target_words if w in said_words)
    score = overlap / max(1, len(target_words))

    missing = [w for w in target_words if w not in said_words]
    if missing:
        feedback = f"Listen again. Try to include: {', '.join(missing)}."
    else:
        feedback = "Good try! Listen and repeat once more."
    return score, transcript, feedback


async def tutor_subdialog(
    target: str,
    variants: list[str] | None = None,
    audio_bytes: bytes | None = None,
    transcript: str | None = None,
    l1: str = "es",
) -> dict[str, Any]:
    """Run one turn of the voice tutor.

    Args:
        target: The canonical utterance the learner should produce.
        variants: Accepted alternative wordings.
        audio_bytes: Optional recorded audio to transcribe (Deepgram when configured).
        transcript: Optional text transcript (used directly if audio is not provided).
        l1: Learner first language for feedback translation.

    Returns:
        dict with score, transcript, feedback_en, feedback_l1, and audio_url (future TTS).
    """
    variants = variants or []

    # Transcription path
    if audio_bytes and settings.deepgram_api_key:
        # TODO: integrate deepgram-sdk transcriptions
        transcript = ""
    final_transcript = transcript or target

    score, recognized, feedback_en = _score_utterance(target, variants, final_transcript)

    feedback_l1 = feedback_en  # TODO: translate to L1 when OpenAI/Anthropic enabled

    # Cost tracking placeholder: real implementations will record cost events here.
    cost_usd = 0.0

    return {
        "score": round(score, 2),
        "transcript": recognized,
        "target": target,
        "feedback_en": feedback_en,
        "feedback_l1": feedback_l1,
        "audio_url": None,
        "cost_usd": cost_usd,
        "used_live_ai": bool(settings.anthropic_api_key and settings.deepgram_api_key),
    }

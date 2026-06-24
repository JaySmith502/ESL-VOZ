"""Voice tutor subdialog service.

M1 stub: when API keys are absent, returns deterministic correction feedback based on
a target utterance and its accepted variants. When keys are present, it can call
Deepgram (ASR), Anthropic (correction), and OpenAI (TTS).
"""

import logging
import re
from typing import Any

from app.core.config import settings
from app.services.asr import DeepgramError, transcribe_deepgram
from app.services.correction import CorrectionError, correct_with_claude
from app.services.cost_tracker import estimate_llm_cost

logger = logging.getLogger(__name__)

# Below this Deepgram confidence we don't trust the transcript enough to grade
# pronunciation — surfacing "couldn't catch that" is honest, scoring noise isn't.
ASR_CONFIDENCE_GATE = 0.5

# Deepgram nova-2 list price; mirrors cost_tracker.COST_RATES["deepgram"]["nova-2"].
DEEPGRAM_USD_PER_HOUR = 0.43


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


def _fail(target: str, feedback: str, **extra: Any) -> dict[str, Any]:
    """Build a no-score response with a learner-facing message."""
    return {
        "score": 0.0,
        "transcript": "",
        "target": target,
        "feedback_en": feedback,
        "feedback_l1": feedback,
        "audio_url": None,
        "cost_usd": 0.0,
        "used_live_ai": False,
        **extra,
    }


async def tutor_subdialog(
    target: str,
    variants: list[str] | None = None,
    audio_bytes: bytes | None = None,
    transcript: str | None = None,
    mimetype: str = "audio/webm",
    l1: str = "es",
) -> dict[str, Any]:
    """Run one turn of the voice tutor.

    Args:
        target: The canonical utterance the learner should produce.
        variants: Accepted alternative wordings.
        audio_bytes: Optional recorded audio to transcribe (Deepgram when configured).
        transcript: Optional text transcript (used directly if audio is not provided).
        mimetype: Audio MIME type for Deepgram Content-Type header.
        l1: Learner first language for feedback translation.

    Returns:
        dict with score, transcript, feedback_en, feedback_l1, audio_url, cost_usd,
        used_live_ai, and (when audio was used) asr_confidence + asr_duration_s.
    """
    variants = variants or []
    cost_usd = 0.0
    asr_meta: dict[str, Any] = {}

    # --- Audio path ---
    if audio_bytes is not None and len(audio_bytes) == 0:
        return _fail(
            target,
            "We didn't hear anything. Tap the mic and try again, or type your answer.",
        )

    if audio_bytes:
        if not settings.deepgram_api_key:
            return _fail(
                target,
                "Speech recognition is unavailable right now. Type your answer to continue.",
            )
        try:
            result = await transcribe_deepgram(
                audio_bytes, settings.deepgram_api_key, mimetype=mimetype
            )
        except DeepgramError as e:
            logger.warning("Deepgram transcription failed: %s", e)
            return _fail(
                target,
                "We couldn't transcribe that. Try again, or type your answer.",
            )
        transcript = result["transcript"]
        confidence = result["confidence"]
        duration_s = result["duration_s"]
        cost_usd = round(duration_s / 3600.0 * DEEPGRAM_USD_PER_HOUR, 6)
        asr_meta = {"asr_confidence": confidence, "asr_duration_s": duration_s}

        if not transcript:
            return _fail(
                target,
                "We didn't catch any words. Speak a little louder and try again.",
                cost_usd=cost_usd,
                **asr_meta,
            )
        if confidence < ASR_CONFIDENCE_GATE:
            # Low ASR confidence: don't grade noise. Roadmap §M1: "ASR confidence
            # gate (correction suppression below threshold)".
            return _fail(
                target,
                "We couldn't hear that clearly. Try again in a quieter spot.",
                cost_usd=cost_usd,
                **asr_meta,
            )

    # --- Text path ---
    if not transcript:
        return _fail(target, "Please record or type an answer.")

    # Grading path. Prefer Claude when configured; fall back to the local
    # string-match scorer if input is rejected, Claude fails, or output is
    # invalid — the learner never sees a hallucinated grade.
    used_llm = False
    correction_meta: dict[str, Any] = {}
    if settings.anthropic_api_key:
        try:
            corr = await correct_with_claude(
                target=target,
                transcript=transcript,
                l1=l1,
                api_key=settings.anthropic_api_key,
            )
            score = corr["score"]
            feedback_en = corr["feedback_en"]
            feedback_l1 = corr["feedback_l1"]
            recognized = transcript
            used_llm = True
            llm_cost = estimate_llm_cost(
                "anthropic",
                "claude-haiku-4-5",
                corr["usage"]["input_tokens"],
                corr["usage"]["output_tokens"],
            )
            cost_usd = round(cost_usd + llm_cost, 6)
            correction_meta = {
                "llm_cost_usd": llm_cost,
                "l1_transfer_note": corr.get("l1_transfer_note"),
            }
        except CorrectionError as e:
            logger.warning("Falling back to local scorer: %s", e)
            score, recognized, feedback_en = _score_utterance(target, variants, transcript)
            feedback_l1 = feedback_en
    else:
        score, recognized, feedback_en = _score_utterance(target, variants, transcript)
        feedback_l1 = feedback_en  # TODO: translate to L1 when OpenAI/Anthropic enabled

    return {
        "score": round(score, 2),
        "transcript": recognized,
        "target": target,
        "feedback_en": feedback_en,
        "feedback_l1": feedback_l1,
        "audio_url": None,
        "cost_usd": cost_usd,
        "used_live_ai": bool((settings.deepgram_api_key and audio_bytes) or used_llm),
        **asr_meta,
        **correction_meta,
    }

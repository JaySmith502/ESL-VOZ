"""Deepgram pre-recorded ASR client.

M1: single non-streaming call to Deepgram's /v1/listen REST endpoint.
Streaming + WebSocket are M2+.
"""

from typing import Any

import httpx

# nova-2 is the rate sitting in cost_tracker.COST_RATES; pin to it on purpose so
# the cost rollup stays accurate. Bump together (model + rate) when changing.
DEEPGRAM_MODEL = "nova-2"
DEEPGRAM_URL = "https://api.deepgram.com/v1/listen"
DEEPGRAM_TIMEOUT_SECONDS = 15.0


class DeepgramError(RuntimeError):
    """Deepgram returned a non-2xx response or an unparseable body."""


async def transcribe_deepgram(
    audio_bytes: bytes,
    api_key: str,
    mimetype: str = "audio/webm",
) -> dict[str, Any]:
    """Transcribe one audio buffer with Deepgram pre-recorded.

    Returns:
        {"transcript": str, "confidence": float, "duration_s": float}

    Raises:
        DeepgramError on HTTP failure or malformed JSON.
    """
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": mimetype or "audio/webm",
    }
    params = {"model": DEEPGRAM_MODEL, "smart_format": "true"}

    async with httpx.AsyncClient(timeout=DEEPGRAM_TIMEOUT_SECONDS) as client:
        resp = await client.post(
            DEEPGRAM_URL, headers=headers, params=params, content=audio_bytes
        )
    if resp.status_code >= 400:
        raise DeepgramError(f"Deepgram {resp.status_code}: {resp.text[:200]}")

    try:
        data = resp.json()
        alt = data["results"]["channels"][0]["alternatives"][0]
        transcript = (alt.get("transcript") or "").strip()
        confidence = float(alt.get("confidence") or 0.0)
        duration_s = float(data.get("metadata", {}).get("duration") or 0.0)
    except (KeyError, IndexError, TypeError, ValueError) as e:
        raise DeepgramError(f"Deepgram response malformed: {e}") from e

    return {"transcript": transcript, "confidence": confidence, "duration_s": duration_s}

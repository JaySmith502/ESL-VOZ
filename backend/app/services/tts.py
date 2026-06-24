"""OpenAI text-to-speech client.

M1: single non-streaming POST to /v1/audio/speech. Streaming is M2+.
"""

import httpx

# tts-1 matches the rate sitting in cost_tracker.COST_RATES["openai"]["tts-1"].
# Bump together (model + rate) when changing.
OPENAI_TTS_MODEL = "tts-1"
# nova is warm/clear and widely used for ESL listening tasks. Roadmap §M4
# leaves multiple personas as pilot-signal-contingent, so we don't expose a
# voice picker yet.
OPENAI_TTS_DEFAULT_VOICE = "nova"
OPENAI_TTS_URL = "https://api.openai.com/v1/audio/speech"
OPENAI_TTS_TIMEOUT_SECONDS = 20.0

# Hard cap on input length per request — keeps a single TTS call cheap and
# protects against accidental paste-of-essay. Lessons hit this in tutor lines
# of ~15-50 chars; 1k is generous.
MAX_TTS_INPUT_CHARS = 1000


class OpenAITTSError(RuntimeError):
    """OpenAI TTS returned a non-2xx response."""


async def synthesize_openai(
    text: str,
    api_key: str,
    voice: str = OPENAI_TTS_DEFAULT_VOICE,
) -> bytes:
    """Synthesize one short utterance with OpenAI TTS.

    Returns mp3 audio bytes (response_format=mp3 is OpenAI's default).
    Raises OpenAITTSError on non-2xx.
    """
    text = (text or "").strip()
    if not text:
        raise OpenAITTSError("Empty input")
    if len(text) > MAX_TTS_INPUT_CHARS:
        raise OpenAITTSError(f"Input exceeds {MAX_TTS_INPUT_CHARS} chars")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {"model": OPENAI_TTS_MODEL, "voice": voice, "input": text}

    async with httpx.AsyncClient(timeout=OPENAI_TTS_TIMEOUT_SECONDS) as client:
        resp = await client.post(OPENAI_TTS_URL, headers=headers, json=payload)
    if resp.status_code >= 400:
        raise OpenAITTSError(f"OpenAI {resp.status_code}: {resp.text[:200]}")
    return resp.content

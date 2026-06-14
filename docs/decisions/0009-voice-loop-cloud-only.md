# ADR 0009 — Cloud-only voice stack

**Status:** Accepted
**Date:** 2026-06-14
**Depends on:** 0007, 0008
**Consumed by:** 0011, 0014

## Context

The project name "ESL-voice" identifies voice as the differentiator. ADR 0008 specified tutor behavior but not the voice pipeline. The user does not have local compute (no mini-PC, no GPU), so local Whisper / Piper / forced-aligner approaches are out. Everything must be cloud-hosted.

Cost discipline matters: at typical pilot usage (20 learners × 20 min/day × 30 days × 60% voice), cloud ASR/TTS/LLM total ~$150–200/mo. Without cost control, this scales linearly per learner and breaks the self-host envelope quickly.

## Decision

**Modality per-step, not platform-wide.** Voice required for `pronunciation_drill`; default for `tutor_conversation`. Text-only learners get every activity except pronunciation drills (those cells stay at `confidence=0`).

**ASR**: **Deepgram Nova-2** — streaming, ~150ms first-token, ~$0.0043/min, strong on Spanish-accented English. **Voice consent mandatory at signup** (bilingual plain-language); raw audio purged within 24h.

**TTS**: **OpenAI `tts-1`** — single vendor for English (`nova`) + Spanish (`shimmer`); streaming output starts playback at first sentence; $15/M chars.

**LLM tiering**:
- **Haiku 4.5** in tutor hot path (latency budget ≤ 2s requires it).
- **Sonnet 4.6** for grader utility (off hot path, accuracy matters).
- **Anthropic prompt caching** on Layer 2 compiled prompts (ADR 0008) — 90% input cost savings; target cache hit rate >95%.

**Pronunciation scoring**:
- *MVP*: Whisper-transcription proxy. Mispronounced → Deepgram transcribes wrong word → minimal-pair contrast inferred from target's phoneme set. Crude (~70%) but lit up.
- *M2*: SpeechAce or equivalent for `pronunciation_drill` only.
- *M3+*: Re-evaluate batch forced alignment on VPS if SpeechAce costs grow.

**Latency budget ≤ 2.0s** end-of-utterance to start-of-tutor-utterance:
- Silero VAD (browser WASM): 50ms
- Deepgram streaming ASR: 300ms
- Network + L1 detection + prompt assembly: ~130ms
- Haiku 4.5 streaming: 600–900ms
- Validator + TTS first byte: ~480ms

**Turn-taking**: half-duplex with Silero VAD endpoint detection. Full-duplex barge-in deferred to M4+.

**ASR-vs-learner error attribution** (extends ADR 0008 validator):
- conf < 0.7 → re-transcribe (consent permitting); still < 0.7 → tutor does not correct; reprompt
- 0.7 ≤ conf < 0.85 → correct high-salience errors only
- conf ≥ 0.85 → full correction pipeline

**Cost-control architecture (mandatory)**:
1. Prompt caching on ADR 0008 Layer 2.
2. Activity-to-model dispatch config: `tutor_conversation → Haiku`, `grader_utility → Sonnet`, etc.
3. **Text-mode promoted as a first-class learner preference** — voice is the differentiator but the cost driver.

## Consequences

- Mandatory Deepgram + OpenAI + Anthropic vendor accounts at MVP.
- Mandatory bilingual voice-consent flow at signup; no opt-in default.
- New tables/modules:
  - `cost_events` — daily rollup per vendor/service/cohort.
  - `voice_turn_metrics` — per-turn latency timing.
  - `pronunciation_attempt` + `contrast_srs_state` tables.
  - `asr_trace` with confidence + retry flags.
- **Offline mode removed from MVP scope.** Reserved as M4+ pilot-signal-contingent.
- US-hosted infra required for FERPA / KY SB 216 alignment.
- Budget estimate at 20-learner pilot: ~$160–215/mo for cloud APIs + ~$15/mo for infra = ~$175–230/mo total. Cost rollup cron alerts at >$15/mo per active learner.

## Alternatives considered

- **Local Whisper + Piper** — rejected by constraint (no local compute).
- **OpenAI Whisper API instead of Deepgram** — viable but pricier ($0.006/min vs $0.0043) with comparable accuracy.
- **ElevenLabs TTS** — rejected at MVP. Better quality, but $99/mo for 100k chars breaks budget.
- **Local LLM (Ollama)** — rejected by constraint; also blows the latency budget.
- **Real-time pronunciation via forced alignment in MVP** — rejected. Needs CPU we don't have; defer to M2 SpeechAce or M3 batch.

# ESL-VOZ — Session Handoff

**Date:** 2026-06-24
**Branch:** main (clean working tree expected at handoff)
**Milestone:** M1 — Walking Skeleton Pilot

---

## Read first

1. `docs/roadmap.md` — what ships in M1 and what doesn't.
2. `docs/PRD.md` — product premise.
3. This file — last session's state, then start.

Run the full suite before changing anything:

```bash
cd backend && uv run pytest -q          # 104 tests
cd ../frontend && npm test              # 18 tests
cd frontend && npm run test:e2e         # 1 Playwright
backend/.venv/Scripts/python.exe scripts/lint_lessons.py
```

All four should be green.

---

## What got done this session

### 1. Critical bug fix — silent "perfect" scoring
`backend/app/services/tutor.py` had `final_transcript = transcript or target` —
when transcription failed or audio was empty, it scored the learner against
the answer it gave itself. Recording silence returned 1.0. Replaced with
explicit failure paths for empty blob / no key / empty transcript / low
confidence. UI was also letting Continue advance on any score; gated to
`>= 0.8`. Regression-guarded.

### 2. Real ASR via Deepgram
`backend/app/services/asr.py` — REST call to `/v1/listen` (`nova-2`) via the
already-installed `httpx`. No new dep. Confidence gate at 0.5: below that we
refuse to grade rather than score noise. Cost computed from `duration_s`,
written to `cost_events`.

### 3. Voice consent gate
`POST /tutor/subdialog/audio` now 403s when the user hasn't granted
`VOICE_AUDIO` consent (M1 acceptance #9). Text endpoint unaffected — consent
gates the mic, not text input.

### 4. `tutor_subdialog` step type
Frontend renderer was missing it; lessons using it would fall to the default
branch and silently advance with 1.0. Implemented as a multi-turn driver over
`ProductionSpeaking`. Mean score reported. Empty-turns guard surfaces a
visible warning.

### 5. OpenAI TTS
`backend/app/services/tts.py` + `POST /tutor/tts` returns mp3 bytes.
Frontend `ListenButton` (🔊) fetches and plays via `Audio`. Backend 503 when
key is unset → button hides itself for the session. Cost-event written per
call.

### 6. Anthropic correction layer (Claude Haiku 4.5)
`backend/app/services/correction.py` — one `/v1/messages` call with a strict
JSON-output system prompt. Two guardrails:
  - **Layer 1 (input):** `sanitize_transcript` trims, length-caps,
    strips control chars, blocks obvious injection markers.
  - **Layer 2 (output):** `_validate_correction` requires valid JSON,
    score ∈ [0,1], feedback ≤ 280 chars, no canary leak. Strips ```json fences.

Wired into `tutor_subdialog`: prefer Claude when keyed; on any
`CorrectionError`, fall back to the deterministic local scorer with a logged
warning. Real token usage → cost event split by vendor.

### 7. Instructor dashboard polish
- New `GET /instructor/students/{id}/interventions` (audit table).
- Student detail filters intervention rows OUT of `recent_recommendations`.
- Frontend: Intervention History list (newest first, timestamped). Replaced
  `alert()` with inline "Recorded." status. Print/PDF button (browser-native
  `window.print()` + `print:hidden` on action panel — no PDF lib).
- Cohort page: "Needs attention" panel (`avg_mastery < 0.4`, never started,
  or inactive > 7 days). Soft amber row highlight in the full table.

### 8. Frontend test fix
Playwright E2E webServer command used `../backend/...` while `cwd` was already
`../backend`; on Windows cmd that resolved to `..` and crashed. Simplified to
`.venv\Scripts\uvicorn.exe ...`.

---

## Where things live

| Concern | File |
|---|---|
| ASR | `backend/app/services/asr.py` |
| TTS | `backend/app/services/tts.py` |
| Anthropic correction + guardrails | `backend/app/services/correction.py` |
| Tutor orchestration (audio + text path) | `backend/app/services/tutor.py` |
| Tutor REST endpoints + cost-event writes | `backend/app/api/tutor.py` |
| Instructor REST | `backend/app/api/instructor.py` |
| Lesson player + step types | `frontend/src/components/lesson-player/StepRenderer.tsx` |
| Voice recorder | `frontend/src/components/lesson-player/VoiceRecorder.tsx` |
| TTS button | `frontend/src/components/lesson-player/ListenButton.tsx` |
| Instructor pages | `frontend/src/app/[locale]/instructor/**` |
| Cost rates | `backend/app/services/cost_tracker.py` |

---

## M1 acceptance scorecard

| # | Criterion | Status |
|---|---|---|
| 1 | Cohort of 8 completes intake + placement | Code path ready, awaits pilot |
| 2 | ≥3 sessions/week × 4 weeks | Awaits pilot |
| 3 | ≥80% mastery cells with Δ>0 over 8 wks | Engine writes cells; awaits pilot |
| 4 | Instructor uses dashboard ≥2×/week | ✅ Dashboard usable end-to-end |
| 5 | ≤ $12/mo per learner | ✅ Vendor-split `cost_events` writers in place |
| 6 | p95 voice turn ≤ 2.5s | ⬜ telemetry table not wired |
| 7 | < 5 errors/learner/week (Sentry) | ⬜ Sentry not wired |
| 8 | Zero affective-filter UI-string lint violations | ⬜ Linter not wired |
| 9 | Magic-link auth + 3-layer consent | ✅ Consent gates audio; magic-link backend exists |
| 10 | Standards Alignment report (single-learner) | ⬜ Not built; M2 leverage |

---

## What to do next (in order of value)

1. **p95 voice-turn telemetry** (M1 #6) — small, mechanical, no pilot needed.
   Add a `voice_turn_events` table (`student_id`, `asr_ms`, `llm_ms`, `tts_ms`,
   `total_ms`, `created_at`). Time each segment in `tutor.py` /
   `tts` endpoint. One read-only endpoint computes p95 over last 7 days.
2. **Sentry wiring** (M1 #7) — backend + frontend, free tier, DSN in env.
3. **Affective-filter UI-string linter** (M1 #8) — a script over
   `frontend/messages/*.json` that fails on banned phrasings ("you failed",
   "wrong", etc.). Add to CI.
4. **Standards Alignment single-learner report** (M1 #10) — extends the
   existing student PDF; needs CEFR descriptor pairing per mastery cell. Used
   as the JCPS-pilot proof artifact.
5. **Anthropic prompt caching** on `correction.py` system prompt once it
   crosses ~1k tokens (currently ~400). Cheap win, M2-flavored.

Items NOT to chase yet (per roadmap discipline):
- Streaming Deepgram / streaming TTS — M2.
- Persona / voice picker — pilot-signal-contingent (M4).
- WIDA toggle, child UI, Mediation mode — M2.
- Cognee/Memgraph — evaluation only, M3.

---

## Known sharp edges

- **Global pytest is broken on the host** (unrelated to this project). Use
  `uv run pytest` from `backend/` — never `pytest` directly.
- **Playwright `webServer` is Windows-shaped.** Linux/macOS CI would need
  `.venv/bin/uvicorn`. When CI gets set up, switch to `uv run uvicorn`.
- **Lesson YAML `lesson.turn` / `lesson.typeAnswer`** keys: `typeAnswer` is
  currently under the `placement` namespace but referenced from
  `StepRenderer`. Works because translation falls back to the key, but worth
  fixing.
- **Recommendation traces and interventions share a table** (`bucket_fired ==
  "intervention"` is the discriminator). Fine for M1; split if audit volume
  grows or schema diverges.
- **No instructor signup UI.** Promote a user to instructor via a Python
  one-liner (`User.role = UserRole.INSTRUCTOR`) — magic-link login then works.

---

## Open decisions

- **TTS voice.** Hard-coded `nova` server-side. Persona library is M4
  pilot-signal-contingent — don't expose a picker yet.
- **Claude model pin.** `claude-haiku-4-5` (in `correction.py`). Bump together
  with the cost row in `cost_tracker.py` if Anthropic re-prices.
- **Confidence gate.** ASR < 0.5 currently refuses to grade. May want to
  lower for noisier environments after the first pilot data.

---

## How to run the dev stack

```bash
make db        # docker-compose Postgres + Redis (skip for sqlite-only)
make dev       # backend on :8000, frontend on :3000
```

`backend/.env` controls API keys. All AI keys are optional — the system
degrades to deterministic scoring + 503 TTS + the stub local scorer when any
are absent.

🧙 Built with WOZCODE

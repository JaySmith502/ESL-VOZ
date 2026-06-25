# ESL-VOZ — Session Handoff

**Date:** 2026-06-24 (evening session)
**Branch:** main (uncommitted changes — see "Uncommitted" below)
**Milestone:** M1 — Walking Skeleton Pilot

---

## Read first

1. `docs/roadmap.md` — what ships in M1 and what doesn't.
2. `docs/PRD.md` — product premise.
3. This file — last session's state, then start.

Run the full suite before changing anything:

```bash
cd backend && uv run pytest -q          # 108 tests
cd ../frontend && npm test              # 18 tests
cd frontend && npm run test:e2e         # 1 Playwright
backend/.venv/Scripts/python.exe scripts/lint_lessons.py
backend/.venv/Scripts/python.exe scripts/lint_ui_strings.py
backend/.venv/Scripts/python.exe scripts/test_lint_ui_strings.py
```

All should be green at handoff.

---

## What got done this session

### 1. p95 voice-turn telemetry (M1 acceptance #6)
- New model `VoiceTurnEvent` (`backend/app/models/voice_turn_event.py`):
  `student_id, asr_ms, llm_ms, tts_ms, total_ms, created_at`. Auto-created via
  `SQLModel.metadata.create_all` — no alembic migration needed.
- `services/tutor.py` times Deepgram and Claude segments with `time.perf_counter`
  and returns `asr_ms` / `llm_ms` in the result dict. Failure paths (`_fail`) do
  NOT include timings, so they never pollute p95.
- `api/tutor.py` writes a row per audio turn (asr + llm) and per TTS call
  (tts only). `total_ms` is the sum of populated segments.
- New endpoint `GET /instructor/telemetry/voice-p95?days=7` →
  `{ window_days, sample_size, voice_turn_count, p95_ms: {asr, llm, tts, voice_turn_total}, target_ms: 2500, meets_target }`.
  Uses stdlib `statistics.quantiles(..., n=100, method="inclusive")[94]`.
  Instructor-only.
- Tests: `backend/tests/test_voice_telemetry.py` — empty case, meets-target with
  100 fast + 5 slow rows, 7-day window excludes old rows, instructor gate.

### 2. Affective-filter UI-string linter (M1 acceptance #8)
- `scripts/lint_ui_strings.py` — walks `frontend/messages/*.json`, fails on a
  small high-signal banlist (EN: wrong, incorrect, failed, failure, stupid,
  dumb, "bad job", "try harder", "you lost"; ES: incorrecto, fallaste, estúpido,
  tonto, "mal hecho"). Word-boundary regex, case-insensitive.
- `scripts/test_lint_ui_strings.py` — assert-based self-check (clean, dirty,
  "wrongful" over-match guard, ES-lemma pin). No pytest needed.
- Current en.json + es.json pass clean.
- NOT wired to CI yet — no `.github/workflows/` in the repo. Wire when CI lands.

---

## Where things live

| Concern | File |
|---|---|
| ASR | `backend/app/services/asr.py` |
| TTS | `backend/app/services/tts.py` |
| Anthropic correction + guardrails | `backend/app/services/correction.py` |
| Tutor orchestration (audio + text path, segment timing) | `backend/app/services/tutor.py` |
| Tutor REST endpoints + cost-event + voice-turn-event writes | `backend/app/api/tutor.py` |
| Instructor REST (incl. telemetry/voice-p95) | `backend/app/api/instructor.py` |
| Voice-turn telemetry model | `backend/app/models/voice_turn_event.py` |
| Lesson player + step types | `frontend/src/components/lesson-player/StepRenderer.tsx` |
| Voice recorder | `frontend/src/components/lesson-player/VoiceRecorder.tsx` |
| TTS button | `frontend/src/components/lesson-player/ListenButton.tsx` |
| Instructor pages | `frontend/src/app/[locale]/instructor/**` |
| Cost rates | `backend/app/services/cost_tracker.py` |
| Lesson YAML linter | `scripts/lint_lessons.py` |
| UI-string affective-filter linter | `scripts/lint_ui_strings.py` |

---

## M1 acceptance scorecard

| # | Criterion | Status |
|---|---|---|
| 1 | Cohort of 8 completes intake + placement | Code path ready, awaits pilot |
| 2 | ≥3 sessions/week × 4 weeks | Awaits pilot |
| 3 | ≥80% mastery cells with Δ>0 over 8 wks | Engine writes cells; awaits pilot |
| 4 | Instructor uses dashboard ≥2×/week | ✅ Dashboard usable end-to-end |
| 5 | ≤ $12/mo per learner | ✅ Vendor-split `cost_events` writers in place |
| 6 | p95 voice turn ≤ 2.5s | ✅ Table + write path + endpoint live; needs traffic to validate |
| 7 | < 5 errors/learner/week (Sentry) | ⬜ Sentry not wired |
| 8 | Zero affective-filter UI-string lint violations | ✅ Linter green; not yet on CI (no CI yet) |
| 9 | Magic-link auth + 3-layer consent | ✅ Consent gates audio; magic-link backend exists |
| 10 | Standards Alignment report (single-learner) | ⬜ Not built; M2 leverage |

---

## Uncommitted at handoff

```
 M backend/app/api/instructor.py
 M backend/app/api/tutor.py
 M backend/app/models/__init__.py
 M backend/app/services/tutor.py
?? backend/app/models/voice_turn_event.py
?? backend/tests/test_voice_telemetry.py
?? scripts/lint_ui_strings.py
?? scripts/test_lint_ui_strings.py
 M MEMORY.md
```

All green. Commit suggestion (two commits, separate concerns):

```bash
git add backend/app/models/voice_turn_event.py backend/app/models/__init__.py \
        backend/app/services/tutor.py backend/app/api/tutor.py \
        backend/app/api/instructor.py backend/tests/test_voice_telemetry.py
git commit -m "M1 #6: voice-turn p95 telemetry table + endpoint"

git add scripts/lint_ui_strings.py scripts/test_lint_ui_strings.py
git commit -m "M1 #8: affective-filter UI-string linter"
```

---

## What to do next (in order of value)

1. **Sentry wiring (M1 #7)** — backend (FastAPI integration) + frontend
   (`@sentry/nextjs`), free tier, DSN in env. The remaining instrumented gap.
2. **Standards Alignment single-learner report (M1 #10)** — extends the
   existing student PDF; needs CEFR descriptor pairing per mastery cell. JCPS
   pilot proof artifact.
3. **Frontend p95 tile** — surface the new `/instructor/telemetry/voice-p95`
   endpoint on the cohort page. Single fetch, three numbers, no library.
4. **Wire `lint_ui_strings.py` into CI** when the first GitHub Action lands.
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
- **Voice-turn telemetry uses stdlib `statistics.quantiles`.** Fine to ~10k
  points; swap for a streaming digest if telemetry volume crosses that.
- **Affective-filter banlist is deliberately small.** It pins the masculine
  Spanish form `incorrecto` only; add feminine/plural forms when they appear
  in UI copy rather than pre-emptively.

---

## Open decisions

- **TTS voice.** Hard-coded `nova` server-side. Persona library is M4
  pilot-signal-contingent — don't expose a picker yet.
- **Claude model pin.** `claude-haiku-4-5` (in `correction.py`). Bump together
  with the cost row in `cost_tracker.py` if Anthropic re-prices.
- **Confidence gate.** ASR < 0.5 currently refuses to grade. May want to
  lower for noisier environments after the first pilot data.
- **p95 voice-turn window.** Endpoint defaults to 7 days. Pilot may want a
  shorter rolling window once traffic exists.

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

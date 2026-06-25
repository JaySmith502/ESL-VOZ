# Memory — desktop

> Generated: 2026-06-24 21:38:41  
> Total memories: **6**  
> Breakdown: instruction: 1, goal: 2, context: 2, learning: 1

---

## Instructions

*Standing rules, constraints, and guidelines to always follow.*

### ESL-VOZ pytest must run as 'uv run pytest' from ba...

ESL-VOZ pytest must run as 'uv run pytest' from backend/ — host's global pytest is broken with ImportError. Lesson lint: backend/.venv/Scripts/python.exe scripts/lint_lessons.py

*Confidence: 1 | Status: active | Created: 2026-06-24T20:28:12*

---

## Facts

*Verified information, project status, and established truths.*

*No memories of this type.*

---

## Decisions

*Architectural choices, approach selections, and their rationale.*

*No memories of this type.*

---

## Goals

*Objectives, targets, and milestones to track progress.*

### ESL-VOZ next chunks in value order (revised 2026-0...

ESL-VOZ next chunks in value order (revised 2026-06-24): (1) Sentry wiring backend+frontend for M1 #7; (2) Standards Alignment single-learner report for M1 #10; (3) frontend tile reading /instructor/telemetry/voice-p95 on cohort page; (4) wire scripts/lint_ui_strings.py into CI when first GitHub Action lands; (5) Anthropic prompt caching once correction system prompt > 1k tokens. Skip until later: streaming ASR/TTS, persona picker, WIDA toggle, Cognee/Memgraph.

*Confidence: 0.95 | Status: active | Created: 2026-06-25T01:38:27*

### ESL-VOZ next chunks in value order: (1) p95 voice-...

ESL-VOZ next chunks in value order: (1) p95 voice-turn telemetry table+endpoint for M1 acceptance #6; (2) Sentry wiring; (3) affective-filter UI-string linter; (4) Standards Alignment single-learner report. Skip until later: streaming ASR/TTS, persona picker, WIDA toggle, prompt caching, Cognee/Memgraph.

*Confidence: 0.95 | Status: active | Created: 2026-06-24T20:28:21*

---

## Commitments

*Promises, obligations, and TODOs that need follow-through.*

*No memories of this type.*

---

## Preferences

*User and entity preferences for personalization.*

*No memories of this type.*

---

## Relationships

*Entity connections, team context, and collaboration patterns.*

*No memories of this type.*

---

## Context

*Session summaries, status updates, and conversation state.*

### ESL-VOZ M1 progress 2026-06-24 evening: completed ...

ESL-VOZ M1 progress 2026-06-24 evening: completed acceptance #6 (voice-turn p95 telemetry — VoiceTurnEvent model + segment timing in tutor.py + GET /instructor/telemetry/voice-p95) and #8 (scripts/lint_ui_strings.py affective-filter linter; passes on en.json+es.json; not on CI yet). 108 backend + 18 frontend + 1 E2E tests passing. Remaining M1 boxes: #7 Sentry wiring, #10 Standards Alignment single-learner report. Uncommitted at handoff — see HANDOFF.md for commit suggestion.

*Confidence: 1 | Status: active | Created: 2026-06-25T01:38:12*

### ESL-VOZ M1 status: walking skeleton complete with ...

ESL-VOZ M1 status: walking skeleton complete with real Deepgram ASR (nova-2, 0.5 confidence gate), OpenAI TTS (tts-1), Claude haiku-4-5 correction with 2-layer guardrails (sanitize_transcript + _validate_correction), voice-consent gate on /tutor/subdialog/audio, instructor dashboard usable with Needs-Attention + audit table + Print/PDF. 104 backend + 18 frontend + 1 E2E tests passing. Read HANDOFF.md at repo root.

*Confidence: 1 | Status: active | Created: 2026-06-24T20:28:36*

---

## Events

*Important conversations, milestones, and temporal occurrences.*

*No memories of this type.*

---

## Learnings

*Knowledge acquired from experience, corrections, and insights.*

### npkill run from C:\ or C:\Users\smith deletes node...

npkill run from C:\ or C:\Users\smith deletes node_modules bundled inside installed apps (VS Code at resources\app\node_modules, Docker Desktop resources, etc.), bricking them with 'This app can't run on your PC'. Always scope npkill to a specific dev folder with -d <path>.

*Confidence: 1 | Status: active | Created: 2026-06-24T19:39:16*

---

## Observations

*Patterns noticed, behavioral notes, and recurring themes.*

*No memories of this type.*

---

## Artifacts

*Tool outputs, files, reports, and external references.*

*No memories of this type.*

---

## Errors

*Failure records, bugs, and lessons learned from mistakes.*

*No memories of this type.*

---

*End of memory export.*

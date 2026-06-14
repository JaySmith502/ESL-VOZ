# ADR 0006 — Placement: hybrid conversational + CAT-lite

**Status:** Accepted
**Date:** 2026-06-14
**Depends on:** 0001, 0002, 0003, 0004
**Consumed by:** 0007, 0008, 0011

## Context

Placement is the first runtime interaction. Without it, the adaptive engine starts cold, the teacher dashboard has nothing to show, and every downstream metric is biased by misplacement. The PRD listed "Placement assessment" in scope but specified no format, item bank, adaptive logic, coverage, or cold-start behavior.

## Decision

**Format — hybrid**:
1. 5-question intake form (1 minute): native language, years in US, prior English study, highest education, primary goal, age band. Seeds per-mode prior bands.
2. 2-minute conversational opener in the learner's preferred language. Lowers affective filter; gives fluency baseline.
3. CAT-lite per-mode discrete probes — 3–6 items per mode at adaptive bands.
4. One Mediation task (M2+).

Total session: 10–15 minutes.

**Adaptive logic — rule-based CAT-lite per mode**:
```
start_band = prior_from_intake(student)   # default A2.1
while items_served < 6 AND consecutive_failures < 2:
    item = sample_item(mode, band=start_band, exclude_seen=true)
    if correct: start_band = up_one; consecutive_failures = 0
    else: start_band = down_one; consecutive_failures += 1
estimated_band = band_at_inflection_point
```

**Coverage**: 5 modes × Survival domain only at MVP. Other domains bootstrap through use.

**Item bank**: corpus-derived candidates + human curation, seed of 80 items at MVP. NGSL bands seed vocab probes; minimal pairs seed pronunciation; story banks seed reading; USCIS 100q seeds civics-reading; CEFR descriptors seed grammar.

**"I don't know" is first-class**: soft-fail, no XP penalty, separate `idk_rate` tracked. Two consecutive IDKs terminate the mode probe (same as 2 consecutive failures).

**Output**: 5 `MasteryCell` rows written at `(student, mode, estimated_band, Survival)` with `mastery_score=0.7`, `confidence=0.6`. Other cells start at zero.

## Consequences

- New tables:
  - `placement_items { id, mode, cefr_band, component, domain, source_chunk_id, item_type, prompt, expected_response_type, scoring_rubric }`
  - `placement_sessions { student_id, started_ts, completed_ts, mode_band_estimates JSON, idk_count, opener_transcript }`
- Speaking + writing + mediation items use an LLM grader against a rubric.
- Multiple-choice + cloze items use deterministic scoring.
- Intake form drives both placement priors *and* Spanish L1 transfer prediction layer activation (ADR 0008).
- M1 ships ~60 items (15 per mode for L/S/R/W); Mediation deferred to M2.

## Alternatives considered

- **Pure discrete quiz** — rejected. Boring, raises affective filter, misses speaking.
- **Pure conversation** — rejected. Hard to score reliably; can't cover reading/writing.
- **Full IRT / Bayesian CAT** — deferred to M3+. Needs 500+ attempts per item for calibration.
- **Cover all 4 domains at placement** — rejected. 5 modes × 4 domains × bands = exploding session length.
- **LLM-generated items at runtime** — rejected. Inconsistent difficulty without calibration.

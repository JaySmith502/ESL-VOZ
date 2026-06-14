# ADR 0003 — Mastery = EWMA over (mode × band × domain) cells + per-word SRS

**Status:** Accepted
**Date:** 2026-06-14
**Depends on:** 0001, 0002
**Consumed by:** 0006, 0007, 0010, 0011

## Context

PRD declared "Mastery before advancement" and "Mastery earns more XP than completion alone" but left mastery undefined as a quantity. Without a definition, placement scoring, XP awards, recommendation engine, advancement logic, and teacher dashboards are all undefined. Four sub-decisions had to resolve together: granularity, score type, decay, attempt unit.

## Decision

**Mastery cells**: track at `(student × mode × CEFR band × domain)` granularity. ~120 sparse cells per learner. CEFR descriptors are sub-evidence for each cell.

**Score type**: graded EWMA (exponentially-weighted moving average) over the last N attempts, weighted by item difficulty. A cell is "mastered" when EWMA ≥ 0.85 sustained over ≥3 attempts spread across ≥2 lessons and ≥7 days.

**Two-channel decay model**:
- `mastery_score`: sticky upward; never decreases automatically.
- `confidence`: decays linearly with inactivity days. Below threshold, schedule verification probes (1–2 quick items). Pass → confidence restored. Fail → mastery downgrades.

**Vocabulary mastery tracked separately** per word via Leitner-style SRS (boxes 1–7). Mastery feeds embedded signal into mode×band×domain cells but tracks independently.

**Pronunciation mastery is per-contrast**: per-minimal-pair-contrast SRS state. Spanish-L1 ★★★ contrasts weighted higher in scheduling.

**Attempt unit**: per voice-tutor turn for AI tutor activities; per lesson step for non-tutor activities. Each `Attempt` row carries: item_id, descriptor(s) probed, score, latency, error tags, hint use.

## Consequences

- New data model:
  - `MasteryCell { student_id, mode, cefr_band, domain, mastery_score, confidence, attempts_count, last_evidence_ts, descriptors_demonstrated[] }`
  - `VocabularyState { student_id, lemma, srs_box, next_review_ts, recall_history[] }`
  - `ContrastSRSState { student_id, contrast_id, srs_box, next_review_ts }`
  - `Attempt { id, student_id, lesson_id, step_id, tutor_turn_id, cefr_descriptor_ids[], score_0_1, latency_ms, error_tags[], used_hint, ts }`
- XP is a *derived view* of attempts + mastery transitions, not its own first-class entity (revisited in ADR 0011).
- PRD's `mastery_records` table replaced by `mastery_cells`.
- Confidence-decay job runs nightly via APScheduler.

## Alternatives considered

- **Per-CEFR-descriptor granularity** (~1500 cells/learner) — rejected. Too sparse; expensive to populate; mastery is unintuitive to teachers.
- **Single overall CEFR level per learner** — rejected. Useless for adaptive recommendation.
- **Binary mastery (mastered / not)** — rejected. Loses the gradient needed for partial progress UI and weighted recommendations.
- **Full Bayesian Knowledge Tracing** — deferred to M3+. Needs calibrated item difficulty parameters we don't have yet.
- **Mastery decays for grammar/mode cells** — rejected. Adults don't unlearn A2 grammar. Decay is in confidence only; sticky upward in score.

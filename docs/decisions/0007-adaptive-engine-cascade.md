# ADR 0007 — Five-bucket cascade ranker + recommendation traces

**Status:** Accepted
**Date:** 2026-06-14
**Depends on:** 0003, 0005, 0006
**Consumed by:** 0008, 0010, 0011, 0012

## Context

PRD called the adaptive engine "select next activity based on weakest area." That's the wrong policy — it produces a learner experience of constant failure, raises the affective filter, and collapses retention. A real adaptive engine balances 5 competing signals. The PRD also required graph-aware reasoning and teacher-justified recommendations without specifying the mechanism.

## Decision

**Selection target — cascade by priority through 5 buckets**, highest-priority non-empty bucket wins:

1. **Overdue SRS reviews** (vocab + pronunciation contrasts) — never skip
2. **Active learning path** (current sequence toward stated goal)
3. **Mastery consolidation** (cells at 0.5–0.85 needing one more push)
4. **Stretch challenge** (one band up, if confidence is high)
5. **Exploration** (unexplored domain × mode)

**Policy structure**: rule-based cascade for MVP; log every recommendation to `recommendation_traces` for future ML ranker training.

**Six activity types** the engine picks from:
- `vocab_review` (3–10 min)
- `lesson` (10–20 min)
- `tutor_conversation` (5–15 min)
- `pronunciation_drill` (3–5 min)
- `reading_passage` (5–15 min)
- `mediation_task` (5–10 min)

`tutor_conversation` is the only activity type that puts the LLM in the hot path.

**Exploration policy — per-learner-tuned ε-greedy**: ε ∈ [0.10, 0.30] based on recent success rate + IDK rate. Anxious learners ε=0.10; confident ε=0.30; default 0.20.

**Five hard constraint filters** (applied before ranking):
- Session length budget (learner-set per session)
- Mode rotation after 20+ min of same mode
- Recency cooldown (no repeat lesson within 7 days unless overdue review)
- Streak protection (suppress stretch-challenge if Current Run ≥ 3)
- Domain alignment with stated goal (bias, not hard filter)

**Reasoning trace on every `/next-activity` response**: structured JSON with `bucket_fired`, `rationale`, `graph_evidence`, `candidates_considered`, `tied_with`, `exploration_roll`. Powers teacher dashboard "why" panel, tutor's prompt context, and ML ranker training corpus.

## Consequences

- New `recommendation_traces` table.
- `/next-activity` endpoint accepts `session_context` payload (time_budget_minutes, current_streak, modes_seen_this_session).
- Engine module is pure Python function over mastery + SRS queue + recent attempts.
- No LLM in `/next-activity` hot path.
- M1 ships buckets 1+2+3 only with ε=0 (no exploration). Buckets 4+5 + ε-greedy activate in M2.
- ML ranker training spec deferred to M3+ once recommendation traces accumulate.

## Alternatives considered

- **Single objective (biggest gap)** — rejected. Produces constant failure UX.
- **Weighted sum of objectives** — rejected. Produces mush; hard to debug.
- **Supervised ML ranker at MVP** — rejected. Zero training data; cascade is interpretable.
- **Reinforcement learning** — rejected. Premature; A/B infra doesn't exist yet.
- **Soft constraints (penalty in score)** — rejected. Hard filters keep behavior predictable.

# ADR 0008 — Compiled prompts + band-determined corrections + validators

**Status:** Accepted
**Date:** 2026-06-14
**Depends on:** 0002, 0004, 0005, 0007
**Consumed by:** 0009, 0010

## Context

The PRD's `ai_behavior` (lines 214–225) was a 10-line wish list passed to an LLM system prompt. Behavior of that shape is non-deterministic: the model decides every turn whether to comply. The result is a tutor that's mostly good and sometimes catastrophic — long explanations on Tuesday, two-question turns on Wednesday, hard explicit correction to an A1.1 learner on Thursday.

For adult Spanish-L1 immigrants whose entire path is anxiety-managed (per the SLA primer's affective-filter rule), unpredictable correction style destroys retention. We need to pull behavior out of LLM judgment wherever it can be made deterministic.

## Decision

**Tutor scope (two responsibilities only)**:
1. Conversation partner in `tutor_conversation` activities.
2. Open-response grader utility for speaking/writing/mediation items in placement, lessons, SRS recall.

Everything else (vocab review, pronunciation drill, reading passage, lesson steps) bypasses the LLM.

**Three-layer compiled prompt**:
- **Layer 1 — Identity** (static, ~200 tokens).
- **Layer 2 — Compiled behavioral rules** (~600 tokens) generated at deploy time from Tier C + `(band, activity_type, domain, l1)`. ~30 cached variants.
- **Layer 3 — Per-turn context** (~400 tokens): activity goal, target descriptors, recent attempts, graph evidence from ADR 0007 trace, last 6 turns, retrieved chunks.

**Error correction — Lyster-Ranta technique by band, deterministic**:
- A1.1, A1.2 → Recasts only
- A2.1 → Recasts + clarification requests
- A2.2, B1.1 → + Elicitation
- B1.2, B2 → All except repetition-with-emphasis

**Bilingual scaffolding — per-band Spanish policy, deterministic**:
- A1.1 → Free use of Spanish as default scaffold
- A1.2 → Spanish for new concepts; English practiced
- A2.1 → Spanish on request only
- A2.2+ → English only except mediation tasks

**L1 transfer detector**: when an error matches a pattern from `data/bilingual/spanish_l1_transfer_cheat_sheet.md`, the correction policy activates a **bridge-recast** — explicit L1 → L2 contrast leveraging Cummins CUP.

**Two-layer guardrails**:
- *Preventive* (compiled prompt rules): turn-length caps per band (A1=40, A2=80, B1=140, B2=240 tokens), one-question caps for A1.x, forbidden constructions (idioms at A1, metalinguistic terms below B1).
- *Detective* (post-generation validators, 6 checks): length, question-count, forbidden-construction, forbidden-correction, L1 leak, ASR confidence gate. Failure → retry; second failure → canned fallback from 20-item library + Sentry log.

## Consequences

- New modules/tables:
  - `tutor_prompt_compiler` — input: (band, activity, domain, l1); output: cached Layer 2 prompt.
  - `tutor_validator` — 6 deterministic checks.
  - `correction_policy` table (7 sub-bands × allowed techniques).
  - `spanish_policy` table (7 sub-bands × Spanish-use rules).
  - `l1_transfer_patterns` table (seeded from cheat sheet).
  - `canned_responses` library (~20 entries).
- Compilation happens at deploy or on Tier C change, not per turn.
- Per-turn data flow: ASR/text → L1 detector → graph trace from ADR 0007 → prompt compiler → Anthropic LLM → validator → (display | retry | fallback) → attempt write → mastery update.
- M1 ships `tutor_conversation` in Speaking + Listening modes only; Reading + Writing in M2.

## Alternatives considered

- **Long behavioral prompt with vibes guidance** — rejected. Non-deterministic; can't debug; raises affective filter unpredictably.
- **Fine-tuned LLM on ESL tutor data** — rejected at MVP. No data, no eval set, cost of fine-tune.
- **No grader utility; tutor scores its own conversations** — rejected. Conflict of interest; grader needs independent rubric scoring.

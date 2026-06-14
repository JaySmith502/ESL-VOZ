# ADR 0010 — Lessons as version-controlled YAML + 12 step types + lint pipeline

**Status:** Accepted
**Date:** 2026-06-14
**Depends on:** 0001, 0002, 0003, 0004, 0007, 0008
**Consumed by:** 0011, 0012

## Context

PRD referenced `Lesson` and `LessonStep` entities but never defined what a lesson is structurally. The adaptive engine picks `lesson` as an activity type (ADR 0007) and the mastery engine writes cells based on what a lesson targets (ADR 0003) — without a lesson schema, both are undefined. M1 ships hand-authored lessons; M3 wants LLM-generated lessons. Both must produce the same shape.

## Decision

**Source of truth: version-controlled YAML in `/content/lessons/`.** DB row is a projection ingested on rebuild. Files are diff-reviewable in git; this is what makes curriculum credible.

**Atomic shape** (selected fields):

```yaml
lesson_id: doctor_visit_a2_survival
title: { en: ..., es: ... }
template_pattern: PPP        # PPP | TBLT | TPR | sheltered
target_descriptors: [cefr-a2.1-spk-surv-#3, ...]
modes: [Speaking, Listening]
components: [Vocabulary, Pragmatics]
domain: Survival
cefr_band: A2.1
estimated_minutes: 15
prerequisites:
  mastery_cells: [...]
  vocab_known: [...]
content_refs: { chunks: [...] }
steps: [...]
completion_rules:
  done_when: all_steps_attempted
  mastered_when: all_production_steps_score >= 0.8
origin: authored             # authored | generated_curated | generated_uncurated
license: cc-by-sa-4.0
```

**12 step types**: `intro`, `vocab_intro`, `vocab_drill`, `grammar_intro`, `comprehension_check`, `listen_passage`, `read_passage`, `production_speaking`, `production_writing`, `mediation`, `tutor_subdialog`, `reflection`.

`tutor_subdialog` is the only LLM-hot-path step.

**Linear sequencing + skip-on-mastery for `intro`-tier steps only**. Full DAG branching deferred to M3+.

**Four completion states**: `started`, `done`, `mastered`, `abandoned`. Re-takes weighted higher in EWMA (per ADR 0003).

**Three origin states**:
- `authored` — human-written, code-reviewed
- `generated_curated` — LLM-drafted, human-edited, promoted (M3+)
- `generated_uncurated` — LLM-drafted, in `/content/lessons/_pending/`, **never serves to learners**

**Mandatory 5-stage lint pipeline** (CI gate on every PR):
1. Schema lint (Pydantic)
2. Content lint (bilingual fields, estimated_minutes ±20%, ≥1 production step)
3. License lint (Tier B redistributable check)
4. CEFR alignment lint (descriptors all in declared band)
5. Pedagogy lint (template_pattern enforces step ordering)

## Consequences

- New tables: `lessons` (expanded), `lesson_steps`, `lesson_rubrics`, `lesson_completions`.
- New directories: `/content/lessons/`, `/content/lessons/_pending/`, `/content/rubrics/`.
- `scripts/ingest_lessons.py` reads YAML → validates via lint → upserts to DB → emits graph edges (aligns_with descriptors, composes steps, prerequisite_of other lessons).
- `make lint-lessons` runs all 5 stages; CI gate.
- Skip-on-mastery evaluator: function called by engine before serving each step.
- M1 seed = **12 hand-authored lessons** A1.1 → A2.1 Survival, all `authored` origin.
- M2 adds 15 more lessons + 7 step types.
- M3 unlocks `generated_curated` pipeline with curator queue UI.

## Alternatives considered

- **CMS web UI as source of truth at MVP** — rejected. Slower than YAML for solo author; harder to diff-review.
- **Lessons in DB only** — rejected. Loses git diff visibility, which matters for credibility with pilot partners.
- **Single generic step type with sub-flags** — rejected. Engine, mastery, and scoring rubrics all benefit from typed steps.
- **Full DAG branching at MVP** — deferred. Linear is enough to ship; M3+ if pilot data shows linear is failing.
- **No origin distinction** — rejected. Generated content needs a gate that authored doesn't.

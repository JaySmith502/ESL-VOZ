# Architecture Decision Records — Index

This directory holds the 15 ADRs from the design grilling session of **2026-06-14** that converted the original `idea.json` v0.2.0 into a buildable plan (captured in `../PRD.md` v2.0 and `../roadmap.md`).

Each ADR follows the standard format: Status, Context, Decision, Consequences. Numbered in the order they were resolved, which is also the dependency order — earlier ADRs are foundations for later ones.

| # | Title | Anchor |
|---|-------|--------|
| [0001](0001-cefr-canonical-wida-projection.md) | CEFR canonical; WIDA as projection | Engine speaks one taxonomy |
| [0002](0002-three-axis-tagging.md) | Three-axis tagging: Mode × Component × Domain | Mediation is a first-class mode |
| [0003](0003-mastery-model.md) | Mastery = EWMA over (mode × band × domain) cells + per-word SRS | Two-channel sticky mastery + decaying confidence |
| [0004](0004-three-tier-corpus.md) | Three-tier corpus: Standards / Learner / TutorRef | Corpus is operative, not decorative |
| [0005](0005-graph-as-projection.md) | SQL is truth; graph is derived projection | Graph layer swappable |
| [0006](0006-placement-design.md) | Placement: hybrid conversational + CAT-lite | Affective-filter-aware bootstrap |
| [0007](0007-adaptive-engine-cascade.md) | Five-bucket cascade ranker + recommendation traces | Interpretable adaptive engine |
| [0008](0008-tutor-compiled-prompts.md) | Compiled prompts + band-determined corrections + validators | Behavior out of LLM judgment |
| [0009](0009-voice-loop-cloud-only.md) | Cloud-only voice stack (Deepgram + OpenAI TTS + Anthropic) | Forced by no local compute |
| [0010](0010-lesson-yaml-schema.md) | Lessons as version-controlled YAML + 12 step types + lint | Authoring as content engineering |
| [0011](0011-xp-and-hours-saved.md) | XP + Hours Saved with affective-filter invariants | No-shame gamification, no TimeBack branding |
| [0012](0012-teacher-dashboard.md) | Two persona views + mastery matrix + equity panels | JCPS-defensible dashboard |
| [0013](0013-users-cohorts-consent.md) | Coordinator-provisioned magic link + 3-layer consent + family accounts | Pilot-org-ready user model |
| [0014](0014-tech-stack.md) | Next.js + FastAPI + Postgres + Hetzner US single VPS | ~$15/mo fixed infra |
| [0015](0015-milestones-and-scope.md) | M1 skeleton + M2 JCPS-ready + M3 scale + M4 partnership | Tracer-bullet milestones |

---

## How to read

- Start at 0001 and read in order if you want to understand *why* the system has its shape.
- Skip to a specific ADR if you need to know why a single decision was made.
- Every ADR references its dependencies (earlier ADRs it builds on) and its consumers (later ADRs that build on it).
- All decisions are **accepted** as of the grilling session date. To overturn one, write a new ADR with status `Supersedes #NNNN` and update this index.

## ADR template

```markdown
# ADRNNNN — Short title

**Status:** Accepted | Proposed | Superseded
**Date:** YYYY-MM-DD
**Depends on:** ADRNNNN, ADRNNNN
**Consumed by:** ADRNNNN, ADRNNNN

## Context
Why this decision had to be made; what was at stake.

## Decision
What was decided. Concise; mechanism-focused.

## Consequences
What changes downstream: schemas, code modules, deferred items, trade-offs accepted.

## Alternatives considered
Optional. Other paths weighed and rejected.
```

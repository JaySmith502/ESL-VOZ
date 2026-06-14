# ADR 0015 — M1 skeleton + M2 JCPS-ready + M3 scale + M4 partnership

**Status:** Accepted
**Date:** 2026-06-14
**Depends on:** All preceding ADRs (0001–0014)
**Consumed by:** —

## Context

Across 14 prior ADRs we designed a substantial system. The original PRD's 4 milestones (lines 420–459) named deliverables but didn't *order* the cuts. Without explicit ordering, M1 becomes an aspirational checklist that takes 9 months instead of 3, and the pilot slips past the funding/attention window.

The honest answer: **most of what we designed doesn't ship in M1.** The pilot question isn't "did we design well" — it's "did we ship something a real cohort can use and a real teacher can defend."

## Decision

### M1 — Walking Skeleton Pilot (La Casita adult cohort, 10–14 weeks)
**Goal**: end-to-end loop for adult Survival-domain learners; prove the engine and affective-filter discipline.

In: CEFR canonical (no WIDA UI); 4 modes (L/S/R/W); 2 components (Vocab/Pronun); **Survival only**; full mastery + SRS; corpus tiers A+B+C ingested; graph schema with structural + per-student edges only; placement 4 modes × Survival × 60-item bank; **engine buckets 1+2+3 only** (ε=0); tutor conversation in Speaking + Listening; full voice cloud loop with Whisper-proxy pronunciation; 5 step types active; **12 hand-authored lessons** A1.1 → A2.1 Survival; XP + Hours Saved + 5 badges; instructor dashboard only with 2 actions + 1 report; adult shell only; magic-link email.

Out (cut from M1): WIDA toggle, Mediation, School/Academic/Workplace, Grammar/Pragmatics components, buckets 4+5, ML ranker, tutor in Reading/Writing, SpeechAce, 7 step types, 10 badges, coordinator view, 3 actions, 3 reports, equity panels, child UI shell, family accounts, SMS, SSO.

**M1 acceptance criteria** (all must pass):
1. ≥1 cohort of 8 learners completes intake + placement
2. ≥3 sessions/week/learner for 4 consecutive weeks
3. ≥80% of touched mastery cells positive Δ over 8 weeks
4. Instructor uses dashboard ≥2×/week per cohort
5. Per-learner cloud cost ≤ $12/mo
6. p95 voice turn ≤ 2.5s
7. Sentry < 5 errors/learner/week
8. Zero affective-filter UI-lint violations
9. Magic-link + 3-layer consent signed bilingually for all enrolled
10. Standards Alignment report (single-learner) renders defensibly

### M2 — JCPS Pilot Readiness (8–10 weeks post-M1)
**Goal**: K-12 pilot possible. WIDA projection + Mediation + child UI + coordinator view + equity panel + signed DSA + Standards Alignment report.

Adds: WIDA projection toggle; Mediation mode; School + Workplace domains; Grammar + Pragmatics components; cascade buckets 4+5 + ε-greedy; tutor in Reading + Writing; SpeechAce pronunciation API; 7 more step types; +15 lessons (A1.1 → B1.1); full badge library; cohort Hours Saved rollup; coordinator view + 5 actions + 4 reports; equity & cost panels; child UI shell + family-managed accounts; SMS magic link; DSA signed.

**M2 acceptance criteria**: DSA signed; 1 K-12 + 1 adult cohort concurrent; Standards Alignment audited by JCPS EL staff; equity panel real data; cost ≤ $15/mo/learner; 2 cohorts × 12 learners × 8 weeks sustained.

### M3 — Scale & Intelligence (3–4 months post-M2)
**Goal**: 100+ learners; LLM-assisted authoring; first ML ranker.

Adds: full DAG lesson branching; generated lesson pipeline (`generated_curated` origin + curator queue); first ML ranker trained on M1+M2 recommendation traces (bucket 4 A/B vs rule-based); bilingual_equivalent + transferred_from graph edges activated in tutor + engine; Academic domain; Google OAuth SSO; Postgres → Supabase Pro migration; second VPS for workers; Cognee/Memgraph evaluation (eval only, not commitment).

**M3 acceptance criteria**: 100+ active learners; LLM-curated lessons cut authoring time ≥50%; ML ranker outperforms rule-based by ≥5% on held-out cohort; cost ≤ $15/mo/learner at 5× growth; Cognee/Memgraph go/no-go documented.

### M4 — Partnership & Polish (open-ended)
**Pilot-signal-contingent items**: District SSO; **adult-ed credit-hour negotiation (the moat)**; persona library; offline-degraded mode; full-duplex barge-in; multi-district admin; Cognee/Memgraph cutover.

**M4 acceptance criteria (one of)**:
1. One signed credit-hour recognition agreement (the moat)
2. OR signed expansion to a second district / community partner
3. OR explicit polish-only release with documented learner-NPS improvement ≥10 points

Without one of these, M4 is acknowledged as polish-only.

### Permanently out of scope (all milestones)
Native mobile apps, enterprise multi-district admin (without contract), high-stakes testing, video generation, hard dependency on any single graph product.

### Scope-creep policy
**Adding anything to M_x requires explicit cut of equivalent-weight scope from same M_x. Backlogs go to M_x+1.**
Exception: items that unblock M_x acceptance criteria can enter M_x without an equivalent cut (they make M_x shippable, not larger).

### CI acceptance-criteria gate
`scripts/check_acceptance_M{n}.py` runs against production data and fails if any criterion misses. Launch is gated by green check.

### Pilot-signal log
`/docs/pilot-signal-log.md` updated after every partner conversation. M4 contingent decisions reference this file. We do not pre-build for speculative needs.

## Consequences

- PRD `milestones` (lines 420–459) replaces with M1–M4 structure including explicit cuts.
- PRD `scope.in_scope` reorganizes per milestone for top-to-bottom buildability.
- PRD `acceptance_criteria` becomes per-milestone, not global.
- New `/docs/roadmap.md` with full milestone tasks.
- New `/docs/scope-creep-log.md`.
- New `/docs/pilot-signal-log.md`.
- CI gate scripts per milestone.
- Open-question lists per milestone (named in roadmap.md).

## Alternatives considered

- **Build everything in M1** — rejected. 9+ month timeline kills pilot momentum.
- **Skip M1 pilot, ship to JCPS directly in M2** — rejected. La Casita adult cohort is lower-stakes proving ground; JCPS won't sign DSA without proof artifact.
- **Open-ended milestones (no acceptance criteria)** — rejected. "Done" becomes ambiguous; launches slip indefinitely.
- **No scope-creep policy** — rejected. M1 becomes M3; the policy is the discipline.
- **Pre-build M4 contingent items** — rejected. Speculative; wastes effort if pilot signal doesn't materialize.

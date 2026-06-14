# ADR 0012 — Two persona views + mastery matrix + equity panels

**Status:** Accepted
**Date:** 2026-06-14
**Depends on:** 0001, 0003, 0005, 0007, 0011
**Consumed by:** 0013, 0015

## Context

PRD's teacher dashboard was named but unspecified: no persona model, no metric leads, no actions, no exports, no equity surfaces. The JCPS pilot decision will be made on this surface. Get it wrong → pilot doesn't expand. Get it right → credible institutional partner.

PRD's secondary users (ESL teachers, tutors, counselors, program coordinators, community support staff) cluster into two workflows that need different views.

## Decision

**Two persona views, one product, RBAC enforced server-side**:
- **Instructor view** — assigned cohorts (1–3 typically); "who needs help today" focus.
- **Coordinator view** — all overseen cohorts; equity + cost panels; reports.
- Users with both roles toggle.

**Instructor landing — cohort grid** (~30 rows × 6 columns): student, last active, current top-mode band, weekly mastery delta, Hours Saved, `needs_attention` flag. Color-coded but not alarmist; no red, no shame.

**Single-student drill-in — CEFR × Mode × Domain mastery matrix** (heatmap). The headline view.

**Headline metric: weekly mastery delta** (cells advanced + mean Δ across active cells). NOT XP — XP is learner currency; teachers need progress signal.

**`needs_attention` flag — 2-of-6 soft signals, never single threshold**:
declining mastery / inactivity ≥5 days / IDK rate >40% / SRS backlog >20 / validator retry rate spiking / voice consent withdrawn.

**Five intervention actions, all audited, none write directly to XP/mastery**:
- Flag (with reason)
- Note (versioned, bilingual via grader)
- Adjust Band (override engine estimate, requires reason)
- Recommend Lesson (push to queue)
- Schedule Check-in (calendar 1:1)

Teacher actions modify *what the engine is told*, never the engine's outputs. Keeps learning signal honest.

**Four standard reports**: per-student progress (parent-conference / IEP), cohort summary (monthly), **Standards Alignment** (CEFR + WIDA + descriptor evidence — JCPS credibility artifact), Outcome report (anonymized cohort aggregate).

**Coordinator equity & cost panels** (required for pilot defensibility):
- Engagement equity (distribution of activities per learner)
- Modality equity (voice vs text mastery deltas)
- Demographic equity (aggregates only, never individual)
- Cost panel (per-cohort cloud spend from ADR 0009 `cost_events`)
- Audit log (all teacher actions, searchable)

## Consequences

- New tables: `teacher_actions`, `teacher_notes`, `cohort_summary` (materialized view, nightly refresh).
- `report_generators/` module — 4 templated exports (PDF via WeasyPrint or similar + CSV).
- Coordinator-only RBAC scope for equity & cost panels.
- Frontend: 2 navigation views, cohort grid + mastery matrix component, intervention modal, report-gen UI.
- Single-student mastery matrix is the most complex visual component — invest in UX there.
- M1 ships instructor view + cohort grid + mastery matrix + Flag/Note actions + per-student PDF only. M2 adds coordinator view, 3 actions, 3 reports, equity panels.

## Alternatives considered

- **Single unified view for all roles** — rejected. Equity panels confuse instructors; cohort grid is overkill for coordinators.
- **XP as headline metric** — rejected. Misleading; learners can grind XP without mastery.
- **Single-threshold "needs attention"** — rejected. False positives + brittle.
- **Teacher can directly edit XP/mastery** — rejected. Corrupts learning signal; un-debuggable.
- **Build equity panels in M2 only** — partially accepted; instructor view ships in M1, coordinator+equity in M2.

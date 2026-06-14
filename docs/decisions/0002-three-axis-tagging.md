# ADR 0002 — Three-axis tagging: Mode × Component × Domain

**Status:** Accepted
**Date:** 2026-06-14
**Depends on:** 0001
**Consumed by:** 0003, 0006, 0007, 0008, 0010

## Context

The original PRD listed nine flat "learning domains": Speaking, Listening, Reading, Writing, Vocabulary, Grammar, Survival English, School English, Academic English. These mashed three orthogonal axes into one list. A lesson on "ordering food at a restaurant" is Speaking + Listening + Vocabulary + Pragmatics + Survival domain — collapsing those into one `skill_area` string loses the ability to compute mastery or recommend along independent dimensions.

CEFR's canonical decomposition is also different from the PRD: CEFR organizes around Reception, Production, Interaction, **Mediation** — silent on Vocabulary/Grammar as separate skills (they're components of the modes).

## Decision

Replace the flat 9-item list with a three-axis tag system:

- **Mode** (5): Listening, Speaking, Reading, Writing, **Mediation**
- **Component** (4): Vocabulary, Grammar, Pronunciation, Pragmatics
- **Domain** (4): Survival, School, Academic, Workplace

Every lesson, content chunk, and mastery cell carries tags on all three axes. Mediation is first-class — it's CEFR's term for translanguaging activities (explain an English notice to your mom in Spanish) and is the differentiator for a Spanish-L1 Louisville population.

PRD's "Survival/School/Academic English" become **domain tags**, not separate skills. Vocabulary and Grammar become components that attach to mode-tagged lessons.

## Consequences

- `lessons.skill_area` (single string) → `lessons.modes[]`, `lessons.components[]`, `lessons.domain`.
- Mastery cells become `(student × mode × cefr_band × domain)` tuples — up to 120 sparse cells per learner (5 × 6 × 4).
- Placement quiz probes each mode independently and produces 5 CEFR band estimates, not 1.
- Graph node types for skills become richer: `Mode`, `Component`, `Domain` nodes with cross-edges.
- The bilingual support corpus (`data/bilingual/`) and translanguaging materials gain a first-class engine home in the Mediation mode.

## Alternatives considered

- **Keep flat 9-domain list as tags** — rejected. Loses CEFR alignment; "Survival" as a skill alongside "Speaking" is a category error.
- **4 CEFR modes + 4 components only, drop domain axis** — rejected. Loses the ability to distinguish "strong in Survival Reading, weak in Academic Reading."
- **Mediation as a sub-mode of Speaking** — rejected. Mediation has its own descriptors in CEFR Companion Volume; collapsing it loses analytic power and discards La Casita's bilingual context.

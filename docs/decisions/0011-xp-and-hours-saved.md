# ADR 0011 — XP + Hours Saved with affective-filter invariants

**Status:** Accepted
**Date:** 2026-06-14
**Depends on:** 0003, 0007, 0010
**Consumed by:** 0012

## Context

XP and rewards were 11 lines of vibes in the original PRD. Done wrong, XP raises the affective filter — most language apps gamify by punishing struggling learners (lose streak, lose XP, fall down leaderboard). For Spanish-L1 adult immigrants this destroys retention.

"Time-back" was the platform's namesake but undefined. User has since clarified: drop hard references to TimeBack branding; inspiration acknowledged in internal docs only.

## Decision

**XP formula** — three sources summed per activity, capped at 2× base completion XP:
- Completion XP (fixed by activity type)
- Mastery delta XP (`(post − pre) × 100`, positive only)
- SRS recall XP (`5 × difficulty_factor`)

**Hard rules**:
- XP is monotone non-decreasing per learner (DB constraint on `amount > 0`).
- "I don't know" is XP-neutral.
- Hint use reduces step XP by 30% but never to zero.

**Levels = CEFR sub-band achievements**, not XP thresholds. XP fills a per-band progress meter; crossing a band triggers a "Level Up" celebration.

**Practice Days + Current Run (no shame streaks)**:
- Practice Days: cumulative count of any active day. Never decreases.
- Current Run: consecutive-day counter; decays by 1 per missed day, never snaps to 0 unless 7+ consecutive days missed.

**~15 named bilingual badges** mapped to concrete mastery cells, lesson groups, or behavioral milestones. M1 ships 5; M2 ships the full 15. Spanish form primary in Spanish-mode UI.

**Hours Saved meter** (renamed from "time-back"):
- Anchored to published adult-ESL teaching-hour benchmarks (~80–100 hours per CEFR sub-band from CASAS / WIDA pacing data).
- Displayed as gain ("You've saved 12 hours of class time"), never deficit.
- Cohort rollup visible as community signal.
- **No "TimeBack" brand reference anywhere in product copy or marketing.**
- M4 goal: negotiate with JCPS adult-ed and La Casita to recognize Hours Saved as adult-ed credit hours (the moat).

**Eight affective-filter invariants** (engineering invariants, code-reviewed):
1. XP monotone non-decreasing.
2. No leaderboards in MVP.
3. IDK is XP-neutral.
4. No "streak lost" notification type.
5. No "you fell behind" framing.
6. Bilingual celebration default.
7. Time-back framed as gain not deficit.
8. Hint use normalized — UI prominent; copy reads "Using hints is part of learning."

**Affective-filter UI string linter**: scans for banned words (`lost / broke / failed / behind / missed`) and flags for rewrite. CI gate.

## Consequences

- `xp_events` table with `amount > 0` DB constraint and `source_type` enum.
- `learner_xp_progress` view (per-band XP pool, practice days, current run, hours saved).
- `badges` registry + `learner_badges` join table.
- `cohort_time_back` rollup (M2).
- `xp_formula.py` module with the three-source formula + cap + hint penalty.
- Teaching-hours-per-band benchmark table sourced from CASAS / WIDA pacing data; citations in code comments.
- `affective_filter_lint.py` script in CI.
- PRD line 244 ("Symbolic time back rewards") replaced with "Hours Saved meter against published adult-ESL teaching-hour benchmarks."

## Alternatives considered

- **Traditional streaks** — rejected. Affective filter risk.
- **Logarithmic XP curve** — rejected. Front-loads dopamine but feels unrewarding at advanced levels.
- **Cash-out time-back at MVP** — rejected. Requires external partner; defer to M4 negotiation.
- **No XP at all (pure mastery)** — rejected. Loses learner motivational signal.
- **Keep "TimeBack" branding** — rejected per user direction; trademark adjacency risk; product stands on its own.

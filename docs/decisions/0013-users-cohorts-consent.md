# ADR 0013 — Coordinator-provisioned magic link + 3-layer consent + family accounts

**Status:** Accepted
**Date:** 2026-06-14
**Depends on:** 0006, 0009, 0012
**Consumed by:** 0015

## Context

Multiple ADRs referenced auth, consent, and cohort structure without pinning the user model. Adult Latino immigrants often lack stable personal email; K-12 students have neither email nor phone. JCPS pilot will hit COPPA + FERPA + KY SB 216. PRD said "email/password or magic link" — too vague to build against.

## Decision

**Auth — coordinator-provisioned + magic link**:
1. Coordinator creates learner account (name, intake answers, contact email or SMS, language preference).
2. Platform sends bilingual welcome message via Resend (email) or Twilio (SMS).
3. Magic links: tokenized, single-use, 7-day expiry, coordinator-regeneratable.
4. SSO (Google OAuth) deferred to M3+; district SSO (Clever/ClassLink) to M4+.

**Cohort model — single primary + secondary tags**:

```yaml
cohort:
  id: la_casita_spring_2026_beginning
  name: { en, es }
  partner_org: la_casita_center
  program_type: adult_community  # adult_community | k12_pull_out | k12_full_immersion | workplace | civics_prep
  primary_instructor_id
  coordinator_id
  start_date / expected_end_date
  cefr_target_band
  default_domain
  status: pre_enrolled | active | paused | completed | archived
```

**`paused` is respected by the engine**: confidence decay pauses, SRS freezes, no recommendations. Coordinator-pause is forgiving.

**3-layer consent**:
1. Platform Terms (required; withdraw → account deactivation)
2. Voice & Audio Processing (required for voice activities per ADR 0009; withdraw → text-only mode)
3. Anonymized Data Sharing (optional; withdraw → removed from aggregates)

All bilingual plain-language (6th-grade reading), versioned receipts, withdrawable from learner profile UI in one click.

**Under-13 / K-12 path — family-managed account**:
- Parent/guardian primary account holds all consents.
- Child sub-profile logs in via parent-managed or coordinator-managed magic link.
- **Separate child UI shell**: larger touch targets, no community features, no external links, friendlier visuals. No Hours Saved meter (concept doesn't translate well to under-13); replaced with growing-tree or filled-jar visual.
- Adult and child shells share the same backend.

**COPPA + FERPA + KY SB 216 compliance**:
- Parental consent gate before any data collection from under-13.
- Educational records access via RBAC scopes.
- **Data Sharing Agreement (DSA) template** in `/docs/legal/DSA-template.md` for JCPS pilot signature.

**3 language modes** — Spanish-first / Bilingual / English-only. First-touch splash with 3 buttons. Coordinator-provisioned accounts inherit cohort default.

## Consequences

- New tables:
  - `users` expanded: `role, contact_method, contact_value, language_mode, is_child, parent_user_id, created_at`
  - `cohorts` per the 13b structure
  - `cohort_memberships` (many-to-many for primary + secondary)
  - `consent_grants` — 3 layers × versioned × withdrawable
  - `magic_link_tokens` (TTL'd via Redis)
- Magic-link service (Resend + Twilio).
- Coordinator roster management UI (provision learners, regenerate links).
- DSA template + legal review for JCPS pilot.
- First-touch language splash + profile-level language toggle.
- RBAC matrix: learner / parent / instructor / coordinator / admin, server-enforced.
- M1 ships adult shell + email magic link + 3-layer consent. M2 adds child shell + SMS + DSA.

## Alternatives considered

- **Email/password** — rejected. Password fatigue; many adult learners lack stable email accounts.
- **Phone+SMS only** — viable but loses adult learners who prefer email.
- **OAuth at MVP** — rejected. Adult learners often lack Gmail; K-12 needs district contracts.
- **Single UI for adult + child** — rejected. Cognitive and safety needs differ; separate route trees are cleaner.
- **Single consent at signup** — rejected. Coupling voice consent to platform consent means voice-refusers can't use the platform; granular consents preserve access.

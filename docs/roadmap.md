# ESL-voice Roadmap

**Last updated:** 2026-06-14
**Owner:** Solo / passion project
**Pilot target:** La Casita Center adult cohort (M1) → JCPS EL site (M2)

This roadmap is the **build document**. The PRD says what the platform is; this says what ships in what order, with hard acceptance gates, and what is explicitly cut from each milestone.

---

## Operating principles

1. **Tracer-bullet vertical slices.** Each milestone is a thinnest-possible end-to-end slice. We do not "build the backend in M1 and the frontend in M2."
2. **Hard acceptance gates.** A milestone is not "done" until all numbered acceptance criteria pass — measured, not asserted.
3. **Scope-creep policy.** Adding anything to a milestone requires an explicit cut of equivalent-weight scope from the same milestone. Backlogs go into M+1.
4. **Pilot-signal contingency.** Some features in M4 are only built if pilot data demands them. We don't pre-build for speculative needs.
5. **Cost discipline.** Every milestone has a per-learner-cloud-cost target. Misses block launch.

---

## M1 — Walking Skeleton Pilot

**Goal:** End-to-end loop works for adult Survival-domain learners in Spanish-L1 Louisville context. Prove the engine and the affective-filter discipline before scaling.

**Pilot:** La Casita Center adult cohort, 1 instructor, 8–15 learners, 12 weeks.

**Estimated duration:** 10–14 weeks of focused build + 2 weeks pre-launch lesson curation.

### In scope

| Area | M1 surface |
|------|-------------|
| Standards | CEFR canonical only (no WIDA toggle in UI) |
| Modes | Speaking, Listening, Reading, Writing |
| Components | Vocabulary, Pronunciation |
| Domains | **Survival only** |
| Mastery | Full EWMA + per-word SRS + per-contrast SRS |
| Corpus | Tiers A + B + C ingested; 3-pass tagging (Pass 2 manual at MVP scale) |
| Graph | Schema built; **structural + per-student** edges actively queried |
| Placement | 4 modes × Survival; 60-item curated bank; CAT-lite |
| Engine | Buckets 1 + 2 + 3 active; ε=0 (no exploration); recommendation traces logged |
| Tutor | `tutor_conversation` in Speaking + Listening; full compiled prompt + 2-layer guardrails |
| Voice | Full cloud loop (Deepgram + OpenAI TTS + Haiku); Whisper-proxy pronunciation |
| Lessons | 5 step types active; **12 hand-authored lessons** A1.1 → A2.1 Survival; full lint pipeline |
| XP | Full formula; 5 named bilingual badges; Practice Days + Current Run |
| Dashboard | Instructor view only; cohort grid + mastery matrix; 2 actions (Flag, Note); 1 report (per-student PDF) |
| Users | Adult UI shell only; magic-link email; 3-layer consent |
| Stack | Full pinned stack deployed; CI/CD; cost rollup; Sentry |

### Out of M1 (cut, deferred to M2+)

- WIDA projection toggle
- Mediation mode
- School / Academic / Workplace domains
- Grammar + Pragmatics components
- Buckets 4 + 5 of the cascade (stretch + exploration)
- ML ranker
- Tutor conversation in Reading + Writing modes
- SpeechAce pronunciation API
- 7 of the 12 step types
- 10 of the 15 badges
- Coordinator view
- 3 remaining intervention actions
- 3 remaining standard reports
- Equity & cost panels
- Child UI shell + family-managed accounts
- SMS magic link
- SSO

### Acceptance criteria (all must pass)

1. ≥1 cohort of 8 learners completes intake + placement.
2. Each learner averages ≥3 sessions/week for 4 consecutive weeks.
3. ≥80% of mastery cells touched show positive Δ over 8 weeks.
4. Instructor uses dashboard ≥2×/week per cohort.
5. Per-learner cloud cost ≤ $12/mo measured by `cost_events`.
6. p95 voice turn ≤ 2.5s in production logs.
7. Sentry receives <5 errors/learner/week.
8. Zero affective-filter-lint violations in shipped UI strings.
9. Magic-link auth + 3-layer consent flow signed by all enrolled learners bilingually.
10. Standards Alignment report (single-learner version) renders defensibly — proof artifact for M2 JCPS conversations.

### Build tasks (M1 backlog, ordered)

#### Week 0 — Infra
- [ ] Provision Hetzner CX22 (US-Ashburn)
- [ ] Provision Cloudflare R2 bucket + DNS + TLS
- [ ] Set up Vercel project for frontend
- [ ] Set up GitHub repo + CI/CD pipeline
- [ ] Set up Sentry project (free tier)
- [ ] Configure Resend + Twilio accounts
- [ ] Set up Anthropic + Deepgram + OpenAI API keys + budget alerts

#### Weeks 1–2 — Foundations
- [ ] Backend scaffold: FastAPI + SQLModel + Alembic
- [ ] Frontend scaffold: Next.js 15 App Router + Tailwind + shadcn + next-intl (es + en)
- [ ] Database schema for users, student_profiles, cohorts, consent_grants, magic_link_tokens
- [ ] Magic-link service (email via Resend)
- [ ] Auth middleware + RBAC scope skeleton
- [ ] First-touch language splash + profile language preference

#### Weeks 3–4 — Corpus & standards ingestion
- [ ] CEFR descriptor extraction from Companion Volume → `cefr_descriptors` table
- [ ] WIDA Can-Do ingestion (for M2 readiness — silent in M1 UI)
- [ ] Tier B corpus chunking pipeline (story banks, USCIS, NGSL/NAWL CSVs, minimal pairs)
- [ ] Tier C corpus → compiled tutor prompt registry (compiler script)
- [ ] License gate enforcement
- [ ] pgvector index on chunks; HNSW config
- [ ] Initial graph rebuild script (structural edges only)

#### Weeks 5–6 — Mastery + placement
- [ ] `mastery_cells` table + EWMA update logic
- [ ] `vocabulary_state` (SRS) + `contrast_srs_state` tables
- [ ] Confidence-decay scheduled job
- [ ] Intake form UI (5 questions, bilingual)
- [ ] Placement item bank curation (60 items: 15 per mode for L/S/R/W)
- [ ] CAT-lite per-mode logic
- [ ] Placement conversational opener (tutor mini-config)
- [ ] Placement results writer (5 mastery cells per learner)

#### Weeks 7–8 — Engine + lessons
- [ ] 5-bucket cascade ranker (buckets 1–3 only in M1)
- [ ] Constraint filters (5 hard filters)
- [ ] `recommendation_traces` table + writer
- [ ] `/next-activity` endpoint
- [ ] Lesson YAML schema (Pydantic) + 5-stage lint pipeline
- [ ] Lesson ingestion script
- [ ] Author **12 lessons** A1.1 → A2.1 Survival (parallel curation track)
- [ ] Lesson runner UI (5 step types: intro, vocab_intro, vocab_drill, production_speaking, tutor_subdialog)
- [ ] Mastery EWMA writers from attempts

#### Weeks 9–10 — AI tutor + voice
- [ ] Tutor prompt compiler (30-cell matrix from Tier C → cached compiled prompts)
- [ ] Lyster-Ranta correction policy table seeded
- [ ] Spanish policy table seeded
- [ ] L1 transfer detector (Spanish patterns from cheat sheet)
- [ ] 6 post-generation validators
- [ ] 20-item canned-response library
- [ ] Voice loop: Silero VAD (browser) → Deepgram streaming → tutor → OpenAI TTS streaming
- [ ] ASR confidence gate (correction suppression below threshold)
- [ ] Anthropic prompt caching on Layer 2
- [ ] Voice consent flow in onboarding

#### Weeks 11–12 — Dashboard + reports + XP
- [ ] Instructor cohort grid view
- [ ] Single-student mastery matrix (CEFR × Mode × Domain heatmap)
- [ ] Flag + Note actions + audit table
- [ ] XP formula module
- [ ] Hours Saved meter (anchored to benchmark hours)
- [ ] Practice Days + Current Run counters
- [ ] 5 named bilingual badges
- [ ] Per-student progress PDF report
- [ ] Cost rollup cron + `cost_events` table
- [ ] Affective-filter UI-string lint in CI

#### Weeks 13–14 — Polish + launch prep
- [ ] Full pilot dress rehearsal with 1 internal test learner
- [ ] DSA-style consent forms reviewed by partner
- [ ] Acceptance-criteria CI check
- [ ] Monitoring dashboards (Sentry + cost panel)
- [ ] Production deploy
- [ ] Learner onboarding script (in-person, bilingual)
- [ ] Instructor training (1 hr)

---

## M2 — JCPS Pilot Readiness

**Goal:** Make the JCPS EL pilot actually possible — child UI shell, WIDA projection, coordinator view, equity panel, signed DSA, defensible Standards Alignment report.

**Pilot:** Adult cohort (continuing) + 1 K-12 EL cohort at JCPS partner site, 8 weeks.

**Estimated duration:** 8–10 weeks post-M1.

### In scope (additions to M1)

- WIDA projection toggle live; K-12 cohorts default to WIDA view
- **Mediation mode** added (placement + tutor conversation)
- **School** + **Workplace** domains
- **Grammar** + **Pragmatics** components active
- Buckets 4 + 5 of the cascade (stretch + exploration)
- Per-learner-tuned ε-greedy
- Tutor conversations in Reading + Writing modes
- **SpeechAce** pronunciation API integrated for `pronunciation_drill` only
- Contrast-SRS for Spanish ★★★ pairs prioritized
- 7 more step types active (full set of 12)
- +15 hand-authored lessons spanning A1.1 → B1.1 across Survival + School
- Full badge library (~15)
- Cohort Hours Saved rollup
- **Coordinator view** + all 5 intervention actions + 3 remaining reports
- **Equity & cost panels** (engagement, modality, demographic, cost)
- **Child UI shell + family-managed accounts**
- SMS magic link (Twilio)
- **DSA template** ready for JCPS signature

### Acceptance criteria

1. DSA signed with at least one school (JCPS pilot site or partner org).
2. ≥1 K-12 cohort runs alongside ≥1 adult cohort concurrently.
3. Standards Alignment Report defensible in a district audit (reviewed by a JCPS EL staff member).
4. Equity panel surfaces real per-cohort variance.
5. Per-learner cost stays ≤ $15/mo even with voice-heavy K-12 use.
6. 2 cohorts × 12 learners each sustain 8 weeks with <2 instructor escalations per cohort.
7. Voice consent withdrawal tested end-to-end without session breakage.

### Build tasks (M2 backlog)

- [ ] WIDA → CEFR projection table + UI toggle in teacher dashboard
- [ ] Mediation activity type + grader rubric + 1 placement item
- [ ] School/Workplace domain content (3 lessons each authored)
- [ ] Grammar + Pragmatics step types + rubrics
- [ ] Cascade buckets 4 + 5 + ε-greedy module
- [ ] Tutor compiled prompts for Reading + Writing × bands
- [ ] SpeechAce integration; per-phoneme scoring → contrast SRS
- [ ] Spanish ★★★ minimal-pair pre-population in SRS state
- [ ] +15 hand-authored lessons (parallel curation; +1 lesson/day for 3 weeks)
- [ ] Full badge library (10 more) + badge engine
- [ ] Cohort Hours Saved aggregation
- [ ] Coordinator view route + RBAC scope
- [ ] Adjust Band / Recommend Lesson / Schedule Check-in actions
- [ ] Cohort summary report (PDF + CSV monthly auto-gen)
- [ ] Standards alignment report (CEFR + WIDA + descriptor evidence + dates)
- [ ] Outcome report (anonymized cohort aggregate)
- [ ] Equity panels (engagement, modality, demographic)
- [ ] Cost panel (per-cohort spend from `cost_events`)
- [ ] Child UI shell (separate route tree, friendlier visuals)
- [ ] Family-managed account model + parent UI + consent inheritance
- [ ] SMS magic-link channel (Twilio)
- [ ] DSA template draft + legal review
- [ ] JCPS staff dry-run of Standards Alignment report

---

## M3 — Scale & Intelligence

**Goal:** Scale past pilot scale; let the LLM start helping with authoring; first signs of learned recommendation.

**Pilot:** 100+ active learners across 4+ cohorts (mixed adult + K-12).

**Estimated duration:** 3–4 months post-M2.

### In scope (additions)

- Full DAG lesson branching available (selective use)
- **Generated lessons pipeline**: LLM drafts → curator queue → `generated_curated` origin → live
- **First ML ranker** trained on M1+M2 recommendation traces; A/B against rule-based cascade for **bucket 4 only**
- **Bilingual_equivalent + transferred_from graph edges** activated in tutor prompt assembly + recommendation logic
- **Academic domain** added
- **Email SSO** (Google OAuth) for adult learners
- **Postgres migration to Supabase Pro**; backup strategy upgraded
- **Second VPS for workers** (cost scaling)
- Cognee or Memgraph **evaluation** per PRD § 7 (evaluation, not commitment)
- Persistent vocab list editor for instructors

### Acceptance criteria

1. 100+ active learners sustained across 4+ cohorts.
2. LLM-curated lessons cut authoring time ≥50% per lesson vs M1 manual baseline.
3. ML ranker (bucket 4 only) outperforms rule-based on a held-out cohort metric (engagement minutes or mastery delta) by ≥5%, with confidence interval excluding zero.
4. Cost per active learner stays ≤ $15/mo despite 5× learner growth.
5. Voice turn p95 stays ≤ 2.5s at scale.
6. Cognee/Memgraph evaluation produces a written recommendation document with go/no-go.

### Build tasks (M3 backlog)

- [ ] Full DAG lesson sequencing engine
- [ ] LLM lesson drafter (Sonnet 4.6, prompt templated per cell)
- [ ] Curator queue UI (review → approve → promote / reject → log)
- [ ] Generated lessons enter `_pending/` and require curator sign-off
- [ ] Recommendation-trace replay logger
- [ ] ML ranker training pipeline (LightGBM on trace features → top-K candidates)
- [ ] A/B framework: bucket 4 routes 50% to rule-based, 50% to ML
- [ ] A/B analysis report
- [ ] Bilingual graph edges (en ↔ es vocabulary) → activated in tutor's bridge-recast
- [ ] L1 transfer graph edges → engine bias for proactive scaffolding
- [ ] Academic domain content + 10 lessons
- [ ] Google OAuth integration
- [ ] Supabase Pro migration: backup, restore, cutover playbook
- [ ] Second VPS provisioning + worker offload
- [ ] Cognee/Memgraph spike + evaluation doc
- [ ] Instructor vocab list editor (custom vocab tags per cohort)

---

## M4 — Partnership & Polish

**Goal:** Make the platform institutionally defensible and start the moat. Most M4 items are **pilot-signal-contingent** — build only if pilot data demands them.

**Estimated duration:** Open-ended.

### Pilot-signal-contingent (build only with evidence)

| Feature | Signal that triggers building |
|---------|-------------------------------|
| District SSO (Clever / ClassLink) | JCPS expansion agreement signed, multi-school rollout |
| Adult-ed credit-hour negotiation (the moat) | One partner expresses formal interest in recognizing Hours Saved |
| Persona library (multiple TTS voices) | Engagement plateau metric: median session length drops 20% from M2 baseline |
| Offline-degraded mode | Pilot interviews surface ≥3 learners blocked by connectivity |
| Full-duplex barge-in voice | Learner survey signals interruption frustration |
| Cognee/Memgraph cutover | M3 evaluation recommends go |
| Multi-district admin layer | Multi-district expansion contract close |

### Acceptance criteria (one of)

1. **One signed credit-hour recognition agreement** with an external partner (the moat).
2. **OR**: signed expansion agreement to a second district or community partner.
3. **OR**: explicit polish-only release with documented learner-NPS improvement ≥10 points.

Without one of these three, M4 is just polish — recognize that explicitly. Polish-only releases are acceptable but should be brief and bounded.

---

## Permanently out of scope (all milestones)

- Native mobile apps (web-responsive only)
- Enterprise multi-district admin layer (without contract signal)
- High-stakes testing
- Video generation
- Hard dependency on any single graph product

These appeared in the original PRD `out_of_scope` and remain so.

---

## Scope-creep policy

**Rule:** Adding anything to a milestone requires explicit cut of equivalent-weight scope from the same milestone. Backlogs go into M+1.

**Process:**
1. Open a PR or note in `/docs/scope-creep-log.md`.
2. Identify the proposed addition (effort estimate, milestone).
3. Identify the equivalent cut (item from same milestone, same effort estimate).
4. Justify why the trade is correct.
5. Update roadmap.md if accepted.
6. If no equivalent cut is identified, the addition goes to M+1.

**Exception:** Items that **unblock M_x acceptance criteria** can enter M_x without an equivalent cut. They never expand M_x; they make it shippable.

---

## CI acceptance-criteria gate

Each milestone has a script `scripts/check_acceptance_M{n}.py` that runs against production data and fails if any criterion misses. Launch is gated by a green check.

For M1, the checks include:
- Sentry error rate query → assertion
- `cost_events` aggregation → per-learner cost calculation → assertion
- Voice turn metrics table → p95 latency query → assertion
- Lesson lint pipeline → all-green assertion
- UI-string affective-filter linter → zero violations assertion
- Cohort attempt density query → ≥3 sessions/week assertion (rolling 4 weeks)

---

## Pilot-signal log

After every pilot observation, interview, or office-hour session with a partner, a brief entry goes to `/docs/pilot-signal-log.md` with date, who was spoken with, what was observed, and which contingent features (if any) gained or lost signal.

This file is the **source of truth for M4 decisions**. We don't build offline mode because it sounds nice; we build it if 3 entries say "connectivity blocked the learner today."

---

## Open questions (tracked for resolution before M_x launch)

### Before M1 launch
- Final naming for the platform (currently "ESL-voice" working name; consider rename before pilot)
- 5 named badges — finalize bilingual labels
- Instructor onboarding script — write and dry-run with La Casita coordinator
- Lesson curation owner — solo, or pair with La Casita instructor?

### Before M2 launch
- DSA template — legal review needed
- Hours Saved benchmark numbers — finalize from CASAS/WIDA pacing data; cite sources in product
- Child UI visual design — collaborate with a JCPS EL teacher or designer
- SpeechAce contract negotiation if usage will exceed free tier

### Before M3 launch
- Move from Hetzner self-host to Supabase Pro — cutover plan, downtime budget
- ML ranker training data volume — minimum bar before training; if M1+M2 don't hit it, defer

### Before M4 launch
- Hours Saved credit-hour recognition — first partner conversation, scoping the ask
- Brand: keep "ESL-voice" or rename for the public launch
- Pricing / sustainability model if scaling beyond solo passion-project

# ESL-voice — Product Requirements Document

**Version:** 2.0
**Updated:** 2026-06-14
**Status:** Draft for pilot validation
**Supersedes:** `idea.json` v0.2.0

---

## 1. What this is

**ESL-voice** is a self-hostable, mastery-based ESL learning platform built around an AI voice tutor, designed for adult Latino immigrants and K-12 EL students in Louisville, KY. It uses CEFR-aligned standards, a hybrid vector-plus-graph knowledge base, and a corpus of free/open ESL materials to deliver short, focused sessions that respect the learner's affective state and produce defensible mastery records for teachers and program partners.

The platform is a **passion project**, not a commercial product. It is designed to pilot with La Casita Center and (in M2) with JCPS, both in Louisville.

## 2. Who it's for

### Primary learners
- Adult Latino immigrant ESL learners (Beginner → Low-Intermediate; CEFR A1 → B1)
- K-12 EL students entering Jefferson County Public Schools (M2+)
- Primary L1: Spanish (mostly Mexican / Central American varieties)

### Secondary users
- **Instructors** — ESL teachers and volunteer tutors who run a single cohort and need to know who needs help today.
- **Coordinators** — program staff at La Casita, JCPS EL programs, and partner organizations who need cohort-level rollups, equity panels, and reportable outcomes.
- **Family / guardians** (under-13 path, M2+) — manage their child's account, hold all consents, see progress.

## 3. Design principles

1. **Mastery before advancement.** A learner doesn't level up because they earned XP; they level up because they crossed a CEFR sub-band.
2. **Affective filter is non-negotiable.** Every UX and engine decision is checked against whether it raises learner anxiety. We don't ship features that punish struggling learners.
3. **The corpus is operative, not decorative.** Every layer of the tutor (level estimation, vocabulary sequencing, grammar progression, pronunciation, pragmatics, correction strategy) is grounded in a corpus file. Vibes don't run the engine.
4. **SQL is the source of truth.** The graph layer is a derived projection, rebuildable at any time. The product is not coupled to a graph database.
5. **Cloud-only with cost discipline.** No local model assumption. Every cloud call has a tier policy, prompt caching where applicable, and an audited per-learner cost line.
6. **Bilingual scaffolding by band, not by guess.** The tutor's use of Spanish is determined by the learner's CEFR band, not by LLM judgment.
7. **Hand-authored quality, machine-assisted scale.** M1 ships hand-authored lessons that pass a lint pipeline. M3 adds LLM-generated drafts that flow through the same lint + curation gate.
8. **Pilot-defensible from day one.** Every recommendation is explainable. Every teacher action is audited. Every aggregate is equity-auditable.

## 4. Standards & taxonomy

### CEFR is canonical
The engine speaks CEFR throughout: bands `A1.1, A1.2, A2.1, A2.2, B1.1, B1.2, B2`. The Council of Europe Companion Volume 2020 (full PDF in `/data/cefr/`) supplies the descriptor set that mastery cells map to.

### WIDA is a projection
For K-12 cohorts and JCPS reporting (M2+), each mastery record carries a derived WIDA proficiency level via a static mapping table. WIDA never becomes an alternate engine — it's a reporting lens.

### Three-axis tagging
Every lesson, content chunk, and mastery cell is tagged on three orthogonal axes:

- **Mode** (5): Listening, Speaking, Reading, Writing, **Mediation** (cross-language paraphrase — the differentiator)
- **Component** (4): Vocabulary, Grammar, Pronunciation, Pragmatics
- **Domain** (4): Survival, School, Academic, Workplace

A lesson on "ordering food at a restaurant" is `modes:[Speaking, Listening]`, `components:[Vocabulary, Pragmatics]`, `domain:Survival`.

### Friendly UI labels
The PRD's original Level 0/1/2/3 names persist as UI aliases for the engine's CEFR sub-bands. Engine writes CEFR; UI may render as "Level 1: Beginning" for Spanish-first learners who find this more legible.

## 5. Mastery model

### Cells
Mastery is tracked per **(student × mode × CEFR band × domain)** — up to 120 sparse cells per learner. Each cell carries:
- `mastery_score` (0–1, EWMA over attempts, **monotone sticky** — never decreases)
- `confidence` (0–1, decays linearly with inactivity)
- `descriptors_demonstrated[]` — which CEFR descriptors evidence the cell

### Mastery threshold
A cell is "mastered" when EWMA ≥ 0.85 sustained over ≥3 attempts spread across ≥2 lessons and ≥7 days.

### Confidence decay
After 30 days of inactivity, confidence drops. When confidence falls below threshold, the engine schedules a **verification probe** (1–2 quick items) rather than re-teaching the cell. Pass → confidence restored. Fail → cell downgrades.

### Vocabulary mastery is separate
Per-word state machines via spaced repetition (Leitner box 1–7). Vocabulary mastery feeds embedded signal into mode×band×domain cells but tracks independently.

### Pronunciation mastery is per-contrast
Per-minimal-pair-contrast SRS, separate from vocabulary. Spanish-L1 high-priority contrasts (`/θ/-/s/`, `/d/-/ð/`, `/b/-/v/`) are weighted higher in scheduling.

## 6. The corpus

### Three-tier classification
Every file in `/data/` is one of three tiers; each has a different runtime role:

| Tier | Role | Examples |
|------|------|----------|
| **A — Standards** | Compiled into the CEFR descriptor table at bootstrap; rarely re-ingested | CEFR Companion Volume, WIDA framework, WIDA Can-Do |
| **B — Learner Content** | Chunked, embedded, retrieved, served to learners | MN Story Bank, USCIS 100q, NGSL/NAWL frequency lists, CMU dict, minimal pairs |
| **C — Tutor Reference** | Compiled into tutor system prompts; never shown to learners | SLA primer, pragmatics inventory, Spanish L1 transfer cheat sheet, lesson templates, translanguaging guidance |

### Heterogeneous chunking
- Standards PDFs → one chunk per CEFR descriptor
- Story PDFs → one chunk per story
- Frequency CSVs → one chunk per row (per word)
- Exercise PDFs (USCIS) → one chunk per Q-A pair
- Markdown reference → per H2 section
- Research PDFs (Krashen, SIOP, translanguaging) → 600–800 token semantic chunks

### Three-pass tagging pipeline
1. **Deterministic** from source metadata (folder structure encodes most tags)
2. **LLM-assisted refinement** (Haiku-tier) fills `cefr_descriptor_ids`, `topic`, `components`
3. **Spot-check** in a curator-only review queue for first 5% of any new source

### License gate
Every Tier B chunk requires explicit license metadata. Non-redistributable content is served as paraphrase only. Tier C never enters the learner-facing retrieval index.

## 7. Knowledge base architecture

### SQL = source of truth, graph = derived projection
All entity state lives in Postgres. The graph layer is a rebuildable projection that supports traversal-shaped queries (prerequisites, semantic neighborhoods, bilingual scaffolds). This is what keeps the platform's graph technology **swappable**.

### Node types (9)
`Standard`, `MasteryCell`, `Lesson`, `LessonStep`, `ContentChunk`, `Vocabulary`, `Topic`, `Student` (minimal mirror), `ErrorPattern`

### Edge types (11 across 4 categories)
- **Structural** (`composes`, `aligns_with`, `belongs_to`) — rebuilt on every SQL write
- **Pedagogical** (`prerequisite_of`, `bilingual_equivalent`, `transferred_from`, `scaffolds`) — rebuilt on corpus ingestion
- **Per-student** (`demonstrated_by`, `gap_in`, `addresses_gap`) — rebuilt nightly + delta on each attempt
- **Semantic** (`similar_to`, `topic_of`) — rebuilt on chunk embedding

### Storage
Postgres graph tables + pgvector for embeddings in MVP. Migration paths to Supabase Pro (M3+) and Cognee/Neo4j (M4+ evaluation candidates, never assumed) are explicit.

### Vector index
pgvector with HNSW indexes. Adequate for the 2k–10k chunks at MVP. No separate vector DB.

## 8. Placement assessment

### Format — hybrid
1. **2-minute conversational opener** in the learner's preferred language. Lowers affective filter; gives fluency baseline.
2. **CAT-lite per-mode probes** — adaptive: start at intake-derived prior band, escalate on correct, drop on incorrect, terminate at 2 consecutive failures or 6 items per mode.
3. **One Mediation task** (M2+).

Total session: 10–15 minutes.

### Coverage
At MVP placement covers **5 modes × Survival domain only**. Other domains bootstrap through use, biased by the learner's stated goal in intake.

### Intake form (5 questions, 1 minute)
Native language, years in US, prior English study, highest education, primary goal, age band. Seeds per-mode priors and activates the Spanish L1 transfer prediction layer.

### Item bank
Corpus-derived candidates curated by a human, seed of ~80 items at MVP. USCIS 100q seeds civics reading. NGSL bands seed vocabulary probes. Minimal pairs seed pronunciation probes. Story banks seed reading comprehension.

### Affective filter protection
"I don't know" is a first-class answer — soft-fail, no XP penalty. Two consecutive IDKs terminate the mode probe with no shame.

### Output
Five `MasteryCell` rows written per placement at `(student, mode, estimated_band, Survival)` with `mastery_score=0.7`, `confidence=0.6`. Other cells start at zero and populate through use.

## 9. Adaptive engine

### Five-bucket cascade ranker
On every `GET /next-activity` request, the engine walks priority buckets top-down and picks one eligible candidate from the highest-priority non-empty bucket:

1. **Overdue SRS reviews** (vocab + pronunciation contrasts) — never skip
2. **Active learning path** (current sequence toward stated goal)
3. **Mastery consolidation** (cells at 0.5–0.85 needing one more push)
4. **Stretch challenge** (one band up, if confidence is high)
5. **Exploration** (unexplored domain × mode)

### Six activity types
`vocab_review`, `lesson`, `tutor_conversation`, `pronunciation_drill`, `reading_passage`, `mediation_task`.

`tutor_conversation` is the only activity type that puts the LLM in the hot path. All others are scripted/authored and bypass the LLM.

### Five hard constraints (applied before ranking)
Session length budget, mode rotation after 20+ min, recency cooldown, streak protection, domain alignment with stated goal.

### Exploration
Per-learner-tuned ε-greedy. ε ∈ [0.10, 0.30] based on recent success rate and IDK rate. Anxious learners get ε=0.10; confident learners get ε=0.30.

### Reasoning trace on every recommendation
Every `/next-activity` response includes a structured trace (`bucket_fired`, `rationale`, `graph_evidence`, `candidates_considered`). Powers the teacher dashboard's "why" panel, the tutor's prompt context, and a future ML ranker's training corpus.

## 10. AI tutor runtime

### Scope (two responsibilities only)
1. **Conversation partner** in `tutor_conversation` activities.
2. **Open-response grader utility** for speaking / writing / mediation items called by other activity types.

Everything else is scripted, deterministic, and LLM-free.

### Three-layer compiled prompt

```
Layer 1: TUTOR IDENTITY        — static, versioned
Layer 2: COMPILED BEHAVIORAL RULES  — generated from Tier C + (band, activity_type, domain, l1)
Layer 3: PER-TURN CONTEXT       — activity goal, target descriptors, recent attempts,
                                   graph evidence, last 6 turns, retrieved chunks
```

Layer 2 is **compiled at deploy time**, not assembled at runtime. The SLA primer, pragmatics inventory, Spanish L1 cheat sheet, and lesson templates are *inputs to a compiler* that emits learner-band-specific rule blocks. ~30 cached prompt variants.

### Error correction (deterministic by band, not LLM judgment)

| Band | Allowed | Forbidden |
|------|---------|-----------|
| A1.1, A1.2 | Recasts only | Everything else |
| A2.1 | Recasts + clarification | Metalinguistic, explicit |
| A2.2, B1.1 | + Elicitation | Explicit |
| B1.2, B2 | All except repetition with emphasis | — |

### Bilingual scaffolding (deterministic by band)

| Band | Spanish use |
|------|-------------|
| A1.1 | Free — Spanish is default scaffold |
| A1.2 | High — Spanish for new concepts |
| A2.1 | On request only |
| A2.2 | Rare — mediation tasks only |
| B1.1+ | Mediation tasks only |

The Spanish L1 transfer detector activates a **bridge-recast pattern**: when a learner's error matches a known transfer pattern from `data/bilingual/spanish_l1_transfer_cheat_sheet.md`, the tutor's recast bridges the L1 explicitly ("In Spanish you say tener hambre — in English we say I'm hungry").

### Two-layer guardrails
**Preventive** (compiled prompt rules): turn-length caps per band, question-count caps, forbidden constructions list.

**Detective** (post-generation validators): length check, question-count check, forbidden-construction check, forbidden-correction check, L1 leak check, ASR-confidence-gate check. Validator failure → retry with explicit fix; second failure → deterministic canned response from a 20-item library + Sentry log.

## 11. Voice loop

### Modality
Per-step, not platform-wide. Voice is required for pronunciation drills, default for tutor conversation. Text-only learners get every activity except pronunciation drills.

### ASR — Deepgram Nova-2
- Streaming, ~150ms first-token latency, ~$0.0043/min
- Strong performance on Spanish-accented English
- **Consent mandatory** at signup (bilingual plain-language)
- Raw audio purged within 24h; transcripts retained per privacy policy

### TTS — OpenAI tts-1
- One vendor for English (`nova`) + Spanish (`shimmer`) scaffolding
- Streaming output (starts playback at first sentence)
- $15/M chars

### LLM
- **Haiku 4.5** in tutor hot path (latency + cost)
- **Sonnet 4.6** for grader utility (off hot path, accuracy matters)
- **Anthropic prompt caching** on Layer 2 compiled prompts — 90% input cost savings; cache hit rate target >95%

### Pronunciation scoring
- **MVP**: Whisper-transcription-proxy. Mispronounced → ASR transcribes wrong word → minimal-pair contrast inferred from target's phoneme set.
- **M2**: SpeechAce or equivalent paid API for `pronunciation_drill` activities only.
- **M3+**: Re-evaluate batch forced alignment on VPS if SpeechAce costs grow.

### Latency budget
≤ 2.0s end-of-learner-utterance to start-of-tutor-utterance.
- Silero VAD (WASM in browser): 50ms
- Deepgram streaming ASR: 300ms
- L1 detection + prompt assembly: 80ms
- Haiku 4.5 streaming: 600–900ms
- Validator + TTS first byte: 480ms

### Turn-taking
Half-duplex with Silero VAD. Tutor finishes → silence detected → learner speaks → VAD endpoints → tutor responds. Full-duplex barge-in deferred to M4+.

### ASR-vs-learner error attribution
ASR confidence gates the validator pipeline. Below 0.7 → re-transcribe (consent-permitting); still below 0.7 → tutor does not correct; reasonable confidence (0.7–0.85) → tutor corrects only high-salience errors. ≥0.85 → full correction pipeline runs.

## 12. Lessons

### Source of truth: version-controlled YAML in `/content/lessons/`
The DB row is a projection. Files are diff-reviewable; this is what makes curriculum credible.

### Atomic shape

```yaml
lesson_id: doctor_visit_a2_survival
title: { en: "At the Doctor's Office", es: "En el Consultorio del Doctor" }
template_pattern: PPP        # PPP | TBLT | TPR | sheltered
target_descriptors: [cefr-a2.1-spk-surv-#3, cefr-a2.1-lis-surv-#7]
modes: [Speaking, Listening]
components: [Vocabulary, Pragmatics]
domain: Survival
cefr_band: A2.1
estimated_minutes: 15
prerequisites:
  mastery_cells: [...]
  vocab_known: [doctor, sick, head, hurt, water]
content_refs: { chunks: [...] }
steps: [...]
completion_rules:
  done_when: all_steps_attempted
  mastered_when: all_production_steps_score >= 0.8
origin: authored             # authored | generated_curated | generated_uncurated
license: cc-by-sa-4.0
```

### Step types (12)
`intro`, `vocab_intro`, `vocab_drill`, `grammar_intro`, `comprehension_check`, `listen_passage`, `read_passage`, `production_speaking`, `production_writing`, `mediation`, `tutor_subdialog`, `reflection`. `tutor_subdialog` is the only LLM hot-path step.

### Sequencing
Linear + skip-on-mastery for `intro`-tier steps. Full DAG branching deferred to M3+.

### Completion states (4)
`started`, `done`, `mastered`, `abandoned`.

### Origin (3)
`authored`, `generated_curated`, `generated_uncurated`. Uncurated lessons never serve to learners; they sit in `/content/lessons/_pending/` for human review.

### Lint pipeline (5-stage, mandatory)
1. Schema lint
2. Content lint (bilingual fields, estimated-minutes ±20%)
3. License lint (Tier B redistributable)
4. CEFR alignment lint (descriptors match declared band)
5. Pedagogy lint (template pattern matches step ordering)

## 13. XP & Hours Saved

### XP formula
Three sources, summed per activity, capped at 2× the base completion XP:
- **Completion XP** — fixed per activity type
- **Mastery delta XP** — `(post − pre) × 100`, only positive
- **SRS recall XP** — `5 × difficulty_factor` where difficulty = SRS box level

### Hard rules
- XP is monotone non-decreasing per learner (DB constraint).
- "I don't know" is XP-neutral.
- Hint use reduces step XP by 30% but never to zero.

### Levels = CEFR sub-band achievements
Not arbitrary XP thresholds. XP fills a per-band progress meter; crossing a band triggers the "Level Up" celebration.

### Practice Days + Current Run (not punishing streaks)
- **Practice Days**: cumulative count of any active day. Never decreases.
- **Current Run**: consecutive-day counter that **decays by one per missed day**, never snaps to zero unless 7+ consecutive days missed.

### Badges (~15 named, bilingual)
Each maps to a concrete mastery cell, lesson group, or behavioral milestone. Bilingual names primary in Spanish-mode UI.

### Hours Saved meter
Anchored to published adult-ESL teaching-hour benchmarks (~80–100 hours per CEFR sub-band from CASAS / WIDA pacing data). Displayed as gain ("You've saved 12 hours of class time"), never deficit. Cohort rollup visible to learners as community signal.

### Strategic note
"Hours Saved" is *symbolic* in MVP — a computed meter against benchmark hours. The M4 goal is to negotiate with JCPS adult-ed and La Casita to **recognize Hours Saved as adult-ed credit hours**. That recognition is the moat.

No reference to TimeBack branding anywhere in product copy or marketing. Inspiration acknowledged in internal docs only.

### Affective-filter invariants (UI lint enforced)
No leaderboards. No "streak lost" notifications. No "you fell behind" framing. Bilingual celebration default. Hints normalized as part of learning. UI strings containing "lost / broke / failed / behind / missed" are flagged for rewrite.

## 14. Teacher dashboard

### Two persona views, one product
- **Instructor view**: assigned cohorts, "who needs help today" focus.
- **Coordinator view**: all overseen cohorts, equity + cost panels, reports.

RBAC enforced server-side. A user with both roles toggles.

### Instructor landing: cohort grid
~30 rows × 6 columns: student, last active, current top-mode band, weekly mastery delta, Hours Saved, `needs_attention` flag. Color-coded but not alarmist; no red, no shame.

### Single-student view: CEFR × Mode × Domain mastery matrix
The headline. Heatmap of mastery scores across all relevant cells, plus recent attempts, engine recommendations with rationale, Hours Saved, Practice Days, Current Run, badges, teacher notes.

### Headline metric: weekly mastery delta
NOT XP. XP is learner currency. Teachers care about cells advanced + mean Δ across active cells.

### `needs_attention` flag (2-of-6 soft signals, never single threshold)
Declining mastery, inactivity ≥5 days, IDK rate >40%, SRS backlog >20, validator retry rate spiking, voice consent withdrawn.

### Five intervention actions (all audited, none write directly to XP/mastery)
Flag, Note (versioned, bilingual via grader), Adjust Band (override engine estimate, requires reason), Recommend Lesson (push to queue), Schedule Check-in.

### Four standard reports
Per-student progress (parent-conference / IEP-style), Cohort summary (monthly), **Standards alignment** (CEFR + WIDA + descriptor evidence — the JCPS credibility artifact), Outcome report (funder / grant aggregate).

### Coordinator equity & cost panels
Engagement equity, modality equity (voice vs text), demographic equity (aggregates only), per-cohort cloud spend, audit log of all teacher actions. **Required for JCPS pilot defensibility.**

## 15. Users, cohorts, consent

### Auth — coordinator-provisioned + magic link
Coordinator creates account; platform sends bilingual welcome link via email or SMS. Tokenized, single-use, 7-day expiry. SSO deferred to M3+ (Google OAuth); district SSO (Clever / ClassLink) to M4+.

### Cohort model
Single primary cohort per learner + optional secondary tags. Cohort lifecycle: `pre_enrolled → active → paused → completed → archived`. **`paused` is respected by the engine** — confidence decay pauses, SRS freezes, no recommendations fire. Coordinator-pause is forgiving.

### 3-layer consent
1. **Platform Terms** — required for any use
2. **Voice & Audio Processing** — required for any voice activity (D9); withdraw → text-only mode
3. **Anonymized Data Sharing** — optional; withdraw → removed from cohort/funder aggregates

All layers bilingual, plain-language (6th-grade reading level), versioned. Receipts stored. Withdrawal available in profile UI in one click.

### Under-13 / K-12 path (M2+)
Family-managed account: parent/guardian primary, child sub-profile. Parent holds all consents. Separate **child UI shell** (larger touch targets, no community features, friendlier visuals — no Hours Saved meter, replaced with growing-tree or filled-jar visual). Adult and child shells share the same backend.

### COPPA / FERPA / KY SB 216
- Parental consent gate before any data collection from under-13.
- Educational records access controls via RBAC.
- **Data Sharing Agreement template** (`/docs/legal/DSA-template.md`) prepared for JCPS pilot signature.

### Language modes (3)
- **Spanish-first** — Spanish primary chrome, English glosses
- **Bilingual** — 50/50 toggle (default for placement)
- **English-only** — English chrome (mediation tasks excepted)

First-touch splash: 3 buttons (Español / English / Bilingüe). Coordinator-provisioned accounts inherit cohort default.

## 16. Tech stack

| Layer | Choice |
|-------|--------|
| Frontend | Next.js 15 App Router + Tailwind + shadcn + Recharts + `next-intl` |
| Backend | Python 3.12 + FastAPI + SQLModel + Alembic + httpx |
| Database | Postgres 16 + pgvector (self-hosted MVP → Supabase Pro M3+) |
| Cache | Redis 7 (in-VPS) |
| Queue | RQ + APScheduler (Celery deferred) |
| Hosting | Hetzner CX22 (US-Ashburn) — single VPS, ~$5/mo |
| Storage | Cloudflare R2 (audio + nightly `pg_dump` backups) |
| Email | Resend (free tier) |
| SMS | Twilio (~$0.0075/msg US) |
| LLM | Anthropic Claude (Haiku 4.5 hot path, Sonnet 4.6 grader) |
| ASR | Deepgram Nova-2 streaming |
| TTS | OpenAI `tts-1` streaming |
| Charts | Recharts (learner/instructor); Plotly (coordinator PDFs only) |
| Observability | Sentry + structured JSON logs + in-DB `cost_events` |

**US data residency:** Hetzner US locations satisfy district preference. Not negotiable for JCPS.

**Fixed infra at pilot scale:** ~$15/mo. Plus cloud APIs (~$160–215/mo at 20-learner pilot). **Total ~$175–230/mo.**

## 17. Non-functional requirements

- **Latency**: p95 voice turn ≤ 2.5s; p50 ≤ 1.8s; cold cache turn ≤ 3.0s.
- **Cost discipline**: per-learner cloud spend tracked daily; alert at >$15/mo per active learner.
- **US-hosted infra**: required for FERPA/KY SB 216 alignment.
- **Bilingual everywhere learner-facing**: no English-only error message, modal, or notification.
- **Accessibility**: WCAG AA on adult shell; AAA on child shell where feasible.
- **Audit retention**: all teacher actions retained for ≥12 months.
- **Backup recoverability**: full restore from R2 backup achievable within 30 minutes from a fresh VPS.

## 18. Privacy & safety

- Minimize PII; intake collects only what informs placement priors.
- Raw learner audio purged within 24h of transcription unless flagged for teacher review.
- Cloud ASR retry requires per-family voice consent — opt-out by default in M1.
- Demographic equity panels show aggregates only; never individual identification.
- Withdrawing voice consent immediately disables voice activities without breaking the learner's session.
- Tutor conversation transcripts are educational records (FERPA) — release governed by DSA.
- Separate RBAC scopes for learner, parent, instructor, coordinator, admin.
- Secrets stored per-env (systemd env vars in prod); never committed.

## 19. Out of scope

### Permanently out (all milestones)
- Native mobile apps
- Enterprise multi-district admin
- High-stakes testing
- Video generation
- Hard dependency on any single graph product

### Pilot-signal-contingent
- Offline mode (M4+ only if pilot interviews reveal connectivity barriers)
- Full-duplex voice (M4+ only if learners ask)
- District SSO (M4+ only if district contracts close)
- TTS persona variety (M4+ only if engagement plateaus)

## 20. Milestone summary

| Milestone | Goal | Duration |
|-----------|------|----------|
| **M1** | Walking Skeleton Pilot — La Casita adult cohort, Survival only, instructor view only | 10–14 weeks |
| **M2** | JCPS Pilot Readiness — Mediation + child UI + coordinator view + equity + DSA | 8–10 weeks |
| **M3** | Scale & Intelligence — generated lessons + first ML ranker + bilingual graph + Academic domain | 3–4 months |
| **M4** | Partnership & Polish — credit-hour negotiation + SSO + persona/offline if signal demands | Open-ended |

Full milestone breakdown with acceptance criteria: see `roadmap.md`.

## 21. Definition of done (M1)

- Local app runs from `make dev`.
- Seed corpus + 12 authored lessons load and pass full lint.
- One adaptive lesson flow works end to end (placement → recommendation → lesson → mastery write → next recommendation).
- One instructor dashboard works (cohort grid + mastery matrix + Flag/Note actions + per-student PDF).
- One retrieval-backed AI tutor conversation works at A2.1 Speaking-Survival.
- Cost rollup cron runs; coordinator can see real spend within 24h.
- Sentry receives errors from production.
- Magic-link auth + 3-layer consent flow signs all enrolled learners bilingually.
- CI/CD pipeline deploys via PR merge.
- All affective-filter UI-string lints pass.

## 22. Acceptance criteria (M1)

1. ≥1 cohort of 8 learners completes intake + placement.
2. Each learner averages ≥3 sessions/week for 4 consecutive weeks.
3. ≥80% of mastery cells touched show positive Δ over 8 weeks.
4. Instructor uses dashboard ≥2×/week per cohort.
5. Per-learner cloud cost ≤ $12/mo measured by `cost_events`.
6. p95 voice turn ≤ 2.5s in production logs.
7. Sentry receives <5 errors/learner/week.
8. Zero affective-filter-lint violations in shipped UI strings.
9. Magic-link auth + 3-layer consent flow signed by all enrolled learners bilingually.
10. Standards Alignment report renders defensibly for any single learner (proof artifact for M2 JCPS conversations).

---

## Appendix A — Repository structure

```
/frontend            Next.js App Router
/backend             FastAPI app
  /engine            5-bucket cascade ranker
  /tutor             Prompt compiler + validators
  /mastery           EWMA + SRS
  /ingestion         Corpus + lesson lint
  /voice             ASR/TTS/streaming
/workers             RQ workers + APScheduler
/content             Lesson YAML + rubrics
  /lessons
  /lessons/_pending
  /rubrics
/data                The corpus (this repo's foundational artifact)
/docs                PRD, roadmap, ADRs, runbooks, legal
  /decisions         15 ADRs
  /legal             DSA template
  /runbooks
/tests
/scripts             pg_dump cron, cost rollup, lesson lint
/infra               Hetzner provisioning, nginx, systemd
```

## Appendix B — Key references

- Council of Europe — *CEFR Companion Volume 2020* (`/data/cefr/`)
- WIDA — ELD Framework + Can-Do Descriptors (`/data/standards/`)
- Browne, Culligan & Phillips — NGSL, NAWL, BSL, TSL (`/data/frequency/`)
- CMU Pronouncing Dictionary (`/data/pronunciation/`)
- Krashen, S. — *Principles and Practice* (summary) (`/data/pedagogy/`)
- Echevarría, Vogt & Short — SIOP Model (`/data/pedagogy/`)
- García & Wei — *Translanguaging: Language, Bilingualism and Education* (`/data/pedagogy/`)
- Ishihara & Cohen — Teaching speech acts (`/data/pedagogy/`)
- JCPS Lau Plan 2024-25 (`/data/local/`)
- La Casita Center program context (`/data/local/`)

## Appendix C — Decision history

See `/docs/decisions/` for 15 Architecture Decision Records (ADRs) capturing every locked decision from the design grilling session of 2026-06-14.

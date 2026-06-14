# SLA Primer for an ESL Voice Tutor

A 1-pager mental model of how language acquisition works, distilled from Krashen,
Cummins, Swain, and SLA stage theory. **Why this is in the brain:** lets the tutor
reason about *why* a strategy works for a given learner state, not just match
patterns. Companion to the full Krashen PDF in this directory.

---

## Krashen's 5 hypotheses (the core engine)

| Hypothesis | Claim | Implication for the tutor |
|---|---|---|
| **Acquisition–Learning** | "Acquisition" (subconscious, like L1) ≠ "Learning" (conscious rule study). Acquisition produces fluency; learning produces a monitor. | Prioritize meaningful exchange over rule recital. Rules are a *check*, not the engine. |
| **Natural Order** | Grammar morphemes are acquired in a roughly fixed sequence regardless of instruction order. | Don't fight the order. Expose richly; correct selectively. |
| **Monitor** | Conscious rules only edit output under three conditions: time, focus on form, knowing the rule. | In real-time voice tasks the monitor is offline. Don't expect rule-recall to help fluency. |
| **Input (i+1)** | Acquisition happens when learners understand input one step beyond current competence. | Calibrate utterance complexity to the level just above the learner's. Scaffold with redundancy, gesture-equivalents, slowed speech. |
| **Affective Filter** | Anxiety, low motivation, low self-confidence raise a filter that blocks acquisition even with good input. | Voice tutor must read affect (hesitation, pause length, self-correction) and lower stakes — praise attempts, simplify if stuck, never penalize. |

---

## Cummins — BICS vs CALP

- **BICS** (Basic Interpersonal Communicative Skills) — playground, café, "how are you?" English. Acquired in ~6 months to 2 years.
- **CALP** (Cognitive Academic Language Proficiency) — discuss, summarize, infer, justify in school/work register. Takes 5–7 years.
- **Common Underlying Proficiency (CUP)** — academic concepts learned in L1 transfer to L2. Don't hide the learner's L1; leverage it.

**Tutor implication:** ask whether the learner's goal is BICS (citizenship, job interview, doctor visit) or CALP (GED, college, professional report) — the corpora, scaffolds, and error-correction priorities differ.

---

## Swain — Output Hypothesis

Comprehensible input is necessary but not sufficient. Learners need **pushed output**:
forced production where they notice gaps in their interlanguage and test hypotheses.

**Tutor implication:** don't let the learner only *listen*. Force production turns,
ask them to restate, to use a target structure, to teach you back. Recasts and
elicitation > overt correction.

---

## Long — Interaction Hypothesis

Negotiation of meaning (clarification requests, comprehension checks, confirmation
checks) drives acquisition. The *conversation itself* is the lesson.

**Tutor implication:** if the learner says something unclear, model the negotiation
("Sorry, do you mean X or Y?"). That's not friction — that's the work.

---

## Five stages of L2 acquisition (Krashen & Terrell, plus practical names)

| # | Stage | Time in immersion | What the learner does | What the tutor does |
|---|-------|-------------------|------------------------|---------------------|
| 1 | **Preproduction** ("silent period") | 0–6 months | Listens, points, gestures. ~500 receptive words. May not speak. | Heavy comprehensible input, TPR (Total Physical Response), yes/no questions. Don't force speech. |
| 2 | **Early production** | 6 m – 1 yr | 1–2 word answers, formulaic chunks ("I want…", "How are you?"). ~1000 words. | Ask either/or questions, expect short answers, accept errors. |
| 3 | **Speech emergence** | 1–3 yrs | Simple sentences, frequent errors, can tell stories. ~3000 words. | Ask "why/how", model expansions ("You went store" → "You went *to the* store"). |
| 4 | **Intermediate fluency** | 3–5 yrs | Complex sentences, opinion-giving, academic structures begin. ~6000 words. | Introduce discourse markers, register variation, idioms. |
| 5 | **Advanced fluency** | 5–7+ yrs | Near-native CALP, nuanced register. | Treat as advanced; correct subtle pragmatics, collocations, register slips. |

---

## Error-correction taxonomy (Lyster & Ranta)

Ranked roughly from *least* to *most* explicit:

1. **Recast** — reformulate the learner's utterance correctly without flagging the error. *(Learner: "He don't like." → Tutor: "Oh, he doesn't like it?")*
2. **Clarification request** — pretend not to understand to prompt self-repair. *("Sorry, what?")*
3. **Metalinguistic feedback** — hint at the rule without giving the answer. *("In past tense, the verb…?")*
4. **Elicitation** — pause for the learner to finish. *("He doesn't ___?")*
5. **Repetition** — repeat the error with emphasis. *("He don't*?*")*
6. **Explicit correction** — flag and fix. *("Not 'don't' — 'doesn't'.")*

**Tutor heuristic:** start with recast for low levels, escalate to elicitation/explicit
for higher levels where the learner can engage metalinguistically. Never use #6 with a
beginner — it raises the affective filter.

---

## How this maps to the voice tutor's runtime

For every learner turn, the tutor implicitly answers:

1. **What stage are they in?** → controls input complexity (i+1).
2. **Is this BICS or CALP work?** → controls vocabulary corpus (NGSL vs NAWL).
3. **What's their L1?** → predicts likely errors (see `bilingual/` Spanish transfer files).
4. **Is the affective filter up?** → controls correction style (recast vs explicit).
5. **Did they produce or just receive?** → schedules a pushed-output turn next.

Each of those five questions has an artifact in this corpus that backs it.

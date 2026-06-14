# ADR 0001 — CEFR canonical; WIDA as projection

**Status:** Accepted
**Date:** 2026-06-14
**Depends on:** —
**Consumed by:** 0002, 0003, 0006, 0007, 0012

## Context

The original PRD declared four custom levels (Level 0/1/2/3) that floated untethered to any external taxonomy. The corpus we built supplies two competing standardized scales: **CEFR** (6 levels, adult-oriented, full Companion Volume 2020 with descriptors per skill) and **WIDA** (6 levels, US K-12 oriented, Can-Do Descriptors per grade band). Mastery scoring, placement, lesson tagging, recommendation engine, and teacher reporting all need a single canonical scale or they fracture.

Custom PRD levels meant we could not align lessons to a published descriptor set, score placement against external standards, reuse third-party content, or justify recommendations to teachers ("Level 2" is meaningless externally; "WIDA Developing" or "CEFR A2.1" is not).

## Decision

**CEFR is canonical throughout the engine.** Internal mastery scale = CEFR sub-bands `A1.1, A1.2, A2.1, A2.2, B1.1, B1.2, B2`.

**WIDA is a projection**, not an alternate engine. Every mastery record carries a derived WIDA proficiency level via a static mapping table. Teacher dashboard for K-12 cohorts and JCPS-facing reports render WIDA labels; the engine never writes WIDA.

**PRD's Level 0/1/2/3 persist as friendly UI aliases** for Spanish-first learners who find them more legible. They map to CEFR sub-band ranges, not specific bands.

## Consequences

- All mastery cells, placement results, and lesson tags use CEFR.
- Teacher dashboard exposes a WIDA toggle (M2+).
- Adult cohorts default to CEFR display; K-12 cohorts default to WIDA display.
- A `cefr_descriptors` table (extracted from Tier A standards ingestion) is the authoritative descriptor registry — referenced from mastery, lessons, placement, and graph nodes.
- The `WIDA Can-Do K` PDF gap (404 on wida.wisc.edu) becomes lower-stakes since K-12 path doesn't ship until M2.
- All compiled documents in `/data/pedagogy/` and `/data/reference/` already use CEFR — no rewriting needed.

## Alternatives considered

- **WIDA canonical** — rejected. Better JCPS alignment but worse for adults; fragments curriculum across grade bands; doesn't match the existing tutor reference docs.
- **Custom levels canonical with both CEFR + WIDA tags** — rejected. Simplest UI but weakest engine; loses the ability to use external descriptor sets directly.

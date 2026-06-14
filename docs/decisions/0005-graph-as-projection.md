# ADR 0005 — SQL is truth; graph is derived projection

**Status:** Accepted
**Date:** 2026-06-14
**Depends on:** 0003, 0004
**Consumed by:** 0007, 0008, 0012

## Context

PRD made hybrid vector+graph a load-bearing architectural commitment AND required that the graph be replaceable without redesigning the product (line 212, "Cognee-style tooling is optional; system must remain modular so the graph layer can be replaced or simplified"). Those two requirements only co-exist if the graph never holds state that SQL doesn't.

Without an explicit graph schema, the PRD's "graph-augmented prompt assembly," "graph-based prerequisite reasoning," and "graph-backed tutor context assembly" are vibes.

## Decision

**SQL is the source of truth for all entity state. The graph is a derived projection rebuildable from SQL via `POST /graph/rebuild`.** If SQL is gone, the graph is recoverable. If the graph is swapped (Postgres native → Neo4j → Cognee), nothing else changes.

**Node types (9)**:
- `Standard` — one per CEFR descriptor (from Tier A)
- `MasteryCell` — per learner cell
- `Lesson`, `LessonStep`, `ContentChunk`
- `Vocabulary` (corpus-derived, not student-specific), `Topic`
- `Student` (minimal mirror — id + level only)
- `ErrorPattern` (Spanish L1 seed table)

**Edge types (11 across 4 categories)**:
- *Structural* (`composes`, `aligns_with`, `belongs_to`) — rebuilt on SQL writes
- *Pedagogical* (`prerequisite_of`, `bilingual_equivalent`, `transferred_from`, `scaffolds`) — rebuilt on ingestion
- *Per-student* (`demonstrated_by`, `gap_in`, `addresses_gap`) — rebuilt nightly + delta on attempts
- *Semantic* (`similar_to`, `topic_of`) — rebuilt on chunk embedding

**Property model**: nodes carry identity + minimal structural facts. All queryable state (mastery scores, attempt counts, XP balances, time-series) stays in SQL.

**Storage boundary**:
- SQL (Postgres) — source of truth for all entity state, attempts, mastery, XP, vocab SRS, raw chunks, embeddings (via pgvector).
- Vector index — pgvector with HNSW, MVP scale.
- Graph layer — Postgres `graph_nodes` + `graph_edges` tables for MVP, recursive CTEs for traversal.
- Cognee/Neo4j evaluation reserved for M3+; never assumed.

## Consequences

- New SQL tables: `cefr_descriptors`, `topics`, `vocabulary`, `error_patterns`.
- `graph_nodes`, `graph_edges` per PRD (with type indexes for traversal performance).
- A `graph_rebuild` script walks SQL and emits nodes/edges idempotently.
- Three named graph query patterns drive runtime behavior:
  - `recommend_next_lesson(student_id)` — multi-hop gap → prereqs → addressing lessons → rank
  - `bilingual_scaffolds(vocab_id)` — `bilingual_equivalent` + `transferred_from` walk
  - `descriptor_neighborhood(descriptor_id)` — `prerequisite_of` + `scaffolds` walk
- **Code-review invariant**: no write to graph that isn't also in SQL. Enforced manually for now; can be linted in M2+.
- M1 ships with structural + per-student edges active. Pedagogical and semantic edges are ingested but unused; activated in M2/M3.

## Alternatives considered

- **Graph DB as source of truth** — rejected. Couples product to graph vendor; violates PRD line 212.
- **No graph layer; pure SQL recursive CTEs** — rejected. Acceptable for MVP but doesn't future-proof the graph-augmented tutor and recommendation goals.
- **Adopt Cognee at MVP** — rejected per PRD line 212; evaluation only.

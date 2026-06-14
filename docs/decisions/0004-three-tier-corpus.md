# ADR 0004 — Three-tier corpus: Standards / Learner / TutorRef

**Status:** Accepted
**Date:** 2026-06-14
**Depends on:** 0001, 0002, 0003
**Consumed by:** 0005, 0007, 0008, 0010

## Context

We built a substantial corpus in `/data/` (~50 files, ~50 MB) but treated all files as undifferentiated. They split cleanly into three runtime roles with completely different lifecycle rules. Without tiering, the retrieval index conflates user-facing reading material with tutor behavioral guidance; licensing enforcement becomes ad-hoc; and the AI tutor receives raw markdown instead of compiled rule blocks.

## Decision

**Tier A — Standards** (read once at bootstrap, rarely re-ingested): CEFR Companion Volume, WIDA framework, WIDA Can-Do. Compiled into the `cefr_descriptors` table that drives the mastery cell registry.

**Tier B — Learner Content** (chunked, embedded, retrieved, served): MN Story Bank, USCIS 100q, NGSL/NAWL/BSL/TSL frequency lists, CMU dict, minimal pairs index, JCPS/La Casita local context.

**Tier C — Tutor Reference** (compiled into tutor system prompts, never shown to learners): SLA primer, pragmatics inventory, Spanish L1 transfer cheat sheet, lesson templates, translanguaging guidance, Krashen summary, SIOP, Bloom×CEFR.

**Heterogeneous chunking strategy per source type**, stored on `ContentSource.chunk_strategy`:
- Standards PDFs → per CEFR descriptor row
- Story PDFs → per story (1–3 pages)
- CSV/dict → per row
- Exercise PDFs → per item / Q-A pair
- Tier C markdown → per H2 section
- Research PDFs → 600–800 token semantic chunks with overlap

**Three-pass tagging pipeline**:
1. Deterministic from source metadata (folder structure encodes most tags).
2. LLM-assisted refinement (Haiku-tier) for `cefr_descriptor_ids`, `topic`, `components`.
3. Spot-check curator queue for first 5% of new sources.

**License gate**: every Tier B source requires explicit license metadata. Non-redistributable content served as paraphrase only. Tier C never enters the vector index that learner retrievals hit.

## Consequences

- `ContentSource` table gains `tier`, `chunk_strategy`, `license`, `redistributable` fields.
- `ContentChunk` gains `cefr_descriptor_ids[]`, `mode[]`, `component[]`, `domain`, `topic`, `l1_supported`, `chunk_strategy_used`.
- Ingestion pipeline becomes 4 stages: classify-tier → chunk-per-strategy → tag (3-pass) → license-gate.
- Tier C compiles into a separate "tutor prompt registry" (see ADR 0008), not the vector index.
- Retrieval API enforces tier-aware routing: Tier B for learner-facing; Tier C for tutor prompts only.
- `gaps.md` license-audit pass added to ingestion.

## Alternatives considered

- **Uniform chunking strategy** — rejected. PRD line 185 implies "PDF and HTML chunking" as one approach; that conflates very different content types.
- **Manual tagging only** — rejected. ~2000 chunks × 7+ tags ≈ 80 hours of work.
- **Fully automatic LLM tagging** — rejected. Inconsistent without verification; chunks miss descriptor alignment.
- **Single retrieval index across all tiers** — rejected. Tier C content leaking into learner output would be a privacy/copyright violation and a quality failure.

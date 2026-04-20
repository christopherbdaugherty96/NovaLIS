# Nova Memory Continuity Upgrade (Candidate Design Note)

**Status:** Candidate Design - Pending Translation into Active Work  
**Last Updated:** 2026-04-20  
**Core Insight:** *Nova already has continuity surfaces; the gap is visibility and usefulness, not existence.*

---

## 1. Executive Summary

Nova's runtime already records session summaries and topic patterns via `nova_self_memory_store` and `session_handler.py`. The foundation exists. The current limitation is that these continuity surfaces are not sufficiently visible to the user, nor are they easily queryable during conversation.

This document outlines low-risk enhancements to **amplify existing continuity features** without rewriting the memory subsystem. All proposals extend the current `memory_api.py` and `session_handler.py` surfaces.

**Immediate Deliverable:** "Continuity Visibility Upgrade" - surface existing session summaries on launch, improve decision query, and add a memory-used indicator tied to actual runtime usage.

---

## 2. Current Memory Architecture (Actual)

| Component | Actual Path | Existing Continuity Features |
| :--- | :--- | :--- |
| `GovernedMemoryStore` | `nova_backend/src/memory/governed_memory_store.py` | Explicit user memories (`remember: X`) |
| `UserMemoryStore` | `nova_backend/src/memory/user_memory_store.py` | Observed preferences |
| `NovaSelfMemoryStore` | `nova_backend/src/memory/nova_self_memory_store.py` | Already has `record_session_summary()`, `get_recent_summaries()`, `record_topic()`, `get_top_topics()` |
| Session Handler | `nova_backend/src/websocket/session_handler.py` | Already writes a session summary at shutdown for sessions with 3 or more turns |
| Memory API | `nova_backend/src/api/memory_api.py` | Already exposes `/api/memory/nova` (summaries, topics) and `/api/memory/context` |
| Governance | `nova_backend/src/governor/` | Five-stage pipeline; all memory writes are governed |
| Ledger | `nova_backend/src/ledger/` plus governed event logging paths | Append-only audit subsystem, not a single design-center file |

**Key Correction:** Nova *does* have a session handoff mechanism. The gap is that users cannot easily see or query it.

---

## 3. Cognitive Fit

Nova's primary user operates as a builder/strategist. The highest-value upgrade is **surfacing existing continuity** to reduce session restart friction.

Three core needs:

1. **Where was I?** -> Display recent session summary on open (already stored; just needs UI surface)
2. **What did we decide?** -> Query existing summaries and governed memory for decision markers
3. **What should I continue?** -> Already saved at shutdown; just needs visibility

---

## 4. Prioritized Enhancements

### Tier 1: Immediate Visibility (Post-Installer Validation)

**Goal:** Surface existing continuity data with zero new storage logic.

| # | Enhancement | Implementation Summary | Real Files to Extend |
| :-- | :--- | :--- | :--- |
| 1 | **Current Focus Card on Open** | On dashboard load, fetch the most recent session summary from `/api/memory/nova` and display it in the existing dashboard surface. No new backend route is required. | `nova_backend/static/` dashboard surface files<br>`nova_backend/src/api/memory_api.py` (consume existing endpoint; backend change only if payload shaping is needed) |
| 2 | **"What Did We Decide?" Query** | Add a bounded `/decisions` surface that searches recent session summaries and governed memory by decision keywords only. Typed decision retrieval remains a later enhancement. | `nova_backend/src/api/memory_api.py` (new endpoint if needed)<br>`nova_backend/src/websocket/session_handler.py` or the real command-routing surface |
| 3 | **Memory Used Indicator** | When memory is actually injected into runtime prompt context, emit metadata from the real injection path so the frontend can display a chip based on actual usage, not just preview availability. | Actual context-injection path in `session_handler.py` / prompt assembly<br>Frontend component in `nova_backend/static/` |

---

### Tier 2: Structured Retrieval (After cap 64 Lock)

| # | Enhancement | Implementation Summary |
| :-- | :--- | :--- |
| 4 | **Memory Types (Tags)** | Extend memory item schema with optional `type` field: `decision`, `priority`, `blocker`, `idea`, `preference`. |
| 5 | **Filtered Recall Commands** | Add `/recall type:decision` that queries `GovernedMemoryStore` by type. |
| 6 | **Recency-Weighted Display** | When displaying memory lists, sort by `last_accessed` descending. |
| 7 | **Explicit Decision Marking** | Allow user to say "Remember that as a decision: X" which sets type automatically. |

---

### Tier 3: Future (Research Track)

| # | Enhancement | Notes |
| :-- | :--- | :--- |
| 8 | **Semantic Search** | ChromaDB + embeddings; keep JSON as source of truth. |
| 9 | **Ledger Pattern Extraction** | Nightly job scanning governed events for repeated behaviors; user approval required. |
| 10 | **Priority Drift Alert** | Compare `Now.md` focus with recent topics. |

**Activation Gate:** All Tier 1/2 stable and user feedback confirms desire for more automation.

---

## 5. What Not to Build

- Silent, autonomous inference (violates trust model)
- Full vector migration before basic continuity visibility is proven
- New parallel API routes when existing ones suffice

---

## 6. Immediate Next Actions

1. Complete installer validation (current `Now.md` priority)
2. Lock cap 64
3. Implement Tier 1 enhancements as a single visibility upgrade
4. Gather feedback on perceived continuity
5. Decide on Tier 2 activation

---

## 7. Acceptance Criteria for Promotion

Before this note becomes active roadmap work, define and verify:

1. A visible focus surface on startup that shows the latest session summary when one exists
2. A bounded decisions surface that returns useful results without relying on future typed-memory schema
3. A memory-used indicator that reflects actual runtime usage rather than memory preview availability
4. No parallel API or command surface when an existing runtime path can be extended

---

## 8. Alignment with Existing Docs

This candidate note aligns with:

- `4-15-26 NEW ROADMAP/Now.md` - current sprint focus
- `docs/capability_verification/STATUS.md` - capability verification
- `docs/future/NOVA_FUTURE_TECHNICAL_CONCEPT_DRAFT_2026-04.md` - future concept reserve
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md` - accurate runtime architecture

**Promotion to active roadmap requires reconciliation with runtime truth and removal of this note's candidate status.**

---

*End of Document*

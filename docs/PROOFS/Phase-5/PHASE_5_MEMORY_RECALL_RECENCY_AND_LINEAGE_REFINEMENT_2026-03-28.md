# Phase 5 Memory Recall, Recency, and Lineage Refinement
Date: 2026-03-28
Status: Implemented runtime refinement

## Purpose
Tighten Nova's explicit memory layer so it feels easier to use day to day without drifting toward implicit memory behavior.

## What Landed
- governed `recent memories` command path
- governed `search memories for <topic>` command path
- stronger relevant-memory ranking for bounded chat recall
- superseded older memory items no longer outrank their replacement during relevant recall
- richer selected-memory detail showing created/updated timestamps, version, and edit lineage
- Memory page button for recent-memory review
- linked-thread memory overview now shows the latest remembered decision when available

## Runtime Files
- `nova_backend/src/memory/governed_memory_store.py`
- `nova_backend/src/executors/memory_governance_executor.py`
- `nova_backend/src/governor/governor_mediator.py`
- `nova_backend/static/index.html`
- `nova_backend/static/dashboard.js`

## Verification
- `python -m pytest tests\phase5\test_memory_governance_executor.py tests\test_governor_mediator_phase4_capabilities.py tests\phase45\test_dashboard_memory_widget.py tests\test_memory_api.py tests\test_governed_memory_store.py -q`
- `python -m pytest tests\conversation\test_general_chat_runtime.py tests\phase45\test_brain_server_memory_and_continuity.py -k "memory or relevant_explicit_memory_context" -q`

## Result Snapshot
- memory / parser / dashboard / API / store bundle: `22 passed`
- bounded chat-memory continuity bundle: `21 passed`

## Boundary
This refinement improves explicit memory usability and bounded recall quality.
It does not introduce silent memory creation, hidden profiling, or autonomous memory mutation.

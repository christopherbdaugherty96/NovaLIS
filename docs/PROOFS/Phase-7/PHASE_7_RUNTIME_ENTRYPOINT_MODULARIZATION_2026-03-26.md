# Phase 7 Runtime Entrypoint Modularization
Date: 2026-03-26
Status: Completed and verified

## Purpose
Reduce the size and responsibility load of `nova_backend/src/brain_server.py` by moving:
- the websocket session runtime into a dedicated module
- the real HTTP route groups into focused API modules

This follows the earlier routing cleanup work and continues aligning the runtime entrypoint with Nova's architectural intent.

## What changed
New modules:
- `nova_backend/src/websocket/session_handler.py`
- `nova_backend/src/api/workspace_api.py`
- `nova_backend/src/api/audit_api.py`
- `nova_backend/src/api/bridge_api.py`
- `nova_backend/src/api/settings_api.py`

Updated assembly file:
- `nova_backend/src/brain_server.py`

## Runtime shape after this change
`brain_server.py` now acts much more like an application assembly file:
- creates the FastAPI app
- mounts static files
- wires routers
- exposes the websocket route as a thin wrapper
- keeps shared runtime helpers and module-level state that the extracted session handler still uses

The moved route groups are:
- app entry shell routes (`/`, `/landing`)
- phase/audit routes
- OpenClaw bridge routes
- runtime settings routes

The websocket route now delegates to:
- `run_websocket_session(...)` in `src/websocket/session_handler.py`

## Important compatibility protection
To avoid breaking current bridge tests and existing monkeypatch seams:
- `brain_server.py` still exposes `_run_bridge_messages(...)`
- the bridge router prefers `deps._run_bridge_messages(...)` if present

This keeps the current testing contract intact while still moving the real route logic out of the monolith.

## Why this matters
This slice improves the codebase as a product system, not just as a code exercise:
- lower risk when changing API surfaces
- lower risk when changing websocket runtime behavior
- clearer mental model for future contributors
- easier test targeting by route family

## Verification
Compile check:

```text
python -m py_compile nova_backend/src/brain_server.py nova_backend/src/api/audit_api.py nova_backend/src/api/bridge_api.py nova_backend/src/api/settings_api.py nova_backend/src/api/workspace_api.py nova_backend/src/websocket/session_handler.py
```

Result:
- passed

Focused route/runtime bundles:

```text
python -m pytest tests\test_runtime_settings_api.py tests\test_openclaw_bridge_api.py tests\test_runtime_auditor.py -q
```

Result:
- `24 passed`

```text
python -m pytest tests\conversation\test_general_chat_runtime.py tests\phase45\test_brain_server_basic_conversation.py -k "pending_escalation_confirmation or hello_uses_deterministic_local_response or what_can_you_do_with_question_mark_stays_on_capability_path or general_chat_receives_relevant_explicit_memory_context or followup_chat_uses_recent_conversation_context or brain_server_carries_structured_conversation_context_between_chat_turns or voice_general_chat_auto_speaks_generated_answer" -q
```

Result:
- `7 passed`

```text
python -m pytest tests\phase45\test_brain_server_trust_status.py tests\phase45\test_brain_server_website_preview.py -q
```

Result:
- `2 passed`

```text
python -m pytest tests\phase45\test_dashboard_onboarding_widget.py tests\phase45\test_dashboard_trust_center_widget.py tests\phase45\test_dashboard_trust_review_widget.py -q
```

Result:
- `10 passed`

Repo truth checks:
- `python scripts/check_runtime_doc_drift.py` -> passed
- `python scripts/check_frontend_mirror_sync.py` -> passed

## Honest remaining gap
`brain_server.py` is now materially smaller in responsibility, but not yet fully minimal.

What still remains there:
- a large number of helper builders and regex command surfaces
- many widget payload builders
- many command-preparation helpers

So the monolith problem is improved, not fully erased.

## Bottom line
This slice completed the next structural move that was recommended:
- API route groups were extracted
- the websocket session loop was extracted
- compatibility was preserved
- runtime tests and repo-truth checks passed

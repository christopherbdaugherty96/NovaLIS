# NOVA Audit TODO
Updated: 2026-03-28

## Purpose
This document converts the 2026-03-28 end-to-end audit into an actionable remediation backlog.

It covers:
- capability implementation gaps
- skill and tool surface drift
- dead or misleading code paths
- documentation truth mismatches
- stale governance and verification tests

## Remaining Open Priorities
After the current hardening and cleanup passes, the main remaining item from this packet is:
- item 7: Windows media-control command semantics

## Recommended Execution Order
1. Fix externally reachable security issues.
2. Fix data-loss and execution-boundary correctness bugs.
3. Correct governance metadata and runtime truth docs.
4. Remove or quarantine dead legacy surfaces.
5. Repair stale tests so the verification layer reflects real behavior.

## P0

### 1. Block DNS rebinding on HTTP and WebSocket surfaces
- Status: closed on `main`
- Risk: remote web pages can reach loopback-only Nova APIs and the websocket endpoint by spoofing `Host` and `Origin`.
- Evidence:
  - `nova_backend/src/brain_server.py`
  - `nova_backend/src/api/memory_api.py`
  - `nova_backend/src/api/settings_api.py`
  - `nova_backend/src/websocket/session_handler.py`
- Required work:
  - add strict trusted-host validation for HTTP requests
  - add explicit websocket `Host` and `Origin` allowlisting before accept
  - confirm local dashboard and remote bridge paths still work after the restriction
  - add regression tests for hostile `Host` / `Origin` values on memory export, runtime settings mutation, and websocket connect
- Validation target:
  - hostile host/origin requests fail
  - local expected surfaces still succeed

## P1

### 2. Prevent lost updates in JSON-backed durable stores
- Status: closed on `main`
- Risk: concurrent writes can silently drop durable state.
- Primary evidence:
  - `nova_backend/src/memory/governed_memory_store.py`
  - `nova_backend/src/executors/memory_governance_executor.py`
  - `nova_backend/src/brain_server.py`
  - `nova_backend/src/websocket/session_handler.py`
- Related stores with the same whole-file pattern:
  - `nova_backend/src/tasks/notification_schedule_store.py`
  - `nova_backend/src/patterns/pattern_review_store.py`
  - `nova_backend/src/policies/atomic_policy_store.py`
- Required work:
  - replace per-instance locking with cross-instance file locking or a shared process-global lock keyed by path
  - ensure writes are atomic and preserve concurrent updates
  - add explicit concurrent-writer regression tests for each durable store family
- Validation target:
  - repeated concurrent save/update operations preserve all expected records

### 3. Make `ExecuteBoundary.run_with_timeout()` enforce a real wall-clock timeout
- Status: closed on `main`
- Risk: timed-out work still occupies the single-action lane until the worker finishes.
- Evidence:
  - `nova_backend/src/governor/execute_boundary/execute_boundary.py`
  - `nova_backend/tests/test_execute_boundary_timeout_behavior.py`
- Required work:
  - redesign timeout handling so the caller returns promptly without waiting for a stuck worker
  - make the queue semantics explicit if true cancellation is impossible
  - update tests to assert actual timeout behavior instead of current delayed return behavior
- Validation target:
  - a short timeout returns near the requested bound rather than after worker completion

## P2

### 4. Correct capability governance metadata for story tracking
- Status: closed on `main`
- Risk: runtime, ledger, and docs describe a durable write path as read-only.
- Evidence:
  - `nova_backend/src/config/registry.json`
  - `nova_backend/src/executors/story_tracker_executor.py`
  - `docs/current_runtime/GOVERNANCE_MATRIX.md`
- Required work:
  - reclassify capability `52` to match durable writes
  - align `authority_class`, `external_effect`, and `reversible` values in executor results
  - regenerate runtime docs after metadata is corrected
  - add tests that assert the contract for story-tracker update responses
- Validation target:
  - registry, runtime docs, ledger metadata, and executor results all agree

### 5. Correct capability governance metadata for headline summary and intelligence brief
- Status: closed on `main`
- Risk: capabilities `49` and `50` are documented as local-only but can perform live network reads.
- Evidence:
  - `nova_backend/src/config/registry.json`
  - `nova_backend/src/governor/governor.py`
  - `nova_backend/src/executors/news_intelligence_executor.py`
  - `docs/current_runtime/GOVERNANCE_MATRIX.md`
- Required work:
  - update registry metadata to reflect governed network access
  - review any dependent trust, ledger, and docs assumptions
  - add tests asserting the intended governance contract, not just the current executor behavior
- Validation target:
  - runtime docs and metadata reflect actual network reachability

### 6. Decide and encode the true governance contract for screen capture
- Status: closed on `main`
- Risk: capability `58` is documented as read-only even though it persists PNG files.
- Evidence:
  - `nova_backend/src/config/registry.json`
  - `nova_backend/src/perception/screen_capture.py`
  - `docs/current_runtime/GOVERNANCE_MATRIX.md`
- Required work:
  - decide whether invocation-time screen capture counts as a persistent local change
  - encode that decision consistently in registry metadata, executor result metadata, and docs
  - add a regression test for the chosen contract
- Validation target:
  - docs and runtime metadata match the intended product contract for saved captures

### 7. Fix Windows media-control command semantics
- Status: open
- Risk: `unmute`, `pause`, and `resume` do not do what they claim on Windows.
- Evidence:
  - `nova_backend/src/system_control/system_control_executor.py`
  - `nova_backend/tests/executors/test_system_control_executor.py`
  - `nova_backend/tests/test_system_control_executor.py`
- Required work:
  - implement state-aware or platform-correct behavior for mute/unmute
  - implement reliable play/pause/resume semantics or narrow the contract if Windows cannot support them cleanly
  - add direct Windows-path tests for media and volume behavior
- Validation target:
  - explicit commands no longer collapse into a generic toggle in tests

## P3

### 8. Fix quiet-hours end-value normalization
- Status: closed on `main`
- Risk: invalid quiet-hours end values silently fall back to the start default.
- Evidence:
  - `nova_backend/src/tasks/notification_schedule_store.py`
- Required work:
  - normalize `quiet_hours_end` against the correct default
  - add malformed-input tests for start and end independently
- Validation target:
  - invalid end values no longer render `start == end` unless explicitly intended

### 9. Repair stale perception governance verification
- Status: closed on `main`
- Risk: verification is red even though runtime invocation-source wiring still exists.
- Evidence:
  - `nova_backend/tests/governance/test_screen_capture_requires_invocation.py`
  - `nova_backend/src/websocket/session_handler.py`
  - `nova_backend/src/brain_server.py`
- Required work:
  - update the test to assert the live wiring location instead of the previous `brain_server.py` location
  - consider strengthening it to assert behavior instead of raw source text
- Validation target:
  - the perception governance slice passes for the current runtime architecture

### 10. Repair stale ledger-governor verification
- Status: closed on `main`
- Risk: the governance test flags harmless string mentions as event emission.
- Evidence:
  - `nova_backend/tests/governance/test_ledger_only_governor_logs_actions.py`
  - `nova_backend/src/executors/os_diagnostics_executor.py`
- Required work:
  - change the test so it detects actual event emission or logger usage instead of naive substring matches
  - keep the rule that skills must not emit governor action events
- Validation target:
  - diagnostics can safely inspect ledger history without failing the policy test

## Skill And Tool Surface Cleanup

### 11. Remove or quarantine dead legacy web-search skill files
- Status: closed on `main`
- Risk: dead compatibility surfaces are still documented as active and can mislead maintainers.
- Evidence:
  - `nova_backend/src/skills/web_search.py`
  - `nova_backend/src/skills/web_search_skill.py`
  - `nova_backend/src/tools/web_search.py`
  - `docs/current_runtime/SKILL_SURFACE_MAP.md`
- Current state:
  - `src/skills/web_search.py` defines a second `NewsSkill` that depends on a tool shim returning `None`
  - `src/skills/web_search_skill.py` is a governed-execution handoff stub not registered in the live skill registry
  - `src/tools/web_search.py` is a sealed compatibility shim that always returns `None`
- Required work:
  - either delete these files, move them to an explicit archive/quarantine area, or mark them as excluded from runtime-doc generation
  - remove stale trust-status bookkeeping references such as the `web_search` / `web_search_skill` branch in `session_handler.py`
  - add a regression test that runtime docs do not report quarantined or compatibility-only skill files as live skills
- Validation target:
  - runtime docs only include reachable skill surfaces

### 12. Clarify the role of `SkillRegistry`
- Status: closed on `main`
- Risk: it is easy to mistake `SkillRegistry` for live runtime routing even though it is no longer on the websocket hot path.
- Evidence:
  - `nova_backend/src/skill_registry.py`
  - `nova_backend/tests/simulation/conversation_simulator.py`
  - `docs/reference/HUMAN_GUIDES/24_NOVA_STATUS_AND_PHASE_REPORT_2026-03-25.md`
- Required work:
  - decide whether `SkillRegistry` should remain as simulation/support infrastructure or move into a simulation-specific location
  - document that scope explicitly if it remains
  - keep current simulation coverage if retained
- Validation target:
  - maintainers can tell at a glance whether `SkillRegistry` is live runtime or support-only code

## Runtime Docs Truth Work

### 13. Make runtime-doc generation exclude unreachable or compatibility-only skill files
- Status: closed on `main`
- Risk: generated docs currently treat every `src/skills/*.py` file as a live skill.
- Evidence:
  - `nova_backend/src/audit/runtime_auditor.py`
  - `docs/current_runtime/SKILL_SURFACE_MAP.md`
- Required work:
  - derive skill rows from reachable runtime wiring, not just filesystem presence
  - optionally annotate support-only and simulation-only surfaces separately
  - add assertions for concrete row content in docs tests
- Validation target:
  - `SKILL_SURFACE_MAP.md` matches actual runtime reachability

### 14. Strengthen runtime-doc tests beyond heading presence
- Status: closed on `main`
- Risk: docs tests currently allow materially false docs to pass.
- Evidence:
  - `nova_backend/tests/test_runtime_governance_docs.py`
- Required work:
  - add checks for specific capability semantics
  - add checks that false-positive skill rows are absent
  - add checks that generated docs stay aligned with current runtime branch logic
- Validation target:
  - incorrect runtime-doc content causes test failure

## Notes For The First Remediation Pass
- Start by fixing the DNS rebinding hole before any metadata or docs cleanup.
- Once metadata is corrected, regenerate `docs/current_runtime/*` so the truth layer catches up.
- Do not delete `SkillRegistry` until the simulation path has a replacement or a clear support-only home.
- Treat the legacy web-search files as cleanup candidates first, not as active behavior to preserve.

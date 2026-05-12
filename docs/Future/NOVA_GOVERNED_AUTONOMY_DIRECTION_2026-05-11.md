# Nova Governed Autonomy — Direction Record

**Date:** 2026-05-11
**Status:** Planning only — direction record. No runtime autonomy expansion authorized by this doc.
**Type:** Future direction / planning record / non-runtime-authority
**PR:** audit/openclaw-freeform-goal-inspection (#153)
**Source:** Audit findings from PASS4_OPENCLAW_FREEFORM_GOAL_INSPECTION_2026-05-11.md +
reviewed ChatGPT second-pass recommendation 2026-05-11
**Reviewed by:** Claude + ChatGPT second-pass (advisory, not authoritative)

---

## Core Position

**Autonomous workflows are allowed in Nova — inside Governor-monitored envelopes.**

This is not a reversal of the governance-first posture. It is the natural extension of it.
The Governor's purpose is to gate execution authority. Within a properly bounded mission
envelope — one that enforces a tool allowlist, caps steps and network calls, routes
mutation-capable actions through GovernorMediator, and preserves human override at every
boundary — an agent continuing to work autonomously without per-step user input is exactly
what the governance architecture was designed to support.

The current OpenClaw freeform goal path (`run_goal()` → `ThinkingLoop` →
`ExecutorSkillAdapter`) is **not** that architecture. It passes the full `ToolRegistry`
singleton to `ThinkingLoop` with no allowlist (agent_runner.py:1154). `ExecutorSkillAdapter.
_execute_sync()` calls `executor.execute(request)` directly at line 77 — no GovernorMediator,
no Governor, no CapabilityRegistry, no SingleActionQueue, no ExecuteBoundary. That path must
be patched before it qualifies as governed.

**Autonomy is approved. Ungoverned execution is not.**

---

## What Changed and Why

The PASS4 audit (2026-05-11) confirmed that `run_goal()` at agent_runner.py:1154 constructs
`ThinkingLoop(registry=self._tool_registry, ...)` passing the raw singleton with no allowlist.
`ThinkingLoop._reason()` at thinking_loop.py:218 builds the LLM prompt with
`f"Available tools: {', '.join(self._registry.tool_names)}"` — all tools visible, including
mutation-capable ones. `ThinkingLoop._select_tools()` at thinking_loop.py:233 filters only
on previously-failed tools. `volume` (registry line 211), `brightness` (line 233), `media`
(line 255), and `open_webpage` (line 279) are all REACHABLE-MUTATION-CAPABLE.

The `/api/openclaw/approve-action` endpoint at openclaw_agent_api.py:461–509 unconditionally
returns `approval_state = auto_allowed` for all inputs and is not wired into the ThinkingLoop
execution chain. ThinkingLoop never calls it before executing a tool — it is purely a future
stub with no current gating effect.

The fix is not to remove the freeform goal path. The fix is to make it governed: enforce a
tool allowlist via PATCH A, add a `MeteredNetworkProxy` budget envelope via PATCH C, wire
real human-in-the-loop suspension for mutation actions via PATCH B, and then build forward
toward richer mission types tier by tier.

---

## Relationship to Existing Architecture

Understanding the gap between the current template path and the current goal path is the
foundation for every governed autonomy patch.

### `run_template()` — the reference governed path

`run_template()` (agent_runner.py:194) already implements the governed envelope pattern:

```text
run_template()
  → TaskEnvelope.from_template()      — budget fields: max_steps, max_network_calls,
                                         max_files_touched, max_bytes_read, max_bytes_written
  → evaluate_manual_envelope()        — preflight gate; raises if envelope not allowed
  → RunBudgetMeter(envelope)          — tracks all five budget dimensions
  → _collect_payload()                — data collection step, metered
  → _summarize_with_local_model() /
    _summarize_with_metered_openai()  — LLM call, metered via MeteredNetworkProxy
  → _store.record_run()               — full audit record committed to run store
```

This is the target architecture for governed autonomy. The template path produces a complete
audit trail, enforces budget limits, and records every run with status, budget usage, and
timing. Governed missions must produce the same.

### `run_goal()` — the current ungoverned path

`run_goal()` (agent_runner.py:1137) already has partial infrastructure:

- **Run store integration:** `_store.set_active_run()`, `_store.update_active_run()` (via
  `_on_step_progress` callback), `_store.finish_active_run()`, `_store.record_run()` — the
  run record skeleton exists.
- **Per-tool budget:** `_per_tool_budget = PerToolBudgetTracker()` and `.record_call()` per
  tool — per-tool usage is tracked but not enforced as a hard budget.
- **Cancellation:** `_store.is_cancel_requested(goal_id)` checked at each step via
  `_on_step_progress` → `RunCancelledError` path. User cancellation already works.
- **ThinkingLoop.MAX_STEPS:** An existing step cap constant in ThinkingLoop; PATCH A's
  allowlist work must not override or conflict with this existing cap.

**What `run_goal()` lacks vs `run_template()`:**
- No `TaskEnvelope` (no unified budget envelope for all five dimensions)
- No `evaluate_manual_envelope()` preflight gate
- No `MeteredNetworkProxy` wrapping (PATCH C)
- No tool allowlist (PATCH A)
- No `approve-action` gating for mutation tools (PATCH B, Tier 3)

Governed autonomy patches `run_goal()` incrementally to close this gap, bringing the goal
path to the same governance standard as the template path.

### API entry points

- `/api/openclaw/agent/goal` — posts a freeform goal to `run_goal()`. This becomes the
  governed mission entry point after PATCH A–C land.
- `/api/openclaw/approve-action` — currently auto-approves all actions and is not connected
  to the execution chain. In Tier 3, this endpoint is restructured to be a real suspension
  gate: it pauses ThinkingLoop, presents the proposed action to the user, and waits for an
  explicit allow/deny before proceeding.
- `/api/openclaw/run-template` — posts a template ID to `run_template()`. This path is
  already governed and is not changed by any governed autonomy patch.

---

## Governed Autonomy Model — Four Tiers

Each tier is a separate planning phase requiring its own reviewed priority lock before any
runtime implementation. Later tiers depend on earlier tiers being stable and tested.

### Tier 1 — Read-Only Missions

Agent operates with a read-only tool allowlist. No mutations. No sends. No external writes.
Informational and inspection tools only. The LLM prompt shows only allowlisted tools; the
LLM cannot select a tool it cannot see.

**Allowed tool frozenset (Tier 1 default — subject to review at lock time):**

```python
_TIER1_ALLOWED_TOOLS = frozenset({
    "weather",       # network read, mediated by NetworkMediator
    "news",          # network read, mediated by NetworkMediator
    "web_search",    # network read, mediated by NetworkMediator
    "memory_search", # local read only
    "time_query",    # local read only
    # future: audit/inspection read-only tools when defined
})
```

All tools with category `"mutation"` or `"collection"` are excluded. Any tool not in the
frozenset is excluded regardless of category.

**Blocked at Tier 1 (explicit):**
- `volume`, `brightness`, `media`, `open_webpage` — mutation-capable, excluded by PATCH A
- `screen_capture` — excluded intentionally; do not rely on the existing param-extractor
  gap as a security control (PATCH D)
- Any tool registered after this document that is not explicitly added to the allowlist

**Budget envelope (Tier 1 conservative defaults):**

| Dimension | Default | Notes |
|---|---|---|
| `max_steps` | 10 | Aligns with ThinkingLoop.MAX_STEPS; adjustable per mission |
| `max_network_calls` | 5 | MeteredNetworkProxy enforcement (PATCH C) |
| `max_files_touched` | 0 | No local file writes at Tier 1 |
| `max_bytes_read` | 512 000 | Conservative; enough for search summaries |
| `max_bytes_written` | 0 | No writes at Tier 1 |
| `max_time_seconds` | 120 | Hard wall-clock cap; adjustable up to 600 |

**Halt behavior:**

| Trigger | Action |
|---|---|
| Step limit reached | Halt immediately, commit partial run record, surface to user |
| Time cap reached | Halt immediately, commit partial run record, surface to user |
| Network budget exhausted | Halt immediately, commit partial run record, surface to user |
| LLM selects non-allowlisted tool | `filtered_registry` prevents this by design — LLM sees only allowlisted tools; if `_registry.create()` raises `KeyError` despite filtering, halt and log |
| Executor error | Record per-step failure, continue if ThinkingLoop retry logic allows; halt if max retries exceeded |
| User cancellation | `RunCancelledError` → `status="cancelled"` record; mission does not resume |
| Goal ambiguous / no tools applicable | ThinkingLoop returns early; record as `status="failed"` with reason |

**Example mission (Tier 1):** "Search for recent news about our Shopify store's product
category and summarize the key themes." Agent runs inside the envelope, picks from the
allowlisted tools, produces a synthesis, commits a run record. No per-step user interaction.
Final receipt surfaced to user.

**Implementation gate:** PATCH A (allowlist + `filtered_registry`) reviewed, implemented,
and tested with rejection tests for `volume`, `brightness`, `open_webpage`. PATCH C
(`MeteredNetworkProxy` in `run_goal()`) implemented and tested. Own reviewed priority lock
required before implementation begins.

---

### Tier 2 — Draft-Only Missions

Agent may produce drafts (email drafts, PR descriptions, plans, issue summaries) but cannot
send, publish, commit, or post. Draft output is an artifact returned to the user for review
and explicit action. Tier 2 missions also include all Tier 1 tools.

**Architecture model:** Cap 64 (`send_email_draft`) — produces a local `mailto:` draft,
user initiates send, no autonomous SMTP. All Tier 2 output follows this model: produce
artifact locally, surface to user, user decides whether to act.

**New tool category needed:** `draft_*` tools that produce output artifacts without executing
persistent writes. A draft tool must:
- Accept a structured output target (email, PR description, markdown file, etc.)
- Write only to a local staging location or return the artifact in the mission receipt
- Never call an external send/publish/commit API
- Set `local_only=True` in its capability registration

**Allowed tool frozenset (Tier 2):** All Tier 1 tools plus draft-class tools when defined.
No mutation-capable tools.

**Halt behavior:** Same as Tier 1. Additionally: if a draft tool attempts an external write,
halt and log.

**Implementation gate:** Tier 1 stable and tested. Draft-class tool architecture defined and
reviewed. At least one draft tool implemented (email draft or PR description). Own reviewed
priority lock required.

---

### Tier 3 — Confirmed-Action Missions

Agent executes actions that can mutate state, but each mutation-capable action requires
explicit human confirmation before proceeding. This is a significant architectural change:

1. **ThinkingLoop suspension:** Before calling `self._executor.call_skill()` for any
   mutation-capable tool, ThinkingLoop must pause and emit a confirmation request.
2. **Real approve-action gating:** The `/api/openclaw/approve-action` endpoint is
   restructured — the auto-approve behavior is removed and replaced with a suspension store.
   ThinkingLoop POSTs the proposed action to the endpoint (or an internal equivalent), waits
   for the user's decision, and proceeds only if `decision == "allow"` from a genuine user
   action. If the user denies, the step is logged as denied and the mission either skips the
   step (if configured) or halts.
3. **GovernorMediator integration:** Each proposed mutation-capable tool call routes through
   `GovernorMediator.mediate()` → `Governor.authorize()` → `CapabilityRegistry` before
   the confirmation request is surfaced to the user. If the Governor rejects the action, it
   does not reach the user confirmation step.

**Confirmation timeout:** If no user decision arrives within `approval_timeout_seconds`
(default: 300), the mission halts with `status="approval_timeout"`. It does not proceed
and does not retry automatically.

**Allowed tool frozenset (Tier 3):** All Tier 1 + Tier 2 tools plus whitelisted
mutation-capable tools (defined at lock time). Each mutation tool must have a corresponding
capability ID in `CapabilityRegistry`.

**Halt behavior:** Same as Tier 1/2 plus: approval denied → step logged as denied, mission
halts or skips per `halt_on_denial` config. Approval timeout → halt immediately.

**Implementation gate:** Tier 2 stable. PATCH A and PATCH C on main. Real approve-action
suspension gate designed and reviewed (replaces auto-approve). GovernorMediator call
instrumented inside ThinkingLoop. Own reviewed priority lock required.

---

### Tier 4 — Routine Agents (Scheduled, Envelope-Bounded)

Agents that run on a schedule inside a bounded envelope, with automatic expiry. Nova
Scheduler integration. Mission authorization expires; re-authorization required to renew.

**Key constraints:**
- Routine agents may not expand their own tool allowlist
- Routine agents may not create new agents or new scheduled jobs
- Routine agents may not modify their own expiry or envelope
- Routine agents may not access the scheduler API
- All Tier 4 jobs are user-created; an agent cannot bootstrap a job for itself

**Expiry semantics:**

| Field | Type | Meaning |
|---|---|---|
| `expiry_datetime` | ISO-8601 timestamp | Agent authorization expires at this time; no runs after |
| `max_runs` | integer (optional) | If set, authorization expires after N successful runs |

Re-authorization requires the user to explicitly extend the mission — it is not automatic and
not triggered by the agent.

**Failure and retry behavior:** If a scheduled run fails (executor error, budget exceeded,
etc.), the failure is logged with full budget snapshot. The scheduler does not auto-retry
within the same run window. The next scheduled invocation proceeds normally unless the
failure count exceeds a configured threshold, at which point the mission is paused pending
user review.

**Implementation gate:** Tiers 1–3 stable and tested. Scheduler integration with governed
missions designed and reviewed (distinct from existing `OpenClawAgentScheduler.run_template()`
path). Own reviewed priority lock required.

---

## Nova Mission Control — Concept Spec

Mission Control is the UX surface where users create, monitor, and control governed
autonomous missions. This is a planning concept only — no implementation authorized.

### Mission Definition Fields

These fields align with the existing `TaskEnvelope`/`RunBudgetMeter` architecture to enable
the template path's governed execution model to be applied to mission-based runs.

| Field | Type | Description | Default |
|---|---|---|---|
| `mission_id` | string | Unique ID for audit trail and reference | auto-generated |
| `goal` | string | Plain-language mission goal | (required) |
| `mission_tier` | int (1–4) | Tier governing tool allowlist and confirmation rules | (required) |
| `allowed_tools` | frozenset | Override: subset of tier's permitted tools | Tier default |
| `denied_tools` | frozenset | Additional exclusions beyond tier defaults | none |
| `context` | string (optional) | Human-provided background for the LLM | none |
| `max_steps` | int | Tool-use iteration cap before halt | 10 |
| `max_network_calls` | int | MeteredNetworkProxy envelope | 5 |
| `max_files_touched` | int | Local file access cap | 0 (Tier 1–2) |
| `max_bytes_read` | int | Read budget in bytes | 512 000 |
| `max_bytes_written` | int | Write budget in bytes | 0 (Tier 1–2) |
| `max_time_seconds` | int | Hard wall-clock cap (up to 600) | 120 |
| `draft_only` | bool | No persistent writes even if tool permits | true (Tier 1–2) |
| `approval_required` | bool | Per-mutation-action human confirmation required | true (Tier 3+) |
| `approval_timeout_seconds` | int | Seconds to wait for user confirmation | 300 |
| `halt_on_denial` | bool | Halt mission if user denies an action | true |
| `receipt_format` | enum | `"markdown"` / `"json"` / `"inline"` | `"markdown"` |
| `expiry_datetime` | ISO-8601 | Authorization expiry (Tier 4) | none |
| `max_runs` | int | Max scheduled runs (Tier 4) | none |

### Mission Runtime Outputs

**Live log:** Updated at each step via `_store.update_active_run()` (infrastructure already
exists in `run_goal()`). Each entry records: step number, tools selected, tool results,
budget usage snapshot, timestamp.

**Step receipt:** After each tool call: what tool was proposed, what was executed or skipped,
the result summary, running budget usage. Format: structured dict committed to run store.

**Final receipt:** On halt or completion: goal text, `mission_tier`, `mission_id`,
`status` (`completed` / `failed` / `cancelled` / `approval_timeout`), steps taken, tools
used, budget usage (all five dimensions), output produced, any refusals or skipped steps,
total duration. Committed to `_store.record_run()`. Format controlled by `receipt_format`.

**Human override:** User can halt at any point. `_store.is_cancel_requested()` is already
checked at each step via `_on_step_progress`. Mission does not resume after cancellation
without a new mission submission.

### What Mission Control Does Not Grant

- No sends or publishes (Tier 1–2; Tier 3 requires per-action confirmation)
- No Shopify writes (any tier)
- No autonomous email send (Cap 64 P5) without explicit user action
- No Google connector runtime (any tier)
- No capability expansion by the agent
- No scheduler job creation by the agent (Tier 4 jobs are user-created only)
- No mission envelope modification mid-run by the agent
- No tool allowlist self-expansion by the agent
- No carry-over of authorization from previous missions or sessions

---

## First Governed Autonomy MVP — Repo Guardian

**Type:** Tier 1 read-only mission
**Goal:** Run a targeted read-only inspection of a specified module or doc set, produce a
structured audit receipt, surface findings for human review.

**Why this first:** This is precisely the workflow already in use manually (PASS1–PASS4
audits). It requires only read-only tools. It produces a documented artifact. It does not
require any new tool development — only PATCH A to enforce the allowlist and PATCH C to
enforce the network budget.

**Definitive allowlist for Repo Guardian:**

```python
_REPO_GUARDIAN_ALLOWED_TOOLS = frozenset({
    "memory_search",  # local read — primary tool for file/doc inspection
    "time_query",     # local read — timestamps and date context
    # "web_search" excluded from Repo Guardian by default; add explicitly if external
    #   reference lookup is needed for a specific mission instance
})
```

Network tools (`weather`, `news`, `web_search`) are excluded from the default Repo Guardian
allowlist to minimize external surface. A specific mission instance may add `web_search`
with a `max_network_calls=3` cap if external reference lookup is required.

**Budget envelope for Repo Guardian:**

| Dimension | Value |
|---|---|
| `max_steps` | 8 |
| `max_network_calls` | 0 (3 if web_search added) |
| `max_files_touched` | 0 |
| `max_bytes_read` | 256 000 |
| `max_bytes_written` | 0 |
| `max_time_seconds` | 90 |

**Receipt format:** Markdown. Written to `docs/audits/REPO_GUARDIAN_{timestamp}.md`
(or returned inline; storage path decided at lock time).

**Mission halt conditions:**

| Trigger | Action |
|---|---|
| Step limit (8) reached | Halt, commit partial findings to receipt |
| Time cap (90s) reached | Halt, commit partial findings to receipt |
| Network budget exhausted | Halt, log which call exceeded budget |
| Tool outside allowlist attempted | Impossible by design (filtered_registry); if `KeyError` raised, halt and log |
| `memory_search` returns empty | Log as finding, continue to next step |
| File not found | Log as finding, continue to next step |
| User cancellation | `RunCancelledError`, commit partial receipt as `status="cancelled"` |

**Implementation gate:** PATCH A reviewed, implemented, and tested (rejection tests pass for
`volume`, `brightness`, `media`, `open_webpage`). PATCH C implemented and tested. Repo
Guardian mission type defined with the exact allowlist and budget above. Own reviewed
priority lock required before any implementation begins.

---

## Execution Flow — Governed Mission Inside Existing Architecture

The governed autonomy execution flow extends `run_goal()` to match `run_template()`'s
envelope discipline, while preserving ThinkingLoop's multi-step reasoning capability.

```text
User submits mission via POST /api/openclaw/agent/goal (+ mission envelope fields)
  → run_goal() validates envelope fields (allowlist, budgets, tier)
  → evaluate_mission_envelope(envelope)       — preflight gate; raises if not allowed
  → RunBudgetMeter(envelope)                  — tracks all five dimensions
  → _store.set_active_run()                   — live status visible immediately
  → filtered_registry = self._tool_registry.filtered(allowed=mission.allowed_tools)
      ↑ PATCH A: Only allowlisted tools in registry view
  → loop = ThinkingLoop(registry=filtered_registry, ...)
  → network = MeteredNetworkProxy(delegate=self._network, meter=budget_meter)
      ↑ PATCH C: Network calls metered against max_network_calls envelope
  → await loop.run(goal.strip())
       → ThinkingLoop._reason()
            ↑ LLM prompt: only allowlisted tool names visible
       → ThinkingLoop._select_tools()
            ↑ Only allowlisted tools returned — cannot select excluded tools
       → self._registry.create(tool_name, **kwargs)
       → [Tier 3+] GovernorMediator.mediate() → Governor.authorize() → CapabilityRegistry
            ↑ PATCH B: mutation-capable tools routed through Governor
       → [Tier 3+] suspend: POST internal approve-action request → wait for user decision
            ↑ PATCH B: real gate, not auto-allow
       → self._executor.call_skill(skill, query)
            → RobustExecutor.call_skill()
            → ExecutorSkillAdapter._execute_sync()
            → executor.execute(request)   — same as today but only for allowed tools
       → budget_meter.record_step()       — tracks against max_steps, max_bytes_read, etc.
       → _store.update_active_run()       — live log updated
       → _on_step_progress checks _store.is_cancel_requested() — user override active
  → [halt if any budget dimension exceeded]
  → _store.record_run()                   — full audit record: status, budget_usage, receipt
  → Final receipt returned to user
```

**The principle:** The agent is autonomous in the sense that it continues executing steps
without per-step user input — inside the envelope. The envelope is the governance. The user
defines the envelope before the mission starts. The Governor mediates authority within it
(Tier 3+). The user holds override (cancellation) at every step. The run store records
everything. Nothing happens outside the envelope.

---

## Open Questions and Decisions Required

These questions must be answered at each tier's priority lock review. They are not resolved
by this direction document.

**Architecture:**
1. Should `filtered_registry` be implemented as `ToolRegistry.filtered(allowed: frozenset)`
   returning a view, or as an `allowed_tools` parameter added to `ThinkingLoop.__init__()`
   filtering inside `_select_tools()`? (See PATCH A alternatives in PATCH_ROADMAP.)
2. Should `evaluate_mission_envelope()` be a new function or an extension of the existing
   `evaluate_manual_envelope()` used by the template path?
3. Should `/api/openclaw/agent/goal` accept the full mission envelope fields directly in
   the POST body, or should missions be pre-registered and referenced by `mission_id`?

**Tier 3 / approve-action:**
4. When ThinkingLoop suspends for user confirmation, how does it hold state? (Coroutine
   suspension with asyncio.Event? Polling the suspension store? WebSocket push to UI?)
5. If `halt_on_denial=False` and the user denies an action, does ThinkingLoop attempt an
   alternative tool, or skip the step and continue reasoning?
6. What happens to the approval_timeout if the server restarts mid-mission?

**Tier 4 / scheduler:**
7. Is Tier 4 a new scheduler integration, or does it reuse `OpenClawAgentScheduler` extended
   with mission-envelope support?
8. How is re-authorization presented to the user when `expiry_datetime` is reached?

**Receipt and run store:**
9. Where are Repo Guardian receipts stored — in the run store only, or also written to
   `docs/audits/` as markdown files?
10. Is `mission_id` user-supplied (for naming) or always auto-generated?

---

## What This Document Does Not Authorize

- No runtime expansion of `run_goal()`, `ThinkingLoop`, or `ExecutorSkillAdapter`
- No implementation of `ToolRegistry.filtered()` or the `allowed_tools` parameter
  (PATCH A requires its own reviewed priority lock)
- No implementation of `MeteredNetworkProxy` in `run_goal()` (PATCH C — separate lock)
- No restructuring of the `/api/openclaw/approve-action` endpoint (PATCH B — separate lock)
- No new tool registrations or allowlist changes
- No Mission Control UI implementation
- No scheduler integration (Tier 4)
- No Cap 64 P5 (autonomous email send)
- No Google connector runtime (any tier)
- No OpenClaw capability expansion beyond what PATCH A–D explicitly scope
- No change to `run_template()` or the existing governed template path
- No change to `AGENTS.md` prohibitions — this direction doc is subordinate to AGENTS.md

PATCH A through PATCH D (from PATCH_ROADMAP_2026-05-11.md) are the required preconditions
for any runtime work in this direction. Each patch requires its own reviewed priority lock.
This document establishes approved direction only. No implementation begins until:

1. The relevant governance patches are complete, tested, and merged to main
2. A separate reviewed implementation priority lock is approved for the specific tier

---

## Required Reading Before Any Implementation

1. `docs/audits/PASS4_OPENCLAW_FREEFORM_GOAL_INSPECTION_2026-05-11.md` — confirmed current
   unsafe state: mutation tool reachability, approve-action wiring gap, full execution path
   map with file:line references
2. `docs/audits/PATCH_ROADMAP_2026-05-11.md` — PATCH A–D specs and ordering
3. `docs/audits/PASS1_RUNTIME_AND_OPENCLAW_AUDIT_2026-05-11.md` — deeper runtime audit
   context including scheduler reachability, remote bridge, deprecated direct-run path
4. `AGENTS.md` — active prohibitions; this direction doc does not supersede any line in it
5. `docs/status/CURRENT_WORK_STATUS.md` — current priority state
6. `nova_backend/src/openclaw/agent_runner.py` — `run_template()` (line 194, reference
   governed architecture) and `run_goal()` (line 1137, current ungoverned state)

**No implementation work begins without confirming PATCH A is complete, tested, and on
main. No strong governance-safety claim about the freeform goal path can be made until
PATCH A is implemented, tested, and verified.**

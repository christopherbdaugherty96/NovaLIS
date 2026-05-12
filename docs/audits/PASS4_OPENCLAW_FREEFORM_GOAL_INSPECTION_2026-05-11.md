# PASS 4 — OpenClaw Freeform Goal Governance Inspection

**Date:** 2026-05-11
**Branch:** audit/openclaw-freeform-goal-inspection
**Main HEAD inspected:** 8845fc9
**Audit type:** Read-only inspection. No runtime changes. No capability expansion.
**Source task:** PATCH_ROADMAP_2026-05-11.md item P1-GOV

---

## CURRENT TRUTH

The OpenClaw freeform goal execution path (`run_goal()` → `ThinkingLoop` →
`ExecutorSkillAdapter`) does not traverse `GovernorMediator`, `Governor`,
`CapabilityRegistry`, `SingleActionQueue`, or `ExecuteBoundary`.

Mutation-capable tools (`volume`, `brightness`, `media`, `open_webpage`) are directly
reachable from the freeform goal path with zero governance mediation.

The `/api/openclaw/approve-action` endpoint unconditionally auto-approves all actions
and is not wired into the `run_goal()` execution chain. It does not gate tool execution.

---

## EXECUTION PATH MAP

```text
POST /api/openclaw/agent/goal
  → OpenClawAgentRunner.run_goal()        [agent_runner.py:1137]
      → ThinkingLoop(registry=self._tool_registry, ...)  [agent_runner.py:1154]
           ↑ self._tool_registry is the full ToolRegistry singleton
           ↑ NO allowlist. NO category filter. NO permission check.
      → await loop.run(goal.strip())       [agent_runner.py:1187]
           → ThinkingLoop._reason()        [thinking_loop.py:218]
                ↑ LLM prompt includes: f"Available tools: {', '.join(self._registry.tool_names)}"
                ↑ All registered tools visible to LLM including mutation-capable ones
           → ThinkingLoop._select_tools()  [thinking_loop.py:233]
                available = [t for t in self._registry.tool_names
                             if t not in (failed_tools or set())]
                ↑ Only filter: previously-failed tools. No allowlist.
           → self._registry.create(tool_name, **kwargs)  [thinking_loop.py:138]
           → self._executor.call_skill(skill, query)     [thinking_loop.py:140]
                → RobustExecutor.call_skill()            [robust_executor.py:77]
                     comment line 47: "This does NOT go through Governor"
                → ExecutorSkillAdapter.handle(query)     [executor_adapter.py:56]
                → ExecutorSkillAdapter._execute_sync()   [executor_adapter.py:70]
                     → executor = self._executor_factory()
                     → request = _ActionRequest(capability_id, params, ...)
                     → action_result = executor.execute(request)  [line:77]
                          ↑ DIRECT CALL. No GovernorMediator.
                          ↑ No Governor. No CapabilityRegistry.
                          ↑ No SingleActionQueue. No ExecuteBoundary.
```

---

## GOVERNANCE CHECK

| Layer | In freeform goal path? | Evidence |
|---|---|---|
| GovernorMediator | **NO** | Not imported in agent_runner.py run_goal path |
| Governor | **NO** | Not in ThinkingLoop or ExecutorSkillAdapter |
| CapabilityRegistry | **NO** | Not checked before tool execution |
| SingleActionQueue | **NO** | Not in freeform goal path |
| ExecuteBoundary | **NO** | Not in freeform goal path |
| NetworkMediator | Partial | Injected if wired; provides SSRF/rate-limit but not budget envelope |
| MeteredNetworkProxy | **NO** | `run_goal()` never creates one; template path does |

**robust_executor.py line 47 comment (verbatim):**
`"This does NOT go through Governor — it wraps the raw skill layer. Governor integration lives one level up in the runner."`

There is no such integration in `run_goal()`.

---

## MUTATION TOOL REACHABILITY

All five mutation-capable tools are registered in `tool_registry.py` and visible to
`ThinkingLoop._select_tools()`.

| Tool | Registry line | Category | Classification |
|---|---|---|---|
| `volume` | 211 | "mutation" | **REACHABLE-MUTATION-CAPABLE** |
| `brightness` | 233 | "mutation" | **REACHABLE-MUTATION-CAPABLE** |
| `media` | 255 | "mutation" | **REACHABLE-MUTATION-CAPABLE** |
| `open_webpage` | 279 | "mutation" | **REACHABLE-MUTATION-CAPABLE** |
| `screen_capture` | 299 | "collection" | HARD-BLOCKED (accidental) |

`screen_capture` is blocked at executor level only because `ExecutorSkillAdapter`'s
param_extractor for `screen_capture` is `lambda q: {"command": q}` (tool_registry.py:297),
which never supplies the required `invocation_source` key. `ScreenCaptureExecutor.execute()`
at line 73 rejects the call when `invocation_source` is not in `ALLOWED_INVOCATION_SOURCES`.
This is **not an intentional governance guard** — it is an accidental block from a
missing parameter. Fixing the param_extractor would unblock `screen_capture`.

`volume`, `brightness`, `media`, `open_webpage`: No guard of any kind. The LLM selects
the tool name; `ThinkingLoop` instantiates it via `self._registry.create()`; the executor
runs directly.

---

## APPROVE-ACTION CHECK

**File:** `nova_backend/src/api/openclaw_agent_api.py`
**Handler:** `approve_openclaw_action()` lines 461–509

The handler unconditionally returns:

```python
{
    "ok": True,
    "decision": "allow",
    "approval_state": "auto_allowed",
}
```

Docstring at line 464: `"returns auto-allow for all actions. Future phases will add real
human-in-the-loop suspension and decision flow here."`

**Critical observation:** The `approve-action` endpoint is not wired into the
`run_goal()` → `ThinkingLoop` execution chain. `ThinkingLoop` never calls it before
executing a tool. The endpoint exists as an API surface for future human-in-the-loop
integration but provides neither a gate nor a veto on tool execution in the freeform goal
path. A caller can POST to `/api/openclaw/approve-action` and receive `allow`, but
that response has no effect on what the currently-running ThinkingLoop will execute.

Classification: **REACHABLE-MUTATION-CAPABLE** (the endpoint auto-approves everything
and is not connected to the execution path that would use the decision)

---

## SCHEDULER / REMOTE BRIDGE CHECK

**Scheduler:** HARD-BLOCKED

`run_goal()` and `ThinkingLoop.run()` contain zero references to `OpenClawAgentScheduler`,
`NotificationScheduleStore`, or scheduled job creation. `OpenClawAgentScheduler.run()`
at agent_scheduler.py:201 calls only `self._runner.run_template(...)`, never `run_goal()`.
The freeform goal path cannot trigger scheduled jobs.

**Remote bridge / network:** GOVERNED/MEDIATED — with unmetered gap

Network-capable tools (`weather`, `news`, `web_search`) receive the `network` object
injected into `ThinkingLoop` from `run_goal()`. If `NetworkMediator` is wired in, SSRF
protection and per-call rate limiting apply. However, `run_goal()` never creates a
`MeteredNetworkProxy` or `RunBudgetMeter`. The envelope-budget cap on network call count
that the template path enforces (`MeteredNetworkProxy.record_network_call()`) does not
apply to the freeform goal path. Network calls are mediated but not budget-bounded.

---

## TEST GAPS

No tests exist that:

1. Call `run_goal()` with a goal that attempts to invoke `volume`, `brightness`, `media`,
   or `open_webpage`, and assert the tool is rejected or blocked.
2. Verify `ThinkingLoop._select_tools()` returns a governance-filtered subset (not the
   full registry) in the freeform goal context.
3. Verify `approve-action` is wired into the execution decision before a tool fires.
4. Verify network calls in the freeform goal path are bounded by a call-count envelope.

---

## REQUIRED PATCHES

These patches are required before any implementation work can proceed or before the
freeform goal path can be called governance-safe. Each needs its own reviewed priority
lock to implement.

### PATCH A (highest priority): Allowlist enforcement in run_goal()

**File:** `nova_backend/src/openclaw/agent_runner.py`
**Proposed approach:**

```python
# Before constructing ThinkingLoop in run_goal():
_FREEFORM_GOAL_ALLOWED_TOOLS = frozenset({
    "weather", "news", "web_search", "memory_search", "time_query",
    # add read-only informational tools only
})
filtered_registry = self._tool_registry.filtered(allowed=_FREEFORM_GOAL_ALLOWED_TOOLS)
loop = ThinkingLoop(registry=filtered_registry, ...)
```

`ToolRegistry` needs a `filtered(allowed: frozenset)` method that returns a view
excluding any tool not in the allowlist.

**Alternative:** Add an `allowed_tools: frozenset | None` parameter to `ThinkingLoop`
and filter inside `_select_tools()` before building the candidate list.

**Tests required:**
- `run_goal()` with a goal targeting `volume` → tool not offered to LLM → not executed
- `run_goal()` with a goal targeting `brightness` → same
- `run_goal()` with a goal targeting `open_webpage` → same
- `run_goal()` with a weather goal → executes correctly (allowed)

### PATCH B: Wire approve-action into ThinkingLoop or remove the false safety surface

**Option 1 — Real human-in-the-loop:** Pause `ThinkingLoop` before each tool execution,
POST the proposed action to `/api/openclaw/approve-action` (or an internal equivalent),
wait for a human decision, proceed only if `decision == "allow"` from a real gated source.

**Option 2 — Remove the misleading endpoint:** If human-in-the-loop is not planned for
the freeform goal path, document that `approve-action` is a future stub only, and remove
or clearly label it as non-operational. Do not leave an endpoint that implies governance
gating but provides none.

### PATCH C: Enforce MeteredNetworkProxy in run_goal()

**File:** `nova_backend/src/openclaw/agent_runner.py`
The `run_goal()` method should wrap `self._network` in `MeteredNetworkProxy` with a
conservative call-count envelope (e.g., `max_calls=5`) before passing to `ThinkingLoop`,
matching the budget enforcement already present in the template path.

### PATCH D: Intentional guard for screen_capture

`screen_capture` is currently blocked by a missing parameter rather than a governance
decision. If `screen_capture` should be excluded from the freeform goal path, add it
explicitly to the excluded set in PATCH A's allowlist. Do not rely on the param-extractor
gap as a security control.

---

## FINAL VERDICT

```text
The OpenClaw freeform goal execution path is NOT governance-safe in its current form.

Confirmed live reachable paths:
- volume, brightness, media, open_webpage executors — directly callable via run_goal()
  with no GovernorMediator, Governor, CapabilityRegistry, or any governance layer
- approve-action endpoint — unconditionally approves all actions and is not wired into
  the execution chain that would use the decision
- Network calls — mediated by NetworkMediator (SSRF/rate-limit) but not budget-bounded

Confirmed hard-blocked paths:
- screen_capture — blocked at executor level by missing param (not an intentional guard)
- scheduler — no code path from freeform goal to scheduler
- remote bridge outside NetworkMediator — no direct HTTP client in openclaw modules

This is not a confirmed autonomous exploitation in production.
The freeform goal path (/api/openclaw/agent/goal) requires explicit API invocation.
However, once invoked, mutation-capable tools are reachable with no governance mediation.

Required before implementation work resumes:
1. PATCH A — allowlist enforcement in run_goal() / ThinkingLoop
2. PATCH B — wire or honestly label approve-action
3. PATCH C — enforce MeteredNetworkProxy budget in goal path
4. PATCH D — intentional exclusion of screen_capture

No strong governance-safety claim about the freeform goal path can be made until
PATCH A is implemented and tested.
```

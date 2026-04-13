# Phase 9 — OpenClaw Intelligence Layer Specification

**Created:** 2026-04-07
**Source:** Gap analysis from Copilot sessions (validated), codebase audit
**Status:** IMPLEMENTED — all 10 gaps addressed across commits 8359b33, 0e72e53, and subsequent hardening
**Depends on:** Phase 8 (OpenClaw foundation) — currently active on main

---

## Current State (Phase 8 Foundation)

OpenClaw currently operates as a **linear, template-driven pipeline**:

```
Template ID (e.g. "morning_brief")
  → Fixed tool set (weather + calendar + news)
  → Collect payload (sequential, hardcoded)
  → Summarize once (single LLM pass)
  → Deliver through personality bridge
```

**What works:**
- Governed execution through envelopes and budget meters
- Pause/cancel on active runs
- Failed run recording
- Narrow-envelope safety (no autonomy drift)
- Deterministic morning brief delivery

**What's missing for full agent capability:**
10 distinct components identified below.

---

## Gap Inventory (10 Components)

### RED — Architectural blockers

#### Gap 1: No Tool Execution Layer (Read-Only Agent)

**Current code:** `strict_preflight.py`
```python
MANUAL_FOUNDATION_ALLOWED_TOOLS = frozenset({
    "calendar", "news", "schedules", "summarize", "weather",
})
```

**Problem:** Agent can only *read* data from 5 sources. Cannot execute
state-changing actions (open files, send emails, control devices, create
tasks, trigger automations).

**Required:** Action-capable tool surface gated through Governor capabilities.

---

#### Gap 2: No Multi-Step Reasoning Loop

**Current code:** `agent_runner.py` lines 180-316
```python
async def run_template(self, template_id, ...):
    payload = await self._collect_payload(template_id)
    prompt = self._build_summary_prompt(template, payload)
    summarized = self._summarize_with_local_model(template, prompt)
    return { ... }
```

**Problem:** Linear pipeline — gather, summarize, done. No iteration,
no LLM-guided tool selection, no check-and-retry, no if-then branching
based on results.

**Required:** Iterative thinking loop where LLM evaluates results and
decides next action, bounded by step limits and budget.

**Key constraint:** `llm_gateway.generate_chat()` is **synchronous**.
Any async thinking loop must wrap calls in `asyncio.to_thread()`.

---

#### Gap 3: No Tool Chaining / Composition

**Current code:** `agent_runner.py` lines 414-432
```python
async def _collect_morning_brief_payload(self):
    weather_result = await self._call_skill(WeatherSkill, ...)
    calendar_result = await self._call_skill(CalendarSkill, ...)
    news_result = await self._call_skill(NewsSkill, ...)
    # Tools never interact — no conditional logic based on results
```

**Problem:** Tools run in isolation. Tool A's output cannot flow into
Tool B. No "if weather is rainy, check indoor activities."

**Required:** Sequential/parallel/conditional chain execution with
data flow between steps.

---

#### Gap 5: Hardcoded Tool Discovery

**Current code:** `agent_runner.py` lines 398-412
```python
async def _collect_payload(self, template_id):
    if template_id == "inbox_check":
        raise RuntimeError("Email connector not available")
    if template_id == "evening_digest":
        return await self._collect_evening_digest_payload()
    return await self._collect_morning_brief_payload()
```

**Problem:** Tools are hardcoded per template. Adding a new tool requires
modifying agent_runner.py. No plugin architecture, no dynamic detection.

**Required:** Tool registry with metadata (timeout, cost, permissions,
tags) and runtime discovery.

---

#### Gap 10: Hardcoded Goal Interpretation

**Current code:** `brain_server.py` — 50+ regex patterns for routing
```python
PHASE42_QUERY_RE = ...
CAPABILITY_HELP_RE = ...
TIME_QUERY_RE = ...
```

**Problem:** OpenClaw can only respond to exact template names.
"Give me a brief about work next week" would not route correctly.

**Required:** LLM-guided goal interpretation that maps natural language
to tool selection and parameter generation.

---

### YELLOW — Important but not blocking

#### Gap 4: No Error Recovery / Retry

**Current code:** `agent_runner.py` lines 564-566
```python
try:
    result = await asyncio.wait_for(skill.handle(query), timeout=timeout_seconds)
except Exception:
    return None  # SILENT FAILURE
```

**Problem:** Network error, API rate limit, transient timeout — all
produce silent `None`. No retry, no backoff, no fallback.

**Required:** Retry with backoff, fallback tool selection, cached result
fallback, graceful degradation.

---

#### Gap 6: No Execution Memory / Learning

**Current code:** `OpenClawAgentRunner.__init__` — no history tracking
```python
def __init__(self, ...):
    self._active_budget_meter = None
    self._active_envelope = None
    # No execution history
```

**Problem:** Each run starts from scratch. No learning from previous
attempts, no "this tool was slow yesterday," no optimization over time.

**Required:** Execution history with tool reliability tracking,
optimal ordering recommendations, and cost analysis. Should integrate
with Governor (capability 61 — MemoryGovernanceExecutor).

---

#### Gap 7: No Per-User Tool Permissions

**Current code:** `strict_preflight.py` — global allow list
```python
MANUAL_FOUNDATION_ALLOWED_TOOLS = frozenset({...})  # Global, not per-user
```

**Problem:** All tools are on or off for everyone. Cannot scope
"weather is on for user A, off for user B" or "news limited to 3x/day
for this user."

**Required:** Per-user permission layer integrated with Governor.

---

#### Gap 8: No Per-Tool Budget Tracking

**Current code:** `RunBudgetMeter` tracks generic buckets:
```
steps_used / steps_budget
network_calls_used / network_calls_budget
```

**Problem:** No per-tool cost tracking. Cannot answer "news API costs
$0.05/call, you've spent $5 this month." No rate limit per tool.

**Required:** Per-tool cost, duration, and call-count tracking with
efficiency metrics.

---

#### Gap 9: No Parallel Tool Execution

**Current code:** Skills called sequentially:
```python
weather_result = await self._call_skill(WeatherSkill, ...)   # Wait 5s
calendar_result = await self._call_skill(CalendarSkill, ...)  # Wait 3s
news_result = await self._call_skill(NewsSkill, ...)          # Wait 8s
# Total: 16s (could be 8s with asyncio.gather)
```

**Problem:** Sequential execution doubles/triples latency for no reason.

**Required:** `asyncio.gather` with budget-aware concurrency limits.

---

## Architecture Target

```
Natural Language Goal
  |
  v
Goal Interpreter (LLM-guided)
  |
  v
Tool Registry (dynamic discovery)
  |
  v
Thinking Loop (iterative, bounded)
  |-- LLM reasons about current state
  |-- Selects tools from registry
  |-- Generates parameters (with template fallback)
  |-- Executes via Governor (robust: retry + fallback)
  |-- Evaluates result
  |-- Repeats or terminates
  |
  v
Execution Memory (learns from history)
  |
  v
Governor + Ledger (permissions, budget, audit)
  |
  v
Personality Bridge → Delivery
```

## Key Design Constraints

1. **`llm_gateway.generate_chat()` is synchronous.** All async wrappers
   must use `asyncio.to_thread()` — never `await` the gateway directly.

2. **Governor is the execution authority.** Tools must go through
   `governor.handle_governed_invocation(capability_id, params)`, not
   bypass it.

3. **LLM mode parameter is ignored.** The gateway deletes `mode` and
   `safety_profile`. Use `mode="general"` as convention.

4. **Bounded execution.** Hard limit of 10 steps. Progressive cost
   reduction (full LLM check early, heuristic check late).

5. **Graceful degradation.** If thinking loop fails, fall back to
   existing deterministic briefing pipeline.

6. **Memory through Governor.** Execution records should save through
   capability 61 (MemoryGovernanceExecutor), not bypass to disk.

---

## Implementation Priority

| Priority | Component | Unlocks |
|---|---|---|
| 1 | Tool Registry + Bootstrap | Foundation for all dynamic behavior |
| 2 | Tool Executor (Governor bridge) | Ability to actually run tools |
| 3 | Parallel execution | Immediate latency win, low risk |
| 4 | Error recovery / retry | Reliability improvement |
| 5 | Thinking loop (iterative) | Core intelligence capability |
| 6 | Execution memory | Learning and optimization |
| 7 | Tool chaining | Complex workflows |
| 8 | Goal interpretation | Natural language routing |
| 9 | Per-tool budget tracking | Cost visibility |
| 10 | Per-user permissions | Multi-user readiness |

---

## Implementation Status (as of 2026-04-08)

All 10 gaps have been addressed. Below is the implementation map:

| Gap | Component | Status | Module(s) |
|-----|-----------|--------|-----------|
| 1 | Tool Execution Layer | DONE | `executor_adapter.py` — generic Governor executor-to-skill bridge; 5 executors registered (volume, brightness, media, open_webpage, screen_capture) |
| 2 | Multi-Step Reasoning Loop | DONE | `thinking_loop.py` — iterative LLM-guided loop with phase-based cost reduction (explore/refine/finalize), max 10 steps |
| 3 | Tool Chaining / Composition | DONE | `tool_chain.py` — sequential, parallel, and phased execution with conditions, fallbacks, param_builders |
| 4 | Error Recovery / Retry | DONE | `robust_executor.py` — configurable retry with backoff, timeout, circuit-breaker pattern |
| 5 | Dynamic Tool Discovery | DONE | `tool_registry.py` — metadata-driven registry with 10 tools, tag/category search, runtime discovery |
| 6 | Execution Memory / Learning | DONE | `execution_memory.py` — per-tool reliability tracking, `optimal_order()` wired into ThinkingLoop for tool sorting |
| 7 | Per-User Tool Permissions | DONE | `user_tool_permissions.py` — per-user allow/block with Governor integration |
| 8 | Per-Tool Budget Tracking | DONE | `per_tool_budget.py` — call count, duration, network limits per tool |
| 9 | Parallel Tool Execution | DONE | `tool_chain.py` `run_parallel()` and `run_phased()` with configurable concurrency |
| 10 | Goal Interpretation | DONE | `agent_runner.py` `run_goal()` + `thinking_loop.py` — natural language goal mapped to tools via LLM |

### Additional hardening (post-initial implementation):
- **LLM synthesis**: ThinkingLoop produces coherent natural-language answers from tool results via LLM (with static fallback)
- **Failure history**: Failed tools are excluded from re-selection in subsequent steps
- **Progress tracking**: `run_goal()` registers active runs with the store, supports step-by-step progress updates and cancellation
- **Optimal ordering**: ExecutionMemory.optimal_order() sorts tools by historical reliability/speed before each step

### Test coverage:
- 165 OpenClaw-specific tests passing
- 1082 total tests passing, 0 failures

## Design Principles (Retained)

- Do NOT bypass Governor for tool execution or memory storage
- Do NOT allow unbounded autonomy — all execution is enveloped and budgeted
- Do NOT skip governance for executor-backed tools — all route through capability IDs

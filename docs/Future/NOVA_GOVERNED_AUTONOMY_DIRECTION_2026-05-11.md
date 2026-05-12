# Nova Governed Autonomy — Direction Record

**Date:** 2026-05-11
**Status:** Planning only — direction record. No runtime autonomy expansion authorized by this doc.
**Type:** Future direction / planning record / non-runtime-authority
**Source:** Audit findings from PASS4_OPENCLAW_FREEFORM_GOAL_INSPECTION_2026-05-11.md +
reviewed ChatGPT second-pass recommendation 2026-05-11
**Branch context:** audit/openclaw-freeform-goal-inspection

---

## Core Position

**Autonomous workflows are allowed in Nova — inside Governor-monitored envelopes.**

This is not a reversal of the governance-first posture. It is the natural extension of it.
The Governor's purpose is to gate execution authority. Within a properly bounded mission
envelope — one that routes through GovernorMediator, enforces an allowlist, caps steps and
network calls, and preserves human override — an agent continuing to work autonomously is
exactly what the governance architecture was designed to support.

The current OpenClaw freeform goal path (`run_goal()` → `ThinkingLoop` →
`ExecutorSkillAdapter`) is **not** that architecture. It bypasses GovernorMediator, has no
tool allowlist, and reaches mutation-capable tools with no mediation. That path must be
patched before it qualifies as governed.

Autonomy is approved. Ungoverned execution is not.

---

## What Changed and Why

The PASS4 audit (2026-05-11) confirmed that `run_goal()` passes the full `ToolRegistry`
singleton to `ThinkingLoop` with no allowlist. `ExecutorSkillAdapter._execute_sync()` calls
`executor.execute(request)` directly — no GovernorMediator, no Governor, no
CapabilityRegistry, no SingleActionQueue, no ExecuteBoundary.

`volume`, `brightness`, `media`, and `open_webpage` are reachable. The `approve-action`
endpoint unconditionally returns `auto_allowed` and is not wired into the execution chain.

The fix is not to remove the freeform goal path. The fix is to make it governed — tool
allowlist, network budget, Governor routing — and then build forward from there toward
richer mission types.

---

## Governed Autonomy Model — Four Tiers

Each tier is a separate planning phase. No tier is authorized for runtime implementation
without its own reviewed priority lock.

### Tier 1 — Read-Only Missions (nearest term)

Agent operates with a read-only tool allowlist. No mutations permitted. No sends. No
external writes. Informational and inspection tools only.

**Allowed tool categories (Tier 1):**
- `weather`, `news`, `web_search` — network, mediated by NetworkMediator
- `memory_search` — local read
- `time_query` — local read
- Audit/inspection tools when added

**Blocked at Tier 1:**
- `volume`, `brightness`, `media`, `open_webpage` — mutation-capable, excluded by PATCH A
- `screen_capture` — excluded intentionally (not reliance on param gap)
- Any tool with category "mutation" or "collection" not explicitly listed above

**Example mission (Tier 1):** "Search for recent news about our Shopify store's product
category and summarize findings." Agent runs, stays inside the read-only envelope, produces
a receipt. No human approval required mid-mission. Final receipt surfaced to user.

**Implementation gate:** PATCH A must be implemented and tested before any Tier 1 mission
can be deployed. PATCH A requires its own reviewed priority lock.

---

### Tier 2 — Draft-Only Missions

Agent may produce drafts (email drafts, PR descriptions, plans, issue descriptions) but
cannot send, publish, commit, or post. Draft output is surfaced to the user for review and
explicit action.

**New tool category needed:** `draft_*` tools that produce output artifacts without
executing persistent writes.

Cap 64 (`send_email_draft`) is the architectural model: it produces a local `mailto:` draft,
user initiates send. No SMTP. Tier 2 missions follow this constraint for all output types.

**Implementation gate:** Tier 1 stable. New draft-class tools defined and registered. Own
reviewed priority lock required.

---

### Tier 3 — Confirmed-Action Missions

Agent executes actions that require confirmation. Each mutation-capable action pauses
execution, surfaces the proposed action to the user, and waits for explicit approval before
proceeding. The `approve-action` endpoint is wired into this tier (PATCH B).

**GovernorMediator integration required:** ThinkingLoop must route each proposed tool call
through GovernorMediator → Governor → CapabilityRegistry before execution.

**Implementation gate:** Tier 2 stable. PATCH B complete. PATCH A in place. Governance
routing instrumented through ThinkingLoop. Own reviewed priority lock required.

---

### Tier 4 — Routine Agents (Scheduled / Envelope-Bounded)

Agents that run on a schedule, inside a bounded step/time/network envelope, with automatic
expiry. Nova Scheduler integration. Envelope expires; re-authorization required to renew.

**Key constraint:** Routine agents may not expand their own allowlist. May not create new
agents. May not modify their own expiry. May not access scheduler API to create new jobs.

**Implementation gate:** Tiers 1–3 stable. Scheduler integration designed and reviewed.
Own reviewed priority lock required.

---

## Nova Mission Control — Concept Spec

Mission Control is the UX surface where users create, monitor, and control governed
autonomous missions. This is a planning concept only — no implementation authorized.

### Mission Definition Fields

| Field | Description | Default |
|---|---|---|
| `goal` | Plain-language mission goal | (required) |
| `allowed_tools` | Explicit allowlist (subset of tier's permitted tools) | Tier default |
| `denied_tools` | Additional exclusions beyond tier defaults | none |
| `max_steps` | Maximum tool-use iterations before mission halts | 10 |
| `max_time_seconds` | Hard wall-clock cap | 120 |
| `max_network_calls` | MeteredNetworkProxy envelope | 5 |
| `draft_only` | If true, no persistent writes even if tool allows | true for Tier 1–2 |
| `approval_required` | Per-action human approval required | true for Tier 3+ |
| `expiry` | Mission authorization expiry (Tier 4) | none |

### Mission Runtime Outputs

- **Live log:** Each tool selection, rationale, result — visible in real time
- **Step receipt:** After each step: what was proposed, what was executed, what was skipped
- **Final receipt:** Mission summary: goal, steps taken, tools used, output produced, any
  halts or refusals
- **Human override:** User can halt mission at any point. Mission does not resume without
  re-authorization.

### What Mission Control Does Not Grant

- No sends or publishes (Tier 1–2)
- No Shopify writes
- No Cap 64 P5 (autonomous email send)
- No Google connector runtime
- No capability expansion by the agent
- No scheduler job creation by the agent (Tier 4 jobs are user-created, not agent-created)
- No access to mission envelope modification mid-run

---

## First Governed Autonomy MVP — Repo Guardian

**Type:** Tier 1 read-only mission
**Goal:** Run a targeted inspection of a specified module or doc set, produce an audit
receipt, surface findings for human review.

**Why this first:** It is exactly the workflow already in use (PASS1–PASS4 audits). It
requires only read-only tools. It produces a documented artifact. It does not require new
tool development — only PATCH A to enforce the allowlist and prevent tool leakage.

**Allowed tools:** `memory_search`, `time_query` (no network required for local inspection)
or + `web_search` with MeteredNetworkProxy cap if external references needed.

**Mission halt conditions:**
- Step limit reached
- Time cap reached
- Any tool not in allowlist selected by LLM → mission halts, logs selection, surfaces to user

**Implementation gate:** PATCH A reviewed, implemented, tested. Repo Guardian mission type
defined with explicit allowlist. Own reviewed priority lock required.

---

## Relationship to Existing Governance Architecture

Governed autonomy does not replace the governance architecture — it runs inside it.

```text
User creates mission
  → Mission envelope validated (allowlist, budgets, tier constraints)
  → ThinkingLoop initialized with filtered_registry (PATCH A)
  → ThinkingLoop._select_tools() returns only allowlisted tools
  → LLM prompt shows only allowlisted tools
  → For each tool call:
       → (Tier 3+) GovernorMediator.mediate() → Governor.authorize() → CapabilityRegistry
       → (Tier 1–2) Tool is in allowlist; proceed (mutation risk = zero by allowlist design)
  → MeteredNetworkProxy.record_network_call() enforces network budget (PATCH C)
  → ExecutorSkillAdapter._execute_sync() → executor.execute(request)
  → Step logged to mission receipt
  → If step limit / time cap reached → halt, surface receipt
  → Final receipt returned to user
```

The agent is autonomous in the sense that it continues executing steps without per-step
user input — inside the envelope. The envelope is the governance. The user set the envelope.
The Governor mediates authority within it. The user holds override at all times.

---

## What This Document Does Not Authorize

- No runtime expansion of `run_goal()` or `ThinkingLoop`
- No tool allowlist changes (PATCH A is a separate priority lock)
- No new tool registrations
- No Mission Control UI implementation
- No scheduler integration
- No Cap 64 P5
- No Google connector runtime
- No OpenClaw capability expansion beyond PATCH A–D

PATCH A through PATCH D (from PATCH_ROADMAP_2026-05-11.md) are the preconditions for
any runtime work in this direction. Each requires its own reviewed priority lock.

This document establishes the approved direction only. It is advisory for planning purposes.
No implementation begins until governance patches land and a separate implementation lock
is reviewed and approved.

---

## Required Reading Before Implementation

1. `docs/audits/PASS4_OPENCLAW_FREEFORM_GOAL_INSPECTION_2026-05-11.md` — current unsafe
   state: mutation-capable tool reachability, approve-action wiring gap
2. `docs/audits/PATCH_ROADMAP_2026-05-11.md` — PATCH A–D required patches, in order
3. `AGENTS.md` — active prohibitions and lock requirements
4. `docs/status/CURRENT_WORK_STATUS.md` — current priority state

No implementation work begins without confirming PATCH A is complete, tested, and on main.

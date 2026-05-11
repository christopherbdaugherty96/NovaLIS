# PASS 1 — Runtime / Generated Truth / OpenClaw Audit

Date: 2026-05-11
Branch: `audit/full-repo-doc-code-alignment`
Audit mode: safety-bounded / audit-only

---

# Scope

This pass audited:

- generated runtime truth
- runtime auditor source chain
- capability registry truth
- capability lock truth
- OpenClaw runtime surfaces
- OpenClaw API reachability
- governance boundary consistency

No runtime changes were made.

---

# Confirmed Runtime Truth

Generated runtime source:

```text
scripts/generate_runtime_docs.py
→ nova_backend/src/audit/runtime_auditor.py
→ registry.json + runtime inspection
```

Current generated runtime truth:

```text
Runtime fingerprint: 8fbc67d96b285a2f0d2475156d80631f88ca0ea16813c32034a4b110831a99df
Runtime surface hash: 6c532671bd6b0091781f76bfe779f00b2b41bfd77ac6b19a52c12c2adef5d379
Capability count: 27
Capabilities disabled: []
```

Enabled capability IDs:

```text
16,17,18,19,20,21,22,31,32,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65
```

Generated runtime currently reports:

```text
Phase 3.5 complete
Phase 4 complete
Phase 4.2 complete
Phase 4.5 partial
Phase 5 complete
Phase 6 complete
Phase 7 complete
Phase 8 active
Phase 9 active
```

Important audit note:

```text
Generated runtime truth is code-derived.
The wording is not purely hand-written status prose.
```

---

# Capability Lock Truth

Important audit distinction:

```text
active != certified
active != locked
active != live-signed-off
```

Capability lock state:

```text
Cap 16 — locked / P1-P5 passed
Cap 64 — P1-P4 passed / P5 pending / not locked
Cap 65 — P1-P4 passed / P5 pending / not locked
Most other active capabilities — lock phases pending
```

Audit rule:

Future docs and summaries must avoid implying that all active runtime capabilities are certification-locked.

---

# CapabilityRegistry Findings

`CapabilityRegistry` currently:

- fails closed on missing registry
- fails closed on malformed registry
- fails closed on duplicate capability IDs
- requires governance fields
- validates authority classes
- validates profile/group references
- rejects confirm-risk capabilities without confirmation requirements
- hardcodes:

```text
EXPECTED_PHASE = "8"
```

Potential drift point:

Generated runtime reports Phase 9 active while registry enforcement still expects Phase 8.

Current classification:

```text
Likely naming/documentation drift.
Not yet proven runtime defect.
Needs explicit documentation.
```

Second-pass clarification:

```text
This does not automatically mean the registry is stale.
Phase 8 registry governance and Phase 9 runtime layers may intentionally coexist.
```

---

# OpenClaw Runtime Findings

Confirmed:

OpenClaw is substantially more implemented than earlier continuity summaries implied.

Confirmed runtime surfaces include:

- OpenClawAgentRunner
- ThinkingLoop
- ExecutionMemory
- RobustExecutor
- ToolRegistry
- envelope issuance
- runtime stores
- scheduler support
- cancellation support
- bounded execution budgets
- deterministic fallback summaries
- optional metered OpenAI lane
- governed remote bridge references

Current correct characterization:

```text
OpenClaw has active bounded runtime surfaces.
```

But:

```text
Broad autonomous external execution is NOT proven.
```

Second-pass clarification:

```text
Current evidence supports bounded/manual/semi-governed runtime surfaces.
It does not yet prove unrestricted autonomous computer-use.
```

---

# OpenClaw Two-Lane Execution Split

The audit must distinguish OpenClaw lanes.

## Lane A — bounded manual template lane

`OpenClawAgentRunner.run_template()` appears materially constrained.

Observed controls:

- creates a `TaskEnvelope`
- calls `evaluate_manual_envelope()`
- applies strict preflight
- meters steps
- meters network calls
- meters file reads
- records budget usage
- supports cancellation
- blocks unavailable templates
- records strict preflight details into run records

Current classification:

```text
The bounded manual template lane appears significantly governed and constrained.
```

## Lane B — freeform goal lane

`/api/openclaw/agent/goal` calls:

```text
deps.openclaw_agent_runner.run_goal(...)
```

Tests confirm `run_goal()` exists, returns structured results, records execution memory, records active/recent runs, handles cancellation/failure, and records goal runs using:

```text
template_id == "goal"
```

`ThinkingLoop` is used in the freeform goal path and selects tools from:

```text
registry.tool_names
```

Current classification:

```text
The strongest governance concern is the freeform goal execution lane, not the bounded manual template lane.
```

Unresolved:

```text
The exact run_goal() body still needs direct inspection to confirm whether it filters mutation tools, uses strict preflight, creates an envelope, or routes through Governor/ExecuteBoundary.
```

---

# Pass 2 / 3 Reachability Findings

Confirmed:

```text
The freeform goal lane is real and tested.
```

Evidence from test coverage:

- `run_goal()` rejects empty goals
- `run_goal()` returns structured results
- `run_goal()` records execution memory
- `run_goal()` records active and recent runs
- `run_goal()` handles cancellation
- `run_goal()` handles failures
- `run_goal()` resets per-tool budget between runs
- goal runs are recorded as `template_id == "goal"`

Confirmed from API surface:

```text
/api/openclaw/agent/goal
```

is a live route that calls:

```text
deps.openclaw_agent_runner.run_goal(...)
```

Confirmed from ThinkingLoop:

```text
Tool selection is LLM-guided and based on registry.tool_names.
```

Confirmed from ToolRegistry:

```text
registry.tool_names includes collection/control/mutation tools unless externally filtered.
```

Current unresolved blocker:

```text
The exact body of OpenClawAgentRunner.run_goal() has not yet been extracted in full due to large-file truncation.
```

Current precise classification:

```text
Confirmed live freeform goal lane.
Confirmed LLM-guided tool selection surface.
Confirmed mutation-capable tools exist in registry.
Unconfirmed whether run_goal() filters or blocks those tools before execution.
```

Audit consequence:

```text
Until run_goal() is directly inspected or tested for mutation-tool rejection, freeform goal execution must remain the highest-priority governance follow-up.
```

---

# Critical Governance Finding

`tool_registry.py` registers executor-backed mutation-capable tools:

```text
volume
brightness
media
open_webpage
screen_capture
```

Those tools are wrapped through:

```text
ExecutorSkillAdapter
```

`ExecutorSkillAdapter` directly calls:

```text
executor.execute(request)
```

This path does not visibly traverse:

```text
GovernorMediator
Governor
CapabilityRegistry
SingleActionQueue
ExecuteBoundary
```

This is the strongest governance concern found in Pass 1.

Second-pass clarification:

```text
This is a governance-surface finding, not yet a proven live exploit.
```

The current audit has not yet proven:

- unrestricted public reachability
- unrestricted mutation execution
- unrestricted scheduler-triggered execution
- unrestricted external writes
- unrestricted computer-use

---

# Containment Findings

Manual template path currently appears constrained.

`strict_preflight.py` currently allows only:

```text
calendar
news
project_read
schedules
summarize
weather
```

Manual templates inspected so far also appear limited to read/summary-style tooling.

Strict preflight additionally constrains:

- max steps
- max duration
- network calls
- files touched
- bytes read
- bytes written
- allowed triggers
- hostnames

This reduces current risk exposure for manual template runs.

Second-pass clarification:

```text
The containment findings currently apply primarily to inspected manual template paths.
They are not yet proven to constrain all ThinkingLoop goal execution paths.
```

---

# Reachability Finding

A live goal endpoint exists:

```text
/api/openclaw/agent/goal
```

This endpoint calls:

```text
deps.openclaw_agent_runner.run_goal(...)
```

`ThinkingLoop` selects tools from:

```text
registry.tool_names
```

Meaning:

```text
The LLM-visible tool surface may include mutation-capable executor-backed tools.
```

Current classification:

```text
Potential governance bypass surface.
Likely reachable unless additional restrictions exist in run_goal().
```

Further Pass 2/3 verification still required before declaring an active exploit path.

Second-pass clarification:

```text
The current audit has not yet verified whether run_goal() internally constrains tool categories before execution.
```

---

# Major Governance Escalation

Endpoint:

```text
/api/openclaw/approve-action
```

currently auto-allows actions:

```text
approval_state = auto_allowed
decision = allow
```

Source comment states:

```text
Future phases will add real human-in-the-loop suspension and decision flow here.
```

Current classification:

```text
High-priority governance review item.
```

This does not automatically prove uncontrolled execution because actual reachable action categories still need verification.

But current wording in docs must avoid overstating approval gating guarantees until this path is fully audited.

Second-pass clarification:

```text
The approve-action endpoint is reachable code, not just dead placeholder text.
```

---

# Current Best Grounded Position

Correct:

```text
OpenClaw exists as a real bounded runtime subsystem.
```

Correct:

```text
OpenClaw is more implemented than older continuity summaries implied.
```

Correct:

```text
The bounded manual template lane appears meaningfully constrained.
```

Not yet proven:

```text
Broad autonomous computer-use.
Broad unrestricted external mutation.
Unbounded execution authority.
```

But also unsafe to claim:

```text
All actions still always pass the full GovernorMediator chain.
```

because executor-backed adapter paths currently appear to exist.

Second-pass clarification:

```text
Ledger logging alone is not equivalent to governance enforcement.
```

The audit must continue distinguishing:

```text
logging
tracking
visibility
receipts
```

from:

```text
hard authority boundaries
execution mediation
confirmation enforcement
```

---

# Required Pass 2 / Pass 3 Focus

Next audit focus:

1. exact `OpenClawAgentRunner.run_goal()` body
2. actual tool allowlist enforcement path
3. whether ThinkingLoop can invoke mutation tools live
4. whether strict preflight always gates run_goal()
5. scheduler reachability
6. whether mutation tools can execute without ExecuteBoundary
7. whether ledgering alone is being mistaken for governance
8. whether approve-action is placeholder-only or actually reachable
9. whether runtime docs overstate or understate current authority
10. whether OpenClaw tool execution bypasses capability receipts
11. whether remote bridge surfaces can invoke goal execution
12. whether scheduler paths can invoke unrestricted ThinkingLoop runs
13. whether freeform goal execution should be disabled or read-only-filtered until full governance mediation exists
14. add or inspect tests that force the LLM to select `volume`, `brightness`, `media`, `open_webpage`, or `screen_capture` through `run_goal()` and verify rejection

---

# Current Audit Verdict

```text
No evidence yet of broad uncontrolled autonomy.
```

But:

```text
A real potential governance bypass surface now exists in the audit record.
```

This is currently the highest-priority governance concern identified in the audit.

Second-pass final clarification:

```text
The audit currently supports "potentially reachable governance bypass surface".
It does NOT yet support claiming a confirmed unrestricted autonomous execution vulnerability.
```

Most precise current finding:

```text
Potential governance-bypass-capable surface likely exists specifically within the freeform goal execution path.
The bounded manual template lane appears substantially more constrained.
```

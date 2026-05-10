# Live Daily Workflow Test Plan — 2026-05-10

Priority lock: `docs/status/ACTIVE_PRIORITY_LOCK_2026-05-10_EVERYDAY_UX_FRICTION.md`

This plan defines the minimum workflow set for the Everyday UX Friction baseline.
Each scenario is run against a live Nova instance and results recorded in the evidence
schema below. The goal is not to prove capabilities again — it is to record whether
Nova feels understandable and useful to a normal user.

---

## Framing

```text
Use Nova normally → record friction → improve response/UI behavior → verify no governance drift.
```

Not:

```text
make Nova more human
```

But:

```text
clearer, smoother, less confusing, still governed.
```

---

## Workflow Scenarios

### Scenario 1 — Start Nova

**Prompt:** Open the dashboard. Observe the start screen.

**What to observe:**
- Is the start screen clear?
- Is it obvious what to do next?
- Are there too many buttons or labels?
- Is any system/proof detail visible that a normal user doesn't need?

---

### Scenario 2 — Ask what Nova can do

**Prompt:** `what can you do`

**Expected behavior:** A concise, useful list of Nova's real capabilities. No governance
jargon. No overwhelming detail. A normal person should feel oriented, not confused.

**What to observe:**
- Is the response too long?
- Is it too short to be useful?
- Does it use internal nouns (cap 16, governed, OpenClaw, ledger)?
- Does it accurately reflect what Nova can actually do today?

---

### Scenario 3 — Normal non-capability chat

**Prompt:** `help me plan my day`

**Expected behavior:** A useful, non-robotic response. May ask a clarifying question.
Should not pretend to have calendar access if not configured. Should not be blocked or
unhelpful.

**What to observe:**
- Is the response natural?
- Is there unnecessary governance language?
- Is the clarification question (if any) clear?

---

### Scenario 4 — Current web search

**Prompt:** `search for latest AI news`

**Expected behavior:** Cap 16 routes, Brave results return, search widget appears with
source links. Response synthesizes results briefly.

**What to observe:**
- Does the search widget appear?
- Are sources visible?
- Is the synthesis too long, too short, or unclear?
- Is the "I searched the web" framing honest and readable?

---

### Scenario 5 — News widget

**Prompt:** `show me the news` or `what's happening today`

**Expected behavior:** News widget appears with headlines. Brief summary.

**What to observe:**
- Does the news widget render cleanly?
- Are headlines readable?
- Is the date/freshness visible?
- Is the response framing clear?

---

### Scenario 6 — Weather

**Prompt:** `what's the weather`

**Expected behavior:** Weather widget with current conditions. May ask for location if
not configured.

**What to observe:**
- Does the weather widget appear?
- Is the location assumption stated clearly?
- Is the clarification request (if triggered) sensible?

---

### Scenario 7 — Vague request

**Prompt:** `help me` or `do something useful`

**Expected behavior:** A clarification question, not an error. Should orient the user
toward what they can do with Nova.

**What to observe:**
- Is the clarification question clear and helpful?
- Does it feel robotic?
- Does it inadvertently list too many internal system details?

---

### Scenario 8 — Setup-required state

**Prompt:** `open my email` or `check my calendar`

**Expected behavior:** A clear, honest setup-required message. Not a crash. Not a generic
error. Should tell the user what to set up and why, in plain terms.

**What to observe:**
- Is the setup-required message honest?
- Is it short enough to scan?
- Does it tell the user what to do next?
- Is there any false confidence (pretending it worked)?

---

### Scenario 9 — Blocked / degraded state

**Prompt:** Trigger a degraded response by disconnecting or causing a search failure (or
use a known-degraded prompt).

**Expected behavior:** An honest degraded-state message. No crash. No false result.
Should suggest a recovery path if one exists.

**What to observe:**
- Is the degraded message honest?
- Is it actionable?
- Does the widget appear in degraded state or disappear?

---

### Scenario 10 — Quick action / button

**Prompt:** Click a quick action button or chip visible in the dashboard.

**Expected behavior:** The action triggers the correct behavior. Label matches behavior.
No misleading label.

**What to observe:**
- Are quick action labels clear?
- Do they match what happens when clicked?
- Are there dead chips (visible but do nothing)?
- Are there too many chips?

---

### Scenario 11 — Follow-up question

**Prompt:** After any successful response, ask `tell me more` or `why?`

**Expected behavior:** A useful continuation. Not "I don't know what you mean." Not a
restart. Not a governance block.

**What to observe:**
- Does Nova maintain context across the follow-up?
- Is the follow-up response coherent?
- Does it feel like a real conversation or a disconnected response?

---

### Scenario 12 — Degraded response recovery

**Prompt:** After a failed/degraded response, ask `what went wrong` or `try again`.

**Expected behavior:** An honest explanation and a useful next step. Should not pretend
success. Should not be overly technical.

**What to observe:**
- Does the recovery response make sense?
- Is it honest about what failed?
- Does it suggest something useful?

---

### Scenario 13 — Daily task help

**Prompt:** `what should I do today` or `help me stay on top of things`

**Expected behavior:** A helpful, realistic response. May use daily brief if configured.
May clarify if more context is needed. Should not be blocked or robotic.

**What to observe:**
- Does Nova attempt to help?
- Is the response useful for a real user?
- Is it clear what Nova can and cannot do for daily task management?

---

## Evidence Schema

For each scenario, record:

| Field | Description |
|---|---|
| `prompt` | The exact prompt used |
| `expected_behavior` | What should happen |
| `actual_response` | What actually happened (summary) |
| `ui_state` | What the dashboard showed |
| `friction_observed` | What was confusing, awkward, or unclear |
| `severity` | `low` / `medium` / `high` / `blocker` |
| `proposed_fix` | What should change (wording, UI, routing, etc.) |
| `boundary_impact` | Does the fix touch runtime code, UI, wording only, or nothing? |

---

## Severity guide

| Severity | Meaning |
|---|---|
| `low` | Minor wording issue, cosmetic |
| `medium` | Clearly confusing but not blocking |
| `high` | Meaningfully hurts usability; should be fixed before claiming UX is ready |
| `blocker` | False claim, misleading state, or governance drift; must fix before merging any fix branch |

---

## Boundary constraints

Fixes discovered during this test plan must not:

- add new capabilities
- expand OpenClaw
- add browser/computer-use
- add external writes
- add autonomous workflows

Fixes may touch:

- response wording in `general_chat_runtime.py` or executor synthesis
- dashboard labels, button text, or helper text (JS/HTML only)
- clarification question phrasing
- blocked/setup-required message text
- search widget framing

Any fix that touches runtime routing, Governor logic, capability registry, or executor
behavior requires a separate reviewed branch and must not be bundled into a wording-only fix.

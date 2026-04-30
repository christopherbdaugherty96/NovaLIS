# OpenClaw Environment Model

OpenClaw is an environment, not the brain.

Nova's brain may decide that a task requires an OpenClaw environment, but execution still requires the governed OpenClaw capability path.

OpenClaw must be treated as a controlled execution surface. It is not an autonomous authority layer and must not become a shortcut around Nova's Governor, CapabilityRegistry, ExecuteBoundary, or ledger discipline.

---

## Core Rule

```text
Brain → Run System → Governor → CapabilityRegistry → ExecuteBoundary → OpenClaw → Ledger
```

OpenClaw should never be called directly from chat, general reasoning, or planning output.

A future OpenClaw action must originate from a bounded Run, use a task envelope, pass the governed capability path, and produce proof.

---

## Role Definition

OpenClaw is:

- a governed execution environment
- a browser/computer-use surface
- a bounded capability target
- a source of proof/receipts

OpenClaw is not:

- the Brain
- the planner
- the authority system
- a free-running agent
- a background autonomy loop

---

## Preferred Default

Prefer an isolated OpenClaw-managed browser profile over the user's personal signed-in browser.

Personal browser sessions are higher-risk because they may contain logged-in accounts, cookies, private data, payment methods, account authority, and user identity.

---

## Environment Types

- `openclaw_isolated_browser`
- `personal_browser_session`
- `browser_use_test_browser`
- `remote_browser`

---

## Provision Request Concept

OpenClaw sessions should be treated like temporary sandboxes.

Conceptual schema:

```json
{
  "task_id": "task_123",
  "run_id": "run_123",
  "environment": "openclaw_isolated_browser",
  "required_screenshots": ["before", "after"],
  "max_runtime_seconds": 300,
  "max_steps": 10,
  "allowed_domains": [],
  "allowed_actions": ["open_url", "read_page", "click_navigation_link"],
  "blocked_actions": ["purchase", "send", "delete", "submit_without_confirmation", "login", "enter_credentials"],
  "stop_condition": "Open the approved pages, summarize results, and stop."
}
```

---

## Task Envelope Requirement

No OpenClaw execution should occur without a task envelope.

The envelope should define:

- allowed actions
- blocked actions
- environment scope
- max runtime
- max steps
- allowed domains when relevant
- stop condition
- failure behavior
- required proof

Example:

```text
Task: Research 5 local website prospects.
Allowed: search, open result pages, read public business pages.
Blocked: contact businesses, submit forms, log in, buy tools, scrape at scale.
Limit: 5 results, 5 browser tabs, no account actions.
Stop: after the five prospects are opened/summarized.
```

---

## Step-Based Execution

OpenClaw work should be step-based, not free-running.

Bad pattern:

```text
Go browse and figure it out.
```

Correct pattern:

```text
1. Open the approved search page.
2. Search the approved query.
3. Open up to five public result pages.
4. Summarize each result.
5. Stop.
```

Each execution step should be bounded, reviewable, and eligible for receipt/proof.

A run-level approval should not become unlimited permission for all downstream browser actions.

---

## Proof Requirements

- session started receipt
- task envelope receipt
- screenshot before meaningful action when appropriate
- proposed action preview for sensitive steps
- confirmation where required
- screenshot after action when appropriate
- list of URLs visited when applicable
- blocked-action record if OpenClaw reaches a boundary
- session closed receipt

---

## Personal Browser Rule

A personal browser session may contain logged-in accounts, cookies, private data, and account authority.

It should require explicit user approval and strong proof.

Personal browser execution should be blocked by default until a future policy explicitly permits it for a narrow, bounded use case.

---

## Automation Loop Rule

OpenClaw must not run hidden background loops.

Any repeated OpenClaw use must be:

- scheduled by the user,
- explicitly initiated by the user,
- or proposed by Nova and approved by the user.

Recurring OpenClaw runs require:

- visible schedule
- task envelope
- rate limits
- stop condition
- receipt or summary output
- easy disable control

Blocked by default:

- unapproved continuous browsing
- autonomous publishing loops
- autonomous outreach loops
- autonomous trading loops
- account-action loops

---

## No Persistent Drift

After a governed browser task, the environment should close or be explicitly preserved by user choice.

The default should avoid silent persistent state drift.

---

## First Safe Integration Slice

The first safe OpenClaw integration should not be broad automation.

Recommended first slice:

```text
Planning run → approved read-only OpenClaw sandbox → open/read limited public pages → summarize → stop → receipt
```

Do not begin with:

- personal browser control
- account login
- form submission
- uploads/publishing
- purchases
- background loops
- multi-app automation chains

---

## Current Status

This document defines the OpenClaw environment model and governance expectations.

It does not claim that full Run-based OpenClaw execution, Co-Work page control, background scheduling, personal-browser operation, or broad computer-use workflows are implemented.

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
- a substitute for user approval

---

## Planning vs Execution Boundary

Nova may plan OpenClaw work before execution.

Planning may include:

- identifying whether OpenClaw is the right environment
- drafting a task envelope
- estimating risk
- listing proposed steps
- asking for approval

Planning must not:

- open a browser
- click links
- read live pages through OpenClaw
- enter credentials
- submit forms
- mutate accounts
- preserve browser state silently

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

## Domain and Navigation Scope

OpenClaw should stay inside the approved navigation scope.

The envelope should declare one of:

```text
specific_urls
allowed_domains
search_query_only
manual_user_selected_pages
```

If OpenClaw reaches an unapproved domain, redirect, popup, or embedded third-party flow, it should pause and ask for direction.

Search results are not blanket permission to open unlimited pages.

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

## Approval Granularity

Approval should be proportional to risk.

Low-risk read-only public browsing may be approved as a bounded batch when the task envelope is narrow.

Higher-risk steps require separate approval, including:

- personal browser use
- login or credential entry
- form submission
- file download/upload
- payment or checkout surfaces
- account settings pages
- messaging or outreach
- publishing/uploading content

If a step crosses from read-only into write/account authority, OpenClaw must pause before continuing.

---

## Boundary Detection

OpenClaw must stop or pause when it reaches a boundary not covered by the envelope.

Boundary examples:

- login screen
- checkout/payment page
- upload button
- send/post/submit button
- delete/archive action
- permission prompt
- credential field
- unexpected personal data exposure
- domain outside allowed scope
- modal requesting consent or permissions
- CAPTCHA or bot challenge
- file picker / OS dialog
- download prompt
- extension/install prompt

Default behavior:

```text
pause → summarize boundary → ask user for direction
```

---

## Interruption Behavior

If the user interrupts an OpenClaw run:

- finish only the current safe step if appropriate
- stop immediately if continuing is unsafe
- pause before the next action
- summarize current browser state
- list completed actions
- list remaining actions
- show whether any approval is pending

OpenClaw must not continue because a prior run was approved.

---

## Failure Handling

OpenClaw failures should be explicit and recoverable.

Failure categories should include:

- navigation failure
- timeout
- page changed unexpectedly
- selector/action failure
- blocked boundary reached
- permission prompt reached
- private data exposure
- network failure
- user interruption

Default recovery options:

- retry once if low risk
- skip the step
- narrow scope
- switch to manual instructions
- cancel run

Failures must not silently widen authority or continue with guessed actions.

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
- failure category if a step fails
- session closed receipt

---

## Personal Browser Rule

A personal browser session may contain logged-in accounts, cookies, private data, and account authority.

It should require explicit user approval and strong proof.

Personal browser execution should be blocked by default until a future policy explicitly permits it for a narrow, bounded use case.

---

## Data Handling Rule

OpenClaw should minimize captured data.

It should avoid collecting:

- credentials
- payment details
- private messages
- private account data
- unrelated page content
- unnecessary screenshots

If private data appears unexpectedly, OpenClaw should pause and report the boundary instead of continuing.

---

## Screenshot and Evidence Hygiene

Screenshots are proof, not unlimited surveillance.

Screenshot capture should be:

- tied to a run and step
- minimized to what proves the action
- avoided for sensitive/private pages unless explicitly approved
- redacted or excluded when credentials, payments, private messages, or unrelated personal data are visible

If screenshot proof conflicts with privacy, Nova should prefer a textual receipt and ask for user direction.

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

Preserving a browser session should require a visible user choice and a reason.

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

## Test Expectations

Future implementation should include tests proving:

- no direct chat-to-OpenClaw path exists
- planning output cannot invoke OpenClaw
- OpenClaw requires a Run
- OpenClaw requires a task envelope
- blocked actions pause instead of execute
- login/payment/submit/upload boundaries pause
- unapproved domains pause
- interruption produces a pause summary
- receipts are emitted for start, boundary, failure, and close events
- personal browser execution is blocked by default

---

## Implementation Preconditions

Before expanding OpenClaw beyond planning, Nova should have:

- stable Task Understanding
- stable Task Envelope
- planning-only RunManager
- visible Run Preview / active run display
- pause/cancel semantics
- approval surface or Trust Flow
- receipt output path
- tests proving no direct chat-to-OpenClaw path

---

## Current Status

This document defines the OpenClaw environment model and governance expectations.

It does not claim that full Run-based OpenClaw execution, Co-Work page control, background scheduling, personal-browser operation, or broad computer-use workflows are implemented.

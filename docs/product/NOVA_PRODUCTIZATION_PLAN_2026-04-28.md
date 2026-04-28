# Nova Productization Plan

Date: 2026-04-28

Status: Productization planning doc / not runtime truth / not release-ready claim

Purpose: define how Nova should move from a technically coherent governed local AI system toward something a non-developer can install, understand, trust, and use without overstating current readiness.

---

## Not Release-Ready Warning

This document does **not** mean Nova is product-ready, release-ready, consumer-ready, or business-customer-ready.

This is a planning document. Current runtime truth must still come from live code, generated runtime docs, capability verification records, and the current priority override.

Core warning:

> **Do not confuse a productization plan with product readiness.**

---

## Source Of Truth Rule

When documents conflict, use this order:

```text
1. Live code and generated runtime truth docs
2. Current priority override
3. Consolidated roadmap
4. Capability verification docs
5. Productization / future planning docs
6. Older audit and roadmap notes
```

Primary references:

```text
4-15-26 NEW ROADMAP/CURRENT_PRIORITY_OVERRIDE_2026-04-27.md
4-15-26 NEW ROADMAP/NOVA_CONSOLIDATED_ROADMAP_2026-04-28.md
docs/product/NOVA_RELEASE_READINESS_CHECKLIST_2026-04-28.md
docs/product/USER_READY_STATUS.md
docs/product/CAPABILITY_MATURITY.md
docs/future/NOVA_REQUEST_UNDERSTANDING_REVIEW_CARD_DONE_MEANS_2026-04-28.md
docs/future/NOVA_FAILURE_MODE_PLAYBOOK_2026-04-28.md
docs/future/NOVA_USER_FACING_LANGUAGE_GUIDE_2026-04-28.md
```

---

## Active Priority Note

This is not the current active implementation task.

Current active implementation remains:

```text
Build the RequestUnderstanding trust/action-history review card.
```

Productization should not displace the current trust/action visibility work.

Current sequence:

```text
conversation visibility
→ local capability confidence
→ connector governance
→ OpenClaw hands
→ voice polish
→ broader integrations
→ productization and distribution readiness
```

---

## Current Product Truth

### What Is Real Now

```text
governance-first architecture
capability registry / governed capability concept
generated runtime truth discipline
conversation / RequestUnderstanding foundation
future docs for connectors, OpenClaw, ElevenLabs, MCP, trust spans, sensitive routing, release readiness, and productization
```

### What Is Partial

```text
trust/action-history visibility
voice experience
OpenClaw hands-layer direction
local capability confidence/signoff
governed learning/memory direction
background reasoning direction
connector ecosystem planning
```

### What Is Paused

```text
Cap 64 P5/P6 email live signoff
Shopify / Cap 65 live work
Auralis / website merger
Google connector implementation
ElevenLabs implementation
broad OpenClaw execution
background reasoning jobs
governed learning persistence
CRM/SaaS packaging
installer/productization close-out as the active sprint
```

### What Is Not Ready

```text
mainstream consumer release
fully nontechnical onboarding
broad external connector ecosystem
unreviewed email/calendar/browser writes
fully productized installer path
release-ready support/security process
business-customer mission-critical usage
```

---

## Productization Definition

Nova is productized when a non-developer can:

```text
install it
start it
ask something useful
understand what Nova can do
understand what Nova cannot do
see what Nova did or did not do
recover from common failures
get help or report issues
trust that paused/unsafe actions will not silently run
```

Productization is not only packaging. It includes:

```text
installation
first-run setup
user-facing language
trust visibility
capability labels
failure handling
support path
release readiness
privacy/security clarity
feedback loop
```

Final definition:

> **Productization means making Nova easier to understand and safer to use — not pretending unfinished capabilities are ready.**

---

## Minimum Productized Slice

The first productized slice should be intentionally small.

Minimum useful target:

```text
A user can start Nova, ask a simple or project-status question, see what Nova understood, see whether any action happened, and understand the next safe step.
```

This slice requires:

```text
RequestUnderstanding trust/action card
clear capability labels
known limitations visible
plain-language failure messages for common startup/model paths
no paused work accidentally resumed
no claim of release readiness
```

This slice does **not** require:

```text
Google connectors
ElevenLabs
OpenClaw hands
MCP
browser automation
Home Assistant
full installer polish
business/customer workflows
external writes
```

MVP productization rule:

> **Productize the smallest honest loop first: ask → understand → answer/draft/block → show what did or did not happen.**

---

## Productization Must Not Hide Governance

Productization should simplify the user experience, not hide risk boundaries.

Good productization:

```text
clear capability labels
plain-language failures
visible non-action statements
clean first-run flow
safe defaults
honest limitations
```

Bad productization:

```text
hiding paused work
calling draft-only actions automation
presenting future integrations as live
removing approval visibility to make flow feel smoother
downplaying cloud/sensitive-data movement
```

Core rule:

> **Reduce confusion without reducing governance.**

---

## Target Users / Readiness Levels

### Owner / Developer User

Status:

```text
closest current fit
```

Needs:

```text
repo truth
roadmap clarity
handoff summaries
local start/debug ability
```

### Technical Beta Tester

Status:

```text
possible after trust/action visibility and cleaner setup guidance
```

Needs:

```text
clear setup instructions
known limitations
issue reporting path
capability labels
```

### Semi-Technical Early Adopter

Status:

```text
future after first-run clarity and local capability confidence
```

Needs:

```text
installer or guided setup
plain-language errors
visible trust/action history
basic support path
```

### Nontechnical Mainstream User

Status:

```text
not ready
```

Needs:

```text
one-click install
stable onboarding
polished UI
safe defaults
support/recovery path
```

### Business Customer

Status:

```text
not ready for mission-critical usage
```

Needs:

```text
support model
privacy/security docs
connector governance
clear SLAs or no-SLA disclaimer
release readiness checklist
stable approval flows
```

---

## Productization Gates

### Gate 1 — Trust Visibility

Must be true:

```text
RequestUnderstanding trust/action card visible
non-action statements appear where relevant
paused work remains paused
user can tell whether Nova answered, drafted, proposed, blocked, or acted
```

### Gate 2 — Local Capability Confidence

Must be true:

```text
local capability signoff matrix started
advertised local capabilities have evidence
failure behavior documented
capability labels match reality
```

### Gate 3 — First-Run Understandability

Must be true:

```text
user sees what Nova is
user sees what is available now
user sees what is paused/future
starter prompts are safe and useful
startup errors are understandable
```

### Gate 4 — Failure And Recovery

Must be true:

```text
common failure messages are plain-language
safe fallback behavior exists
no raw stack traces to normal users
non-action statements are used
support/reporting path exists
```

### Gate 5 — Release Readiness

Must be true:

```text
release readiness checklist mostly satisfied
runtime truth docs current
known limitations visible
security/privacy docs available
no paused/future work presented as live
```

---

## Product Surfaces To Improve

```text
README
Quickstart
first-run screen
dashboard / home screen
trust/action-history panel
settings / connections
capability status view
known limitations page
support / issue templates
release notes / changelog
privacy/security docs
installer/startup diagnostics
```

Each surface should answer:

```text
What can Nova do now?
What is read-only?
What is draft-only?
What requires approval?
What is paused?
What is future only?
What happened last?
What did not happen?
```

---

## Productization Roadmap

### Stage 1 — Trust-Visible Alpha

Exit criteria:

```text
RequestUnderstanding trust/action card visible
basic conversation live checks pass
paused work remains paused
known limitations visible
failure messages improved for common paths
```

### Stage 2 — Local Capability Confidence

Exit criteria:

```text
local capability signoff matrix started
advertised local capabilities have evidence
failure behavior documented
capability labels match reality
```

### Stage 3 — Guided First-Run Beta

Exit criteria:

```text
startup diagnostics visible
first-run starter prompts available
user-ready status doc updated
release readiness checklist partially satisfied
clean machine setup path documented
```

### Stage 4 — Connector-Aware Beta

Exit criteria:

```text
connector registry foundation exists
Google/email direction resolved
read-only connectors labeled clearly
approval requirements visible
sensitive-data routing policy visible
```

### Stage 5 — Broader Product Readiness

Exit criteria:

```text
clean VM install tested
support path exists
privacy/security docs visible
known limitations clear
changelog/release process exists
beta feedback loop active
release readiness checklist mostly satisfied
```

---

## Productization Metrics

Track later:

```text
time to first useful response
first-run success rate
user confusion count
number of support-blocking setup issues
capability label accuracy
trust/action card visibility rate
beta tester return rate
startup time
first response latency
failure recovery success rate
```

Beta questions:

```text
What was confusing?
What was valuable?
Would you use Nova again tomorrow?
What did you expect to happen that did not?
What would make you recommend Nova to someone else?
```

---

## Product Docs To Keep Current

```text
docs/product/USER_READY_STATUS.md
docs/product/CAPABILITY_MATURITY.md
docs/product/NOVA_RELEASE_READINESS_CHECKLIST_2026-04-28.md
docs/product/NOVA_PRODUCTIZATION_PLAN_2026-04-28.md
docs/future/NOVA_USER_FACING_LANGUAGE_GUIDE_2026-04-28.md
docs/future/NOVA_FAILURE_MODE_PLAYBOOK_2026-04-28.md
docs/future/NOVA_REQUEST_UNDERSTANDING_REVIEW_CARD_DONE_MEANS_2026-04-28.md
4-15-26 NEW ROADMAP/NOVA_CONSOLIDATED_ROADMAP_2026-04-28.md
```

---

## Do Not Productize By Overclaiming

Avoid claims like:

```text
fully autonomous assistant
production-ready business operator
fully voice-first product
email/calendar automation ready
OpenClaw hands are live and safe
Google integration complete
mainstream installer ready
release-ready
```

unless current runtime truth and verification support them.

Preferred phrasing:

```text
governance-first local AI system
governed local assistant under active development
local-first system with visible action boundaries
read-heavy capabilities with bounded local actions
future connector and voice plans documented but not broadly implemented
```

---

## Release Readiness Relationship

This productization plan describes the direction.

The release checklist decides whether broader testing/release is honest:

```text
docs/product/NOVA_RELEASE_READINESS_CHECKLIST_2026-04-28.md
```

If the release checklist fails, Nova should not be called release-ready even if this productization plan exists.

---

## Final Rule

> **Productization means reducing user confusion without reducing governance.**

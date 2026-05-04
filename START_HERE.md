# Start Here

Last reviewed: 2026-05-03

This is the shortest human path through NovaLIS.

Nova is a governance-first local AI system. It is designed to separate intelligence from execution so useful actions can stay bounded, visible, and reviewable.

Nova is currently an alpha build for technical users and early adopters. It is not a finished consumer product.

---

## The Fast Path

1. Read this page.
2. Follow [Quickstart](QUICKSTART.md).
3. Run Nova locally.
4. Try the commands in [First 5 Minutes](docs/product/FIRST_5_MINUTES.md).
5. Check [What Works Today](docs/product/WHAT_WORKS_TODAY.md).
6. Read the [Conversation and Memory Model](docs/product/CONVERSATION_AND_MEMORY_MODEL.md).
7. Check [Known Limitations](docs/product/KNOWN_LIMITATIONS.md).

Use generated runtime truth docs for exact current capability status:

- [Current Runtime State](docs/current_runtime/CURRENT_RUNTIME_STATE.md)
- [Runtime Capability Reference](docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md)
- [Governance Matrix](docs/current_runtime/GOVERNANCE_MATRIX.md)

---

## What To Look For First

Do not evaluate Nova only by feature count.

Evaluate whether it makes these things clear:

- What the user asked for
- What Nova thinks the request means
- Whether a real action is involved
- Which capability is allowed to act
- Whether the action is bounded or blocked
- Whether the result is visible and reviewable

Nova now has Action Receipts and a Trust Receipt API for inspecting governed-action outcomes. A fuller Trust Review Card / Trust Panel remains future work.

---

## Best First Commands

Try these after startup:

1. `What works today?`
2. `Explain what Nova can do.`
3. `What capabilities are active?`
4. `Summarize today's news.`
5. `Draft an email to test@example.com about tomorrow.`
6. `remember: My preferred tone is concise.`
7. `review memories`
8. `Plan my week`

Notes:
- Memory commands are explicit and receipted.
- Plan My Week produces a proposal and records approval decisions.
- Neither memory nor planning executes real-world actions.
- Email draft opens a local mail client; Nova does not send email.

---

## Best Reading Order

For a first-time visitor:

1. [README](README.md)
2. [Quickstart](QUICKSTART.md)
3. [First 5 Minutes](docs/product/FIRST_5_MINUTES.md)
4. [Try These Commands](docs/product/TRY_THESE_COMMANDS.md)
5. [What Works Today](docs/product/WHAT_WORKS_TODAY.md)
6. [Conversation and Memory Model](docs/product/CONVERSATION_AND_MEMORY_MODEL.md)
7. [Capability Signoff Matrix](docs/product/CAPABILITY_SIGNOFF_MATRIX.md)
8. [Known Limitations](docs/product/KNOWN_LIMITATIONS.md)
9. [Documentation Index](docs/INDEX.md)

For implementation detail:

- [Governed System Architecture](docs/product/GOVERNED_SYSTEM_ARCHITECTURE.md)
- [Current Runtime State](docs/current_runtime/CURRENT_RUNTIME_STATE.md)
- [Governance Matrix](docs/current_runtime/GOVERNANCE_MATRIX.md)

---

## Current Brutal Truth

Nova now has a strong governed reasoning and workflow substrate:

- explicit memory loop (receipted, user-controlled)
- bounded Context Pack (labeled, filtered, conflict-aware)
- Brain Mode contracts and trace (non-authorizing)
- RoutineGraph (Daily Brief)
- Plan My Week (proposal + approval record)

However:

- plans do not execute actions
- routines do not automate workflows
- Brain Mode is not visible in UI
- Context Pack is mostly invisible to users
- there is no unified workflow dashboard yet

The bottleneck is no longer core architecture.

The bottleneck is:
- making the system visible
- proving value through one clear workflow
- improving onboarding and setup
- strengthening trust UI and proof surfaces

---

## What Nova Is Right Now

A governed reasoning system with structured workflows that do not yet execute real-world actions.

---

## What Nova Is Not Yet

- not an autonomous agent
- not a workflow automation system
- not a polished daily-use product

---

## What Comes Next

The next step is not more internal architecture.

The next step is:

> build one visible workflow that proves Nova is useful

Example direction:
- daily operator dashboard
- plan → review → approve → follow-up flow
- small business workflow (Auralis direction)

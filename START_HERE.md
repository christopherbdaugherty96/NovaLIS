# Start Here

Last reviewed: 2026-08-25

This is the shortest human path through NovaLIS.

Nova is a local-first, governed awareness and decision-support system that maintains context,
identifies what matters, reduces uncertainty, and coordinates authorized tools only when evidence
and authority justify action.

Nova is currently an alpha build for technical users and early adopters. It is not a finished
consumer product. For current work state and authority boundaries, see the
[Daily Command Center](docs/status/DAILY_COMMAND_CENTER.md).

---

## Current Truth First

Before the fast path below, use this recommended reading order:

1. [Canonical Truth Index](docs/CANONICAL/00_INDEX.md) — how to read repo truth
2. [Daily Command Center](docs/status/DAILY_COMMAND_CENTER.md) — where the project is right now
3. [Capability Inventory](docs/capability_verification/CAPABILITY_INVENTORY.md) — what verifiably works
4. [Product Definition](docs/product/PRODUCT_DEFINITION.md) — identity, mission, phases
5. [Current Runtime State](docs/current_runtime/CURRENT_RUNTIME_STATE.md) — generated runtime truth

If any doc below conflicts with these, resolve by CANONICAL truth rules; for runtime-existence
claims, generated runtime docs win.

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

Use its permanent architectural model:

```text
Awareness -> Decision -> Authority -> Execution -> Outcome
```

Capability describes what the runtime can technically do; it does not grant permission.

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

## Current Grounded Truth

Nova has a real governed runtime and verified awareness surfaces:

- conversational interaction and frontend/backend WebSocket communication
- governed information retrieval, weather, news, calendar, arithmetic, and morning awareness
- capability registry, authority checks, receipts, runtime-truth generation, and drift verification
- bounded/manual-first OpenClaw runtime surfaces, without broad autonomous authority
- Authorization Integrity Slice 1 merged through PR #325
- Wave C proof and stabilization complete with immutable validated baseline
  `ec20a7146f7d6d55b8983cb7d6d3918d5fad9915`

Current repository HEAD is a moving Git fact and should be resolved from Git when needed rather
than treated as an immutable value in this document.

However:

- Nova is not a finished continuously reliable consumer product
- PR #335 Google Workspace Foundation reconciliation remains Post-Wave-C, separate, and not authorized by this page
- Google domain-data access is not active
- Operational Continuity is strategically accepted but implementation-inactive
- hosted GitHub Actions remain `NOT EXECUTED` under Issue #354; that evidence source was waived for Wave C without being called PASS
- economic, browser/computer-use, financial-write, outreach, posting, contracting,
  autonomous-business, and delegation lanes remain inactive

Do not infer permission from capability, a roadmap, memory, prior approval, OAuth scope, connection
state, or historical implementation.

---

## What Nova Is Right Now

A local-first governed awareness and decision-support system with real runtime capabilities and
explicit authority boundaries. It can reason, recommend, and use currently governed surfaces; it
is not authorized to pursue broad goals or expand its own authority.

---

## What Nova Is Not Yet

- not an autonomous agent
- not a finished persistent personal operations system
- not a polished mainstream consumer product

---

## What Comes Next

Current ordered direction:

1. Post-Wave-C Google Workspace Foundation reconciliation — next, separately authorized work.
2. If that foundation is separately reviewed and merged, run Google identity-only live proof.
3. Build and prove Google Tasks READ as the first provider-backed Google evidence vertical under its own authorization.
4. Prove source identity, provenance, freshness, privacy, and truthful degradation for that evidence.
5. Only then warrant, scope, authorize, and prove a minimal Operational Continuity Slice 1.
6. Run the planned 7–14 day owner Continuity proof.
7. After credible owner proof, run the planned 3–10 external-user pilot.
8. Use that evidence to justify beta-readiness/productization work before any public downloadable beta.

Public beta remains a future productization gate, not current implementation authority. Google
writes, Gmail/Calendar/Drive expansion, broader autonomy, and later external actions remain
separately scoped and separately authorized.

This page records the navigation path and current boundary. It does not activate any lane.

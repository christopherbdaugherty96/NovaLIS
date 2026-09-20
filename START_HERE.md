# Start Here

Last reviewed: 2026-09-20

This is the shortest human path through NovaLIS.

Nova is a local-first, governed awareness and decision-support system that maintains context,
identifies what matters, reduces uncertainty, and coordinates authorized tools only when evidence
and authority justify action.

Nova is currently an alpha build for technical users and early adopters. It is not a finished
consumer product. For current work state and authority boundaries, see the
[Daily Command Center](docs/status/DAILY_COMMAND_CENTER.md).

## Current post-#405 beta-readiness order — 2026-09-20

```text
BETA_READINESS_SEQUENCE_V1: ACTIVE
verified main after Lane 5A authority foundation: 3a3e9d332c6b744dcea0fef9d3532e5fcde60e51
#397 through #405: COMPLETE / MERGED
COMPLETE: #406 governed-memory ID collision correctness (PR #411; main `ca66a06d`)
COMPLETE: #408 durability/state-ownership decision (PR #412; main `2592ad91`)
COMPLETE: durability implementation lane 1 - canonical state registry/migration detection (PR #413; main `e74fdca0`)
COMPLETE: durability implementation lane 2 - corruption-safe readers (PR #416; main `80e1c86f`)
COMPLETE: durability implementation lane 3 - maintenance locking + mutation quiescence (PR #419; main `2bfe202e`)
COMPLETE: durability implementation lane 4 - versioned snapshot + manifest (PR #421; main `4e32b501`)
FRESH-MAIN CLOSEOUT: PASS (314 focused durability/operational-truth tests passed; 1 expected Windows POSIX-FIFO skip; runtime structural smoke PASS)
COMPLETE: #409 release integrity / repository control (PR #423; main `aa39515f`)
COMPLETE: #410 private-beta freeze criteria (PR #410; main `3ad3f544`)
AUTHORIZED / ACTIVE: Lane 5A recovery construction (owner authorization; base main `3ad3f544`)
COMPLETE: Lane 5A step 1 - inactive recovery candidate migration (PR #424; main `298b7731`)
MIGRATION PROOF: PASS (173 durability tests passed; 1 expected Windows POSIX-FIFO skip)
COMPLETE: Lane 5A step 2 - recovery candidate validation (PR #426; main `9de640cd`)
VALIDATION PROOF: PASS (184 durability tests passed; 1 expected Windows POSIX-FIFO skip)
COMPLETE: Lane 5A step 3 - controlled recovery activation (PR #427; main `678dda6c`)
ACTIVATION PROOF: PASS (192 durability tests passed; 1 expected Windows POSIX-FIFO skip)
COMPLETE: Lane 5A authority-foundation correction (PR #428; main `3a3e9d33`)
AUTHORITY FOUNDATION PROOF: PASS (201 durability tests passed; 1 expected Windows POSIX-FIFO skip)
RECOVERY AUTHORITY MODEL: dual-slot highest-valid-generation selection
NEXT: rollback/restore proof
THEN: bounded beta product-translation/readiness pass
THEN: clean Windows operator proof
THEN: frozen-SHA full beta acceptance
THEN: private-beta candidacy/distribution decision
```

Google/provider expansion remains paused. Operational Continuity implementation remains paused.
New capabilities remain paused. Voice expansion remains paused. Broader UI work remains paused.
Other feature expansion remains paused. This current order supersedes older ordering language below and
grants no new capability or authority.

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
- stabilization Waves A1, A2, B1, B2, B3, B4, and Wave C are complete and merged
- immutable Wave C validated runtime baseline: `ec20a7146f7d6d55b8983cb7d6d3918d5fad9915`

However:

- Nova is not a finished continuously reliable consumer product
- GitHub-hosted Wave C jobs remain `NOT EXECUTED` under the external account/billing limitation in Issue #354; the owner waived that source as mandatory Wave C exit evidence without calling it PASS
- `POST-WAVE-C DOCUMENTATION CLOSEOUT: COMPLETE`; truth/checker hardening is merged through PR #385
- PR #366 truth-hygiene provenance: MERGED
- PR #378 narration/front-door package: MERGED / VERIFIED
- #388: COMPLETE / TRUTH-CHECKER PREREQUISITE SATISFIED
- #368: NEXT BOUNDED TECHNICAL LANE
- #387: AFTER #368 / DOCS-ONLY
- PR #335 reconstruction: PENDING SEPARATE OWNER DECISION / NOT AUTHORIZED
- PR #335 remains draft/unmerged historical Google Foundation/auth/identity code and is not a current Nova capability
- Google Tasks, Gmail, Calendar OAuth/domain data, Drive, Docs, and Sheets are not current Nova capabilities through PR #335
- Operational Continuity is strategically accepted but implementation-inactive and non-authorizing
- economic, browser/computer-use, financial-write, outreach, posting, contracting,
  autonomous-business, and broad delegation lanes remain inactive

Do not infer permission from capability, a roadmap, memory, prior approval, OAuth scope, connection state, or a future issue/PR.

---

## What Nova Is Right Now

A local-first governed awareness and decision-support system with real runtime capabilities and
explicit authority boundaries. It can reason, recommend, and use currently governed surfaces; it
is not authorized to pursue broad goals or expand its own authority.

---

## What Nova Is Not Yet

- not an autonomous agent
- not a broad workflow automation system
- not a polished daily-use product
- not a Google Workspace personal-operations layer yet
- not an implemented Operational Continuity system

---

## Current Decision Sequence

The documentation prerequisite is complete. The current sequence is:

1. Issue #388 is COMPLETE; its TRUTH-CHECKER PREREQUISITE is SATISFIED.
2. Issue #368 is the NEXT BOUNDED TECHNICAL LANE.
3. Issue #387 is AFTER #368 / DOCS-ONLY.
4. PR #335 reconstruction remains PENDING SEPARATE OWNER DECISION / NOT AUTHORIZED.
5. The owner may later decide whether to authorize reconstruction/reconciliation of PR #335 against exact validated baseline `ec20a7146f7d6d55b8983cb7d6d3918d5fad9915`.
6. If separately authorized, harden the bounded #335 OAuth/identity lifecycle defects, perform exact-head verification, and complete an independent security/architecture review.
7. Make the #335 merge decision separately.
8. Prove Google identity-only connection live without treating OAuth scope as Nova authority.
9. Add Google Tasks READ as the first provider-backed Google evidence vertical and prove provenance/freshness/evidence boundaries.
10. Only then evaluate an evidence-based Operational Continuity implementation warrant.

This page records the navigation path and durable boundary. It does not activate any lane.

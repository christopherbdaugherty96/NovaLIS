# Nova Roadmap Handoff — 2026-07-25

## Purpose

This file converts the 2026-07-25 strategy session into a concise roadmap handoff.

It does not authorize implementation. It identifies where the session decisions should be incorporated when the owner next approves a documentation or implementation lane.

---

## Canonical Files

Ordering authority:

- `docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md`

Active work truth:

- `docs/todo/ACTIVE_TODO.md`
- `docs/status/DAILY_COMMAND_CENTER.md`
- `docs/status/CURRENT_WORK_STATUS.md`

Existing email design sources:

- `docs/future/EMAIL_COORDINATION_BOARD.md`
- `docs/future/NOVA_GOOGLE_CONNECTOR_MODEL.md`
- `docs/future/GOOGLE_WORKSPACE_CONNECTOR_PLAN.md`

Session record:

- `2026-07-25_NOVA_DIRECTION_SESSION/README.md`

---

## Roadmap Candidate To Add

### Multi-Account Email Awareness

```text
Unified read-only awareness across separately governed personal,
employment, and business email identities.

Gmail read-only first.
Multiple Gmail identities second.
Microsoft 365/Outlook later.
Generic IMAP only if evidence justifies it.

Every message, thread, summary, action, and draft retains source account.
Permissions remain per account.
Wrong-account drafting or sending is blocked.
Sensitive content follows visible local-only or ask-first routing.
Cross-account awareness does not automatically become long-term memory.
```

Status:

```text
Observation-driven future candidate.
Not authorized for implementation by this file.
```

---

## Recommended Active TODO Wording

Current conceptual order:

```text
Google Tasks -> Gmail -> Traffic
```

Recommended clarified order:

```text
Google Tasks / Reminders
-> Multi-Account Email Awareness
   - one Gmail account, read-only
   - multiple Gmail identities
   - personal/work/business role separation
   - unified awareness with permanent provenance
   - prepared drafts only after read path is proven
-> Traffic / leave-time awareness
```

---

## Dedicated Design Document To Create Before Implementation

Proposed path:

`docs/future/NOVA_MULTI_ACCOUNT_EMAIL_AWARENESS_PLAN.md`

Required sections:

- account registry schema;
- account-role taxonomy;
- per-account OAuth scopes;
- provider adapter contract;
- normalized message and thread schemas;
- account-level permission policy;
- unified awareness output;
- cross-account entity correlation;
- wrong-account blocking;
- privacy and sensitive-data routing;
- memory promotion rules;
- receipts and provenance;
- degraded behavior;
- capability contracts;
- negative/adversarial tests;
- phased acceptance gates.

---

## Capability Sequence

Read and awareness:

```text
EMAIL_ACCOUNT_CONNECT
EMAIL_ACCOUNT_LIST
EMAIL_MESSAGE_SEARCH
EMAIL_THREAD_READ
EMAIL_AWARENESS_SUMMARY
EMAIL_CROSS_ACCOUNT_CORRELATE
```

Preparation:

```text
EMAIL_DRAFT_PREPARE
EMAIL_DRAFT_REVIEW
```

Later independently governed effects:

```text
EMAIL_SEND_CONFIRMED
EMAIL_ARCHIVE_CONFIRMED
EMAIL_LABEL_MODIFY_CONFIRMED
```

Do not combine these into one broad email capability.

---

## First-Lane Acceptance Requirements

### Account safety

- Every item retains `account_id`.
- Account identity is visible in every email result.
- Permissions granted to one account do not apply to another.
- Personal, employment, and business roles remain separate.
- Wrong-account draft selection is blocked.

### Privacy

- OAuth tokens never enter repository files, prompts, memory, logs, or receipts.
- Sensitive email defaults to local-only or ask-first provider routing.
- Cross-account reasoning context is not silently promoted into long-term memory.
- Every inferred relationship exposes source evidence and confidence.

### Reliability

- One failing mailbox does not break the other accounts.
- Expired OAuth produces a clear reconnect state.
- Partial results remain usable and visibly degraded.
- Repeated reads do not duplicate stored items or receipts.
- Timeouts do not poison the next request.

### Authority

- Read access does not authorize drafting.
- Drafting does not authorize sending.
- Memory does not authorize account access or external effects.
- No background monitoring unless a separate approved routine exists.

---

## Broader Improvement Order Preserved From Session

```text
1. Reliability and recovery
2. Startup and interaction latency
3. One calm daily operating surface
4. Tasks and reminders
5. Multi-account email awareness
6. Traffic and leave-time awareness
7. Structured world model
8. Prepared-action and approval inbox
9. Shadow mode
10. Cross-platform installation
11. Narrow earned autonomy
```

---

## Do Not Prioritize Ahead of This

- more agents for their own sake;
- more model providers without measured need;
- broad OpenClaw execution;
- autonomous email sending;
- autonomous social posting;
- browser/computer-use expansion;
- larger technical dashboard;
- vector database without a defined retrieval problem;
- silent memory promotion;
- silent cloud routing of sensitive data;
- new roadmap documents that compete with the canonical master roadmap.

---

## Definition To Preserve

```text
Nova is an awareness and governed orchestration platform.
It is not merely an API wrapper.
OpenClaw is an internal bounded subsystem, not Nova's authority layer.

Nova becomes more powerful by becoming more reliable, context-aware,
prepared, measurable, and useful — not simply by acquiring more tools.
```

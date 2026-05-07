# Auralis Digital Client Intake OS — Agreed Decision

Last updated: 2026-05-06

Status: agreed future integration boundary.

Primary docs:

- `docs/future/AURALIS_DIGITAL_CLIENT_INTAKE_OS.md`
- `docs/future/AURALIS_DIGITAL_CLIENT_INTAKE_OS_SECOND_PASS.md`

---

## Agreement

Auralis Digital should build the client intake system first as a structured form-first workflow.

NovaLIS should not implement this as a public chatbot, live lead system, connector expansion, or autonomous business automation right now.

The agreed future role for Nova is internal and governed:

```text
Auralis structured lead record
→ Nova review card
→ lead summary
→ missing-info check
→ likely route/package recommendation
→ draft follow-up
→ user approval
→ manual or governed next step
```

---

## What Is Agreed

1. The Auralis intake idea is valid.
2. The first Auralis implementation should be form-first, not AI-chat-first.
3. Nova should not be the public-facing Auralis website chatbot at this stage.
4. Nova may later help internally with lead summaries, missing-info checks, package recommendations, and draft follow-ups.
5. Nova must not send, quote, schedule, charge, or commit without explicit governed authority.
6. Drafting and sending must stay separate.
7. Recommendations and execution must stay separate.
8. Read/reasoning paths and write/action paths must stay separate.
9. Any future implementation must respect review cards, capability boundaries, approval gates, receipts, and generated runtime truth.
10. The concept remains future-only unless it directly supports a safe read-only proof under the active priority lock.

---

## Current NovaLIS Boundary

Current status:

```text
Future concept only.
No runtime implementation.
No new capability.
No connector expansion.
No business automation expansion.
```

This document does not authorize:

```text
Gmail runtime connector work
Google OAuth work
CRM write connectors
public chatbot integration
email sending
proposal sending
quote automation
payment automation
client-facing action automation
```

---

## Safe Near-Term Use

If this idea is used soon inside NovaLIS, it should only be used as a safe read-only workflow proof.

Allowed proof shape:

```text
local sample lead record
→ Nova summary
→ missing-info list
→ draft follow-up
→ non-action receipt
```

Hard limits:

```text
No live Gmail
No live CRM
No external writes
No autonomous send
No real customer data unless explicitly provided by the user for that session
No persistent business automation
```

---

## Future Acceptance Criteria

Before this can become runtime work, confirm:

```text
[ ] Active priority lock allows the work, or the work directly supports the locked read-only proof.
[ ] Lead source is read-only or explicitly user-provided.
[ ] Review card payload can show the needed fields.
[ ] Authority boundary is explicit.
[ ] Drafting and sending are separate states.
[ ] External actions are separate governed capabilities.
[ ] No quote, deadline, acceptance, payment, or client-facing message occurs without explicit approval.
[ ] Ledger/receipt records exist for reviewed recommendations and approved actions.
[ ] Generated runtime truth is updated if capability surface changes.
```

---

## Final Locked Position

```text
Auralis should build structured intake now.
Nova should support it later only as a governed internal review assistant.
The first move is not public AI/chat automation.
The future Nova path is review, summarize, draft, and wait for approval.
```
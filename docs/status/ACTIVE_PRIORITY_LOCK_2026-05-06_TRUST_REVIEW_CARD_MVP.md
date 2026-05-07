# Active Priority Lock - 2026-05-06 Trust Review Card MVP

Status: active.

This is human-maintained priority guidance, not generated runtime truth.

Generated runtime docs and actual code remain authoritative if they conflict with this lock.

---

## Active Workstream

```text
Trust Review Card MVP / Visible Non-Action Receipt Surface
```

---

## Purpose

Create the first visible trust/review surface for the planning-only and read-only governance work completed in the prior OpenClaw proof chain.

This lock exists to connect the current backend governance/proof infrastructure to a visible user-facing review surface without expanding authority.

The target is a minimal read-only review/trust card surface.

This is not an automation-expansion lock.

---

## Required Inputs

- PR #103 planning-task preview runtime handoff proof
- PR #104 RequestUnderstanding review-card payload contract
- PR #105 local capability signoff matrix
- PR #106 OpenClawMediator skeleton
- PR #107 first read-only OpenClaw workflow proof
- PR #110 runtime truth regeneration / audit
- `docs/status/LOCAL_CAPABILITY_SIGNOFF_MATRIX_2026-05-06.md`
- `docs/status/CURRENT_WORK_STATUS.md`
- `docs/todo/ACTIVE_TODO.md`

---

## Allowed Scope

- render a minimal read-only RequestUnderstanding review card in the UI
- render non-action / non-authorizing status fields clearly
- render receipt fields such as:
  - what happened
  - what did not happen
  - blocked actions
  - history unavailable / not available states
- add tests proving the trust card cannot imply execution occurred
- improve trust wording clarity where needed
- regenerate runtime docs through the generator path if runtime truth changes
- audit wording for OpenClaw overstatement or authority drift

---

## Explicitly Not Approved

- no OpenClaw execution
- no direct Cap 63 shortcut use
- no browser/computer-use
- no filesystem writes
- no external writes
- no email/calendar/Shopify/account actions
- no autonomous workflow execution
- no Google connector runtime work
- no capability registry expansion
- no workflow automation expansion
- no scheduler expansion
- no installer work

---

## Acceptance Gates

This lock is complete only if:

1. The visible trust/review card remains read-only.
2. The UI cannot imply execution or authorization occurred.
3. Receipts clearly state what did not happen.
4. OpenClawMediator remains non-executing and non-authorizing.
5. No new runtime authority path bypasses GovernorMediator.
6. No broad OpenClaw automation is added.
7. Runtime docs remain generator-grounded if updated.
8. Final audit confirms no authority drift.

---

## Boundary Rule

Do not use this lock to start broad OpenClaw automation or workflow expansion.

This lock is only for the visible trust/review surface associated with the existing planning-only and read-only proof infrastructure.

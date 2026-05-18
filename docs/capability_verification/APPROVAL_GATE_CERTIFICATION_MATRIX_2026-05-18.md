# Approval Gate Certification Matrix — 2026-05-18

Status:

```text
inventory filled / verification pending
not a certification document
```

Purpose:

```text
Define the exact proof requirements before any approval-gate certification or lock-closeout claim.
```

This document:

- does not certify the approval gate
- does not change runtime behavior
- does not modify capability locks
- does not expand authority
- does not authorize autonomous execution

---

# Certification Discipline

```text
focused coverage != full certification
active != certified != locked
```

Current verified truth:

```text
PR #171 merged focused regression coverage for tested Cap 22 / Cap 64 paths.
PR #172 merged behavioral live-session coverage for tested Cap 22 / Cap 64 paths.
PR #175 documented broader workflow verification.
PR #176 fixed workflow regressions found by that pass.
Full approval-gate certification remains pending.
```

---

# Capability Inventory Source

Inventory source:

```text
nova_backend/src/config/registry.json on main at 1b0ab10900ca3ceb2955520a6e658e6d8f674605
```

Registry rule used:

```text
requires_confirmation == true
```

Current confirmation-bound capability inventory:

```text
Cap 22 — open_file_folder
Cap 64 — send_email_draft
```

No other active capability in `registry.json` currently has `requires_confirmation: true`.

---

# Required Certification Matrix

| Capability | Registry Confirmation Required | Pending State Tested | Approve Path Tested | Deny Path Tested | Cancel/Unrelated Input Tested | Ledger Sequence Tested | Live WS Session Tested | Runtime Verified | Certification Status |
|---|---|---|---|---|---|---|---|---|---|
| Cap 22 `open_file_folder` | yes | yes — PR #171 / #172 focused coverage | yes — PR #171 / #172 focused coverage | yes — PR #171 / #172 focused coverage | yes — PR #172 focused coverage | partial — focused governed ledger sequence covered | yes — PR #172 focused coverage | partial | pending |
| Cap 64 `send_email_draft` | yes | yes — PR #171 / #172 focused coverage | yes — PR #171 / #172 focused coverage | yes — PR #171 / #172 focused coverage | yes — PR #172 focused coverage | partial — focused governed ledger sequence covered | yes — PR #172 focused coverage | partial | pending |

---

# Non-Confirmation Active Capabilities

The following active capabilities currently have `requires_confirmation: false` in `registry.json` and are not part of approval-gate certification scope unless registry truth changes:

```text
16 governed_web_search
17 open_website
18 speak_text
19 volume_up_down
20 media_play_pause
21 brightness_control
31 response_verification
32 os_diagnostics
48 multi_source_reporting
49 headline_summary
50 intelligence_brief
51 topic_memory_map
52 story_tracker_update
53 story_tracker_view
54 analysis_document
55 weather_snapshot
56 news_snapshot
57 calendar_snapshot
58 screen_capture
59 screen_analysis
60 explain_anything
61 memory_governance
62 external_reasoning_review
63 openclaw_execute
65 shopify_intelligence_report
```

Important note:

```text
Some non-confirmation capabilities may still be persistent, networked, or externally observable.
This matrix only tracks approval-gate certification for registry-confirmation-bound capabilities.
It does not certify the broader governance posture of every active capability.
```

---

# Required Proof Before Certification Claim

## 1. Capability inventory complete

Current state:

```text
complete for current registry truth — Cap 22 and Cap 64 only
```

Certification remains pending because inventory completion is not proof completion.

---

## 2. Behavioral proof complete

Required:

```text
pending path blocks executor dispatch
approve path resumes through governed execution
no/cancel path does not execute
unrelated input does not execute
```

Current state:

```text
focused coverage exists for Cap 22 / Cap 64 via PR #171 and PR #172
broader/full-suite verification pending
```

---

## 3. Ledger proof complete

Required:

```text
ACTION_ATTEMPTED
ACTION_COMPLETED
ACTION_DENIED or equivalent refusal/cancel/no-execution evidence
pending-state events where implemented
```

must appear only in expected governed sequences.

Current state:

```text
partial focused ledger coverage exists
full certification-level ledger review pending
```

---

## 4. Live-session proof complete

Required:

```text
WebSocket/session approval flows verified
frontend state transitions verified where applicable
```

Current state:

```text
focused WebSocket/session coverage exists for Cap 22 / Cap 64 via PR #172
broader/full-suite live-session verification pending
```

---

## 5. Regression protection complete

Required:

```text
must-fail tests for bypass attempts
executor dispatch forbidden during pending state
approval cannot be inferred from unrelated text
```

Current state:

```text
focused regression coverage exists
full certification-level bypass matrix pending
```

---

## 6. Scope boundaries preserved

Certification work must not include:

```text
OpenClaw expansion
browser/computer-use expansion
external writes
Shopify writes
email sending
autonomous workflows
```

---

# Current Safe Interpretation

```text
Approval-gate focused coverage exists for current confirmation-bound Cap 22 / Cap 64 paths.
The current confirmation-bound capability inventory is filled from registry truth.
Broader/full-suite approval-gate certification is still pending.
```

No document should currently say:

```text
approval gate fully certified
all confirmation paths proven
approval-gate closeout complete
```

until this matrix is fully resolved and independently verified.

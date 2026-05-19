# Approval Gate Certification Matrix — 2026-05-18

Status:

```text
evidence complete / certification decision pending
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
PR #188 filled confirmation-bound capability inventory (Cap 22 + Cap 64 only).
PR #191 defined approval gate workflow simulation targets.
PR #192 landed Cap 64 operator journey proof scaffold.
PR #193 landed Cap 22 operator journey proof scaffold.
PR #195 captured Cap 64 automated evidence (132 tests, 0 failures, scenarios A-D).
PR #196 captured Cap 64 live mailto proof and receipt evidence (1 live request).
PR #197 added duplicate-yes non-double-execution tests for Cap 22 / Cap 64.
PR #198 recorded the full Cap 64 live checklist evidence.
PR #200 captured Cap 22 automated evidence (23 tests, 0 failures).
PR #201 captured Cap 22 live proof and receipt evidence (approval + denial).
PR #203 captured recovery evidence for Cap 22 and Cap 64 (3 tests).
All confirmation-bound evidence dimensions now captured for both capabilities.
Full approval-gate certification: evidence complete / decision pending.
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

Based on this registry snapshot, no other active capability has `requires_confirmation: true`.

---

# Required Certification Matrix

| Capability | Registry Confirmation Required | Pending State Tested | Approve Path Tested | Deny Path Tested | Cancel/Unrelated Input Tested | Duplicate-Yes Tested | Ledger Sequence Tested | Live WS Session Tested | Live Proof Captured | Automated Evidence | Runtime Verified | Certification Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Cap 22 `open_file_folder` | yes | yes — PR #171 / #172 | yes — PR #171 / #172 | yes — PR #171 / #172 | yes — PR #172 | yes — PR #197 | yes — PR #172 + PR #200 automated evidence | yes — PR #172 | yes — PR #201 (approval + denial + receipt) | yes — PR #200 (23 tests, 0 failures) | yes — recovery PR #203 (3 tests) | evidence complete / decision pending |
| Cap 64 `send_email_draft` | yes | yes — PR #171 / #172 | yes — PR #171 / #172 | yes — PR #171 / #172 | yes — PR #172 | yes — PR #197 | yes — PR #172 + PR #195 scenarios A-D | yes — PR #172 | yes — PR #196 (1 live request + receipt) | yes — PR #195 (132 tests, 0 failures) | yes — recovery PR #203 (3 tests) | evidence complete / decision pending |

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
duplicate yes does not double-execute
```

Current state:

```text
Cap 64: strong behavioral coverage — PR #171, #172 (focused), PR #195 (132 automated
  tests across scenarios A-D), PR #197 (duplicate-yes non-double-execution).
Cap 22: focused behavioral coverage — PR #171, #172, PR #197 (duplicate-yes),
  plus PR #200 automated evidence (23 tests, 0 failures).
Recovery behavior evidence: captured for both capabilities — PR #203
  (3 tests: disconnect clears pending state, new session does not inherit stale state,
  new session can still create fresh pending and confirm).
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
Cap 64: governed ledger sequence verified in PR #172, PR #195 scenarios A-D,
  and PR #196 live receipt endpoint evidence.
Cap 22: focused governed ledger sequence verified in PR #172, with broader
  automated ledger assertions captured in PR #200. Live receipt endpoint
  evidence captured in PR #201.
```

---

## 4. Live-session proof complete

Required:

```text
WebSocket/session approval flows verified
frontend state transitions verified where applicable
live checklist tests passed (per capability_verification/live_checklists/)
```

Current state:

```text
Cap 64: focused WS coverage (PR #172) + full live checklist passed (PR #196/PR #198:
  Test 1 full draft, Test 2 recipient-only, Test 3 body-hint, Test 4 receipt,
  Test 5 gate denial — all 5/5 passed).
Cap 22: focused WS coverage (PR #172) + live proof captured (PR #201:
  approval test — Documents folder opened after confirmation, receipt verified;
  denial test — Downloads open denied with "no", no new receipt created).
```

---

## 5. Regression protection complete

Required:

```text
must-fail tests for bypass attempts
executor dispatch forbidden during pending state
approval cannot be inferred from unrelated text
duplicate yes does not double-execute
```

Current state:

```text
Cap 64: focused regression (PR #171) + automated scenarios A-D (PR #195, 132 tests)
  + duplicate-yes (PR #197). Strong regression coverage.
Cap 22: focused regression (PR #171) + duplicate-yes (PR #197)
  + automated evidence suite (PR #200, 23 tests) + live proof (PR #201)
  + recovery evidence (PR #203). Strong regression coverage.
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
Cap 64: evidence complete — automated (132+ tests), live checklist (5/5),
  duplicate-yes protection, receipt verification, recovery (PR #203).
Cap 22: evidence complete — automated (23 tests), live proof + receipt (PR #201),
  duplicate-yes protection, path-root boundary (5 tests), recovery (PR #203).
Both confirmation-bound capabilities have all evidence dimensions captured.
Approval-gate certification decision is now possible for the tested
  registry-confirmation-bound scope (Cap 22 + Cap 64 only).
```

No document should currently say:

```text
approval gate fully certified
all confirmation paths proven
approval-gate closeout complete
Cap 64 P5 complete
Cap 64 locked
```

until this matrix is fully resolved and independently verified.

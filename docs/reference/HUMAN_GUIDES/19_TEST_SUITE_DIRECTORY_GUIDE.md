# Test Suite Directory Guide
Updated: 2026-04-18

## Purpose
This guide explains the major test folders inside `nova_backend/tests/`.

## Main Test Areas

### `adversarial/`
Stress-style or pressure tests that try to catch unsafe or boundary-violating behavior.

### `certification/`
Formal per-capability certification tests organized into 6 phases.

Structure:
```
certification/
  test_lock_regression_guard.py     <- runs on every CI invocation
  cap_64_send_email_draft/
    test_p1_unit.py                 <- re-exports from executors/
    test_p2_routing.py              <- re-exports from test_send_email_draft_routing.py
    test_p3_integration.py          <- full Governor spine
    test_p4_api.py                  <- HTTP/WebSocket API shape
```

The regression guard (`test_lock_regression_guard.py`) enforces:
- every registered capability has a lock file entry
- every locked capability has all 5 phases passing
- locked capability governance fields (authority_class, risk_level, external_effect, reversible) match the snapshot taken at lock time

### `conversation/`
Tests for conversation handling, routing, and user-facing response behavior.

### `evaluation/`
Evaluation-oriented tests for broader behavior quality.

### `executors/`
Unit and behavior tests for the concrete executor layer.

### `governance/`
High-value governance tests that protect Nova's authority and safety invariants.

### `phase42/`
Tests focused on Phase-4.2 cognitive and reporting behavior.

### `phase45/`
Tests focused on Phase-4.5 UX, dashboard, screen, and perception behavior.

### `phase5/`
Tests focused on continuity, governed memory, and related runtime slices.

### `rendering/`
Tests focused on presentation and output structure.

### `simulation/`
Simulation-style tests used to model broader runtime flows.

## Why These Folders Matter
The folder split helps make it clear what kind of correctness is being checked.

Examples:
- if you care about authority boundaries, start in `governance/`
- if you care about a concrete feature, start in `executors/`
- if you care about perception and UX, start in `phase45/`
- if you care about continuity and memory, start in `phase5/`
- if you care about capability lock state and regressions, start in `certification/`

## Short Version
The test suite is not just checking whether Nova works.
It is also checking whether Nova stayed inside the system's intended rules.
And once a capability is locked, the certification guard ensures it stays that way.

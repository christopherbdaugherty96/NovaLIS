# Testing and Validation Guide
Updated: 2026-04-18

## Purpose
This guide explains how Nova's testing and validation system is organized.

## Why Testing Matters So Much In Nova
Nova is not only trying to be useful.
It is also trying to preserve governance boundaries while becoming more capable.

That means tests are not just checking whether code works.
They are also checking whether Nova stayed inside its intended rules.

## Main Test Location
The main test suite lives in:
- `nova_backend/tests/`

## Major Test Areas

### `governance/`
Tests for core safety and authority boundaries.
These are some of the most important tests in the project.

### `executors/`
Tests for individual capabilities and executor behavior.

### `conversation/`
Tests for conversation behavior and routing.

### `phase42/`
Tests focused on the Phase-4.2 cognitive/reporting layer.

### `phase45/`
Tests focused on perception, dashboard, and UX-layer behavior.

### `phase5/`
Tests focused on continuity, governed memory, and related runtime slices.

### `adversarial/`
Tests that try to catch violations or edge cases in higher-risk behavior.

### `rendering/`
Tests that focus on the structure and presentation of output.

### `certification/`
Formal per-capability certification tests organized into phases.

This folder holds the 6-phase verification system for all 26 live capabilities.
It is explained in full in Guide 33: `33_CAPABILITY_VERIFICATION_GUIDE.md`.

The key file that runs on every CI invocation is:
- `certification/test_lock_regression_guard.py`

This guard enforces that once a capability is locked, its governance fields cannot silently change.

## What Nova's Tests Are Trying To Protect
Nova's tests help protect things like:
- no hidden autonomy
- governed execution path integrity
- runtime/doc alignment
- safe capability behavior
- proper continuity behavior
- explicit memory operations
- stable perception behavior
- locked capability governance fields

## Runtime Doc Checks
Nova also includes script-based checks that help keep runtime documentation aligned.

Examples include:
- runtime doc drift checks
- frontend mirror sync checks

These checks matter because Nova treats documentation as part of the system's legibility and trust surface.
For frontend review, the runtime-served canonical UI is `nova_backend/static/`; the mirror check exists to detect when `Nova-Frontend-Dashboard/` drifts from it.

## Capability Certification CLI
Nova ships a CLI tool for managing capability certification:

```
python scripts/certify_capability.py status              # show all capabilities
python scripts/certify_capability.py status 64           # show one capability
python scripts/certify_capability.py advance 64 p3_integration
python scripts/certify_capability.py live-signoff 64 --notes "all tests pass"
python scripts/certify_capability.py lock 64
python scripts/certify_capability.py unlock 64 --reason "breaking change"
python scripts/certify_capability.py check-tests 64
```

Phases that can be advanced via CLI: p1_unit, p2_routing, p3_integration, p4_api
Phase 5 requires manual live testing by the user before sign-off.
Phase 6 (lock) requires all 5 earlier phases to pass.

## The Big Idea
Nova's testing philosophy is not just:
- does the feature work?

It is also:
- does the feature stay inside Nova's rules?
- has a human verified it end-to-end?
- is regression prevention active?

That is why the test system matters so much to the whole project.

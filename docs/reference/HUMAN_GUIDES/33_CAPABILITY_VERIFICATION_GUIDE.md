# Capability Verification Guide
Guide 33 of the Human Guides series
Updated: 2026-04-23

## Runtime Truth First
Human Guides explain the system in plain language. Exact live counts, enabled capabilities, and current phase state are generated at runtime.

See:
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/GOVERNANCE_MATRIX.md`

## What This Guide Is
This guide explains Nova's 6-phase capability verification system in plain language.

## The Problem This Solves
Nova has a live capability set that changes over time. Each capability has a governance contract covering authority, risk, external effect, and reversibility.

Without a formal verification layer, behavior can drift silently.

## The 6 Phases
1. Unit
2. Routing
3. Integration
4. API
5. Live Human Signoff
6. Lock

## Current Status
For the exact current status, run:
`python scripts/certify_capability.py status`

Or see:
`docs/capability_verification/STATUS.md`

# Test Suite Directory Guide
Updated: 2026-03-13

## Purpose
This guide explains the major test folders inside `nova_backend/tests/`.

## Main Test Areas

### `adversarial/`
Stress-style or pressure tests that try to catch unsafe or boundary-violating behavior.

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

## Short Version
The test suite is not just checking whether Nova works.
It is also checking whether Nova stayed inside the system's intended rules.

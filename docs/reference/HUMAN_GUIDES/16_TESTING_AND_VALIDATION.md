# Testing and Validation Guide
Updated: 2026-03-13

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

## What Nova's Tests Are Trying To Protect
Nova's tests help protect things like:
- no hidden autonomy
- governed execution path integrity
- runtime/doc alignment
- safe capability behavior
- proper continuity behavior
- explicit memory operations
- stable perception behavior

## Runtime Doc Checks
Nova also includes script-based checks that help keep runtime documentation aligned.

Examples include:
- runtime doc drift checks
- frontend mirror sync checks

These checks matter because Nova treats documentation as part of the system's legibility and trust surface.
For frontend review, the runtime-served canonical UI is `nova_backend/static/`; the mirror check exists to detect when `Nova-Frontend-Dashboard/` drifts from it.

## The Big Idea
Nova's testing philosophy is not just:
- does the feature work?

It is also:
- does the feature stay inside Nova's rules?

That is why the test system matters so much to the whole project.

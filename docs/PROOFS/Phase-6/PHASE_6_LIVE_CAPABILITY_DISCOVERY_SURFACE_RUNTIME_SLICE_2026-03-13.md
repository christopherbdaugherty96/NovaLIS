# Phase-6 Live Capability Discovery Surface Runtime Slice
Date: 2026-03-13
Status: Implemented in runtime
Scope: Home-page discoverability surface for the current governed capability set

## Purpose
Add a truthful "What Nova Can Do Right Now" surface so Nova shows live available actions without relying on static help copy.

## What Landed
- system-status payload now includes a live capability surface derived from enabled registry entries
- Home page now renders a "What Nova Can Do Right Now" panel
- the panel groups current capabilities into practical areas such as:
  - Research
  - News and Briefing
  - Documents
  - Screen
  - Computer
  - System
  - Voice
  - Memory

## Truth Rule
This panel is registry-driven and Governor-facing.

It reflects:
- currently enabled capabilities
- currently exposed governed actions

It does not describe:
- planned features
- disabled delegated runtime
- speculative future capability classes

## Files
- `nova_backend/src/executors/os_diagnostics_executor.py`
- `nova_backend/static/index.html`
- `nova_backend/static/dashboard.js`
- `nova_backend/static/style.phase1.css`

## Verification
- focused widget and system-status tests passed
- frontend mirror sync passed
- runtime doc drift check passed

## Why This Matters
This slice improves:
- discoverability
- trust
- runtime legibility
- product feel

It also gives Nova a live capability map that updates from the active registry surface rather than from static dashboard text.

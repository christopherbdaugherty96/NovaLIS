# Phase 6 Update and Component Delivery Specification
Date: 2026-03-13
Status: Productization planning note only; not runtime truth
Scope: Version delivery, update flow, and component-update model for a packaged Nova app

## Purpose
This document defines the simplest trustworthy update path for Nova once it is distributed as desktop software.

## Core Recommendation
Recommended first update model:
- versioned release updates
- startup or on-demand update check
- user-visible prompt
- restart-based update application

This is the simplest stable path for early Nova releases.

## Recommended First Update Source
Recommended early source:
- GitHub Releases

Why:
- simple infrastructure
- compatible with alpha and beta distribution
- fits Nova's current repo-centered development flow

## Early Update Flow
Recommended first flow:
1. Nova starts
2. Nova checks for a newer official release
3. Nova informs the user
4. user chooses whether to update
5. Nova downloads the update package
6. Nova restarts into the new version

## Update Modes

### Restart update
Recommended first mode.

Why:
- safer
- easier to verify
- easier to audit

### Live patch or hot update
Not recommended as the first product path.

Why:
- more complex
- easier to destabilize
- harder to keep aligned with Nova's trust model

## User Control
Nova should expose update preferences such as:
- check automatically
- download automatically
- notify only

This fits Nova's privacy-first and user-controlled positioning.

## Update Logging
Nova should record update actions in the ledger.

Example lifecycle ideas:
- update check performed
- update available
- update downloaded
- update applied

This keeps the update system aligned with Nova's audit philosophy.

## Component-Level Updates
Later, Nova may support separate update tracks for:
- core app
- UI
- capability packs
- local models

But the first shipping path should treat Nova as one coherent release package.

## Data Preservation Rule
Updates must not wipe:
- user config
- user data
- local memory data
- logs
- downloaded models

The update system should replace the app layer without silently erasing operator state.

## Trust Rule
Updates must not silently expand authority.

That means:
- authority changes should be visible in release notes
- new capability groups should be reviewable
- runtime truth and proof docs should be updated with the same release

## Bottom Line
Nova's first trustworthy update system should be:
- simple
- user-visible
- restart-based
- ledger-aligned

Complex live patching can come later if the product needs it.

# Phase 6 Endgame Productization Roadmap
Date: 2026-03-13
Status: Productization planning note only; not runtime truth
Scope: Distribution, packaging, updates, launch readiness, and business/legal preparation for the end of the Phase-6 era

## Purpose
This document records the realistic path from:
- strong governed local runtime

to:
- downloadable product

for Nova.

The goal is not "more architecture."
It is the transition from:
- project

to:
- installable product with a believable launch path

## Interpretation Rule
This is not a runtime-authority document.
It does not claim Nova already ships as a desktop app or already has legal/commercial readiness.

It is a planning packet for what Phase 6 should prepare by the time the delegated-policy platform is mature enough to package.

This is not legal advice.
State filing rules, tax setup, model licenses, API terms, and commercial obligations should be verified directly against current official sources before launch.

## Recommended First Distribution Model
The recommended first distribution model is:
- local desktop app

Why:
- it fits Nova's privacy-first architecture
- it preserves the local FastAPI + Governor runtime shape already in the repo
- it keeps Nova aligned with local models and governed execution
- it is much more consistent with Nova's identity than full SaaS

Primary early distribution channels:
- GitHub Releases
- direct download website
- technical early-adopter communities

Not recommended as the first model:
- full SaaS as Nova's default identity

Possible later model:
- hybrid desktop + optional cloud services

## End-of-Phase-6 Productization Sequence

### 1. Desktop Packaging
Convert Nova from a developer runtime into an installable local desktop app.

Recommended outcome:
- a normal installer or signed desktop bundle
- a launcher that starts the FastAPI backend automatically
- a desktop window that connects to Nova's local UI and websocket surfaces

Reference:
- `docs/design/Phase 6/PHASE_6_DESKTOP_APP_PACKAGING_AND_DISTRIBUTION_SPEC.md`

### 2. Update and Version Delivery
Ship Nova with a simple, trustworthy update path.

Recommended outcome:
- versioned releases
- update checks at startup or on demand
- restart-based update flow first
- preserved user data across updates

Reference:
- `docs/design/Phase 6/PHASE_6_UPDATE_AND_COMPONENT_DELIVERY_SPEC.md`

### 3. API and External-Service Readiness
Prepare Nova for real user installations without changing its core backend architecture.

Recommended outcome:
- user-configured API keys where needed
- external-service terms review
- attribution where required
- stable config locations and network-disclosure language

Reference:
- `docs/design/Phase 6/PHASE_6_API_CONFIGURATION_AND_EXTERNAL_SERVICE_COMPLIANCE_SPEC.md`

### 4. Early-Launch Legal and Business Readiness
Prepare the minimum legal package needed for a careful alpha or beta launch.

Recommended outcome:
- terms of service
- privacy policy
- third-party licenses
- software license position
- security contact
- clear company-formation trigger points

Reference:
- `docs/design/Phase 6/PHASE_6_EARLY_LAUNCH_LEGAL_AND_BUSINESS_READINESS.md`

### 5. Alpha Launch
Launch to technical early adopters first.

Recommended audience:
- developers
- local-AI users
- governance-minded power users

Primary goal:
- feedback, not scale

### 6. Beta Refinement
Use the alpha to tighten:
- onboarding
- installer reliability
- docs
- update flow
- daily utility surfaces
- explain-anything polish

### 7. Public Product Direction
Only after the above are stable should Nova be framed as:
- a local AI desktop product
- or a future local AI appliance direction

## Success Threshold for the End of Phase 6
By the end of the Phase-6 era, the productization threshold should look like this:
- Nova installs like software, not a developer project
- Nova preserves its local governed architecture
- Nova can update cleanly
- Nova exposes API/config responsibility clearly
- Nova has the minimum legal and license packet for an early launch
- Nova has a clear alpha/beta distribution path

## What Should Still Remain True
Even after packaging and launch preparation:
- Governor remains the authority spine
- ExecuteBoundary remains enforced
- delegated triggers remain visible and auditable
- updates do not silently expand authority
- local-first identity remains intact
- API/network use remains mediated and reviewable

## Relationship to the Appliance Direction
This roadmap is the software path that makes the appliance direction believable.

It connects directly to:
- `docs/design/Phase 6/PHASE_6_LOCAL_AI_APPLIANCE_AND_PRODUCT_DIRECTION.md`

In plain terms:
- first make Nova installable
- then make Nova updateable
- then make Nova legally and operationally launchable
- only then does the "Nova Hub" direction become credible

## Supporting Documents
- `docs/design/Phase 6/PHASE_6_DESKTOP_APP_PACKAGING_AND_DISTRIBUTION_SPEC.md`
- `docs/design/Phase 6/PHASE_6_UPDATE_AND_COMPONENT_DELIVERY_SPEC.md`
- `docs/design/Phase 6/PHASE_6_API_CONFIGURATION_AND_EXTERNAL_SERVICE_COMPLIANCE_SPEC.md`
- `docs/design/Phase 6/PHASE_6_EARLY_LAUNCH_LEGAL_AND_BUSINESS_READINESS.md`

## Bottom Line
The end of Phase 6 is not just about delegated policy infrastructure.

It is also the point where Nova should become:
- packageable
- updateable
- legally and operationally launchable

without giving up the local governed system it already is.

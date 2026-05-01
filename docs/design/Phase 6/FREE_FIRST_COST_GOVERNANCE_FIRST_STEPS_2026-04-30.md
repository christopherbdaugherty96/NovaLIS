# Free-First Cost Governance — First Implementation Steps
Date: 2026-04-30
Status: Implementation planning note; not runtime truth
Scope: First safe steps for turning the Free-First Principle into runtime-visible Nova behavior

## Purpose
This document defines the first practical implementation steps for Nova's Free-First Principle.

The goal is not to block useful integrations.
The goal is to make cost posture visible, reviewable, and eventually enforceable through Nova's normal governance path.

## Governing Rule
Nova defaults to free, open-source, local-first, or user-owned paths.

Anything that may introduce billing, quota, credit usage, paid plans, or vendor lock-in must be flagged before it is recommended as the preferred path or used as an execution route.

This extends Nova's authority model:

- Intelligence does not imply authority.
- Capability does not imply cost permission.

## Runtime Truth Boundary
This document is design-layer guidance only.

Do not claim runtime enforcement until the behavior appears in:
- generated current-runtime docs
- capability registry truth
- verified proof packets
- tests or runtime evidence

## Step 1 — Add Cost Posture Metadata To Capabilities
Add a `cost_posture` field to capability metadata.

Allowed values:
- `free`
- `free_tier`
- `paid`
- `unknown_cost`

Recommended default:
- existing local-only capabilities: `free`
- external/network capabilities where terms are not reviewed yet: `unknown_cost`
- provider APIs with quotas or billing setup: `free_tier`
- explicitly paid/credit-metered services: `paid`

Initial target file:
- `nova_backend/src/config/registry.json`

Do this as a metadata-only change first.
Do not add blocking behavior in the same first patch.

## Step 2 — Add Registry Validation
Add tests or validation ensuring every active capability has a valid `cost_posture`.

Minimum checks:
- field exists
- value is one of the allowed enum values
- no active capability defaults silently to paid or unknown without review visibility

Potential test area:
- existing capability registry / runtime governance doc tests

## Step 3 — Surface Cost Posture In Runtime Docs
Update generated runtime documentation paths so cost posture appears wherever capability metadata is rendered.

Likely surfaces:
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`
- runtime audit or capability reference endpoints if they render capability metadata

Important:
- update the generator, not just the generated output
- regenerate docs only after generator support exists

## Step 4 — Governor Soft Flag Only
Add a non-blocking Governor or mediator-level flag for non-free cost posture.

Behavior:
- `free`: no special flag
- `free_tier`: visible cost/limit warning
- `paid`: visible cost warning and confirmation path candidate
- `unknown_cost`: visible unknown-cost warning

First implementation should not block execution.
It should make cost posture visible in the action review/result path.

This avoids breaking current capability flows while proving the metadata path.

## Step 5 — Trust Review Surface
Add cost posture to the Trust Review Card or equivalent visible action review surface.

Minimum visible field:
- Cost Status: Free / Free Tier / Paid / Unknown

Recommended wording:
- Free: No known billing exposure for intended use.
- Free Tier: Limits, quota, credits, or billing setup may apply.
- Paid: May require payment, credits, or metered billing.
- Unknown: Cost posture has not been verified.

## Step 6 — Ledger Event Planning
Add ledger visibility after the soft flag is visible.

Possible event:
- `COST_POSTURE_FLAGGED`

Suggested fields:
- capability id
- capability name
- cost_posture
- user_acknowledged
- provider
- action id or request id when available

Do not add ledger noise for every free/local action unless needed.
Focus first on `free_tier`, `paid`, and `unknown_cost`.

## Step 7 — Enforcement Later, Not First
Only after metadata, docs, UI, and ledger visibility exist should Nova consider enforcement.

Future enforcement rule candidate:
- `free`: allowed under existing capability rules
- `free_tier`: allowed with visible flag
- `paid`: requires explicit approval
- `unknown_cost`: requires verification or explicit user acknowledgment before use

Do not implement this until the soft-flag path is tested.

## First PR Shape
Recommended first PR should include:

1. `cost_posture` field added to registry entries
2. enum validation test
3. generated runtime docs updated through generator changes
4. no Governor blocking behavior

Recommended PR title:
- `Add capability cost posture metadata`

## Second PR Shape
Recommended second PR should include:

1. mediator or Governor soft flag
2. user-visible warning text
3. test proving non-free cost posture is surfaced
4. no execution blocking unless explicitly approved

Recommended PR title:
- `Surface capability cost posture in governed action review`

## Third PR Shape
Recommended third PR should include:

1. trust review UI field
2. optional ledger event for non-free/unknown posture
3. proof packet or implementation note

Recommended PR title:
- `Add cost posture visibility to trust and ledger surfaces`

## Google Integration First Classification
For Google-related planning, use this initial classification unless verified otherwise:

- Google OAuth / Identity: `free`
- Gmail API: `free_tier`
- Google Calendar API: `free_tier`
- Google Drive API: `free_tier`
- Google Docs API: `free_tier`
- Google Sheets API: `free_tier`
- Google Maps Platform: `free_tier`
- Vertex AI / Google Cloud AI services: `paid` or `unknown_cost` until exact free-credit/billing terms are verified

Reason:
Many Google APIs can be free for small usage but still depend on quotas, project setup, policy limits, or billing configuration. Nova should not label them as fully free unless the intended path has no billing exposure.

## Non-Goals
This first implementation is not:
- a payment system
- a billing monitor
- a provider pricing database
- a blocker for all external APIs
- a replacement for NetworkMediator
- a replacement for capability authority checks

## Done Criteria
This work is ready to be called runtime-visible only when:
- every active capability has valid `cost_posture`
- generated runtime docs expose cost posture
- at least one test enforces valid cost posture metadata
- non-free/unknown posture can be surfaced to the user without breaking existing flows

## Bottom Line
The first safe move is metadata and visibility, not hard blocking.

Nova should become cost-aware the same way it became authority-aware:
- classify first
- surface second
- log third
- enforce only after the path is proven

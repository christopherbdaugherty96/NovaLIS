# Nova Docs

This folder is the documentation home for Nova.

The docs are intentionally split by authority level so people can quickly tell:
- what is explanatory
- what is planned
- what is proven
- what is authoritative for the live runtime

## Obsidian Overlay

Nova also supports an Obsidian overlay at the repository root.

Use:
- `C:\Nova-Project` as the Obsidian vault root
- `_MOCs/` as the generated entry point
- `scripts/generate_runtime_docs.py` to refresh runtime docs and the overlay together

The important rule is:
- source docs and source code stay untouched
- the overlay is generated on top for navigation, graph colors, and map-of-content notes

This lets docs and code appear in the same Obsidian graph, grouped by concern area.

## Start Here

If you are new to Nova, use this reading order:

1. `docs/reference/HUMAN_GUIDES/README.md`
2. `docs/reference/HUMAN_GUIDES/14_FRONTEND_AND_UI_GUIDE.md`
3. `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
4. `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`
5. `docs/current_runtime/RUNTIME_FINGERPRINT.md`
6. `docs/design/README.md`

If you want the most grounded current-status and next-step view after that, read:
- `docs/design/Phase 6/NOVA_GROUNDED_CURRENT_STATUS_AND_NEXT_ROADMAP_2026-04-02.md`
- `docs/design/Phase 8/NOVA_LOCAL_CODE_OPERATOR_ROADMAP_2026-04-13.md`

If you want the best plain-language system walkthrough with diagrams, read:
- `docs/reference/HUMAN_GUIDES/32_NOVA_SYSTEM_PROCESS_AND_EXPLAINABILITY_GUIDE.md`

If you want the current product truth for what Nova is becoming, read:
- `docs/design/Phase 11/NOVA_HOME_ASSISTANT_PRODUCT_TRUTH_2026-04-02.md`

This sequence gives you:
- the human explanation first
- the product/frontend shape early
- the live runtime truth second
- the deeper planning backlog after that

## The Four Main Doc Layers

### 1. Human guides
Location:
- `docs/reference/HUMAN_GUIDES/`

Related inactive reference packets:
- `docs/reference/inactive/`

Use this when you want:
- a plain-language explanation of Nova
- a product overview
- onboarding guidance
- a clearer understanding of memory, continuity, voice, screen, and trust

These docs are explanatory.
They do not authorize runtime behavior.

Inactive reference packets in `docs/reference/inactive/` are preserved standards and checklists that are not active Nova-wide rules unless explicitly adopted later.

### 2. Runtime truth
Location:
- `docs/current_runtime/`

Use this when you want:
- the live runtime state
- active capabilities
- implementation-aligned authority truth
- current system boundaries

This is the most important authority rule in the docs:

If any explanatory, historical, or design doc conflicts with runtime truth, the runtime truth docs win.

Start with:
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`
- `docs/current_runtime/RUNTIME_FINGERPRINT.md`

### 3. Proof packets
Location:
- `docs/PROOFS/`

Use this when you want:
- implementation evidence
- completion packets
- validation artifacts
- phase-specific proof summaries

These docs help answer:
- what was built
- what was verified
- what proof exists for specific slices

### 4. Design and planning
Location:
- `docs/design/`

Use this when you want:
- future direction
- architecture planning
- backlog notes
- product-shaping packets
- phase roadmaps

These docs are intentionally non-authorizing.
They express intended direction, not live runtime truth.

Start with:
- `docs/design/README.md`
- `docs/design/DESIGN_AUTHORITY.md`

## Canonical Governance

Location:
- `docs/canonical/`

Use this when you want:
- constitutional source material
- governance law
- canonical system principles

This is the deepest source material for Nova's trust and control model.

## Best Reading Paths By Goal

### I want to understand Nova quickly
1. `docs/reference/HUMAN_GUIDES/README.md`
2. `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
3. `docs/design/README.md`

### I want to know exactly what is live
1. `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
2. `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`
3. `docs/current_runtime/RUNTIME_FINGERPRINT.md`

### I want to review implementation evidence
1. `docs/PROOFS/`
2. relevant phase proof index
3. matching runtime docs

### I want to understand future direction
1. `docs/design/README.md`
2. `docs/design/Phase 6/NOVA_GROUNDED_CURRENT_STATUS_AND_NEXT_ROADMAP_2026-04-02.md`
3. relevant roadmap or TODO packet
4. compare against `docs/current_runtime/CURRENT_RUNTIME_STATE.md`

### I want to understand governance
1. `docs/canonical/`
2. `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
3. `docs/design/DESIGN_AUTHORITY.md`

## Current Reality Check

Nova already has a meaningful live runtime.

The live system includes:
- governed web research
- answer-first news and reporting flows
- screen explanation surfaces
- governed memory and continuity
- voice and dashboard UI
- bounded OpenClaw home-agent surfaces
- shipped user profile and connection-card setup surfaces
- guided onboarding and readiness flow
- structured morning brief delivery across chat and OpenClaw
- visible OpenClaw active-run state
- setup-aware capability guidance that adapts to connected sources

But Nova is still intentionally narrower than broad unsafe agent systems.

The most honest current product description is:
- a calm local-first home assistant on your computer
- a governed intelligence workspace
- a narrow but real operator surface

The main unfinished layers are still:
- full connector-rich calendar integration
- pause/resume and fuller visible run controls
- full governed envelope execution

The product direction now being emphasized in design truth is:
- Nova should feel like a calm home assistant
- the Governor should remain strict underneath
- the user experience should become simpler, softer, and less system-shaped
- local coding help should grow through a governed OpenClaw operator lane, starting with read-only project analysis before any approval-gated write flow

Important current gaps still called out in runtime truth include:
- full calendar integration
- full governed envelope execution

That distinction matters:
- design docs may describe broader future capabilities
- runtime docs describe what the system can actually do today

## Stability Aliases

These exist as compatibility pointers:
- `docs/runtime/` -> `docs/current_runtime/`
- `docs/canon/` -> `docs/canonical/`
- `docs/proofs/` -> `docs/PROOFS/`

## Recommended Habit For Reviewers

When reviewing Nova, keep this order in mind:

1. read human guides for intent
2. read runtime docs for truth
3. read proofs for evidence
4. read design docs for future direction

That order prevents a lot of confusion.

## Short Version

Use:
- `docs/reference/HUMAN_GUIDES/` for understanding
- `docs/current_runtime/` for truth
- `docs/PROOFS/` for evidence
- `docs/design/` for the roadmap
- `docs/canonical/` for governance law

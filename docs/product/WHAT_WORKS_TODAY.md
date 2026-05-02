# What Works Today

Last reviewed: 2026-05-01

This page separates Nova's current surfaces by readiness level.

Use generated runtime docs for exact active capability truth.
Use this page for user-facing readiness expectations.

Latest proof packages:
- [Daily operating baseline proof](../demo_proof/daily_operating_baseline/DAILY_BRIEF_PROOF.md)
- [2026-04-29 conversation + search proof](../demo_proof/2026-04-29_conversation_search_proof/CONVERSATION_SEARCH_REPORT.md)
- [Brain live test report](../demo_proof/brain_live_test/REPORT.md)
- [2026-04-28 user test](../demo_proof/2026-04-28_user_test/USER_TEST_REPORT.md)

---

## Proven / Core Paths

| Area | Status | Notes |
|---|---|---|
| Chat / conversations | Proven core path | Core local assistant runtime is available. |
| Dashboard UI | Proven core path | Local dashboard surfaces load in the local-first follow-up pass: Intro, Home, Chat, News, Workspace, Memory, Rules/Policies, Trust, and Settings. |
| Runtime truth docs | Proven core path | Generated runtime state and capability references exist. |
| Research / summaries | Proven core path | Primary read-oriented assistant value. |
| Trust receipts API | Proven core path | `/api/trust/receipts` and `/api/trust/receipts/summary` expose governed-action receipt evidence from the ledger. |
| Trust receipts UI | Proven core path with label friction | The Trust page renders Action Receipts in the local-first proof pass; some receipt rows still need friendlier names when ledger payloads only include capability IDs. |
| Local self-description fallback | Proven core path | Core prompts such as `What works today?`, `Explain what Nova can do.`, and memory-authority questions answer from local runtime truth even when the daily metered token budget is exhausted. |
| Task Clarifier | Proven narrow Brain behavior | Tested ambiguity/boundary prompts now clarify missing service area, personal-account/account-write boundaries, browser environment distinction, Shopify read-only limits, and memory authority limits before implying action. This is not full Brain routing. |
| Governed web search / citations | Proven with friction | Cap 16 can answer current questions with visible source links, confidence, and known/unclear notes. Search Evidence Synthesis now structures evidence metadata for the existing governed search path; it is not a new capability or authority path. |

---

## Works With Setup / Environment Dependence

| Area | Status | Notes |
|---|---|---|
| Local device controls | Setup-dependent | OS and hardware behavior may vary. |
| Weather / news / calendar snapshots | Setup-dependent | Some surfaces depend on local config, data sources, or connector setup. |
| Voice input/output | Setup-dependent | Requires local speech tooling and model paths. |
| Shopify intelligence | Setup-dependent, read-only | Requires Shopify environment variables and credentials. Current implementation is read-only reporting, not store automation. |

---

## Implemented But Still Maturing

| Area | Status | Notes |
|---|---|---|
| Memory / continuity | Implemented, evolving UX | Useful surface, still being refined. Memory supports continuity; it does not authorize execution. |
| Brain architecture / schema scaffold | Implemented as scaffold | Brain docs, Brain runtime architecture, EnvironmentRequest schema, Task Clarifier, Task Understanding / Task Envelope planning scaffolds, planning-only RunManager, planning Run Preview, Search Evidence Synthesis, and a static Capability Contract catalog for Cap 16/63/64/65 exist. Full Task Environment Router, Dry Run API, Brain Trace UI, live runtime contract lookup, Context Assembler, Intention Parser, Sandbox Boundary Enforcer, Persona Filter, Model Router, and project context engine remain future work. |
| Screen capture / analysis | Experimental | Request-time capture exists, but the experience is still maturing. |
| Email draft | Implemented, safety-limited, paused | Opens a local mail client draft through `mailto:` after confirmation. Nova does not use SMTP, access inboxes, or send autonomously. Cap 64 live signoff is paused while Cap 16 conversation/search proof is the active sprint. |
| OpenClaw execution surface | Advanced / constrained | Governed, limited, not broad autonomy. |
| Action Receipts | Implemented, maturing UX | Visible receipt surface exists for governed-action outcomes. A fuller Trust Panel remains future work. |
| Daily Brief MVP | Implemented, maturing UX | Deterministic on-demand session brief with session, memory, receipts, weather, calendar, email placeholder, continuity fields, and deterministic next-action recommendations. No execution authority, no LLM call, no background automation. |

---

## Not Yet Product-Ready

| Area | Status | Notes |
|---|---|---|
| Full daily operating layer | Future / not implemented | Daily Brief MVP exists, but routines, background context awareness, approved automation loops, durable memory loop proof, and full operating-system behavior remain future work. |
| Approved automation routines / envelopes | Future / not implemented | Conceptual direction only. No broad recurring automation loop should be claimed as live. |
| Small-model full Brain runtime stack | Future / not implemented | Context Assembler, Model Router, Intention Parser, Tool Bridge, Sandbox Boundary Enforcer, and Persona Filter are documented architecture, not live runtime behavior. Search Evidence Synthesis is implemented only as deterministic Cap 16 evidence structuring, not as a general Brain planner. |
| Google read/context connector | Future / not implemented | The Google connector model documents OAuth, Gmail read-only, Calendar read-only, and Gmail context for Cap 64 draft-only replies. It is a future read/context path, not Gmail send/write authority. |
| Free-first cost governance | Design planning / not runtime-enforced | Free-first policy docs describe future cost posture metadata and visibility. Runtime enforcement does not exist until registry metadata, generator output, tests, and UI/proof paths exist. |
| Auralis Website Coworker | Future planning / not implemented | Future business workflow and production discipline layer only. No publish, deploy, domain, DNS, or client-send authority exists. |
| YouTubeLIS | Planning-only tool folder | Content planning docs/templates only. No upload, publish, account automation, or YouTube Studio control exists. |
| Fuller Trust Panel / Trust Review Card | Partial / future work | Action Receipts and trust receipt API exist; richer blocked-reason drill-down, confirmation previews, proof browsing, and polished demo flow remain future work. |
| One-click installer | Not implemented | Needed for broader adoption. |
| Mainstream consumer onboarding | Not ready | Current setup expects a technical user. |
| Broad autonomous execution | Intentionally limited | Not current product direction. |
| Cap 64 live lock | Paused | Automated checks and confirmation-boundary proof are strong, but local mail-client live proof is intentionally paused until conversation/search proof is stronger. |
| Cap 65 live lock | Blocked on credentials | Requires real Shopify credentials and read-only live proof before lock. |

---

## What This Means

Nova already has meaningful working surfaces.

The current focus is no longer raw feature count.
The focus is:
- clarity
- trust visibility
- onboarding quality
- usability
- proof

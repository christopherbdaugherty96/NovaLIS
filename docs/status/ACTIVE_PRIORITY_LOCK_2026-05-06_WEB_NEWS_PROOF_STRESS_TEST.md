# Active Priority Lock - 2026-05-06 Web / News / Reporting + UI Proof / Stress Test

Status: active.

This is human-maintained priority guidance, not generated runtime truth.

Generated runtime docs and actual code remain authoritative if they conflict with this lock.

---

## Active Workstream

```text
Governed Web / News / Reporting + UI / Commands Proof + Stress Test
```

---

## Purpose

Pause current Trust Review Card MVP implementation work and create a dedicated proof and stress-test package for:

1. governed web/news/reporting capability surfaces
2. visible Nova UI/button/command behavior
3. governance-boundary reliability
4. stress/failure behavior
5. simulation/adversarial testing

The goal is to verify that Nova's visible surfaces actually behave correctly before broader automation or Trust Panel expansion.

This includes verifying that all visible buttons, commands, widgets, and UI states either:

- work correctly
- refuse safely
- clearly explain setup/dependency requirements
- clearly show blocked/not-approved status

No silent failures.

No misleading authority.

Expected outcome is truthful behavior, not guaranteed success.

---

## Capability Scope

This lock focuses on:

### Governed information/reporting surfaces

- governed_web_search
- open_website
- headline_summary
- multi_source_reporting
- intelligence_brief
- topic_memory_map
- story_tracker_update
- story_tracker_view

### UI / command surfaces

- dashboard UI
- buttons
- command entry
- widgets
- navigation
- settings/status surfaces
- confirmation prompts
- degraded/error states
- blocked-action messaging
- voice/media/system controls
- analysis/memory/document surfaces

Related supporting systems allowed for proof context:

- NetworkMediator
- LedgerWriter
- Search Evidence Synthesis
- News snapshot cache
- Weather/news/current-information flows
- analysis_document for proof writeups

---

## Required Proof Targets

Nova should be able to:

- search the web through a governed network path
- open websites/articles through a governed browser-opening route
- summarize headlines
- compare headline clusters
- build structured multi-source reports
- build compact intelligence briefs
- track stories over time
- show topic maps of current headline themes
- render working UI buttons/commands for approved surfaces
- clearly refuse or explain unavailable surfaces
- show setup-required states accurately
- surface degraded/error states honestly

---

## Required Deliverables

Create/update proof folder trees for:

```text
docs/PROOFS/Web-News-Reporting/
docs/PROOFS/UI-Commands/
```

Expected proof areas:

- governed web search proof
- browser/article open proof
- headline summary proof
- cluster comparison proof
- multi-source report proof
- intelligence brief proof
- story tracker proof
- topic map proof
- UI/button proof
- command proof
- failure-mode proof
- governance-boundary proof
- hallucination/drift review
- Codex simulation/stress-test prompts
- adversarial prompt suite
- latency/reliability observations
- source-label and credibility verification
- WebSocket/connectivity failure handling
- degraded-state UI handling

---

## Stress-Test Goals

Use Codex/Claude/reviewer systems to simulate:

- malformed headline feeds
- conflicting article narratives
- stale caches
- duplicate stories
- fake or low-credibility sources
- governance bypass attempts
- direct execution coercion attempts
- hallucinated source attribution
- topic-map instability
- story-linking errors
- article-open failures
- network failure/retry paths
- oversized result sets
- prompt injection attempts from article content
- rapid repeated button presses
- stale WebSocket state
- partial backend startup
- missing API/provider configuration
- malformed widget payloads
- blocked-action UI coercion attempts
- command alias/typo handling
- degraded-state rendering

The pass condition for stress tests is honest bounded behavior: work when approved and available, clear refusal when blocked, exact setup/degraded messaging when dependencies are missing, and no implication that execution or authority occurred when it did not.

---

## Truthful UI Rule

Nova UI must never imply:

- execution occurred when it did not
- authority was granted when it was not
- data is live/current when stale
- a command succeeded when degraded
- a capability exists when setup is missing
- a blocked action is available

Standard visible states for this lock:

- `working`
- `blocked`
- `setup-required`
- `degraded`
- `offline`
- `unsupported`

---

## Explicitly Not Approved

- no OpenClaw execution expansion
- no browser/computer-use expansion
- no external writes
- no autonomous workflow execution
- no direct Cap 63 shortcut use
- no Google connector runtime expansion
- no capability registry expansion
- no Trust Review Card implementation work while paused
- no installer work

---

## Acceptance Gates

This lock is complete only if:

1. Each listed capability has at least one concrete proof artifact.
2. Governance boundaries are explicitly tested.
3. Failure-mode behavior is documented.
4. Source-label and credibility behavior are verified.
5. Hallucination/drift observations are documented.
6. Codex/Claude stress-test prompts exist.
7. Visible UI/button/command behavior is verified.
8. Buttons/commands either work, refuse safely, or clearly explain setup/block state.
9. Proofs distinguish success, failure, blocked, setup-dependent, degraded, unsupported, and not-yet-tested behavior.
10. UI/runtime/docs mismatches are recorded as blockers or follow-ups instead of papered over.
11. No authority drift or execution expansion occurs.
12. Runtime truth claims remain grounded.

---

## Boundary Rule

This lock exists to validate and pressure-test existing governed information/reporting and UI/command surfaces.

It does not authorize broader automation or OpenClaw execution expansion.

## Next After This Lock

After this proof/stress-test lock closes, the recommended next reviewed workstream is:

```text
Trust Review Card MVP / Visible Non-Action Receipt Surface
```

Do not resume Trust Review Card implementation from this lock.

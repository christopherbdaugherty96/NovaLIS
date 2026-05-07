# Active Priority Lock - 2026-05-06 Web / News / Reporting Proof + Stress Test

Status: active.

This is human-maintained priority guidance, not generated runtime truth.

Generated runtime docs and actual code remain authoritative if they conflict with this lock.

---

## Active Workstream

```text
Governed Web / News / Reporting Capability Proof + Stress Test
```

---

## Purpose

Pause current Trust Review Card MVP implementation work and create a dedicated proof and stress-test package for the current governed web/news/reporting capability family.

The goal is to:

1. Verify current runtime behavior matches claims.
2. Create durable proof artifacts.
3. Create simulation/stress-test plans for Codex/Claude/reviewer systems.
4. Identify runtime drift, hallucination risk, governance bypass risk, and reliability gaps.
5. Validate these capabilities before broader automation or Trust Panel expansion.

---

## Capability Scope

This lock focuses only on:

- governed_web_search
- open_website
- headline_summary
- multi_source_reporting
- intelligence_brief
- topic_memory_map
- story_tracker_update
- story_tracker_view

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

---

## Required Deliverables

Create a dedicated proof folder tree for:

```text
docs/PROOFS/Web-News-Reporting/
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
- failure-mode proof
- governance-boundary proof
- hallucination/drift review
- Codex simulation/stress-test prompts
- adversarial prompt suite
- latency/reliability observations
- source-label and credibility verification

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
7. No authority drift or execution expansion occurs.
8. Runtime truth claims remain grounded.

---

## Boundary Rule

This lock exists to validate and pressure-test existing governed information/reporting surfaces.

It does not authorize broader automation or OpenClaw execution expansion.

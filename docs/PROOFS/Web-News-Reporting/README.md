# Web / News / Reporting Proof Package

Status: active proof/stress-test scaffold.

This folder exists to validate the current governed information/reporting surfaces before broader automation or Trust Panel expansion.

Active lock:

`docs/status/ACTIVE_PRIORITY_LOCK_2026-05-06_WEB_NEWS_PROOF_STRESS_TEST.md`

---

## Target Capability Family

- governed_web_search
- open_website
- headline_summary
- multi_source_reporting
- intelligence_brief
- topic_memory_map
- story_tracker_update
- story_tracker_view

---

## Required Proof Areas

- governed web search proof
- browser/article open proof
- headline summary proof
- cluster comparison proof
- multi-source report proof
- intelligence brief proof
- story tracker proof
- topic map proof
- governance-boundary proof
- hallucination/drift review
- adversarial stress testing
- prompt-injection review
- latency/reliability review
- stale-cache behavior review
- source-label and credibility review

---

## Required Evidence Pattern

Each proof should record:

- what was requested
- what happened
- what did not happen
- governance boundary
- source labels and freshness caveats
- failure/degraded behavior
- hallucination observations
- prompt-injection observations when relevant
- raw transcript or payload evidence
- screenshot only if it proves a visible UI state

Expected outcome is truthful behavior, not guaranteed success.

---

## Required Boundaries

The proof package must not:

- approve OpenClaw execution expansion
- approve browser/computer-use expansion
- approve autonomous workflows
- approve direct Cap 63 shortcut use
- approve external writes
- approve Google connector runtime expansion
- overstate runtime truth

---

## Suggested Folder Layout

```text
Web-News-Reporting/
├── README.md
├── governed_web_search/
├── open_website/
├── headline_summary/
├── multi_source_reporting/
├── intelligence_brief/
├── topic_memory_map/
├── story_tracker/
├── governance_boundaries/
├── adversarial_tests/
├── codex_simulations/
├── hallucination_review/
├── stale_cache_review/
├── latency_reliability/
└── source_credibility/
```

---

## Codex Stress-Test Focus

Stress tests should focus on:

- conflicting narratives
- hallucinated source attribution
- fake/stale news
- duplicate-story collapse
- malformed feeds
- prompt injection from article content
- governance bypass attempts
- oversized topic clusters
- story-linking instability
- network failure behavior
- credibility ranking drift
- cache inconsistency

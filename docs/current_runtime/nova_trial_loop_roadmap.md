# Nova Trial Loop - Operational Roadmap And Gap Closure Plan

Version: 1.1
Date: 2026-04-21
Status: Active execution plan
Proposed destination: `docs/current_runtime/nova_trial_loop_roadmap.md` or `docs/future/nova_trial_loop_roadmap.md`
Related artifacts:

- Scenario library: `nova_backend/tests/simulation/scenarios/`
- Trial runner: `nova_backend/tests/simulation/nova_trial_runner.py`
- Latest generated report: `nova_backend/tests/simulation/reports/latest_trial_report.md`

Non-goal: This roadmap should not become a feature wishlist. It should stay tied to measured Trial Loop gaps.

## Baseline

Baseline report:

- Generated report: `nova_backend/tests/simulation/reports/latest_trial_report.md`
- Generated at: 2026-04-21T22:07:39.435200+00:00
- Scenario count: 36
- Passed: 3
- Failed: 33
- Total gaps: 47
- Total turns: 119
- Error rate: 0.3277
- Gap categories: routing=15, response_quality=14, execution=11, clarification=4, safety=3

This document should be updated after each sprint with a fresh report timestamp and the new rollup numbers. Do not treat the baseline as timeless.

## Executive Summary

The Nova Trial Loop is a simulation-based audit framework that exposes weaknesses in Nova's routing, runtime behavior, memory, safety, and conversational quality.

The key achievement is not that Nova passes the scenarios today. It is that Nova can now reveal where it fails. That turns vague product discomfort into a prioritized engineering loop.

## How The Improvement Loop Works

1. Run the scenario library.
2. Read the generated report and gap summary.
3. Select one sprint target from the highest-impact gap category.
4. Implement the fix.
5. Add or update scenarios that define the expected behavior.
6. Re-run the trial loop.
7. Record the new metrics here.

## Trend Tracking

| Run | Report Timestamp | Passed | Failed | Total Gaps | Routing | Response Quality | Execution | Clarification | Safety | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Baseline | 2026-04-21T22:07:39.435200+00:00 | 3 | 33 | 47 | 15 | 14 | 11 | 4 | 3 | First broad scenario pack |
| After Sprint 1 | TBD | | | | | | | | | |
| After Sprint 2 | TBD | | | | | | | | | |
| After Sprint 3 | TBD | | | | | | | | | |
| After Sprint 4 | TBD | | | | | | | | | |

## Weaknesses And User Impact

| Priority | Weakness | Technical Description | User Experience |
| --- | --- | --- | --- |
| P0 | Runtime degradation | Local model failures, provider errors, budget limits, and circuit breaker states produce dead ends. | "Nova is broken." |
| P1 | Semantic routing ambiguity | Ambiguous commands route to the wrong tool or skip clarification. | "Nova does not understand me." |
| P1 | Cancellation UX weakness | Cancellation requests are not handled as a clear conversational state. | "I cannot stop this." |
| P2 | Memory contradiction handling | New facts can conflict with old facts without clear replacement or explanation. | "Nova forgot or lied." |
| P2 | Safety inconsistency | Unsafe requests do not always produce the expected refusal path. | "Nova might do something dangerous." |
| P3 | Monetization/product language | Subscription, payment, and support flows lack mature product wording. | "Nova feels unfinished." |

## Sprint 1: Routing And Intent Recovery

Goal: reduce routing gaps from 15 to 8 or fewer.

Tasks:

- Add explicit clarification when routing confidence is low.
- Instrument routing confidence in trial logs.
- Refine music intent handling: play music vs discuss music.
- Refine overloaded request handling: clarify before choosing a random tool.
- Add five routing-specific scenarios after changes.

Success criteria:

- Routing gaps <= 8.
- Ambiguous scenarios trigger clarification in at least 80 percent of expected cases.

## Sprint 2: Runtime Degraded Mode And Recovery

Goal: reduce execution gaps from 11 to 5 or fewer.

Tasks:

- Add a friendly degraded-runtime response when the local model circuit breaker opens.
- Surface runtime degraded state through WebSocket or existing status endpoints.
- Add retry/backoff for transient provider errors where safe.
- Make cancellation work even when runtime is degraded.
- Add provider-failure scenarios with expected fallback language.

Success criteria:

- Execution gaps <= 5.
- Provider failure scenarios do not end in opaque dead ends.
- Circuit breaker state is visible to the user.

## Sprint 3: Memory Trust Layer

Goal: make contradiction handling visible and auditable.

Tasks:

- Add confidence metadata to extracted facts.
- Mark superseded facts rather than silently deleting them.
- Prefer newer high-confidence facts over older conflicting facts.
- Generate user-visible correction language.
- Keep scenarios for location, preferences, and disabled extraction.

Success criteria:

- Memory contradiction scenarios pass at least 70 percent.
- User sees correction language when facts change.
- Mutually exclusive facts are not both active without explanation.

## Sprint 4: Safety And Product Language

Goal: reduce safety gaps to zero and make monetization flows feel polished.

Tasks:

- Tighten unsafe request detection for credential theft, malware, and financial execution.
- Standardize refusal language.
- Create product copy for upgrade, cancellation, failed payment, and data export flows.
- Add expected fragments to scenarios after wording is chosen.

Success criteria:

- Safety gaps = 0.
- Monetization scenarios pass at least 80 percent.
- Refusals are clear, calm, and non-robotic.

## Focus Protection

Do not work on these until the reliability loop improves:

- new flashy integrations
- major UI redesigns
- advanced monetization features
- speculative memory features beyond contradiction handling
- broad product expansion unrelated to trial-loop gaps

## Future Enhancements

- Run the trial loop in CI for routing, memory, and safety changes.
- Add anonymized production replay with privacy controls.
- Add learned expectations after enough manually reviewed scenarios exist.
- Add scenario tags and category-level reports.

## Bottom Line

The Trial Loop is Nova's practice field. The baseline is intentionally uncomfortable. The goal is to make failure visible, close gaps one category at a time, and measure the product becoming trustworthy.

## First Commit Slice

1. Move this roadmap to the chosen docs location.
2. Add a short command block showing how to run the Trial Loop.
3. Keep generated reports ignored; commit scenarios and evaluator code, not report artifacts.
4. Re-run the Trial Loop after each sprint and update the trend table.

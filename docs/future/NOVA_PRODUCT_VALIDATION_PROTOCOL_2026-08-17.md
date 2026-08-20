# Nova Product Validation Protocol — 2026-08-17

Status: strategic/product proof protocol; non-authorizing.

This document defines how Nova should validate the product thesis once Google evidence and minimal Continuity exist. It does not authorize implementation, provider access, new capabilities, external writes, Continuity runtime work, or user-data collection beyond separately reviewed scope.

## Purpose

The next major product question is not `Can Nova do more?` It is:

> **Can Nova maintain accurate operational state across days, focus attention correctly, and help close real loops without silently taking authority?**

This protocol prevents the answer from becoming subjective.

## Phase A — Owner 7–14 day Continuity proof

Minimum evidence sources when available and separately authorized:

- Nova conversation state;
- Google Tasks READ;
- Calendar READ;
- GitHub/project evidence where relevant;
- Nova receipts/outcome evidence;
- Gmail READ only if already live and separately authorized.

Minimum Continuity objects:

- commitment;
- open loop;
- waiting item;
- blocker;
- decision/reference state where implemented;
- verified/unverified completion state.

Nova should be tested daily against these questions:

```text
What am I trying to accomplish?
What did I commit to?
What is due?
What changed?
What am I waiting on?
What is blocked?
What did I decide?
What actually executed?
What was verified?
What remains unresolved?
What deserves attention next?
```

### Metrics

Record at least:

- correct active commitments surfaced;
- missed active commitments;
- false commitments invented;
- correct waiting items;
- stale waiting items not retired/reconciled;
- correct blockers;
- stale/incorrect blockers;
- due-date/time-scope accuracy;
- source/provenance accuracy;
- verified-vs-unverified outcome accuracy;
- state conflicts surfaced instead of silently overwritten;
- number of useful unresolved items surfaced before the owner remembered them independently;
- number of loops materially advanced or closed after Nova surfaced/prepared the next step;
- number of times the owner had to reconstruct context manually;
- recommendation usefulness / ignored recommendations;
- trust failures where Nova overstated what it knew or what happened;
- daily voluntary use.

Do not optimize for raw notification count, message count, capability count, or amount of information shown.

### Pass signal

There is no fixed numeric pass threshold yet. The owner proof should be considered promising when Nova repeatedly:

- preserves important state across days;
- does not invent commitments;
- correctly distinguishes waiting/blocked/completed/verified state;
- reduces manual reconstruction;
- surfaces forgotten or unresolved work at useful times;
- helps advance or close real loops;
- remains trusted enough that the owner returns voluntarily.

If the owner repeatedly corrects basic state, stops trusting Today/Attention, or continues reconstructing context manually, the response should be to repair Continuity/request-understanding rather than add capability breadth.

## Phase B — External-user proof

Only after the owner proof is credible should Nova be tested with approximately 3–10 external users.

Preferred early-user profile:

- multiple concurrent projects or clients;
- fragmented work across email, calendar, tasks, files, GitHub/business tools;
- already uses one or more AI assistants;
- experiences repeated context reconstruction or dropped follow-ups.

### External-user evidence

Measure behavior rather than enthusiasm:

```text
Did the user return the next day/week?
Did Nova surface something important they had forgotten?
Did Nova reduce app switching or state reconstruction?
Did Nova help close a real loop?
Did the user act on a prepared recommendation/draft?
Did the user correct Nova's state frequently?
Did trust fail because Nova overstated evidence or outcomes?
What caused abandonment?
```

Useful metrics may include:

- D1/D7 return use for the small pilot;
- sessions initiated without prompting;
- unresolved items correctly carried forward;
- useful attention items per day;
- loops advanced/closed;
- reconstruction events avoided;
- state corrections per user-day;
- false-positive attention items;
- trust/outcome-truth failures;
- qualitative reasons for return or abandonment.

Do not treat `this is cool`, feature requests, or hypothetical willingness-to-pay as product proof.

## Cost-aware validation

When model-provider routing exists, also measure:

- local completion rate;
- frontier escalation rate;
- cost per completed workflow;
- frontier cost per user-day;
- quality improvement from escalation;
- latency difference;
- user/provider overrides.

A high local-completion rate is valuable only if correctness and user value remain acceptable. No fixed local percentage is assumed in advance.

## Decision gates after validation

```text
Strong owner proof + external repeat use
-> justify deeper product investment / recurring engineering help

Strong owner proof + weak external use
-> investigate onboarding / target-user / UX / positioning before architecture expansion

Weak owner proof
-> repair request-understanding / Continuity / evidence reconciliation

Persistent weak proof after disciplined repair
-> reconsider product thesis rather than compensate with more capabilities
```

## Non-goals

This protocol does not authorize:

- automatic commitment extraction without reviewed rules;
- silent profiling;
- expanded data collection;
- new Google scopes;
- external writes;
- autonomous OpenClaw/browser work;
- provider spending;
- production telemetry infrastructure;
- team hiring.

The protocol defines how future evidence should be judged, not permission to collect or act.
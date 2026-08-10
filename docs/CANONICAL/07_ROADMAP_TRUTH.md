# 07 — Roadmap Truth (what is next)

**Status: current.** Ordering is hand-maintained. This file points to the single ordering
authority; it does not invent new promises.

## Source of record (ordering authority)

- [`../future/NOVA_MASTER_ROADMAP_2026-07-05.md`](../future/NOVA_MASTER_ROADMAP_2026-07-05.md)
  — "the single source of truth for what comes next and in what order, across all lanes."

Its own authority rules:

```text
1. This document ORDERS work. It does not re-scope work.
2. Lane-specific lock docs remain the scope authority for their lane.
3. Everything in docs/future/ and root future/ NOT referenced by it is
   reference/archive material, not an active priority.
4. On ordering conflicts the roadmap wins; on scope conflicts the lane lock wins.
```

## Current continuity (where we actually are)

- **Human continuity note:** [`../status/CURRENT_WORK_STATUS.md`](../status/CURRENT_WORK_STATUS.md)
  — committed vs local vs in-progress. Not generated truth; code wins on conflict.
- **Where-we-are surface:** [`../status/DAILY_COMMAND_CENTER.md`](../status/DAILY_COMMAND_CENTER.md).

## The current gate (as of 2026-08-09)

`main` is at `dfef1db5df89bfdb276904acce26205d1c894331` after PR #332. Seven-morning
observation, grounded brief/category routing, and the post-#312 product-selection gate are complete.

The two evidence-selected trust lanes are closed:

- **Commitment Truth + Natural Reminder Handoff — COMPLETE.** PR #330 implemented truthful natural
  calendar-to-reminder handoff and result-backed persistence language. PR #332 fixed the remaining
  notification-schedule command precedence defect. Fresh-main proof at `dfef1db5...` confirmed the
  exact August 7 flow, a real `SCH-...` record, `show schedules`, `reminders`, fresh-session
  retrieval, and preservation of calendar-query routing.
- **Local Action Outcome Truth — COMPLETE.** PR #331 aligned Cap 22 action responses, durable
  receipts, and receipt consumers with the distinction between request acceptance and verified
  visible effect; Cap 19 natural-language coverage was repaired. Merged-main live proof passed.

The separate `tomorrow` calendar-scope wording defect was not part of PR #332 or its closeout. It
remains an inactive observation, not a reason to reopen Commitment Truth.

Authorization integrity now has three distinct states:

- **Slice 1 — MERGED through PR #325.** The Governor owns an exact-action-bound ApprovalGrant
  lifecycle.
- **Slice 2A — NOT IMPLEMENTED ON MAIN.** The owner approved bounded local implementation under a
  separate exact scope and publication boundary. It remains separately approved but paused; this
  ordering update neither cancels nor activates it.
- **Slice 2B — DEFERRED.** Later cooperative cancellation and capability-specific reconciliation
  remain separately gated.

The current ordering is:

1. Implement **Semantic Substrate Slice 1** as a small provider-neutral contract-and-test lane:
   `SourceIdentity`, `EvidenceEnvelope`, `Freshness`, `Confidence`, `ObservedState`,
   `IntendedState`, `StateDelta`, and shared `OutcomeSemantics`. No provider call, network I/O,
   capability, authority, or execution path belongs in this slice.
2. Implement **Google Workspace Foundation**: OAuth with PKCE, account identity, encrypted token
   storage, granted-scope inventory, explicit reconnect/grant profiles, revoke, and disconnect.
   Foundation connects an account but reads no domain data and performs no domain write.
3. Implement the first **Google Tasks vertical**: read evidence first, then separately governed
   writes only after read behavior, provenance, freshness, authority mapping, idempotency, outcome
   verification, and reconciliation are proven.
4. Expand Google evidence one family at a time: Gmail read, Calendar read, selected Drive access,
   then Docs/Sheets reads over selected resources. Unified awareness follows proven individual
   sources; local prepared proposals precede external mutation.
5. Add Google action families one at a time under explicit operation-level authority. Event-driven
   synchronization remains optional and evidence-driven.

Permanent Google boundary:

```text
Google capability != Google authorization != Nova authority
connected != evidence collected != action permitted
```

Google is an external evidence/action ecosystem under Nova, not part of Nova's authority model.
An OAuth grant proves only that the software can call an API; Nova Authority still decides whether
the exact operation, account, resource, parameters, and time are permitted. Google outcomes must
reuse Nova's request-accepted / effect-verified / outcome-state vocabulary rather than a second
boolean success model.

Secondary candidates remain inactive. No economic-value proof, expanded OpenClaw,
browser/computer-use, financial-write, outreach, posting, contracting, autonomous-business, or
delegation lane is active. OpenClaw remains a replaceable actuator rather than an authority.
This file records ordering only and authorizes nothing beyond an already explicit owner decision.

## Historical gate (as of 2026-07-23)

Phase 3 — "Can Nova become a habit?" — is the current product phase. Per
`CURRENT_WORK_STATUS.md` and the product definition, **observed daily use gates product-usability
and capability-expansion work** — build only what observed behavior proves is missing. Success
metric: Nova eliminates one uncertainty before the user reaches for another app. This evidence
rule scopes product/capability lanes; it does NOT gate the hardening track: authorization
integrity is the separately reviewed first hardening lane, which does not require another morning
to justify it (this truth-sync does not start it).

**Seven-morning threshold COMPLETE (2026-07-22).** Mornings 1-7 are logged and synthesized in
`../observation/SEVEN_MORNING_SYNTHESIS_2026-07-22.md`, which declared the evidence threshold
complete and named grounded brief/category routing the rank-1 defect. That lane shipped via
**PR #312** (merged 2026-07-23), after **PR #311** timeout containment, and is verified on fresh
`main` (`../status/GROUNDED_BRIEF_ROUTING_CLOSEOUT_2026-07-23.md`). It is COMPLETE, not
pending. No additional seven-morning or open-ended observation gate is required.

The next input is ONE targeted post-#312 morning for additional real-use / product-acceptance
input (not a re-verification of #312); after it the owner selects the next evidence-ranked
**product-usability** lane. Two distinct lists feed that choice (none authorized here):

- Synthesis-ranked secondary repairs (each a separate decision):
  - connection-truth / source-label repair;
  - runtime-generator (fingerprint) reconciliation;
  - business-context freshness/tense repair: stale past-dated memory-derived status
    (e.g. `Watch: July 9...`) must not present as current; separately authorize; no
    business action or external write;
  - corruption-safe loading remains PARKED unless an actual corruption/loading failure is observed.
- Standing personal gap-fill list (NOT synthesis-ranked): Google Tasks -> Gmail -> Traffic.

The post-#312 morning determines whether any product gap is selected.

Per the authorization-integrity lock
(`../status/PRIORITY_LOCK_2026-07-10_AUTHORIZATION_INTEGRITY.md`), **authorization integrity is
the first post-observation hardening lane**: a correctness/security lane that runs in parallel
priority with the top-ranked product lane, does not require a morning to justify it, and is
superseded only by a higher-severity correctness/governance defect. Its sequencing steps 1-2
(seven mornings; evidence-ranked product bottleneck) are now satisfied, so it is activatable.
This file records ordering only and authorizes nothing.

**Earlier 2026-07-11 observation state:** Step 0 documentation/protocol landed in PR #294
(morning-log template + single launch procedure + config truth) and Morning 1 is in progress.
One truth-critical repair landed in PR #295 (truthful availability — false "not configured"
labels for news/weather fixed), taken under explicit owner approval without lifting the freeze.
A conversation-grounding trace found that, at that time, the LLM
did not receive brief facts, so the next candidate lane — **"Grounded follow-up conversation
over brief items"** — is DEFINED BUT HELD until at least one completed morning after #295; it is
also the prerequisite before any local-vs-cloud (DeepSeek) model-quality test is meaningful. See
the master roadmap candidate list and `docs/status/DAILY_COMMAND_CENTER.md` (2026-07-11 block).

**Later 2026-07-11 update:** the grounded follow-up lane fired and landed in PR #298 after
Morning 1/Morning 2 evidence showed Nova still felt like a status panel rather than something
Chris could discuss the brief with. PR #297 also closed the input-reliability slice. Post-merge
#298 smoke from fresh main passed for news selected-story carry-forward, weather no-invention,
calendar selected-event "after that", and unrelated prompt isolation. DeepSeek/cloud
conversation remains parked until observed use of the grounded path proves a genuine
model-quality gap.

## Queued, not active (needs a separate reviewed priority lock)

From `CURRENT_WORK_STATUS.md`, none of these is authorized without its own lock:

```text
Google connector runtime, Shopify writes, ElevenLabs, OpenClaw expansion,
browser/computer-use expansion, external writes, finance automation,
social posting automation, autonomous workflow execution.
```

## What this file is *not*

It does not add roadmap promises, timelines, or scope. If it disagrees with the master roadmap
on ordering, the master roadmap wins; if it disagrees with a lane lock on scope, the lock wins.

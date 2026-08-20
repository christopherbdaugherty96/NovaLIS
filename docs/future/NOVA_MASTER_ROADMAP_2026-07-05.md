# Nova Master Roadmap - 2026-07-05 (Final)

Status: canonical ordering document — the single source of truth for what comes next and in
what order, across all lanes. Assembled 2026-07-05 from the live session, the pre-PR-4 code
audit, and a full mining pass over all three archive trees (docs/future/, future/,
"4-15-26 NEW ROADMAP").

Authority rules:

```text
1. This document ORDERS work. It does not re-scope work.
2. Lane-specific lock docs remain the scope authority for their lane.
3. Everything in docs/future/ and the root future/ tree NOT
   referenced by this document is reference/archive material, not
   an active priority.
4. When this document and an older doc disagree on ordering, this
   document wins. When they disagree on scope, the lane lock wins.
```

## Long-Term Direction Compass (non-authorizing)

`NOVA_AUTHORITY_AND_DECISION_OS_DIRECTION_2026-07-28.md` records the converged long-term
product thesis: Nova as a local-first personal authority and decision operating system,
organized as five permanently separated systems: Awareness, Decision, Authority, Execution,
and Outcome. It includes Prepared Reality as the non-executing decision handoff; mandate,
provenance, simulation, action-risk, attention, learning, privacy, incident, replaceability,
and retirement guardrails; the OpenClaw-as-replaceable-actuator boundary; and the
non-negotiable rule that learning may improve proposals but never permissions. It also defines
the Continuity Model as persistent reconciled state surrounding—not joining—the five systems,
and preserves Issue #326's economic-value progression as a strategic, non-activating dependency
chain.

That document is a strategic compass, not an ordering or scope authority. It synthesizes
existing roadmap concepts (including H13, H20, H23, H25, H28, and H31) and adds no active lane.
This roadmap still determines ordering; lane locks still determine scope; owner decisions still
activate work. Issue #326 and the strategic compass cannot activate Slice 2A, an economic-value
proof, OpenClaw work, or delegation.

## Current Ordering — 2026-08-20

Wave A1 began from merged-main checkpoint:

```text
1a517d8832a2c834c80b10a7062bed878f6312cc
```

That SHA is a planning checkpoint, not a permanent alias for current HEAD and not a validated
baseline.

The August 12 stabilization sequence has materially advanced. The following packages are merged
and must not be selected again as pending work:

```text
#337 / #338  P1-A commitment/capability truth
#339         P1-B receipt-correlated session action/outcome history
#340         Cap 19 outcome truth
#341 / #344  explicit weather-location preservation / WebSocket repair
#345         brightness outcome truth
#346         turn-down-volume routing/wording
#347         current-information freshness/source-boundary routing
#348         broad awareness follow-up interpretation
#349         Calendar source-selection overmatch repair
#350         Calendar tomorrow-scope preservation
#351         local schedule-cancellation routing
#352         private Drive source-selection truth
```

The current stabilization checkpoint is Issue #343. It **does not rewrite this roadmap**; it
places a truth/proof gate around the existing Google-evidence -> Continuity sequence so Nova
resumes that roadmap from a coherent baseline rather than from stale operational instructions.

Current order:

```text
WAVE A — truth reconciliation
  A1 operational truth synchronization
  A2 strategy reconciliation

WAVE B — truth-integrity repairs
  B1 runtime-truth instrumentation
  B2 capability narration
  B3 memory governance
  B4 reproducibility hygiene

WAVE C — proof and stabilization checkpoint
  exact candidate commit
  repaired runtime-truth regeneration
  supported proof matrix
  semantic-contract regression
  current Issue #227/local-inference benchmark
  reproduced-defect-only fixes
  immutable validated baseline
  reconstruct/reconcile #335
  OAuth hardening cases
  exact-head #335 verification
  independent security/architecture review
  separate merge decision

POST-STABILIZATION
  Google identity-only live proof
  -> Google Tasks READ / first provider-backed Google evidence vertical
  -> separately warranted Operational Continuity slice
```

PR #335 remains **OPEN / DRAFT / UNMERGED** at
`befb69ef75881a9f418472549b64243219c138f9`, with historical base
`c44b6d0cd72f0f91a6ec517427ad3fe2076beb30`. Its Foundation/auth/identity-only implementation
must not be merged in that historical state. It is reconstructed/reconciled only after Wave C
records an exact validated baseline; historical #335 fingerprints and test totals are not reused
as proof for the reconciled branch.

Operational Continuity remains **STRATEGICALLY ACCEPTED / INACTIVE / NOT
IMPLEMENTATION-AUTHORIZED**. It surrounds Awareness, Decision, Authority, Execution, and Outcome
as persistent reconciled state; it is not a sixth authority system. Its expansion remains earned
by trustworthy provider-backed evidence and demonstrated user value.

The future governed-protection-wall concept is long-term security/digital-sovereignty reference
material. It does not replace Nova's current product identity, activate a runtime lane, or displace
the current Google-evidence -> Continuity ordering.

Permanent boundary:

```text
connection != capability
capability != authority
Google capability != Google authorization != Nova authority
connected != evidence collected != action permitted
recommendation != permission
request acceptance != verified effect
memory != Operational Continuity
```

This current block ORDERS work. It does not itself authorize Wave B implementation, #335 mutation
or merge, Google domain-data access, external writes, capability/authority expansion, Operational
Continuity runtime, broad OpenClaw expansion, or provider expansion.

## Historical Ordering — 2026-08-12 (superseded by the 2026-08-20 gate)

`main` was at `c44b6d0cd72f0f91a6ec517427ad3fe2076beb30` after PR #334.

Durable state at that time:

- PR #333 merged the roadmap/current-state reconciliation.
- PR #334 merged Semantic Substrate Slice 1. Its provider-neutral source/evidence/state/outcome
  contracts and tests are durable infrastructure; it added no provider call, Google integration,
  capability, authority, or execution path.
- PR #335 contained the implemented Google Workspace identity-only foundation, but remained
  **DRAFT / UNMERGED** at `befb69ef75881a9f418472549b64243219c138f9`.

The 2026-08-12 fresh-main real-user acceptance record is
`../observation/FRESH_MAIN_REAL_USER_ACCEPTANCE_2026-08-12.md`. It was prospective planning evidence
against the exact current-main SHA above. The supplied 25-step golden regression was covered with
additional targeted probes; the complete 36-section stress catalog was not fully exercised.

The lower authority/execution layers held: ApprovalGrant integrity, approval cancellation/replay,
memory != authority, bypass strings != authority, Cap 22 outcome underclaiming, local reminder
persistence/retrieval, and measured Cap 19 effects. No unauthorized external action was observed.
The acceptance run nevertheless selected two P1 product-truth repairs:

1. **P1-A — user-visible commitment/capability truth.** Close the unsupported Google Calendar
   completion claim and the streamed reminder promise that appeared before persistence evidence.
2. **P1-B — receipt-correlated action/outcome history.** Derive session-action recaps from
   correlated receipts, deterministic/background reads, and explicit uncertainty rather than
   generative reconstruction.

The then-current order was:

1. Bound and implement P1-A only under a separate reviewed implementation authorization.
2. After P1-A separately merges, run targeted P1-A fresh-main live proof.
3. Bound and implement P1-B as a separate package under its own reviewed authorization.
4. After P1-B separately merges, run targeted P1-B / live P1 fresh-main proof.
5. Address P2 findings by failure class, not one broad cleanup PR.
6. Complete the untested/partial rows from the 36-section catalog.
7. Run the full fresh-main regression.
8. Resume PR #335 review.
9. If #335 merges, prove the identity-only foundation live.
10. Only then select **Google Tasks READ** as the first Google domain-data vertical.

This historical sequence is retained as provenance. Its P1/P2 pending-work language is superseded
because #337-#352 have since merged.

### Historical Continuity Model strategic ordering

The Continuity Model was already **STRATEGICALLY ACCEPTED / INACTIVE / NOT
IMPLEMENTATION-AUTHORIZED**. It was persistent reconciled state surrounding Awareness, Decision,
Authority, Execution, and Outcome; not a sixth system or an authority plane.

The intended dependency remained:

```text
stabilization
-> Google Workspace Foundation review/merge decision
-> live identity-only proof
-> first Google READ/evidence vertical
-> separately warranted, scoped, authorized, implemented, and proved Continuity Slice 1
```

## Historical Ordering — 2026-08-09

`main` was at `dfef1db5df89bfdb276904acce26205d1c894331` after PR #332. The meaningful
post-#319 sequence was:

- PR #320 synchronized continuity and deliberately excluded the post-#312 acceptance scaffold.
- PRs #321/#322/#324 grounded Auralis decision follow-ups and their exact display contract.
- PR #323 restored hosted CI and runtime-fingerprint cleanliness.
- PR #325 merged Authorization Integrity Slice 1.
- Issue #326 and PR #327 preserve non-authorizing strategy only.
- PR #328 merged the product, roadmap, and landing-page truth-sync.
- PR #329 recorded the August 7 owner-use evidence and selected Commitment Truth.
- PR #330 implemented Commitment Truth + Natural Reminder Handoff.
- PR #331 implemented and live-proved Local Action Outcome Truth.
- PR #332 closed notification-schedule command precedence and retrieval routing.

The targeted post-#312 owner-use session occurred on 2026-08-07 and is recorded in
`../observation/OWNER_ACCEPTANCE_POST_312_2026-08-07.md`. It is prospective owner-use evidence
suitable for product prioritization. Exact commit-level attribution is limited because the running
SHA and branch were not captured. This closed the pending product-selection input without
fabricating missing runtime provenance.

The selected product repair was complete. Fresh-main verification at
`dfef1db5df89bfdb276904acce26205d1c894331` proved the exact August 7 natural handoff, real
reminder persistence, same-session `show schedules` and `reminders`, fresh-session retrieval, and
preservation of calendar-query routing.

PR #331's local-action outcome-truth lane was also closed after merged-main live proof. Nova
preserved the distinction between launch/request acceptance and visible-effect verification in
the action response, durable receipt, and later receipt consumers.

Authorization Integrity Slice 1 was **MERGED**. Slice 2A was **NOT IMPLEMENTED ON MAIN** and
remained separately owner-approved under its existing exact scope and publication boundary. Slice
2B remained **DEFERRED** and separately gated.

The then-current order was:

1. **Semantic Substrate Slice 1.** Establish only the minimal provider-neutral contracts and tests
   for source identity, evidence envelopes, freshness, confidence, observed/intended state,
   state deltas, and shared outcome semantics.
2. **Google Workspace Foundation.** Establish OAuth with PKCE, account identity, encrypted token
   storage, granted-scope inventory, explicit reconnect/grant profiles, revoke, and disconnect.
3. **Google Tasks vertical.** Prove account identity -> scoped API read -> normalized evidence ->
   provenance/freshness -> Nova awareness.
4. **Google Evidence expansion.** Gmail read -> Calendar read -> selected Drive access ->
   Docs/Sheets reads over selected resources -> unified Google awareness.
5. **Google Action expansion.** Local prepared proposals first; then one separately governed write
   family at a time.

### Google Workspace permanent boundary

```text
Google capability != Google authorization != Nova authority
connected != evidence collected != action permitted
Prepared Reality is local; creating or changing a Google resource is external mutation.
```

Google Workspace is Nova's first major external evidence/action ecosystem, but it remains below
Nova's Awareness, Decision, Authority, Execution, and Outcome architecture. An OAuth token proves
technical API eligibility only. Every operation is classified independently for data sensitivity,
mutation risk, authority, reversibility, and outcome verification.

Google outcomes must reuse Nova's existing truth vocabulary. A connector result should be able to
carry service, operation, account identity, resource identity/version, granted scope,
request-accepted, effect-verified, outcome-state/reason, partial failure, idempotency key,
authority receipt identity, and observation time. This remains a target contract, not current
runtime behavior.

OAuth scope growth is an explicit reconnect/grant event. Foundation is not blanket access. Gmail
and Drive read access must be treated according to data sensitivity, not merely labeled safe
because it is read-only. Event-driven infrastructure remains deferred until real evidence justifies
its operational cost.

## Observation-driven candidates (historical 2026-07-11 through 2026-07-28 context)

The Phase-3 observation period generated roadmap candidates from real behavior. Recorded here as
historical context; none is authorized to build merely because it appears below.

```text
SEVEN-MORNING THRESHOLD COMPLETE (2026-07-22):
  Mornings 1-7 logged and synthesized in
  docs/observation/SEVEN_MORNING_SYNTHESIS_2026-07-22.md. The synthesis declared the evidence
  threshold complete and named grounded brief/category routing the rank-1 defect. No additional
  seven-morning or open-ended observation gate is required.
  Next PRODUCT input at that time was ONE targeted post-#312 morning for additional real-use/
  product-acceptance input.
  HARDENING lane, in parallel: authorization integrity was the first post-observation hardening
  lane per docs/status/PRIORITY_LOCK_2026-07-10_AUTHORIZATION_INTEGRITY.md.

LANDED (freeze-exempt, owner-approved):
  #311  Timeout containment - isolate turns after a response timeout.
  #312  Grounded brief/category routing, merged 2026-07-23 and verified on fresh main.
  #294  Observation Step 0 documentation + protocol.
  #295  Truthful availability under dashboard refresh.
  #297  Input reliability repair.
  #298  Grounded follow-up conversation over brief items.

HISTORICAL SPEC (implemented by PR #298; retained for scope context):
  "Grounded follow-up conversation over brief items" routed discussion-shaped follow-ups to
  conversation over structured sourced session state before LLM fallback and preserved the
  unsupported-fact boundary.

STILL PARKED behind evidence at that time: model preset / governed cloud-conversation brain
(DeepSeek), gated on observed use producing a genuine model-quality signal.
```

## North Star

```text
Nova is a Jarvis-style personal butler with governed execution:
a personal butler at the interface layer,
a governed runtime at the execution layer.

Jarvis is product voice, not execution authority.
Personality may increase initiative, never authority.
Intelligence is not authority.
```

The five questions Nova should answer at all times:

```text
Is Nova healthy?
What did Nova understand?
What can Nova do now?
What needs my approval?
What happened, with proof?
```

## The Map (today -> endgame, one screen)

```text
TODAY        governed engine, thin daily product
  |
NOW gate     owner actions: Instagram, verification, filming,
  |          token rotation, Auralis-Digital security, GitHub bio
  |          (no code moves the business today)
  v
LANE A       one calm surface       (nav collapse, labels, ratchets)
LANE B       unbreakable engine     (tests, ledger, backup, contracts)
LANE C       daily usefulness       (Auralis spine: open -> pocket -> Friday)
LANE D       butler feel            (rituals, recovery, previews, receipts)
  |
HORIZON      earned Jarvis          (shadow mode -> earned autonomy ->
  |                                  household -> orb -> weekly packet)
  v
ENDGAME      a personal operating system that feels like Jarvis and
             audits like a flight recorder - authority earned one
             approved, receipted step at a time
```

## Permanent Doctrines (apply to every lane, forever)

```text
- Do Not Expand: no new branch/tool/connector/capability while
  Revenue, Proof, or Audience has not moved, unless it unblocks one.
- One PR per step. No PR implements more than one roadmap step.
- Read-only awareness boundary holds (2026-06-18 direction) until
  explicitly revised: no Shopify writes, no posting, no broad agent
  execution.
- Background doctrine: Nova may THINK in the background; Nova must
  not ACT in the background. Local-first, not local-only: cloud
  lanes allowed with clear labels, cost visibility, and no hidden
  provider switching for sensitive content.
  (NOVA_BACKGROUND_REASONING_NOT_AUTOMATION_PLAN.md)
- Remote surfaces (Telegram or any future pager) are READ-ONLY
  until an approval-identity design exists (H4). The approval
  channel is the crown jewel.
- No secrets in cross-assistant handoffs: name where credentials
  live, never paste values.
- Team operating model: ChatGPT plans/reviews, Codex and Claude
  Code are both real workers (assign by freshest context), Chris
  approves anything public/financial/destructive/legal/identity.
  Cross-assistant tasks use the handoff template: Goal / Allowed /
  Forbidden / Inputs / Credential rule / Expected output /
  Verification / Stop if.
- Approval UX principle: approval gates feel like a polished
  handoff ("I have this ready - approve, edit, or dismiss?"), not
  a security warning, unless the action is genuinely risky.
```

## NOW - Owner Actions (historical 2026-07-05 gate; not current Nova implementation ordering)

```text
1. Instagram: bio rewrite, products UTM link, highlights, unfollow batches.
2. Meta business verification.
3. Filming: first product Reel.
4. OpenClaw token rotation.
5. Small Auralis commerce/admin batch.
6. Google Merchant review check.
7. Auralis-Digital repository/hosting security migration.
8. GitHub profile bio fix.
```

These owner actions are retained as July context. They do not override the current Wave A/B/C
Nova stabilization gate.

## Lane A-D detailed bodies (2026-07-05) — RETAINED REFERENCE, not current status

> **Supersession boundary.** The detailed Lane A/B/C/D bodies below were written on
> 2026-07-05, before the Phase-3 observation cycle. They are retained as backlog/reference
> material for per-lane scope and sequencing. They DO NOT describe current status and DO NOT
> override the top current-ordering block.

## Lane A - UX Simplification

Scope authority: `docs/status/UX_SIMPLIFICATION_PRIORITY_LOCK_2026-07-02.md`.

```text
A1. UX PR 3 merged as PR #262 (quick-action reduction).
    The July front-door/roadmap truth-sync landed as PR #263 and was refreshed post-#312 in #314.
A2. PR 4 - navigation collapse; completed through PR #264.
A3. PR 5 - label rewrite + Home simplification.
A4. PR 6 - usability regression ratchets.
```

## Lane B - Engineering Robustness

```text
B1. Test suite completion / timeout containment.
    [RESOLVED 2026-07-27] full suite green after #315 + #316: 3799 passed, exit 0.
B2. Ledger hardening: rotation/compaction, hash chaining, verify command, data relocation.
B3. Runtime-state backup WITH restore drill.
B4. Async provider probes / startup-freeze root cause.
B5. Degraded-mode contract + latency budget.
B6. Monolith ratchet.
B7. Upgrade story + state schema versioning.
B8. Break-glass mode.
B9. Receipt privacy classes.
B10. Idempotency keys — required before future write capability.
B11. Local auth / session lock.
B12. Telemetry standard / OpenTelemetry conventions.

Deferred with trigger:
- Pre-action state snapshots [trigger: first write capability, alongside B10]

Five Nova-defining engineering features:
ledger integrity (B2), break-glass (B8), restore drills (B3),
idempotency keys (B10), shadow mode (H1).
```

The current Wave B truth-integrity packages are a stabilization checkpoint around this larger
engineering lane; they do not delete or reorder the broader backlog above.

## Lane C - Auralis Awareness

Scope authority: the converged Auralis-awareness specification and current Auralis product docs.

```text
C1. Auralis Today v1 — shipped/frozen baseline.
C2. Friction aging v1.1.
C3. Telegram delivery via OpenClaw pager, gated on token rotation + scheduler lifecycle repair.
C4. Friday Risk Loop / Weekly Review Packet seed.

Deferred with named triggers:
- New-product publishing checklist
- Channel review monitor
- Content queue assistant
- Product promotion readiness score
- Customer proof loop
- Finance/margin watch
- Repo health scripts
```

## Lane D - Product Coherence

```text
D1.  Unified startup hydration.
D2.  Recovery journal.
D3.  Plan preview / dry run.
D4.  Unsupported-capability recognition + why-not explanations.
D5.  Preamble-tolerant routing.
D6.  Receipts as quiet professionalism / per-answer trust summary.
D7.  Rituals: end-of-day wrap, what changed, what needs approval, what was prepared.
D8.  Stale-doc guard.
D9.  One killer demo loop.
D10. Installer / first-run reliability pass.
D11. Permission diff view.
D12. Capability dependency graph.
D13. Readiness score.
D14. Personal operating memory view.
D15. Brain trace surface.
```

Existing specs remain the substrate for those items; do not re-spec them unless current evidence
shows the contract itself is wrong.

## Horizon - Identity-Defining (not scheduled; revisit after active gates)

Theme index:

```text
Trust that evolves ......... H1, H2, H4
Presence and surfaces ...... H3, H9, H10, H18, H19
People and scale ........... H5, H15
Continuity and survival .... H6, H7
Knowledge and judgment ..... H8, H11, H13, H21
Privacy .................... H20
Business and rituals ....... H12, H14, H16, H22
Reactivity ................. H17
Ambient intelligence ....... H23-H31
```

```text
H1.  Shadow mode: capabilities audition (would-have-done receipts) before enablement.
H2.  Earned-autonomy proposals using approval history; never automatic authority.
H3.  Attention governance + attention ledger.
H4.  Approval-path security design.
H5.  Household profiles + local/revocable voice identity substrate.
H6.  Portability bundle: export/import Nova's mind in open format.
H7.  Self-drills: automated failure rehearsal with concise reporting.
H8.  Candor duty.
H9.  Orb presence light; display/presence before physical-world automation.
H10. Mobile / pocket read-only brief surface.
H11. Prioritization engine: dependency, ROI, urgency, risk, proof value, preference.
H12. Capability packs and Auralis client-services direction; parked until justified.
H13. Second Brain / future world-model substrate; Slice 1 lock accepted, deferred.
H14. Parked domains: market sandbox, YouTubeLIS, governed desktop runs / Continuous Nova.
H15. Manager hierarchy with one Personality Layer; managers never create authority.
H16. Weekly Review Packet.
H17. Signal Registry; signals start awareness, never grant execution.
H18. Co-Work Page for governed multi-run future.
H19. Premium online voice lane as presentation-only upgrade.
H20. Sensitive-data routing with provider-level privacy modes; mandatory before connector expansion.
H21. Adaptive knowledge system — adapt in knowledge first, planning second, execution last.
H22. GaaS/commercial framing using the same governed understand -> propose -> approve -> execute -> remember loop.
H23. Prepared Reality: prepared-but-unexecuted next moves.
H24. Night Cycle: background reasoning/consolidation/preparation, no action authority.
H25. Temporal recall over ledger + memory evidence.
H26. Presence rituals through read-only signals.
H27. Explicit session-scoped co-watching built on screen-awareness capabilities.
H28. What-if simulator: deterministic scenario math, proposal only.
H29. Generative UI from constrained widget vocabulary.
H30. Multimodal intake over explicitly supplied/approved inputs.
H31. MCP-governed connector boundary + Governor permissions + receipts + privacy routing.
```

Detailed historical substrate references for H1-H31 remain discoverable in Git history and the
referenced `future/` / `docs/future/` design documents. This Wave A1 edit does not activate,
re-scope, or delete any horizon item.

## Horizon Graduation Rule

Horizon items graduate via the promotion ladder in `future/brain/PROMOTION_PATH.md`:

```text
idea -> future planning doc -> implementation design -> schema/
contract -> dry-run prototype -> tests -> trust/review surface ->
governed runtime integration -> generated runtime truth -> docs
```

No horizon item skips stages. Usefulness is not implementation.

## Historical Ordering Summary

```text
DONE (historical cycle)
  A1 front-door/roadmap truth-sync (#263, refreshed #314).
  A2+B2 navigation collapse + ledger start (#264).
  B1 full-suite stall cleared (#315+#316; 3799 passed on merged main at that time).
  C1 Auralis Today v1 shipped/frozen.
  Seven-morning observation complete; #311 timeout containment; #312 grounded brief/category routing.

OWNER (parallel historical business actions)
  Instagram, verification, filming, token rotation, Auralis-Digital security, GitHub bio.

PARKED / SEPARATE DECISIONS AT THAT TIME
  Connection-truth repair.
  Runtime-generator reconciliation.
  Business-context freshness/tense.
  Corruption-safe loading unless an actual failure is observed.
  Tasks -> Gmail -> Traffic as a separate gap-fill list.

LATER (unchanged horizon ordering)
  A3-A4 labels, Home, ratchets.
  B3-B12 engineering robustness backlog.
  C2-C4 Auralis awareness progression.
  D1-D15 coherence layer.
  H1-H31 horizon via the promotion ladder.
```

## Supersession Note

This document supersedes, as ordering authority only:

```text
docs/future/ROADMAP.md and older dated plan/vision docs in docs/future/
docs/todo/ACTIVE_TODO.md priority ordering (items may remain valid task inventory)
"4-15-26 NEW ROADMAP" directory as archive/future-reference ordering
future/ root tree ordering — content remains design reference; PROMOTION_PATH.md is adopted
docs/future/ai_ecosystem_operating_model/ — docs-only coordination reference
```

Their content remains valid as design/reference material unless separately superseded. Nothing is
promoted merely by existing in a future/archive tree.

For classification of uncited `docs/future/` documents, use `docs/future/FUTURE_DOCS_MAP.md`.
That map records status only; it does not promote work into an active lane.

Alignment notes:

- generated/runtime truth beats roadmap language for implemented-behavior claims, but generated
  evidence is authoritative only for what its machinery actually measures;
- lane locks/specs remain scope authority;
- current operational truth lives in the Wave A1-reconciled status/canonical surfaces;
- `docs/todo/TECH_DEBT.md` agent-scheduler repair remains a named gate on historical C3;
- older Auralis business-direction statements remain historical/business context rather than Nova
  runtime authority;
- no roadmap or future document may turn memory, learning, recommendations, OAuth scopes, or
  repeated success into execution authority.

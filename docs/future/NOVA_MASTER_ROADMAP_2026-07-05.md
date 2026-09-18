# Nova Master Roadmap - 2026-07-05 (Final)

Status: canonical ordering document — the single source of truth for what comes next and in
what order, across all lanes. Assembled 2026-07-05 from the live session, the pre-PR-4 code
audit, and a full mining pass over all three archive trees (docs/future/, future/,
"4-15-26 NEW ROADMAP").

Authority rules:

```text
1. This document ORDERS work. It does not re-scope work.
2. Lane-specific lock docs remain the scope authority for their lane
   (e.g. UX_SIMPLIFICATION_PRIORITY_LOCK_2026-07-02.md for Lane A).
3. Everything in docs/future/ and the root future/ tree NOT
   referenced by this document is reference/archive material, not
   an active priority.
4. When this document and an older doc disagree on ordering, this
   document wins. When they disagree on scope, the lane lock wins.
```

## Current post-#405 beta-readiness order — 2026-09-17

```text
BETA_READINESS_SEQUENCE_V1: ACTIVE
verified main at sync start: 4e32b501934e176e89e049fef5597ccdaaa4e6c8
#397 through #405: COMPLETE / MERGED
COMPLETE: #406 governed-memory ID collision correctness (PR #411; main `ca66a06d`)
COMPLETE: #408 durability/state-ownership decision (PR #412; main `2592ad91`)
COMPLETE: durability implementation lane 1 - canonical state registry/migration detection (PR #413; main `e74fdca0`)
COMPLETE: durability implementation lane 2 - corruption-safe readers (PR #416; main `80e1c86f`)
COMPLETE: durability implementation lane 3 - maintenance locking + mutation quiescence (PR #419; main `2bfe202e`)
COMPLETE: durability implementation lane 4 - versioned snapshot + manifest (PR #421; main `4e32b501`)
FRESH-MAIN CLOSEOUT: PASS (314 focused durability/operational-truth tests passed; 1 expected Windows POSIX-FIFO skip; runtime structural smoke PASS)
NEXT: #409 release integrity / repository control (separately scoped)
THEN: rebase and exact-head review #410 private-beta freeze criteria
THEN: separate owner authorization decision for recovery construction (Lane 5A)
THEN: separately authorized recovery proof: inactive candidate migration -> candidate validation -> activation -> rollback/restore semantics
THEN: clean Windows operator proof
THEN: frozen-SHA full beta acceptance
THEN: private-beta candidacy/distribution decision
```

Google/provider expansion remains paused. Operational Continuity implementation remains paused.
New capabilities remain paused. Voice expansion remains paused. Broader UI work remains paused.
Other feature expansion remains paused. This order supersedes older current-order language below and grants
no new capability or authority.

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
proof, OpenClaw work, or delegation. Current status and ordering are recorded immediately below.

## Current Ordering — 2026-08-28

The post-#394 boundary is now:

```text
#388 COMPLETE
#368 COMPLETE
#387 COMPLETE / DOCS-ONLY
#393 COMPLETE / EXACT-HEAD PROOF POLICY
#394 GOOGLE WORKSPACE FOUNDATION COMPLETE / MERGED
main at reconciliation start: 691a397d14e93c1e0607a73de2ab54b9bbfc3cc2

Historical PR #335: OPEN / DRAFT / UNMERGED / UNTOUCHED
Historical PR #335 implementation path: SUPERSEDED BY MERGED PR #394

NEXT: Google identity-only live proof
LATER / SEPARATE AUTHORIZATION REQUIRED: Google Tasks READ -> minimal Continuity -> owner daily-use proof
```

The next item is a real-provider proof of the already merged foundation, not a new implementation
lane. It authorizes no additional scope, Google domain-data access, or capability. The pre-#394
ordering below is retained as historical decision provenance and is superseded where it conflicts
with this block.

### Historical pre-#394 ordering

Current repository HEAD is moving state and must be resolved from Git when needed. Issue #387 was
executed from `main@4fc7ab2de1047c49d4649d7239cafc9174e8f5fc`, after PR #391 closed Issue
#368. That SHA is execution provenance for this docs-only synchronization; it is not a permanent
alias for current HEAD and is not the validated runtime baseline.

The immutable Wave C runtime-validated baseline remains:

```text
validated_baseline_sha: ec20a7146f7d6d55b8983cb7d6d3918d5fad9915
```

Later documentation, truth-checker, terminology, and roadmap merges do not establish a new
runtime-validated baseline.

### Completed stabilization and truth-hardening chain

```text
Wave A1 operational truth synchronization       COMPLETE / MERGED
Wave A2 strategy reconciliation                 COMPLETE / MERGED
Wave B1 runtime-truth instrumentation           COMPLETE / MERGED
Wave B2 capability narration                    COMPLETE / MERGED
Wave B3 memory governance                       COMPLETE / MERGED
Wave B4 reproducibility hygiene                 COMPLETE / MERGED
Wave C full-system validation                   COMPLETE / MERGED / VALIDATED
post-Wave-C documentation and truth hardening   COMPLETE through PR #385
Issue #388 truth/checker prerequisite            COMPLETE / CLOSED via PR #390
Issue #368 workspace/session terminology proof  COMPLETE / CLOSED via PR #391
Issue #387 long-lived roadmap synchronization   COMPLETE / DOCS-ONLY (this block)
```

The August 12 P1/P2 stabilization packages (#337 through #352) are also merged and historical.
They must not be selected again as pending work without new reproduced evidence. Issue #388 was a
truth/checker correction, not a runtime lane. Issue #368 qualified existing workspace/session
continuity wording; it did not implement Operational Continuity or authorize Google work.

### Historical pre-#394 decision order

```text
COMPLETED BOUNDED CONSISTENCY WORK
  #388
  -> #368
  -> #387

NEXT PROOF-PATH / PROCESS DEBT
  establish a trustworthy executable proof path
  -> resolve Issue #354 if practical, or preserve an explicitly accepted exact-head local/Codex path
  -> revisit branch/review protection and required-check policy with that proof path

SUPERSEDED IMPLEMENTATION PATH
  historical PR #335: OPEN / DRAFT / UNMERGED / UNTOUCHED
  -> superseded by merged PR #394

CURRENT PROOF INPUT
  Google identity-only live proof
  -> Google Tasks READ / first provider-backed Google evidence vertical
  -> later Google READ/evidence verticals
  -> evidence-based Operational Continuity warrant
```

Issue #354 remains open proof-path infrastructure debt. GitHub-hosted jobs that execute zero steps
are `NOT EXECUTED`, not behavioral PASS or behavioral FAIL. The Wave C owner waiver remains valid
for the immutable baseline above; it does not make those hosted jobs successful and does not
automatically waive proof requirements for security-sensitive #335 reconstruction.

PR #335 remains **OPEN / DRAFT / UNMERGED / UNTOUCHED** at historical head
`befb69ef75881a9f418472549b64243219c138f9`, with historical base
`c44b6d0cd72f0f91a6ec517427ad3fe2076beb30`. It is not the current task and must not be merged,
reconstructed, rebased, or modified; PR #394 supersedes it as the implementation path. Connection Foundation,
OAuth scope, or an existing draft branch do not grant Nova capability or authority.

If reconstruction is later authorized, the four confirmed lifecycle findings remain required:

1. invalid OAuth callbacks must not consume a legitimate authorization attempt;
2. post-token identity lookup failure must best-effort revoke issued refresh/access credentials
   and avoid external/local lifecycle mismatch;
3. identity proof must require explicit `email_verified is True` rather than accepting a missing
   claim; and
4. insufficient-scope grants must not silently retain reusable provider credentials; prefer
   best-effort revocation and metadata-only `SCOPE_INSUFFICIENT` unless retention is separately
   justified and security-reviewed.

### Public / Product Readiness Track — Issue #386

Issue #386 is a parallel, planned, non-runtime, and **non-authorizing** readiness track. It does
not displace the technical order above. It permits planning/preparation only; actual publication,
outreach, data collection, access grants, visibility changes, licensing changes, or telemetry each
require a separate owner decision.

```text
NOW / PARALLEL, NON-RUNTIME PREPARATION
  public-story / landing-page draft
  -> naming and brand review
  -> early-access design
  -> design-partner candidate identification
  -> Google onboarding / OAuth ownership decision planning
  -> separate owner decision for actual publication, outreach, or data collection

PUBLIC-ALPHA GATE AFTER ORDERED TECHNICAL PROOF
  Google identity + first provider-backed read evidence
  -> publication audit of source, Git history, and GitHub metadata
  -> licensing and third-party redistribution review
  -> applicable Google external-user / OAuth production readiness
  -> local attack-surface and supply-chain/reproducibility proof
  -> newcomer and community-health surfaces
  -> visibility-transition and protection plan
  -> clean-machine and outside-user hero-flow proof
  -> tagged immutable alpha release
  -> separate owner decision on public/source-available repository release
```

Operational Continuity is not a prerequisite for technical public alpha. Public preparation is
not publication authority; a public story is not a public repository; source-available is not
open source; outside-user evidence is not runtime authority; local observability is not outbound
telemetry; and repository visibility is not release readiness.

Operational Continuity remains **STRATEGICALLY ACCEPTED / INACTIVE / NOT
IMPLEMENTATION-AUTHORIZED**. It surrounds Awareness, Decision, Authority, Execution, and Outcome
as persistent reconciled state; it is not a sixth authority system. Its expansion remains earned
by trustworthy provider-backed evidence and demonstrated user value.

The future governed-protection-wall concept is long-term security/digital-sovereignty reference
material. It does not replace Nova's current product identity, activate a runtime lane, or displace
the current Google-evidence -> Continuity ordering.

Permanent boundaries:

```text
current HEAD != immutable validated runtime baseline
completed stabilization != authorization for #335
#388 prerequisite truth correction != runtime lane
#368 technical completion != #335 authorization
#335 pending decision != #335 next task
connection != capability
capability != authority
Google capability != Google authorization != Nova authority
connected != evidence collected != action permitted
recommendation != permission
request acceptance != verified effect
memory != Operational Continuity
public story != public repository
source-available != open source
public preparation != public publication authorization
outside-user evidence != runtime authority
local observability != outbound telemetry
repository visibility != release readiness
```

This current block orders work but authorizes no runtime/source change, generated-runtime-artifact
edit, #335 mutation or merge, Google/OAuth implementation, Google domain-data access, external
write, capability/authority expansion, Operational Continuity runtime, public publication or
outreach, private-repository collaborator grant, repository visibility change, license change,
telemetry transmission, broad OpenClaw expansion, provider expansion, or new stabilization wave.

## Historical Ordering — 2026-08-12 (superseded by the block above)

`main` was at `c44b6d0cd72f0f91a6ec517427ad3fe2076beb30` after PR #334.

Durable state since the prior ordering block:

- PR #333 merged the roadmap/current-state reconciliation.
- PR #334 merged Semantic Substrate Slice 1. Its provider-neutral source/evidence/state/outcome
  contracts and tests are durable infrastructure; it added no provider call, Google integration,
  capability, authority, or execution path.
- PR #335 contains the implemented Google Workspace identity-only foundation, but remains
  **DRAFT / UNMERGED** at `befb69ef75881a9f418472549b64243219c138f9`. Draft implementation is
  not current-main capability.

The 2026-08-12 fresh-main real-user acceptance record is
`../observation/FRESH_MAIN_REAL_USER_ACCEPTANCE_2026-08-12.md`. It is prospective planning evidence
against the exact then-current-main SHA above. The supplied 25-step golden regression was covered
with additional targeted probes; the complete 36-section stress catalog was not fully exercised.

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
2. After P1-A separately merges, run targeted P1-A fresh-main live proof: Calendar-write claim,
   streamed reminder truth, persistence success/failure/timeout, and no unauthorized execution.
3. Bound and implement P1-B as a separate package under its own reviewed authorization.
4. After P1-B separately merges, run targeted P1-B / live P1 fresh-main proof: action-history
   correlation, background-read recap truth, verified/failed/unknown outcomes, and no unauthorized
   execution.
5. Address P2 findings by failure class, not one broad cleanup PR:
   - capability/copy truth — Google Tasks narration and background-alert claims;
   - deterministic routing/temporal/source truth — arbitrary-location weather, `tomorrow` Calendar,
     schedule cancellation, private Drive intent, verification routing, and related stress gaps;
   - News governed-parameter defect — establish the callback/canonicalization hypothesis with a
     focused regression before calling it root cause.
6. Complete the untested/partial rows from the 36-section catalog.
7. Run the full fresh-main regression, combining the golden 25-step flow with the remaining
   high-value stress cases rather than repeating proven authority paths unnecessarily.
8. Resume PR #335 review. Any branch modification, ready transition, or merge remains separately
   authorized. The pause does not cancel or invalidate its existing implementation.
9. If #335 merges, prove the identity-only foundation live: account identity, granted scopes,
   credential validity/refresh, reconnect, revoke, disconnect, and absence of token leakage.
10. Only then select **Google Tasks READ** as the first Google domain-data vertical. A Tasks write,
   Gmail/Calendar/Drive/Docs/Sheets evidence, and later Google actions remain separately ordered,
   separately scoped, and separately authorized.

This historical sequence is retained as provenance. Its P1/P2 pending-work language is superseded
because #337-#352 have since merged.

### Continuity Model strategic ordering

The Continuity Model was already **STRATEGICALLY ACCEPTED / INACTIVE / NOT
IMPLEMENTATION-AUTHORIZED**. It is persistent reconciled state surrounding Awareness, Decision,
Authority, Execution, and Outcome; it is not a sixth system or an authority plane.

Earliest consideration remained after the then-ordered stabilization and Google evidence work:

```text
P2 stabilization
-> remaining acceptance coverage
-> full fresh-main regression
-> Google Workspace Foundation review/merge decision
-> live identity-only proof
-> first Google READ/evidence vertical
-> separately warranted, scoped, authorized, implemented, and proved Continuity Slice 1
```

Permanent boundary:

```text
Google capability != Google authorization != Nova authority
connected != evidence collected != action permitted
Prepared Reality is local; creating or changing a Google resource is external mutation.
```

Authorization Integrity Slice 1 remained merged through PR #325. Slice 2A remained separately
owner-approved, paused, and not implemented on main. Slice 2B remained deferred and separately
gated.

## Historical Ordering — 2026-08-09 (superseded by the blocks above)

`main` is at `dfef1db5df89bfdb276904acce26205d1c894331` after PR #332. The meaningful
post-#319 sequence is concise:

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
SHA and branch were not captured. This closes the pending product-selection input without
fabricating missing runtime provenance.

The selected product repair is now complete. Fresh-main verification at
`dfef1db5df89bfdb276904acce26205d1c894331` proved the exact August 7 natural handoff, real
reminder persistence, same-session `show schedules` and `reminders`, fresh-session retrieval, and
preservation of calendar-query routing. The Commitment Truth lane is CLOSED. The separate
`tomorrow` calendar-scope wording defect was outside this proof and remains inactive.

PR #331's local-action outcome-truth lane is also CLOSED after merged-main live proof. Nova now
preserves the distinction between launch/request acceptance and visible-effect verification in
the action response, durable receipt, and later receipt consumers.

Authorization Integrity Slice 1 is **MERGED**. Slice 2A is **NOT IMPLEMENTED ON MAIN** and remains
separately owner-approved under its existing exact scope and publication boundary. It is paused;
this ordering neither cancels nor activates it. Slice 2B is **DEFERRED** and separately gated.

Current order at that time:

1. **Semantic Substrate Slice 1.** Establish only the minimal provider-neutral contracts and tests
   for source identity, evidence envelopes, freshness, confidence, observed/intended state,
   state deltas, and shared outcome semantics. No network/provider I/O, runtime capability,
   authority, execution, migration, or broad refactor belongs in Slice 1.
2. **Google Workspace Foundation.** Establish OAuth with PKCE, account identity, encrypted token
   storage, granted-scope inventory, explicit reconnect/grant profiles, revoke, and disconnect.
   Connection alone reads no domain data and performs no domain mutation.
3. **Google Tasks vertical.** Prove account identity -> scoped API read -> normalized evidence ->
   provenance/freshness -> Nova awareness. Only afterward may a separately scoped Tasks write
   family prove operation-level authority, idempotency, effect verification, and reconciliation.
4. **Google Evidence expansion.** Gmail read -> Calendar read -> selected Drive access ->
   Docs/Sheets reads over selected resources -> unified Google awareness.
5. **Google Action expansion.** Local prepared proposals first; then one separately governed write
   family at a time. Push/event synchronization is optional and requires evidence that polling or
   refresh-on-use is insufficient.

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
authority receipt identity, and observation time. This is a target contract, not current runtime
behavior.

OAuth scope growth is an explicit reconnect/grant event. Foundation is not blanket access. Gmail
and Drive read access must be treated according to data sensitivity, not merely labeled safe
because it is read-only. Event-driven infrastructure remains deferred until real evidence justifies
its operational cost.

Secondary candidates - arbitrary-location weather routing, stale Auralis freshness,
local-first identity copy, visible STT/TTS state, startup cohesion, and the separate `tomorrow`
calendar-scope wording defect - remain historical/inactive here. No economic-value proof, expanded
OpenClaw, browser/computer-use, financial-write, outreach, posting, contracting,
autonomous-business, or delegation lane was active.

## Observation-driven candidates (historical 2026-07-11 through 2026-07-28 context)

The Phase-3 observation period generates roadmap candidates from real behavior. Recorded here
as they surface; none is authorized to build except via the stated gate.

```text
SEVEN-MORNING THRESHOLD COMPLETE (2026-07-22):
  Mornings 1-7 logged and synthesized in
  docs/observation/SEVEN_MORNING_SYNTHESIS_2026-07-22.md. The synthesis declared the evidence
  threshold complete and named grounded brief/category routing the rank-1 defect. No additional
  seven-morning or open-ended observation gate is required.
  Next PRODUCT input is ONE targeted post-#312 morning for additional real-use/product-acceptance
  input (PR #312 is already verified on fresh main per
  docs/status/GROUNDED_BRIEF_ROUTING_CLOSEOUT_2026-07-23.md; this is not that verification),
  then owner selection of the next evidence-ranked product-usability lane. Two distinct lists
  feed that choice (none authorized here):
    Synthesis-ranked secondary repairs (each a separate decision):
      - connection-truth/source-label repair;
      - runtime-generator (fingerprint) reconciliation;
      - business-context freshness/tense repair: stale past-dated memory-derived status
        (e.g. "Watch: July 9...") must not present as current; separately authorize; no
        business action or external write;
      - corruption-safe loading stays PARKED unless an actual corruption/loading failure is observed.
    Standing personal gap-fill list (NOT synthesis-ranked): Google Tasks -> Gmail -> Traffic.
  The post-#312 morning determines whether any product gap is selected.
  HARDENING lane, in parallel (do not lose): authorization integrity is the FIRST
  post-observation hardening lane per
  docs/status/PRIORITY_LOCK_2026-07-10_AUTHORIZATION_INTEGRITY.md. Its sequencing steps 1-2 are
  satisfied, so it is activatable in parallel priority with the top product lane and is superseded
  only by a higher-severity correctness/governance defect. LOCK ONLY; not started here.

LANDED (freeze-exempt, owner-approved):
  #311  Timeout containment - isolate turns after a response timeout so a timed-out model turn
        no longer blocks the next deterministic request (Morning 6-7 evidence).
  #312  Grounded brief/category routing (synthesis rank-1 defect), merged 2026-07-23 -
        "show me <category> news" reaches governed Cap 49; brief/story follow-ups bind to the
        rendered Cap 50 clusters / active surface; numeric story commands resolve against a
        stable active-surface map; one confidence value feeds body + Trust; deterministic
        source-bounded fallback preserved. 205 focused tests, prove_runtime_truth PASS, live
        branch verification plus fresh-main verification
        (docs/status/GROUNDED_BRIEF_ROUTING_CLOSEOUT_2026-07-23.md). This shipped the scope
        earlier called "Slice 1"; lane now CLOSED.
  #294  Observation Step 0 (documentation + protocol) — morning-log template + single launch
        procedure + config truth (runtime reads Windows User-scope env, not nova_backend/.env).
  #295  Truth-critical repair — Truthful availability under dashboard refresh: fixed false
        "not configured" labels for news + weather (news 180s cache vs cap-56 rate-limit
        exhaustion; weather widget-envelope unwrap; honest "temporarily unavailable" language;
        news no longer blames Brave).
  #297  Input reliability repair - dashboard websocket idle/reconnect loop fixed with visible
        keepalive, server ping no-op, hidden-tab reconnect suppression, and refocus reconnect
        once. Post-merge smoke from main passed.
  #298  Grounded follow-up conversation over brief items - fetch prompts stay deterministic;
        follow-ups over loaded news/weather/calendar/runtime brief facts answer from structured
        sourced session state before LLM fallback. Guardrails prevent unsupported fact
        laundering, background focus theft, unrelated prompt routing, GeneralChat prompt
        contamination, news refresh identity drift, and calendar event-order drift. Post-merge
        smoke from main passed.

HISTORICAL SPEC (implemented by PR #298; retained for scope context):
  "Grounded follow-up conversation over brief items" — route discussion-shaped follow-ups
  ("what do you think about that?") to the conversation lane instead of the widget; inject the
  sourced brief facts (news/weather/calendar) already in session_state into the LLM context;
  keep unsupported claims tagged, not laundered (the P0 hallucination boundary). This lane was
  the prerequisite before any local-vs-cloud (DeepSeek) model-quality test was meaningful: a
  pre-#298 read-only trace confirmed the conversation LLM received no brief facts, so a weak
  conversation would have been plumbing evidence, not model evidence.
  memory "grounded-conversation-lane" + docs/status/DAILY_COMMAND_CENTER.md (2026-07-11 block).

STILL PARKED behind evidence: model preset / governed cloud-conversation brain (DeepSeek),
gated on observed use of the grounded follow-up path producing a genuine model-quality signal.
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

## NOW - Owner Actions (the gate in front of the roadmap, cost ~zero)

```text
1. Instagram: bio rewrite (approved 4-line copy), single /products
   UTM link, rename highlights (Shop / Custom / Drops / Made to
   Order), start unfollow batches. Afterwards confirm the bio link
   renders on the logged-out/incognito view.
2. Meta business verification.
3. Filming: first product Reel (Sun of Life sherpa), WELCOME10 in
   caption. Reviewed in Meta Business Suite before posting.
4. OpenClaw token rotation (three locations, including
   NOVA_OPENCLAW_BRIDGE_TOKEN in nova_backend/.env).
5. Small batch: footer signup retitle, order-email branding, tag
   order #1001 as family in Shopify admin, proof email to pillow
   customer, phone storefront walkthrough ("can I see the art?"),
   Depth hoodie L-only decision.
6. Scheduled (2026-07-05 owner item; the July 9 date is now past): Google Merchant review check.
7. SECURITY: Auralis-Digital repo is PUBLIC with the business
   playbook readable (profit table, margins, operating rhythm,
   internal/) because free-plan GitHub Pages serves the site from
   it. Fix: migrate hosting to Netlify/Cloudflare Pages from a
   private repo, then flip the repo private (git rm alone does NOT
   fix history). Same exposure class that motivated the NovaLIS
   privacy flip, on the repo that matters more.
8. GitHub profile bio fix (two minutes, alongside the Instagram
   bio): "Building Nova - a local-first, governed AI system.
   Intelligence proposes, Nova governs, you decide." Add website
   link once hosting is settled.
```

## Lane A-D detailed bodies (2026-07-05) — RETAINED REFERENCE, not current status

> **Supersession boundary.** The detailed Lane A/B/C/D bodies below were written on
> 2026-07-05, before the Phase-3 observation cycle. They are retained as backlog / reference
> material for per-lane scope and sequencing. They DO NOT describe current status and DO NOT
> override the top current-ordering block. The observation-candidate and
> historical ordering sections preserve earlier status only. Where a body below says a lane is
> "active", "next", "not yet built", or
> "after A2 lands", read it as 2026-07-05 framing, superseded. Completed since: A1 (the July
> truth-sync), A2+B2 (PR #264), C1 (Auralis Today, shipped/frozen). The current 2026-08-20
> Wave A1 uses the same label for a new operational-truth checkpoint; it does not reopen the
> historical July A1 task.

## Lane A - UX Simplification (2026-07-05 lane body — see supersession boundary above)

Scope authority: `docs/status/UX_SIMPLIFICATION_PRIORITY_LOCK_2026-07-02.md`.

```text
A1. UX PR 3 merged as PR #262 (quick-action reduction, branch
    ux/quick-action-reduction, commits 5f8a924 and a1b54a8).
    [DONE] Landing this roadmap as a docs-only PR + refreshing the stale
    front-door docs was the A1 task; complete via PR #263 and the
    post-#312 front-door/status refresh in PR #314.
A2. PR 4 - navigation collapse: move Agent, Rules, Activity, and
    status/debug surfaces behind Settings -> Advanced. Includes
    cross-page quick-action chip cleanup and frontend mirror sync.
A3. PR 5 - label rewrite + Home simplification.
    Build from NOVA_USER_FACING_LANGUAGE_GUIDE_2026-04-28.md.
A4. PR 6 - usability regression ratchets (nav count, quick-action
    count, label lint).
```

## Lane B - Engineering Robustness (rides alongside Lane A)

B1-B2 may ride with the PR 4 work session; the rest queue behind Lane A.

```text
B1. Test suite completion: install pytest-timeout (config already
    references it; plugin missing), convert the 85-91% stall into a
    named failing test, then fix it. Everything inherits this.
    [RESOLVED 2026-07-27] pytest-timeout present; the 85-91% stall did not
    reproduce on merged main; the isolation/hermeticity failures it masked were
    fixed in #315 + #316; full suite green (3799 passed, exit 0).
B2. Ledger hardening: rotation/compaction (file is ~475 MB), hash
    chaining for tamper evidence, `ledger verify` command, relocate
    out of src/data/.
B3. Runtime-state backup WITH restore drill: scheduled copy of
    ledger + memory + data + .env inventory to a second location,
    plus periodic automated restore into a temp runtime verifying
    memory count, ledger chain, settings, and capabilities. Backup
    is not real until restore works; emits a "backup verified"
    receipt.
B4. Async provider probes: fix the root cause of startup freezes
    (sync Ollama/provider calls blocking the event loop), not just
    the hydration symptom.
B5. Degraded-mode contract: tested promise that Nova opens useful
    within N seconds with Ollama down / no network / no connectors.
    Latency budget (open -> greeting) as a CI-tested contract.
B6. Monolith ratchet: CI check for no net line growth in
    session_handler.py (4,176 lines) and brain_server.py (3,324).
B7. Upgrade story + state schema versioning: documented
    deliberate-change path for the constitutional model lock;
    explicit schema versions and migration checks for ledger,
    memory, goals, profiles, provider settings, and schedules.
B8. Break-glass mode: one command that puts Nova read-only
    immediately - stop scheduled runs, block external effects,
    disable approvals, keep chat/brief/status alive.
B9. Receipt privacy classes: receipt fields classified
    (safe-to-show / private / secret / redact-by-default /
    export-only-with-confirmation).
B10. Idempotency keys: stable action ids on every effectful action
     so retries cannot duplicate effects. REQUIRED before any
     future write capability.
B11. Local auth / session lock: trusted device, optional PIN,
     idle lock, re-auth for sensitive pages.
B12. Telemetry standard: adopt OpenTelemetry conventions for
     traces (request paths), metrics (latency/errors/tool use),
     and logs - feeding D12/D13/D15 and the degraded-mode contract
     (B5). Spacecraft-grade observability; boring until it saves
     you.

Deferred with trigger:
- Pre-action state snapshots ("before" state in receipts)
  [trigger: first write capability, alongside B10]

The five most Nova-defining engineering features (agreed 2026-07-05):
ledger integrity (B2), break-glass (B8), restore drills (B3),
idempotency keys (B10), shadow mode (H1).
```

## Lane C - Auralis Awareness (2026-07-05 lane body — C1 has since shipped; see boundary above)

Scope authority: converged spec in Claude memory (auralis-awareness-direction) — one data
spine, three deliveries. Do not re-derive the plan. When Lane C opens, commit the spec into
the repo as C1's design doc so it is visible to any worker, not only sessions with Claude
memory access.

```text
C1. Auralis Today v1: build_auralis_today_section() in
    awareness_brief.py. Five lines: Status / Revenue Reality /
    Owner Blocker / Best Move Today (deterministic) / Watch.
    Connector extensions: order tags, discountCodes (WELCOME10),
    publication counts. Memory seeds: locked decisions, owner-action
    queue (needs_chris / agent_doable / scheduled / blocked), static
    promotion queue, proof-asset checklist, customer message draft
    bank.
C2. Friction aging v1.1: 7-day stale owner task -> suggest smallest
    next step (pre-authored per item).
C3. Telegram delivery via OpenClaw pager: same spine, read-only.
    GATED on (a) owner token rotation (NOW item 4) AND
    (b) agent_scheduler.py lifecycle repair (open TECH_DEBT item:
    suppression recording, trigger/completion logging,
    duplicate-window anti-spam). Hardening subset per
    OPENCLAW_ROBUST_HARDENING_AUDIT_2026-05-01.md applies even to
    read-only delivery (envelope, budgets, receipts).
C4. Friday Risk Loop: weekly spine variant + finance/support checks
    (taxes, payouts, refunds, disapprovals, abandoned checkout,
    unanswered messages, account security/2FA status, reviews-app
    health). Seed of the endgame Weekly Review Packet (H16).

Deferred with named triggers (do not build early):
- New-product publishing checklist  [trigger: next new product]
- Channel review monitor            [trigger: Merchant Center connector]
- Content queue assistant           [trigger: posting cadence exists]
- Product promotion readiness score [trigger: 8-post rollout underway]
- Customer proof loop               [trigger: stranger orders exist]
- Finance/margin watch              [trigger: first public sale]
- Repo health scripts (gitleaks weekly, branch/drift checks)
  [plain scheduled scripts, NOT Nova capabilities]
```

## Lane D - Product Coherence (after Lanes A-C v1)

The butler-feel layer, ordered by value:

```text
D1.  Unified startup hydration: one composed startup payload
     replacing the widget command burst (pairs with B4).
D2.  Recovery journal: failures narrated as receipts.
D3.  Plan preview / dry run: "what I understood / can prepare /
     needs approval / will not do" before multi-step or
     higher-authority requests. Includes command decomposition
     (multi-intent classification, no auto-execution).
D4.  Unsupported-capability recognition + "why not" explanations:
     refusals that name the missing path. Refusal becomes trust.
D5.  Preamble-tolerant routing for deterministic commands.
D6.  Receipts as quiet professionalism: user-facing receipt
     language pass ("Prepared draft only. No message sent.").
     Includes the per-answer trust summary ("Nothing left this
     device. No tools ran. 3 suggestions prepared. 2 memories
     used. 0 secrets exposed.") - visible trust as the
     differentiator most assistants hide.
D7.  Rituals: end-of-day wrap, "what changed while you were away",
     "what needs approval", "what I prepared". Include explicit
     privacy assurance lines when true: "nothing ran / nothing
     left this device".
D8.  Stale-doc guard: front-door freshness check.
D9.  One killer demo loop: open -> Daily Brief -> notices issue ->
     prepares email draft -> approval -> receipt -> What Changed.
D10. Installer / first-run reliability pass.
D11. Permission diff view: "this grants X, still does not allow Y,
     new risks Z". No blind approvals.
D12. Capability dependency graph: human-readable degraded causes.
     Pairs with B5.
D13. Readiness score: healthy / useful / degraded / setup needed,
     from model, ledger, backup freshness, connectors, runtime
     health, and drill status.
D14. Personal operating memory view: active projects, open loops,
     preferences, routines, recent decisions, rejected suggestions
     - "I remembered this because you approved it". Context, never
     permission.
D15. Brain trace surface: user-visible trace cards. BrainTrace
     already exists implemented and non-authorizing - this item is
     SURFACING it, not building it.

Existing specs to build from (do NOT re-spec):
- D2  -> NOVA_FAILURE_MODE_PLAYBOOK_2026-04-28.md
- D3  -> NOVA_APPROVAL_QUEUE_PRODUCT_PLAN_2026-04-27.md + old
         ROADMAP.md Boundary Detector / Uncertainty Classifier
- D6  -> NOVA_USER_FACING_LANGUAGE_GUIDE_2026-04-28.md
- D12 -> TRACE_AND_OBSERVABILITY_SPEC.md
- D15 -> NOVA_TRUST_SPANS_TRACE_CARDS_PLAN_2026-04-27.md (15 span
         types; "show decisions and evidence, not private
         chain-of-thought")
```

## Horizon - Identity-Defining (not scheduled; revisit after Lanes A-D v1)

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
Ambient intelligence ....... H23-H31 (sci-fi now: prepared
                             reality, night cycle, temporal
                             recall, presence, co-watching,
                             what-if, generative UI, multimodal
                             intake, MCP boundary)
```

```text
H1.  Shadow mode: capabilities audition (would-have-done receipts)
     before enablement. Try-before-trust. Substrate:
     future/governed_desktop_runs/ (envelope schema, state machine,
     policy evaluator); the promotion ladder's dry-run stage is
     shadow mode by another name.
H2.  Earned-autonomy proposals: Nova cites its own approval record
     to propose standing approvals. Governance that visibly learns.
     Substrate: AUTO_APPROVAL_POLICY.md graduated levels (0 none /
     1 read-only / 2 preparation / 3 limited / 4 trusted flow);
     RECEIPT_TO_MEMORY.md promotion policy (receipts -> structured
     learning records, never automatically); LEARNING_LAYER_SPEC.md
     epistemic ladder (observed_signal -> candidate -> confirmed ->
     doctrine). H1+H2 are the defining differentiator: how Nova
     becomes Jarvis one receipted step at a time.
H3.  Attention governance + attention ledger: interruption budget,
     batching, interruptions logged as first-class events with
     dismissed/useful outcomes. Urgent once the pager exists.
H4.  Approval-path security design (unlocks remote approvals; until
     then remote stays read-only per doctrine).
H5.  Household profiles: per-person governance (src/profiles seed).
     Technical foundation: local voice identity / speaker
     recognition (enrolled voices only, on-device, revocable) so
     each speaker automatically gets their permission profile.
H6.  Portability bundle: export/import Nova's mind, open format.
H7.  Self-drills: monthly automated failure rehearsal, one-line
     report in the brief.
H8.  Candor duty: personality-layer permission to disagree and to
     surface what the user is avoiding.
H9.  Orb presence light (Nova-Orb-Raspberry-Pi): ambient glow /
     approval pulse. Read-only physical surface. Hardware staging
     rule: display/voice/dashboard BEFORE cameras, sensors, or
     physical-world automation.
H10. Mobile / pocket read-only brief surface.
H11. Prioritization engine: dependency, ROI, urgency, risk, proof
     value, user preference - the upgrade path for C1's
     deterministic Best Move Today.
H12. Capability packs (everyday / business / household / creator)
     and the Auralis client-services direction ("Auralis builds
     the website, Nova handles the leads") - a SECOND business
     model, parked until Lucid Creations proves the first.
H13. Second Brain (future/brain/second_brain/): most build-ready
     horizon item - full blueprint exists (8 slices, acceptance
     gate, test fixtures, JSON schemas, mock Obsidian vault).
     Slice 1 lock ACCEPTED (PR #234), deferred. Start here, not
     from scratch. End state: the WORLD MODEL - a structured map
     of people, projects, businesses, products, tasks, risks,
     preferences, systems, rituals, and open loops - from which
     every brief and suggestion draws (with D14 as its user-facing
     view). This is where Nova starts feeling intelligent instead
     of chatty.
H14. Parked domains (correct safety posture, no active work):
     market sandbox (paper-trading/learning only; real-money action
     stays prohibited), YouTubeLIS, governed desktop runs /
     Continuous Nova ("continuous presence is not continuous
     authority").
H15. Manager hierarchy: Global Manager -> Domain Managers
     (Personal / Home / Commerce / Code / Research / Admin) ->
     Task Assistants, all presented through one Personality Layer
     so many internal agents feel like ONE assistant. Substrate:
     NOVA_PERSONAL_HOME_BUSINESS_OS_SUMMARY.md operating model;
     DOMAIN_PERMISSION_PROFILES.md risk matrix (domain / action /
     risk_level / approval_required).
H16. Weekly Review Packet: the endgame business ritual - one
     weekly approval session assembling drafts, campaign calendar,
     creative queue, analytics, fulfillment readiness. "Task loop
     -> draft work -> review packet -> user approval -> governed
     execution -> ledgered result." C4 is its v1 seed. Source:
     GOVERNED_CREATIVE_COMMERCE_ORCHESTRATION_ENDGAME_2026-05-19.md.
H17. Signal Registry: whitelist of approved triggers (user /
     scheduled / file-folder / external-data) with per-type default
     authority. Governance for REACTIVITY - required prerequisite
     for any Continuous Nova presence. Signals start awareness,
     never grant execution. Source: future/brain/SIGNAL_REGISTRY.md.
H18. Co-Work Page: working surface for the multi-run future -
     active runs panel, focused run view, pending approvals,
     per-run scoped chat. Relevant once governed runs exist.
     Source: future/brain/CO_WORK_PAGE.md.
H19. Premium voice lane: high-quality online voice (e.g.
     ElevenLabs) as PRESENTATION-ONLY upgrade over local TTS -
     "the voice speaks the approved response; it never receives
     tools, webhooks, or authority." Voice discipline rules:
     push-to-talk first; daily brief read aloud; "what needs me?";
     "prepare that, don't send it"; voice confirmation required
     before any external effect; selectable tones (brief / butler /
     operator / coach). The sci-fi move is the right sentence at
     the right moment, not constant talking. Source:
     NOVA_ELEVENLABS_VOICE_OPPORTUNITY_MAP_2026-04-27.md.
H20. Sensitive data routing: provider-level privacy policy with
     routing modes (LOCAL_ONLY / LOCAL_FIRST_CLOUD_FALLBACK /
     CLOUD_ALLOWED / CLOUD_REDACTED / ASK_FIRST / BLOCKED) over a
     sensitive-category taxonomy (credentials, financial, medical,
     identity, customer records, minors, home/security, business
     secrets). Pairs with B9; MANDATORY before any connector
     expansion. Make the controls product-visible, not buried in
     docs (aligns with the NIST AI RMF Generative AI Profile:
     governance, privacy, provenance, disclosure). Source:
     NOVA_SENSITIVE_DATA_ROUTING_PLAN_2026-04-27.md.
H21. Adaptive knowledge system: governed awareness of new tools,
     AI progress, APIs, and opportunities around active projects.
     "Adapt in knowledge first, planning second, execution last" -
     never self-install, never self-expand. Source:
     future/brain/ADAPTIVE_KNOWLEDGE_SYSTEM.md.
H22. GaaS framing (commercial endgame): Nova as Growth-as-a-Service
     - the same engine loop (understand state -> leverage points ->
     safe next actions -> execute one approved step -> remember
     what worked -> human stays in authority) productized for a
     person, household, creator, or small business. Lucid Creations
     is the first case study. Ties to H12. Source:
     nova_gaas_strategy.md.

Ambient intelligence - "sci-fi now" additions (2026-07-05). Rule:
every item adds awareness, preparation, or presence; NONE adds
execution authority. All legal under the background doctrine.

H23. PREPARED REALITY (the umbrella concept): Nova continuously
     turns messy context into prepared-but-unexecuted next moves -
     checklists, drafts, captions, PR descriptions - each with why
     it matters, exact proposed change, risk level, approval
     affordance, and receipt-on-completion. "Nova already did the
     thinking, but still waits at the door before doing the
     acting." Builds on D3's approval-queue spec + assistive
     noticing; includes anticipatory pre-staging (Friday loop
     pre-computed Thursday night, brief warm before usual wake
     time). Preparation-only (auto-approval Level 2).
H24. Night Cycle: while the user sleeps, Nova uses idle local
     compute to replay the day's ledger, consolidate memory
     CANDIDATES (never auto-promote), pre-compute the morning
     brief, run self-drills (H7), and pre-stage predictable work.
     "While you slept, I thought about X." Pure background
     reasoning - the doctrine makes it legal; the idle GPU makes
     it free.
H25. Temporal recall: query-and-narrate layer over the existing
     ledger + memory - "what were we doing on June 3rd?" replays
     any day with receipts. Near-zero new infrastructure; unique
     to Nova because Nova kept receipts.
H26. Presence rituals: phone-on-wifi / BLE beacon as a read-only
     Signal Registry (H17) trigger - spoken greeting + micro-brief
     on arrival ("welcome back - two things happened"), watch-list
     prompt on departure, orb (H9) glow on entry.
H27. Co-watching sessions: explicit session-scoped screen
     awareness built on caps 58-60 - visible indicator, Nova
     notices and comments ("that draft says Tuesday; your calendar
     conflicts"), nothing persists without approval, ends on
     command.
H28. What-if simulator: deterministic scenario math over real data
     (repricing -> margin/WELCOME10 interaction; skipped filming ->
     queue slip), LLM narrates only. Pure proposal; ties to H11.
H29. Generative UI: Nova composes the right widget for the current
     question from a constrained widget vocabulary (LLM -> widget
     JSON -> existing renderer). The screen is never generic.
H30. Multimodal intake: voice notes -> tasks/plans, document/
     receipt/photo parsing, product-photo feedback for Auralis -
     only what the user explicitly provides or approved connectors
     expose, routed through H20 privacy modes.
H31. MCP-governed tool boundary: standardized connector protocol
     (Model Context Protocol-style) for tools/data sources, with
     Nova's twist: MCP connectivity + Governor-mediated permissions
     + receipts + H20 privacy routing. Clean protocol boundary
     instead of bespoke connectors.
```

## Horizon Graduation Rule

Horizon items graduate via the promotion ladder in `future/brain/PROMOTION_PATH.md`:

```text
idea -> future planning doc -> implementation design -> schema/
contract -> dry-run prototype -> tests -> trust/review surface ->
governed runtime integration -> generated runtime truth -> docs
```

No horizon item skips stages. Usefulness is not implementation.

## Historical Ordering Summary (superseded by the current ordering above)

```text
DONE (this cycle)
  A1  front-door/roadmap truth-sync (PR #263, refreshed by PR #314 post-#312).
  A2+B2  PR 4 navigation collapse + ledger start (PR #264). B1 pytest-timeout
         guard landed; the full-suite stall is now CLEARED (2026-07-27, #315+#316 -
         3799 passed on merged main, no stall/timeout).
  C1  Auralis Today v1 shipped, frozen baseline.
  Seven-morning observation (Mornings 1-7 + 2026-07-22 synthesis); PR #311 timeout
    containment; PR #312 grounded brief/category routing closed the evidence-ranked
    product bottleneck and is verified on fresh main.

OWNER (parallel, outside Nova implementation)
  Instagram 1-4, verification, filming, token rotation, small batch,
  Auralis-Digital security migration, GitHub bio.

NOW
  One post-#312 real-use/product-acceptance morning.

PRODUCT
  Owner selects the next evidence-ranked product lane.

HARDENING
  Authorization integrity is the first activatable post-observation hardening lane;
  separate owner activation required; runs in parallel with the selected product lane.

PARKED / SEPARATE DECISIONS
  Connection-truth repair.
  Runtime-generator reconciliation.
  Business-context freshness/tense.
  Corruption-safe loading remains parked unless an actual failure is observed.
  Tasks -> Gmail -> Traffic is a separate standing gap-fill list (NOT synthesis-ranked).

LATER (unchanged horizon ordering)
  A3-A4  labels, Home, ratchets.
  B3-B11 backup+restore drill, async probes, degraded/latency contracts, monolith
         ratchet, schema versions, break-glass, receipt privacy, idempotency, local auth.
  C2-C4  friction aging -> pager (post-rotation + scheduler repair) -> Friday loop.
  D1-D15 coherence layer, ordered.
  H1-H31 horizon, graduated deliberately via the promotion ladder - never as scope creep.
```

## Supersession Note

This document supersedes, as ordering authority only:

```text
docs/future/ROADMAP.md and all dated plan/vision docs in docs/future/
docs/todo/ACTIVE_TODO.md priority ordering (items remain valid as a
  task inventory)
"4-15-26 NEW ROADMAP" directory (archive)
future/ root tree ordering (future/brain/, future/governed_desktop_
  runs/, future/market_sandbox/, future/youtubelis/) - content
  remains design reference; PROMOTION_PATH.md is ADOPTED as the
  horizon graduation rule
docs/future/ai_ecosystem_operating_model/ (docs-only coordination
  package, reference)
```

Their content remains valid as design reference. Nothing is deleted; it is de-prioritized
until referenced from a lane above.

For a classification of the uncited `docs/future/` docs (active / roadmap-lane / horizon /
design-history / superseded / owner-paused / fixture), see `docs/future/FUTURE_DOCS_MAP.md`. That
map records status only; it does not promote anything into a lane.

Alignment notes (2026-07-05 archive deep-dive):

- This document's authority rules agree with docs/future/README.md
  (code > generated truth > active locks > future docs > archive).
- [HISTORICAL 2026-07-05; SUPERSEDED] At the time, docs/todo/ACTIVE_TODO.md still
  named the superseded 2026-06-17 runtime recovery lock as active and
  docs/status/DAILY_COMMAND_CENTER.md was stale; the planned A1 docs-only PR was to
  refresh both. This was addressed by the post-#312 truth-sync (PR #314), and the later
  2026-08-20 Wave A1 now performs a distinct current operational-truth reconciliation.
- docs/todo/TECH_DEBT.md agent_scheduler repair is a named gate on C3.
- The Auralis web-design/client-intake doc family is historical business-direction context,
  not authority for the current Nova stabilization gate.
- The 2026-04-27 owner HARD PAUSE on Auralis merger work remains a historical owner decision
  unless separately superseded by later Auralis strategy.

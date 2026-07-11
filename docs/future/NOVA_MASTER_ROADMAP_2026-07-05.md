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

## Observation-driven candidates (added 2026-07-11)

The Phase-3 observation period generates roadmap candidates from real behavior. Recorded here
as they surface; none is authorized to build except via the stated gate.

```text
LANDED (truth-critical repairs, freeze-exempt, owner-approved):
  #294  Observation Step 0 — morning-log template + single launch procedure + config truth
        (runtime reads Windows User-scope env, not nova_backend/.env).
  #295  Truthful availability under dashboard refresh — fixed false "not configured" labels for
        news + weather (news 180s cache vs cap-56 rate-limit exhaustion; weather widget-envelope
        unwrap; honest "temporarily unavailable" language; news no longer blames Brave).

DEFINED, NOT FIRED (owner HOLD until >=1 completed morning after #295):
  "Grounded follow-up conversation over brief items" — route discussion-shaped follow-ups
  ("what do you think about that?") to the conversation lane instead of the widget; inject the
  sourced brief facts (news/weather/calendar) already in session_state into the LLM context;
  keep unsupported claims tagged, not laundered (the P0 hallucination boundary). This lane is
  the PREREQUISITE before any local-vs-cloud (DeepSeek) model-quality test is meaningful — a
  2026-07-11 read-only trace confirmed the conversation LLM currently receives no brief facts,
  so a weak conversation would be plumbing evidence, not model evidence. Full spec: project
  memory "grounded-conversation-lane" + docs/status/DAILY_COMMAND_CENTER.md (2026-07-11 block).

STILL PARKED behind evidence: model preset / governed cloud-conversation brain (DeepSeek),
gated on the grounded-conversation lane producing a genuine model-quality signal.
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
6. Scheduled: July 9 Google Merchant review check.
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

## Lane A - UX Simplification (active lane)

Scope authority: `docs/status/UX_SIMPLIFICATION_PRIORITY_LOCK_2026-07-02.md`.

```text
A1. UX PR 3 merged as PR #262 (quick-action reduction, branch
    ux/quick-action-reduction, commits 5f8a924 and a1b54a8).
    Land this roadmap as a docs-only PR next, along
    with the refreshed README.md (updated 2026-07-05: butler north
    star, current active task, roadmap as ordering authority) and
    the two stale front-door docs (see Supersession Note).
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

## Lane C - Auralis Awareness (after A2 lands)

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

## Ordering Summary (one screen)

```text
NOW    owner: Instagram 1-4, verification, filming, token rotation,
       small batch, July 9 check, Auralis-Digital security migration,
       GitHub bio
A1     PR #262 merged; land this roadmap (docs-only PR) + refresh
       stale front-door docs
A2+B1+B2   PR 4 session: nav collapse + pytest-timeout + ledger start
C1     Auralis Today v1 (locked spec, committed to repo)
A3-A4  labels, Home, ratchets
B3-B11 backup+restore drill, async probes, degraded/latency
       contracts, monolith ratchet, schema versions, break-glass,
       receipt privacy, idempotency, local auth
C2-C4  friction aging -> pager (post-rotation + scheduler repair)
       -> Friday loop
D1-D15 coherence layer, ordered
H1-H31 horizon, graduated deliberately via the promotion ladder -
       never as scope creep
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
- docs/todo/ACTIVE_TODO.md still names the superseded 2026-06-17
  runtime recovery lock as active; docs/status/DAILY_COMMAND_CENTER.md
  is also stale. The A1 docs-only PR refreshes BOTH to point at
  this document and the UX lane. Keep generated runtime doc
  modifications separate unless intentionally included.
- docs/todo/TECH_DEBT.md agent_scheduler repair is a named gate on C3.
- The Auralis web-design/client-intake doc family is a second
  business (client services), parked as H12, not contradicted.
- The 2026-04-27 owner HARD PAUSE on Auralis merger work remains the
  recorded owner decision (4-15-26 NEW ROADMAP/BackLog.md).

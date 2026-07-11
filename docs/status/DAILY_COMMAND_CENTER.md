# Daily Command Center

Status: manual continuity surface.
Last reviewed: 2026-07-11 (observation underway; two truth-fix lanes merged).
Source: observation Step 0 + runtime truth-defect repairs + conversation-grounding trace.

## 2026-07-11 session (latest — read this first)

```text
OBSERVATION UNDERWAY. Engineering freeze holds; only truth-critical repairs taken, each with
explicit owner approval. Next product input is still a completed morning, not a PR.

STEP 0 — observation readiness (PR #294 merged): ratified morning-log template
(docs/observation/MORNING_LOG_TEMPLATE.md) + single launch procedure. Config truth established:
the runtime does NOT load nova_backend/.env — Windows User-scope env vars are the operative
source (OLLAMA_MODEL=gemma2:2b, NOVA_CALENDAR_ICS_PATH); .env is a documented mirror only.
Calendar is wired end-to-end (a daily 6:00 AM scheduled task re-exports the .ics; it currently
holds no upcoming events, so "Nothing on your calendar today" is TRUE). Morning 1 in progress
(docs/observation/MORNING_01_2026-07-11.md — Chris completes the experiential fields).

TRUTH-FIX LANE (PR #295 merged — "Truthful availability under dashboard refresh"): fixed the
false "not configured" labels for news and weather. THREE findings: (1) the news skill fans out
to ~26 governed network calls per request; the ~70s dashboard refresh re-spent them and blew the
mediator's 50/min rate limit, so later fetches returned empty and were mislabeled "not
configured / check Brave" — fixed with a 180s news result cache. (2) STRUCTURAL BUG: the brief
read a top-level `connected` flag but the weather widget nests it under `data`, so a WORKING
forecast always rendered "not configured" regardless of rate-limiting — fixed by unwrapping the
envelope. (3) Labels now truthful: empty/rate-limited => "temporarily unavailable", never "not
configured", and news no longer blames Brave (Brave is web search, not the news source).
Verified live (warm server): repeated briefs show weather=ok + news=ok. GH Actions still
billing-gated; local-verification standard used (same as #292/#293).

CONVERSATION-GROUNDING TRACE (read-only, no code changed): the conversation LLM does NOT receive
news/weather facts. GeneralChatSkill.can_handle excludes "news"/"weather"/"forecast"/"headlines"
(routes them to widgets, never the LLM), and the prompt assembly never reads
session_state["news_cache"]/weather. So "converse about the news" does not exist yet; a weak
conversation would be PLUMBING evidence, not model evidence. => The DeepSeek-vs-gemma2:2b
model-quality test is INVALID until grounding lands.

NEXT LANE, DEFINED NOT FIRED: "Grounded follow-up conversation over brief items" (route
discussion-shaped follow-ups to chat + inject sourced brief facts + keep unsupported claims
tagged not laundered). Owner ruling: HOLD until >=1 completed morning after #295 — don't move
the observation baseline again before capturing a finished day. Lane spec lives in project
memory + the master roadmap candidate list.
```

## 2026-07-07 session

```text
Phase 3 formally CLOSED: engineering FROZEN, only critical bugs may be fixed, behavior generates
the roadmap. Tag phase-3-complete on main (963f1d8; all lanes #262-#272 merged).

Pre-observation LIVE VERIFICATION ran on fresh main (QA Rule #1). Report + evidence:
  PR #273 -> docs/capability_verification/LIVE_VERIFICATION_2026-07-07.md.
  Verdict: READY FOR OBSERVATION. Weather/news/calendar/brief/arithmetic/search/email-degrade
  PASS live; email-inbox/tasks/traffic NOT IMPLEMENTED. Governance intact (27 caps, no writes).
  Headline finding: the model-VERSION LOCK fired on fresh start (stale trust fingerprint) and
  blocked LLM inference until an owner-authorized "confirm model update" cleared it (hash
  rewritten, MODEL_UPDATED ledger event); it gates the LLM only, deterministic surfaces work
  under it, and it won't re-trigger unless model/prompt/wrapper changes. Freeform LLM chat
  times out on 8GB CPU (#227) - non-blocking for mornings.

Product IDENTITY converged (PR #274 -> docs/product/PRODUCT_DEFINITION.md): Nova = an awareness
  engine; objective function "help me make the next better decision"; governance is
  infrastructure (visible: Awareness->Conversation->Capabilities + hidden Decision Engine);
  three trust classes Fact/Reasoning/Inference + core principle "never present inference as
  fact"; awareness tiers Passive->Contextual->Predictive. Theory is CONVERGED - next input is a
  logged morning, not more refinement.

GATE: no new build until >=7 mornings are logged (collect before analyzing; trend, not n=1).
PR #273 and PR #274 are merged. Main now contains the live verification report and converged
product identity. Next input is observed morning use. Resolved: src/models/current_model_hash.txt
is now untracked (local machine trust state, not repo truth) — a fresh checkout/other machine
still needs its own "confirm model update", which is governance working correctly.
```

Product definition: `docs/product/PRODUCT_DEFINITION.md`
Ordering authority: `docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md`
What works (verified): `docs/capability_verification/CAPABILITY_INVENTORY.md`

This note is a human-facing command surface for current repo/vault
orientation. It is not generated runtime truth and it does not
authorize execution.

For exact runtime facts, use:

- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_FINGERPRINT.md`
- actual code
- receipts and logs

## Current Phase: 3 — Can Nova become a habit?

Build lanes are COMPLETE. Engineering and verification are no longer the question. The only
input that moves the project now is OBSERVED DAILY USE.

```text
1. OBSERVATION (Claude's role now = observe, not build): Chris opens Nova each morning; Claude
   watches the real session and reports where behavior diverges from what Nova assumed.
   Metrics: followed / quality / time-to-decision / reason-ignored / surprise / FIRST
   UNANSWERED QUESTION. Single success metric: did Nova eliminate ONE uncertainty before Chris
   reached for another app?
2. Owner NOW gate (only Chris can do): Auralis-Digital repo hosting migration + privacy flip,
   Instagram bio/link/filming, Meta verification, OpenClaw token rotation.
3. Do NOT build/verify/define more until observed use proves a gap. Evidence earns the build.
4. Preserve governance boundaries; keep certified capabilities locked.
```

## Current Blockers

```text
Test suite pre-existing stall at 85-91%: the B1 pytest-timeout
guard landed via PR #264 (timeout = 180s enforced), so the next
full-suite run converts the silent hang into a named failing test.
Root-cause fix still pending (B1 remainder).
```

## Decisions Needed

```text
1. Machine side: NONE. Build lanes complete; next input is observed use, not a decision.
2. Owner: choose Auralis-Digital hosting migration path (Netlify/Cloudflare from a private
   repo vs repo split vs GitHub Pro) - the business playbook is currently public.
```

## This Week

```text
1. Chris opens Nova each morning FIRST and logs the observation metrics (Phase 3).
2. Owner NOW items: Auralis-Digital migration, Instagram, filming, verification, rotation.
3. Nothing to build/verify/define unless observed use surfaces a real gap.
```

## Morning coverage (what Nova reliably does today, verified 2026-07-06)

```text
Weather  OK  |  News  OK  |  Calendar  OK  |  Business/C1  OK
Email  NOT IMPLEMENTED  |  Reminders  NOT IMPLEMENTED  |  Traffic  NOT IMPLEMENTED
~3 of Chris's ~5-6 morning checks. Gap-fill order (only when evidence pulls it):
Google Tasks -> Gmail -> Traffic. Full detail: CAPABILITY_INVENTORY.md.
```

## Branch State

```text
main is current; no active feature branch. All build lanes merged (#262-#270).
Next work is observation, not a branch.
Remote review candidates: second-brain-slice1-activation (keep - roadmap H13);
others likely superseded (owner review pending).
```

## Recent Landed Stack (since 2026-06-17)

```text
PR #255 - Runtime state clarity (2026-06-17).
PR #257 - Runtime health truth (2026-06-17).
PR #258 - Startup health stabilization (2026-07-02).
PR #259 - UX simplification priority lock doc (2026-07-02).
PR #260 - Daily Awareness Brief surface (2026-07-02).
PR #261 - Daily Brief unification and routing (2026-07-02).
PR #262 - UX PR 3: quick-action reduction (2026-07-05).
PR #263 - A1: master roadmap + front-door truth sync (2026-07-05).
PR #264 - UX PR 4: navigation collapse + B1 pytest-timeout guard
          + B2-start ledger health diagnostic (2026-07-05).
```

## Earlier Landed Stack (2026-06-14 to 2026-06-16)

```text
PR #245 - Provider budget visibility foundation (2026-06-15).
PR #246 - Provider/dependency status visibility (2026-06-15).
PR #247 - DeepSeek log-only budget check (2026-06-15).
PR #248 - DeepSeek hard budget enforcement (2026-06-15).
PR #249 - Provider budget status accuracy / fallback (2026-06-16).
PR #250 - First-user intent routing and fallback clarity (2026-06-16).
PR #251 - Batch 2/3 pattern coverage tightening (2026-06-16).
PR #252 - Route protection coverage / local-only guards (2026-06-16).
PR #253 - Continuity sync after route protection (2026-06-16).
PR #254 - Recent workstream closeout (2026-06-16).
```

## Earlier Landed Stack (2026-06-08 to 2026-06-13)

```text
PR #236 - Baseline CI/dependency cleanup.
PR #237 - AI ecosystem operating model.
PR #235 - Obsidian authority-tier overlay.
PR #240 - Repo-doc operating-loop proof.
PR #241 - Continuity freshness sync and Daily Command Center.
PR #242 - Post-merge command center refresh.
PR #243 - Second Brain Slice 1 + governed Morning Brief activation.
PR #244 - Trust review snapshot CI fix.
```

## Recent Product Direction

```text
Nova is a governed daily awareness assistant.
Opening Nova should be useful within 30 seconds.
Seven awareness sections on open: weather, news, calendar,
project state, Shopify snapshot, Printify snapshot, what changed.
Each section is independently optional with graceful degradation.
Read-only awareness first, governed action second.
See: docs/status/PRODUCT_DIRECTION_DAILY_AWARENESS_2026-06-18.md
```

## Boundary

```text
Obsidian ranks and navigates reality.
Repo docs record reviewed project truth.
Nova governance/runtime remains the execution authority boundary.
Notes do not grant permission.
```

## Not Authorized Here

```text
runtime authority expansion
capability_locks.json changes
GovernorMediator changes
Shopify writes or commerce mutation
OpenClaw integration or expansion
browser/computer-use expansion
scheduler/background-loop expansion outside the existing explicit narrow governed carve-out
external writes
memory promotion
Second Brain implementation (deferred behind active lane)
Plan My Week
model presets
more agents
more providers
bigger dashboard redesign
autonomous workflow execution
Obsidian execution authority
```

# Daily Command Center

Status: manual continuity surface.
Last reviewed: 2026-07-07 (Phase 3 CLOSED — observation begins).
Source: pre-observation live verification + product-identity convergence.

## 2026-07-07 session (latest — read this first)

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

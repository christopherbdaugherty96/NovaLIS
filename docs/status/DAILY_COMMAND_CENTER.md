# Daily Command Center

Status: manual continuity surface.
Last reviewed: 2026-07-05.
Source: master roadmap consolidation and pre-PR-4 audit sync.

Ordering authority for all current and future work:
`docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md`

This note is a human-facing command surface for current repo/vault
orientation. It is not generated runtime truth and it does not
authorize execution.

For exact runtime facts, use:

- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_FINGERPRINT.md`
- actual code
- receipts and logs

## Current Priorities

```text
1. UX simplification lane (2026-07-02 lock): PR 3 merged,
   PR 4 navigation collapse next.
2. Owner NOW gate (see master roadmap): Instagram conversion fixes,
   Meta verification, filming, OpenClaw token rotation,
   Auralis-Digital repo privacy migration.
3. Preserve visible user trust when Nova stalls or degrades.
4. Preserve the Obsidian authority boundary.
5. Keep all four certified capabilities locked.
```

## Current Blockers

```text
Test suite pre-existing stall at 85-91% remains a verification
friction item. New clue (2026-07-05): pytest config references a
timeout option but pytest-timeout is not installed, so hangs are
unbounded. Fix queued as roadmap item B1.
```

## Decisions Needed

```text
1. Land the master roadmap + refreshed front-door docs as the A1
   docs PR.
2. Owner: choose Auralis-Digital hosting migration path
   (Netlify/Cloudflare from private repo vs repo split vs GitHub
   Pro) - the business playbook is currently public.
```

## This Week

```text
1. Owner NOW items (Instagram, verification, filming, rotation,
   security migration - see master roadmap NOW gate).
2. A1: land roadmap docs PR.
3. A2: PR 4 navigation collapse (+ pytest-timeout and ledger
   hardening start riding along, roadmap B1-B2).
4. Continue Morning Brief friction logging.
5. Keep Second Brain implementation deferred (roadmap H13).
```

## Chosen Next Lane

```text
UX simplification and discoverability (PR 3 -> PR 4 -> PR 5 -> PR 6),
then Auralis Today (roadmap Lane C).
```

Priority lock:

```text
docs/status/UX_SIMPLIFICATION_PRIORITY_LOCK_2026-07-02.md
(supersedes the 2026-06-17 runtime recovery lock, absorbed P2-P5)
```

## Active Branch: codex/a1-roadmap-front-door-docs

```text
PR #262 merged 2026-07-05:
  5f8a924 - ux: reduce visible quick actions to high-value outcome
            tasks (UX lane PR 3)
  a1b54a8 - docs: regenerate runtime docs after quick-action reduction

This A1 docs PR includes:
  - README.md refresh (butler north star, current task, roadmap link)
  - docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md (lands as the A1
    docs-only PR)
  - this file + docs/todo/ACTIVE_TODO.md refresh (A1 docs PR)
```

## Recent Landed Stack (since 2026-06-17)

```text
PR #255 - Runtime state clarity (2026-06-17).
PR #257 - Runtime health truth (2026-06-17).
PR #258 - Startup health stabilization (2026-07-02).
PR #259 - UX simplification priority lock doc (2026-07-02).
PR #260 - Daily Awareness Brief surface (2026-07-02).
PR #261 - Daily Brief unification and routing (2026-07-02).
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
scheduler or background loops
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

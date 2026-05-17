# Branch Consolidation Audit - 2026-05-17

Audit branch: branch/consolidate-stale-branches-audit.

Grounding commands completed from live repo state: git status, git branch --show-current, git fetch --all --prune, git checkout main, git pull --ff-only, gh pr list --state open, and git branch -r --sort=-committerdate.

## Current Main Truth

- origin/main includes PR #171 focused approval-gate regression coverage.
- origin/main includes PR #172 behavioral live-session approval-gate coverage.
- Conservative approval-gate status remains: focused regression coverage merged; behavioral live-session coverage merged; full approval-gate certification pending.
- No branch in this audit is approved for direct merge into main.

## Open PR Review

- PR #173 is current, conservative, docs-only status sync. Keep open for review/merge through PR.
- PR #166 is stale against current main because it rewrites docs/todo/ACTIVE_TODO.md toward older #141/search-widget and pre-approval-gate status. Do not merge directly; close or supersede if Shopify truth still needs a fresh narrow patch.

## Branch Inventory Summary

Total remote non-main branches reviewed: 55
- A. Already merged / safe delete: 7
- B. Superseded / stale: 46
- D. Active PR branch: 2

## Branch Classification Table

| Branch | Latest SHA / date | Merged into main? | Unique commits | Diff summary | Touches | Bucket | Action | Reason |
| --- | --- | --- | ---: | --- | --- | --- | --- | --- |
| audit/full-repo-doc-code-alignment | 61161036fdc8 / 2026-05-11 | no | 6 |  3 files changed, 1063 insertions(+) | future docs, proof/audit docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| audit/openclaw-freeform-goal-inspection | 37e742d388ac / 2026-05-11 | no | 4 |  12 files changed, 1135 insertions(+), 120 deletions(-) | generated runtime docs, future docs, proof/audit docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| claude/adoring-ramanujan-2c80f6 | 23e89522b5ac / 2026-05-01 | no | 1 |  8 files changed, 81 insertions(+), 30 deletions(-) | future docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| claude/review-repo-status-f2E7Q | 0cc126ecfd93 / 2026-05-12 | no | 1 |  8 files changed, 125 insertions(+), 141 deletions(-) | governance/status docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| codex/harden-web-ui-proof-lock-wording | 8eb608d50345 / 2026-05-06 | no | 1 |  4 files changed, 103 insertions(+), 2 deletions(-) | governance/status docs, proof/audit docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| codex/ui-web-news-proof-evidence | 91fbcf1038fc / 2026-05-07 | no | 1 |  20 files changed, 18779 insertions(+) | proof/audit docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| docs/active-priority-lock-openclaw-path | b4056c53e67e / 2026-05-04 | no | 5 |  3 files changed, 144 insertions(+), 371 deletions(-) | governance/status docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| docs/approval-gate-wiring-priority-lock | 7e3bc2ad89d0 / 2026-05-14 | no | 1 |  6 files changed, 141 insertions(+), 28 deletions(-) | governance/status docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| docs/close-runtime-truth-audit-lock | c667ca10bed8 / 2026-05-06 | no | 3 |  3 files changed, 53 insertions(+), 51 deletions(-) | governance/status docs, proof/audit docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| docs/correct-shopify-future-operator-truth | 392e7a6295a1 / 2026-05-14 | no | 2 |  8 files changed, 231 insertions(+), 76 deletions(-) | governance/status docs, future docs, proof/audit docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| docs/everyday-ux-friction-closeout-review | 763a6d05dd77 / 2026-05-10 | no | 1 |  1 file changed, 148 insertions(+) | proof/audit docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| docs/everyday-ux-friction-priority-lock | 6c447ac954d4 / 2026-05-10 | yes | 0 | empty | other/docs | A. Already merged / safe delete | delete after human approval | Tip is contained in origin/main; no unique commits remain. |
| docs/five-pass-stability-and-operational-roadmap | fa02bed0e750 / 2026-05-12 | no | 4 |  2 files changed, 416 insertions(+), 2 deletions(-) | governance/status docs, future docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| docs/fix-approval-gate-next-sequence | e781966cd8d1 / 2026-05-14 | no | 1 |  1 file changed, 2 insertions(+), 2 deletions(-) | governance/status docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| docs/fix-shopify-truth-and-active-todo | 79cd15a6a028 / 2026-05-13 | no | 1 |  1 file changed, 107 insertions(+), 52 deletions(-) | governance/status docs | D. Active PR branch | close or supersede PR #166 | Open PR edits ACTIVE_TODO toward older #141/search-widget and pre-approval-gate state; stale against current main after #171/#172. |
| docs/governed-autonomy-direction-lock | df48a119e8a6 / 2026-05-11 | no | 1 |  1 file changed, 318 insertions(+) | governance/status docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| docs/lock-audit-first-safety-boundary | 25e72b177fe4 / 2026-05-11 | no | 1 |  1 file changed, 48 insertions(+), 13 deletions(-) | governance/status docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| docs/lock-two-domain-nova-direction | cd796bf8a3a8 / 2026-05-11 | no | 4 |  2 files changed, 366 insertions(+) | future docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| docs/nova-conversation-response-contract | 87c48212d37a / 2026-05-10 | no | 1 |  1 file changed, 234 insertions(+) | other/docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| docs/patch-shopify-operator-truth-header | 2185b8817033 / 2026-05-12 | yes | 0 | empty | other/docs | A. Already merged / safe delete | delete after human approval | Tip is contained in origin/main; no unique commits remain. |
| docs/piper-first-voice-direction | 7f015c65546e / 2026-05-11 | no | 1 |  1 file changed, 111 insertions(+), 72 deletions(-) | future docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| docs/post-149-current-priority-closeout | 0220d538d706 / 2026-05-11 | no | 4 |  3 files changed, 196 insertions(+), 28 deletions(-) | governance/status docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| docs/proof-infrastructure-closeout-review | cefe06388b12 / 2026-05-09 | yes | 0 | empty | other/docs | A. Already merged / safe delete | delete after human approval | Tip is contained in origin/main; no unique commits remain. |
| docs/readme-current-state-v0.5 | 6c2ed8729fcc / 2026-05-12 | no | 1 |  1 file changed, 40 insertions(+), 10 deletions(-) | other/docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| docs/regenerate-runtime-docs | 2fbe726a51b8 / 2026-05-11 | no | 1 |  10 files changed, 344 insertions(+), 120 deletions(-) | generated runtime docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| docs/regenerate-runtime-docs-post-openclaw-hardening | 1f2e8ca0b09f / 2026-05-11 | no | 1 |  1 file changed, 57 insertions(+), 7 deletions(-) | governance/status docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| docs/shopify-pod-business-intelligence-plan | da47d2b188fc / 2026-05-11 | no | 3 |  2 files changed, 573 insertions(+) | governance/status docs, future docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| docs/stage-6-truth-sync | c2011e3c3b1f / 2026-05-03 | no | 10 |  9 files changed, 259 insertions(+), 330 deletions(-) | governance/status docs, future docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| docs/sync-after-web-news-stress-fixtures | 2860896c9923 / 2026-05-07 | no | 1 |  2 files changed, 41 insertions(+), 14 deletions(-) | governance/status docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| docs/sync-agents-and-active-todo-after-pr159 | 0dd507899e88 / 2026-05-12 | no | 2 |  2 files changed, 41 insertions(+), 4 deletions(-) | governance/status docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| docs/sync-approval-gate-coverage-status | d8dfcefdad13 / 2026-05-17 | no | 1 |  3 files changed, 76 insertions(+), 29 deletions(-) | governance/status docs | D. Active PR branch | keep / review PR #173 | Current conservative approval-gate status sync PR; merge through PR only if accepted. |
| docs/sync-current-priority-after-runtime-doc-todo | ce9cb2209f9e / 2026-05-11 | no | 4 |  4 files changed, 125 insertions(+), 55 deletions(-) | governance/status docs, future docs, proof/audit docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| docs/sync-current-status-after-direction-updates | 97f7f2ae13c5 / 2026-05-11 | no | 4 |  4 files changed, 247 insertions(+), 470 deletions(-) | governance/status docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| docs/sync-everyday-ux-closeout-status | 6d5830971344 / 2026-05-11 | no | 1 |  3 files changed, 61 insertions(+), 43 deletions(-) | governance/status docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| docs/sync-post-openclaw-audit-hardening-status | dfb3c02d58f1 / 2026-05-11 | no | 3 |  3 files changed, 208 insertions(+), 101 deletions(-) | governance/status docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| docs/sync-proof-library-progress | d10d9db3be71 / 2026-05-07 | no | 2 |  2 files changed, 59 insertions(+), 25 deletions(-) | governance/status docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| docs/sync-trust-review-card-lock-status | 64e724f16ef8 / 2026-05-06 | no | 2 |  2 files changed, 71 insertions(+), 25 deletions(-) | governance/status docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| docs/trust-review-card-priority-lock | 1092665a6fc6 / 2026-05-06 | no | 2 |  2 files changed, 127 insertions(+), 17 deletions(-) | governance/status docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| docs/ui-simplification-inventory | dede4bca94a1 / 2026-05-09 | yes | 0 | empty | other/docs | A. Already merged / safe delete | delete after human approval | Tip is contained in origin/main; no unique commits remain. |
| docs/web-news-proof-priority-lock | fb2d3d63a256 / 2026-05-06 | no | 7 |  6 files changed, 537 insertions(+), 124 deletions(-) | governance/status docs, proof/audit docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| docs/web-news-ui-proof-lock-closeout-review | 1375f8bb0df5 / 2026-05-07 | no | 1 |  5 files changed, 296 insertions(+), 93 deletions(-) | governance/status docs, proof/audit docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| docs/work-style-enforcement-lock | fb42a219339f / 2026-05-10 | no | 2 |  1 file changed, 375 insertions(+) | governance/status docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| feature/trust-review-card-mvp | db10b5f7ece8 / 2026-05-07 | no | 1 |  21 files changed, 538 insertions(+), 72 deletions(-) | runtime code, tests, generated runtime docs, governance/status docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| fix/everyday-ux-friction-slice-9 | 1ef59e44796c / 2026-05-10 | no | 2 |  4 files changed, 337 insertions(+), 16 deletions(-) | runtime code, tests | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| fix/openclaw-freeform-goal-governance-patches | abb848cf6c44 / 2026-05-11 | no | 6 |  16 files changed, 647 insertions(+), 71 deletions(-) | runtime code, tests, generated runtime docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| fix/ui-web-news-proof-blockers | f44a31982aff / 2026-05-07 | no | 1 |  17 files changed, 1111 insertions(+), 65 deletions(-) | runtime code, tests, proof/audit docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| fix/ui-web-news-proof-followups | e5166ca4e19c / 2026-05-07 | no | 1 |  22 files changed, 318 insertions(+), 41 deletions(-) | runtime code, tests, proof/audit docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| fix/web-news-weak-query-confidence-current-main | 447ec4143dad / 2026-05-11 | no | 1 |  1 file changed, 1 deletion(-) | runtime code | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| proof/cap-16-certification-lock | 677f3cded53d / 2026-05-10 | yes | 0 | empty | other/docs | A. Already merged / safe delete | delete after human approval | Tip is contained in origin/main; no unique commits remain. |
| proof/dashboard-stale-degraded-rendering | b84ae9b2fd08 / 2026-05-07 | no | 1 |  26 files changed, 586 insertions(+), 70 deletions(-) | tests, generated runtime docs, governance/status docs, proof/audit docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| proof/everyday-ux-live-workflow-baseline | a087d58d184b / 2026-05-10 | no | 3 |  1 file changed, 646 insertions(+) | proof/audit docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| proof/stale-provider-credibility-fixtures | 5bf33463cfe3 / 2026-05-07 | no | 1 |  22 files changed, 791 insertions(+), 76 deletions(-) | runtime code, tests, generated runtime docs, governance/status docs, proof/audit docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| proof/ui-malformed-rapid-click-stress | df0fec389cb8 / 2026-05-07 | no | 1 |  21 files changed, 405 insertions(+), 55 deletions(-) | tests, generated runtime docs, governance/status docs, proof/audit docs | B. Superseded / stale | do not merge; keep until human delete approval | Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current. |
| test/dashboard-event-replay-harness | c3fe766e538e / 2026-05-09 | yes | 0 | empty | other/docs | A. Already merged / safe delete | delete after human approval | Tip is contained in origin/main; no unique commits remain. |
| test/non-search-widget-fuzzing | 2543aff2dec3 / 2026-05-09 | yes | 0 | empty | other/docs | A. Already merged / safe delete | delete after human approval | Tip is contained in origin/main; no unique commits remain. |

## Unique Content Worth Preserving

- docs/sync-approval-gate-coverage-status / PR #173: current conservative status sync after #171/#172. Keep as active PR branch; merge through PR if accepted.
- docs/fix-shopify-truth-and-active-todo / PR #166: contains older Shopify truth language, but its ACTIVE_TODO base is stale after #171/#172 and should be closed or superseded rather than merged.

No runtime/test branch content was extracted in this pass. Branches with unique runtime/test diffs require targeted review and focused tests before preserving anything.

## Branches Safe To Delete

- docs/everyday-ux-friction-priority-lock - Tip is contained in origin/main; no unique commits remain.
- docs/patch-shopify-operator-truth-header - Tip is contained in origin/main; no unique commits remain.
- docs/proof-infrastructure-closeout-review - Tip is contained in origin/main; no unique commits remain.
- docs/ui-simplification-inventory - Tip is contained in origin/main; no unique commits remain.
- proof/cap-16-certification-lock - Tip is contained in origin/main; no unique commits remain.
- test/dashboard-event-replay-harness - Tip is contained in origin/main; no unique commits remain.
- test/non-search-widget-fuzzing - Tip is contained in origin/main; no unique commits remain.

## Branches To Keep

- main.
- docs/fix-shopify-truth-and-active-todo - close or supersede PR #166.
- docs/sync-approval-gate-coverage-status - keep / review PR #173.
- Non-merged stale branches until human approval confirms deletion or extraction.

## Branches Needing Human Review

- All branches classified as B before deletion. They are not recommended for merge, but they retain unique/parallel diffs and should be deleted only after human approval.
- audit/full-repo-doc-code-alignment - future docs, proof/audit docs;  3 files changed, 1063 insertions(+)
- audit/openclaw-freeform-goal-inspection - generated runtime docs, future docs, proof/audit docs;  12 files changed, 1135 insertions(+), 120 deletions(-)
- claude/adoring-ramanujan-2c80f6 - future docs;  8 files changed, 81 insertions(+), 30 deletions(-)
- claude/review-repo-status-f2E7Q - governance/status docs;  8 files changed, 125 insertions(+), 141 deletions(-)
- codex/harden-web-ui-proof-lock-wording - governance/status docs, proof/audit docs;  4 files changed, 103 insertions(+), 2 deletions(-)
- codex/ui-web-news-proof-evidence - proof/audit docs;  20 files changed, 18779 insertions(+)
- docs/active-priority-lock-openclaw-path - governance/status docs;  3 files changed, 144 insertions(+), 371 deletions(-)
- docs/approval-gate-wiring-priority-lock - governance/status docs;  6 files changed, 141 insertions(+), 28 deletions(-)
- docs/close-runtime-truth-audit-lock - governance/status docs, proof/audit docs;  3 files changed, 53 insertions(+), 51 deletions(-)
- docs/correct-shopify-future-operator-truth - governance/status docs, future docs, proof/audit docs;  8 files changed, 231 insertions(+), 76 deletions(-)
- docs/everyday-ux-friction-closeout-review - proof/audit docs;  1 file changed, 148 insertions(+)
- docs/five-pass-stability-and-operational-roadmap - governance/status docs, future docs;  2 files changed, 416 insertions(+), 2 deletions(-)
- docs/fix-approval-gate-next-sequence - governance/status docs;  1 file changed, 2 insertions(+), 2 deletions(-)
- docs/governed-autonomy-direction-lock - governance/status docs;  1 file changed, 318 insertions(+)
- docs/lock-audit-first-safety-boundary - governance/status docs;  1 file changed, 48 insertions(+), 13 deletions(-)
- docs/lock-two-domain-nova-direction - future docs;  2 files changed, 366 insertions(+)
- docs/nova-conversation-response-contract - other/docs;  1 file changed, 234 insertions(+)
- docs/piper-first-voice-direction - future docs;  1 file changed, 111 insertions(+), 72 deletions(-)
- docs/post-149-current-priority-closeout - governance/status docs;  3 files changed, 196 insertions(+), 28 deletions(-)
- docs/readme-current-state-v0.5 - other/docs;  1 file changed, 40 insertions(+), 10 deletions(-)
- docs/regenerate-runtime-docs - generated runtime docs;  10 files changed, 344 insertions(+), 120 deletions(-)
- docs/regenerate-runtime-docs-post-openclaw-hardening - governance/status docs;  1 file changed, 57 insertions(+), 7 deletions(-)
- docs/shopify-pod-business-intelligence-plan - governance/status docs, future docs;  2 files changed, 573 insertions(+)
- docs/stage-6-truth-sync - governance/status docs, future docs;  9 files changed, 259 insertions(+), 330 deletions(-)
- docs/sync-after-web-news-stress-fixtures - governance/status docs;  2 files changed, 41 insertions(+), 14 deletions(-)
- docs/sync-agents-and-active-todo-after-pr159 - governance/status docs;  2 files changed, 41 insertions(+), 4 deletions(-)
- docs/sync-current-priority-after-runtime-doc-todo - governance/status docs, future docs, proof/audit docs;  4 files changed, 125 insertions(+), 55 deletions(-)
- docs/sync-current-status-after-direction-updates - governance/status docs;  4 files changed, 247 insertions(+), 470 deletions(-)
- docs/sync-everyday-ux-closeout-status - governance/status docs;  3 files changed, 61 insertions(+), 43 deletions(-)
- docs/sync-post-openclaw-audit-hardening-status - governance/status docs;  3 files changed, 208 insertions(+), 101 deletions(-)
- docs/sync-proof-library-progress - governance/status docs;  2 files changed, 59 insertions(+), 25 deletions(-)
- docs/sync-trust-review-card-lock-status - governance/status docs;  2 files changed, 71 insertions(+), 25 deletions(-)
- docs/trust-review-card-priority-lock - governance/status docs;  2 files changed, 127 insertions(+), 17 deletions(-)
- docs/web-news-proof-priority-lock - governance/status docs, proof/audit docs;  6 files changed, 537 insertions(+), 124 deletions(-)
- docs/web-news-ui-proof-lock-closeout-review - governance/status docs, proof/audit docs;  5 files changed, 296 insertions(+), 93 deletions(-)
- docs/work-style-enforcement-lock - governance/status docs;  1 file changed, 375 insertions(+)
- feature/trust-review-card-mvp - runtime code, tests, generated runtime docs, governance/status docs;  21 files changed, 538 insertions(+), 72 deletions(-)
- fix/everyday-ux-friction-slice-9 - runtime code, tests;  4 files changed, 337 insertions(+), 16 deletions(-)
- fix/openclaw-freeform-goal-governance-patches - runtime code, tests, generated runtime docs;  16 files changed, 647 insertions(+), 71 deletions(-)
- fix/ui-web-news-proof-blockers - runtime code, tests, proof/audit docs;  17 files changed, 1111 insertions(+), 65 deletions(-)
- fix/ui-web-news-proof-followups - runtime code, tests, proof/audit docs;  22 files changed, 318 insertions(+), 41 deletions(-)
- fix/web-news-weak-query-confidence-current-main - runtime code;  1 file changed, 1 deletion(-)
- proof/dashboard-stale-degraded-rendering - tests, generated runtime docs, governance/status docs, proof/audit docs;  26 files changed, 586 insertions(+), 70 deletions(-)
- proof/everyday-ux-live-workflow-baseline - proof/audit docs;  1 file changed, 646 insertions(+)
- proof/stale-provider-credibility-fixtures - runtime code, tests, generated runtime docs, governance/status docs, proof/audit docs;  22 files changed, 791 insertions(+), 76 deletions(-)
- proof/ui-malformed-rapid-click-stress - tests, generated runtime docs, governance/status docs, proof/audit docs;  21 files changed, 405 insertions(+), 55 deletions(-)
- docs/fix-shopify-truth-and-active-todo / PR #166 - stale against current main; close or replace with a fresh narrow Shopify truth patch if still needed.

## Patches Created

- This audit document.
- branches_safe_to_delete.txt, a deletion plan only. No remote branches were deleted.

## Tests Run

- No runtime tests run; this pass produced docs/audit artifacts only.
- Git diff/log/name-only checks were collected per branch and recorded below.

## Risks

- Some stale branches have unique historical diffs. They should not be merged directly because they may reintroduce old priority language, generated runtime doc edits, or superseded governance claims.
- PR #166 may still contain individually useful Shopify truth sentences, but the patch as a whole is stale and should not be merged.

## Next Action

1. Review/merge or close PR #173.
2. Close/supersede PR #166 rather than merging it.
3. Ask for human approval before deleting branches listed in branches_safe_to_delete.txt.
4. For non-merged stale branches, inspect only if an owner believes the branch contains still-current work.

## Final Verdict

No branch should be merged directly; only extracted patches are recommended.

These specific branches are safe to delete after human approval.

These specific branches need review before deletion.

This consolidation PR is safe to merge because it only updates current docs/audit truth.

## Per-Branch Evidence

### audit/full-repo-doc-code-alignment

- latest: 61161036fdc8 / 2026-05-11
- merged into main: no
- unique commits: 6
- diff summary:  3 files changed, 1063 insertions(+)
- touches: future docs, proof/audit docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/audit/full-repo-doc-code-alignment | head -50):

```text
6116103 (origin/audit/full-repo-doc-code-alignment, audit/full-repo-doc-code-alignment) audit: correct PASS3 verdict and promote OpenClaw gov inspection to P1-GOV
e8fa0de audit: full repo/doc/code alignment audit — findings and patch roadmap
50e01bb audit: add pass 2 reachability findings
bed77ed audit: document openclaw two-lane execution split
e5775bd audit: add second-pass caveats and missing findings
d48ce7f audit: add pass 1 runtime and openclaw audit findings
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 3 files changed, 1063 insertions(+)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
docs/audits/PASS1_RUNTIME_AND_OPENCLAW_AUDIT_2026-05-11.md
docs/audits/PASS3_FULL_ALIGNMENT_AUDIT_2026-05-11.md
docs/audits/PATCH_ROADMAP_2026-05-11.md
```

### audit/openclaw-freeform-goal-inspection

- latest: 37e742d388ac / 2026-05-11
- merged into main: no
- unique commits: 4
- diff summary:  12 files changed, 1135 insertions(+), 120 deletions(-)
- touches: generated runtime docs, future docs, proof/audit docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/audit/openclaw-freeform-goal-inspection | head -50):

```text
37e742d (origin/audit/openclaw-freeform-goal-inspection, audit/openclaw-freeform-goal-inspection) docs: regenerate runtime docs for audit branch state
4a60ea8 docs: strengthen Governed Autonomy direction with architecture grounding and gap analysis
44b56b4 docs: establish Governed Autonomy direction — autonomy allowed inside Governor-monitored envelopes
4bda0b0 audit: OpenClaw freeform goal governance inspection — PASS 4
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 12 files changed, 1135 insertions(+), 120 deletions(-)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
_MOCs/BY_PHASE.md
_MOCs/BY_TOPIC.md
_MOCs/BY_TYPE.md
_MOCs/CODE_BY_LAYER.md
_MOCs/CODE_MODULES.md
_MOCs/HOME.md
_MOCs/RECENT.md
_MOCs/REPO_BY_FOLDER.md
docs/Future/NOVA_GOVERNED_AUTONOMY_DIRECTION_2026-05-11.md
docs/audits/PASS4_OPENCLAW_FREEFORM_GOAL_INSPECTION_2026-05-11.md
docs/current_runtime/CURRENT_RUNTIME_STATE.md
docs/current_runtime/RUNTIME_FINGERPRINT.md
```

### claude/adoring-ramanujan-2c80f6

- latest: 23e89522b5ac / 2026-05-01
- merged into main: no
- unique commits: 1
- diff summary:  8 files changed, 81 insertions(+), 30 deletions(-)
- touches: future docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/claude/adoring-ramanujan-2c80f6 | head -50):

```text
23e8952 (origin/claude/adoring-ramanujan-2c80f6, claude/adoring-ramanujan-2c80f6) docs: save Auralis planning refinements and roadmap handoff notes
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 8 files changed, 81 insertions(+), 30 deletions(-)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
4-15-26 NEW ROADMAP/HANDOFF_2026-04-26_TRUST_RECEIPT_RECOVERY.md
4-15-26 NEW ROADMAP/Now.md
docs/future/AURALIS_CLIENT_FUNNEL.md
docs/future/AURALIS_MVP_EXECUTION_PLAN.md
docs/future/AURALIS_NOVALIS_INTEGRATION_GOALS.md
docs/future/AURALIS_RISK_AND_POLICY.md
docs/future/AURALIS_TECHNICAL_INTEGRATION_SPEC.md
docs/future/NOVA_EVERYDAY_MODE_REVIEW_SUMMARY_2026-04-26.md
```

### claude/review-repo-status-f2E7Q

- latest: 0cc126ecfd93 / 2026-05-12
- merged into main: no
- unique commits: 1
- diff summary:  8 files changed, 125 insertions(+), 141 deletions(-)
- touches: governance/status docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/claude/review-repo-status-f2E7Q | head -50):

```text
0cc126e (origin/claude/review-repo-status-f2E7Q) docs: runtime-doc regen confirmed current; refresh MOCs and close task
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 8 files changed, 125 insertions(+), 141 deletions(-)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
.agent_context/current_priority.md
AGENTS.md
_MOCs/BY_TYPE.md
_MOCs/HOME.md
_MOCs/RECENT.md
_MOCs/REPO_BY_FOLDER.md
docs/status/CURRENT_WORK_STATUS.md
docs/todo/ACTIVE_TODO.md
```

### codex/harden-web-ui-proof-lock-wording

- latest: 8eb608d50345 / 2026-05-06
- merged into main: no
- unique commits: 1
- diff summary:  4 files changed, 103 insertions(+), 2 deletions(-)
- touches: governance/status docs, proof/audit docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/codex/harden-web-ui-proof-lock-wording | head -50):

```text
8eb608d (origin/codex/harden-web-ui-proof-lock-wording, codex/harden-web-ui-proof-lock-wording) docs: harden web UI proof lock wording
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 4 files changed, 103 insertions(+), 2 deletions(-)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
docs/PROOFS/UI-Commands/README.md
docs/PROOFS/Web-News-Reporting/README.md
docs/status/ACTIVE_PRIORITY_LOCK_2026-05-06_WEB_NEWS_PROOF_STRESS_TEST.md
docs/todo/ACTIVE_TODO.md
```

### codex/ui-web-news-proof-evidence

- latest: 91fbcf1038fc / 2026-05-07
- merged into main: no
- unique commits: 1
- diff summary:  20 files changed, 18779 insertions(+)
- touches: proof/audit docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/codex/ui-web-news-proof-evidence | head -50):

```text
91fbcf1 (origin/codex/ui-web-news-proof-evidence, codex/ui-web-news-proof-evidence) docs: add UI and web news proof evidence
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 20 files changed, 18779 insertions(+)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
docs/PROOFS/UI-Commands/BLOCKERS.md
docs/PROOFS/UI-Commands/FRICTION_LOG.md
docs/PROOFS/UI-Commands/README.md
docs/PROOFS/UI-Commands/REGRESSION_RECOMMENDATIONS.md
docs/PROOFS/UI-Commands/REPORT.md
docs/PROOFS/UI-Commands/VERIFICATION_MATRIX.md
docs/PROOFS/UI-Commands/evidence/2026-05-06/raw/browser_use_failure.txt
docs/PROOFS/UI-Commands/evidence/2026-05-06/raw/start_daemon_output.txt
docs/PROOFS/UI-Commands/evidence/2026-05-06/raw/static_button_inventory.json
docs/PROOFS/UI-Commands/evidence/2026-05-06/raw/stop_daemon_output.txt
docs/PROOFS/UI-Commands/evidence/2026-05-06/raw/websocket_command_probe.json
docs/PROOFS/UI-Commands/evidence/2026-05-06/raw/websocket_command_probe_corrected.json
docs/PROOFS/UI-Commands/evidence/2026-05-06/raw/websocket_command_probe_summary.json
docs/PROOFS/Web-News-Reporting/BLOCKERS.md
docs/PROOFS/Web-News-Reporting/FRICTION_LOG.md
docs/PROOFS/Web-News-Reporting/README.md
docs/PROOFS/Web-News-Reporting/REGRESSION_RECOMMENDATIONS.md
docs/PROOFS/Web-News-Reporting/REPORT.md
docs/PROOFS/Web-News-Reporting/evidence/2026-05-06/raw/websocket_web_news_probe.json
docs/PROOFS/Web-News-Reporting/evidence/2026-05-06/raw/websocket_web_news_probe_corrected.json
```

### docs/active-priority-lock-openclaw-path

- latest: b4056c53e67e / 2026-05-04
- merged into main: no
- unique commits: 5
- diff summary:  3 files changed, 144 insertions(+), 371 deletions(-)
- touches: governance/status docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/docs/active-priority-lock-openclaw-path | head -50):

```text
b4056c5 (origin/docs/active-priority-lock-openclaw-path) docs: remove redundant heading in current work status
0f6ecad docs: clarify priority lock authority
8c55461 docs: add priority lock to current work status
10a73bd docs: add priority lock override to active todo
86d73a6 docs: add active priority lock
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 3 files changed, 144 insertions(+), 371 deletions(-)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
docs/status/ACTIVE_PRIORITY_LOCK_2026-05-04.md
docs/status/CURRENT_WORK_STATUS.md
docs/todo/ACTIVE_TODO.md
```

### docs/approval-gate-wiring-priority-lock

- latest: 7e3bc2ad89d0 / 2026-05-14
- merged into main: no
- unique commits: 1
- diff summary:  6 files changed, 141 insertions(+), 28 deletions(-)
- touches: governance/status docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/docs/approval-gate-wiring-priority-lock | head -50):

```text
7e3bc2a (origin/docs/approval-gate-wiring-priority-lock, docs/approval-gate-wiring-priority-lock) docs: add approval gate wiring priority lock
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 6 files changed, 141 insertions(+), 28 deletions(-)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
.agent_context/current_priority.md
AGENTS.md
README.md
docs/status/ACTIVE_PRIORITY_LOCK_2026-05-15_APPROVAL_GATE_WIRING.md
docs/status/CURRENT_WORK_STATUS.md
docs/todo/ACTIVE_TODO.md
```

### docs/close-runtime-truth-audit-lock

- latest: c667ca10bed8 / 2026-05-06
- merged into main: no
- unique commits: 3
- diff summary:  3 files changed, 53 insertions(+), 51 deletions(-)
- touches: governance/status docs, proof/audit docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/docs/close-runtime-truth-audit-lock | head -50):

```text
c667ca1 (origin/docs/close-runtime-truth-audit-lock) docs: close runtime truth audit lock
21574e0 docs: close runtime truth audit lock
be70797 docs: close runtime truth audit lock
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 3 files changed, 53 insertions(+), 51 deletions(-)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
docs/status/ACTIVE_PRIORITY_LOCK_2026-05-06_RUNTIME_TRUTH_AUDIT.md
docs/status/CURRENT_WORK_STATUS.md
docs/todo/ACTIVE_TODO.md
```

### docs/correct-shopify-future-operator-truth

- latest: 392e7a6295a1 / 2026-05-14
- merged into main: no
- unique commits: 2
- diff summary:  8 files changed, 231 insertions(+), 76 deletions(-)
- touches: governance/status docs, future docs, proof/audit docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/docs/correct-shopify-future-operator-truth | head -50):

```text
392e7a6 (origin/docs/correct-shopify-future-operator-truth) docs: record #141 live proof and open Trust Panel MVP lock
0b17f1d docs: correct Shopify future operator truth header
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 8 files changed, 231 insertions(+), 76 deletions(-)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
.agent_context/current_priority.md
AGENTS.md
README.md
docs/PROOFS/Cap-16/SEARCH_WIDGET_WS_LIVE_PROOF_2026-05-14.md
docs/future/NOVA_SHOPIFY_GOVERNED_OPERATOR_DESIGN_2026-04-20.md
docs/status/ACTIVE_PRIORITY_LOCK_2026-05-14_TRUST_PANEL_MVP.md
docs/status/CURRENT_WORK_STATUS.md
docs/todo/ACTIVE_TODO.md
```

### docs/everyday-ux-friction-closeout-review

- latest: 763a6d05dd77 / 2026-05-10
- merged into main: no
- unique commits: 1
- diff summary:  1 file changed, 148 insertions(+)
- touches: proof/audit docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/docs/everyday-ux-friction-closeout-review | head -50):

```text
763a6d0 (origin/docs/everyday-ux-friction-closeout-review, docs/everyday-ux-friction-closeout-review) docs: Everyday UX Friction workstream closeout
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 1 file changed, 148 insertions(+)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
docs/PROOFS/Everyday-UX/EVERYDAY_UX_FRICTION_CLOSEOUT_2026-05-11.md
```

### docs/everyday-ux-friction-priority-lock

- latest: 6c447ac954d4 / 2026-05-10
- merged into main: yes
- unique commits: 0
- diff summary: empty
- touches: other/docs
- classification: A. Already merged / safe delete
- action: delete after human approval
- reason: Tip is contained in origin/main; no unique commits remain.

- required log check (git log --oneline --decorate origin/main..origin/docs/everyday-ux-friction-priority-lock | head -50):

```text
empty
```
- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
empty
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
empty
```

### docs/five-pass-stability-and-operational-roadmap

- latest: fa02bed0e750 / 2026-05-12
- merged into main: no
- unique commits: 4
- diff summary:  2 files changed, 416 insertions(+), 2 deletions(-)
- touches: governance/status docs, future docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/docs/five-pass-stability-and-operational-roadmap | head -50):

```text
fa02bed (origin/docs/five-pass-stability-and-operational-roadmap) docs: refine five-pass roadmap terminology
4e4379a docs: harden five-pass roadmap boundaries
ba04c20 docs: add five-pass roadmap reference and sync PR159 wording
e27e399 docs: add five-pass stability and operational roadmap
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 2 files changed, 416 insertions(+), 2 deletions(-)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
docs/status/CURRENT_WORK_STATUS.md
docs/status/FIVE_PASS_STABILITY_AND_OPERATIONAL_ROADMAP_2026-05-12.md
```

### docs/fix-approval-gate-next-sequence

- latest: e781966cd8d1 / 2026-05-14
- merged into main: no
- unique commits: 1
- diff summary:  1 file changed, 2 insertions(+), 2 deletions(-)
- touches: governance/status docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/docs/fix-approval-gate-next-sequence | head -50):

```text
e781966 (origin/docs/fix-approval-gate-next-sequence, docs/fix-approval-gate-next-sequence) docs: correct approval gate next sequence
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 1 file changed, 2 insertions(+), 2 deletions(-)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
.agent_context/current_priority.md
```

### docs/fix-shopify-truth-and-active-todo

- latest: 79cd15a6a028 / 2026-05-13
- merged into main: no
- unique commits: 1
- diff summary:  1 file changed, 107 insertions(+), 52 deletions(-)
- touches: governance/status docs
- classification: D. Active PR branch
- action: close or supersede PR #166
- reason: Open PR edits ACTIVE_TODO toward older #141/search-widget and pre-approval-gate state; stale against current main after #171/#172.
- open PR: PR #166: docs: sync ACTIVE_TODO with current runtime/shopify truth (https://github.com/christopherbdaugherty96/NovaLIS/pull/166); draft=False

- required log check (git log --oneline --decorate origin/main..origin/docs/fix-shopify-truth-and-active-todo | head -50):

```text
79cd15a (origin/docs/fix-shopify-truth-and-active-todo) docs: fix active todo after runtime-doc regen and Shopify review
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 1 file changed, 107 insertions(+), 52 deletions(-)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
docs/todo/ACTIVE_TODO.md
```

### docs/governed-autonomy-direction-lock

- latest: df48a119e8a6 / 2026-05-11
- merged into main: no
- unique commits: 1
- diff summary:  1 file changed, 318 insertions(+)
- touches: governance/status docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/docs/governed-autonomy-direction-lock | head -50):

```text
df48a11 (origin/docs/governed-autonomy-direction-lock) docs: lock governed autonomy direction
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 1 file changed, 318 insertions(+)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
docs/status/GOVERNED_AUTONOMY_DIRECTION_LOCK_2026-05-11.md
```

### docs/lock-audit-first-safety-boundary

- latest: 25e72b177fe4 / 2026-05-11
- merged into main: no
- unique commits: 1
- diff summary:  1 file changed, 48 insertions(+), 13 deletions(-)
- touches: governance/status docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/docs/lock-audit-first-safety-boundary | head -50):

```text
25e72b1 (origin/docs/lock-audit-first-safety-boundary) docs: lock audit-first safety boundary
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 1 file changed, 48 insertions(+), 13 deletions(-)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
.agent_context/current_priority.md
```

### docs/lock-two-domain-nova-direction

- latest: cd796bf8a3a8 / 2026-05-11
- merged into main: no
- unique commits: 4
- diff summary:  2 files changed, 366 insertions(+)
- touches: future docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/docs/lock-two-domain-nova-direction | head -50):

```text
cd796bf (origin/docs/lock-two-domain-nova-direction) docs: clarify what Nova is in two-domain direction
bc6f6ae docs: clarify two-domain direction status wording
7b1f332 docs: clarify two-domain Nova direction in README
11b2cec docs: lock two-domain Nova direction
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 2 files changed, 366 insertions(+)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
README.md
docs/future/NOVA_TWO_DOMAIN_DIRECTION_2026-05-11.md
```

### docs/nova-conversation-response-contract

- latest: 87c48212d37a / 2026-05-10
- merged into main: no
- unique commits: 1
- diff summary:  1 file changed, 234 insertions(+)
- touches: other/docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/docs/nova-conversation-response-contract | head -50):

```text
87c4821 (origin/docs/nova-conversation-response-contract, docs/nova-conversation-response-contract) docs: add Nova conversation response contract
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 1 file changed, 234 insertions(+)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
docs/nova-conversation-response-contract.md
```

### docs/patch-shopify-operator-truth-header

- latest: 2185b8817033 / 2026-05-12
- merged into main: yes
- unique commits: 0
- diff summary: empty
- touches: other/docs
- classification: A. Already merged / safe delete
- action: delete after human approval
- reason: Tip is contained in origin/main; no unique commits remain.

- required log check (git log --oneline --decorate origin/main..origin/docs/patch-shopify-operator-truth-header | head -50):

```text
empty
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
empty
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
empty
```

### docs/piper-first-voice-direction

- latest: 7f015c65546e / 2026-05-11
- merged into main: no
- unique commits: 1
- diff summary:  1 file changed, 111 insertions(+), 72 deletions(-)
- touches: future docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/docs/piper-first-voice-direction | head -50):

```text
7f015c6 (origin/docs/piper-first-voice-direction) docs: make Piper current voice path and ElevenLabs future optional
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 1 file changed, 111 insertions(+), 72 deletions(-)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
docs/future/NOVA_ELEVENLABS_VOICE_INTEGRATION_PLAN.md
```

### docs/post-149-current-priority-closeout

- latest: 0220d538d706 / 2026-05-11
- merged into main: no
- unique commits: 4
- diff summary:  3 files changed, 196 insertions(+), 28 deletions(-)
- touches: governance/status docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/docs/post-149-current-priority-closeout | head -50):

```text
0220d53 (origin/docs/post-149-current-priority-closeout) docs: update active todo after PR 149 merge
91be8e9 docs: close stale post-149 continuity wording
4eee869 docs: soften search widget follow-up wording
3c288a6 docs: close post-149 priority sync
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 3 files changed, 196 insertions(+), 28 deletions(-)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
.agent_context/current_priority.md
docs/status/CURRENT_WORK_STATUS.md
docs/todo/ACTIVE_TODO.md
```

### docs/proof-infrastructure-closeout-review

- latest: cefe06388b12 / 2026-05-09
- merged into main: yes
- unique commits: 0
- diff summary: empty
- touches: other/docs
- classification: A. Already merged / safe delete
- action: delete after human approval
- reason: Tip is contained in origin/main; no unique commits remain.

- required log check (git log --oneline --decorate origin/main..origin/docs/proof-infrastructure-closeout-review | head -50):

```text
empty
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
empty
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
empty
```

### docs/readme-current-state-v0.5

- latest: 6c2ed8729fcc / 2026-05-12
- merged into main: no
- unique commits: 1
- diff summary:  1 file changed, 40 insertions(+), 10 deletions(-)
- touches: other/docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/docs/readme-current-state-v0.5 | head -50):

```text
6c2ed87 (origin/docs/readme-current-state-v0.5) docs: update README current state to v0.5
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 1 file changed, 40 insertions(+), 10 deletions(-)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
README.md
```

### docs/regenerate-runtime-docs

- latest: 2fbe726a51b8 / 2026-05-11
- merged into main: no
- unique commits: 1
- diff summary:  10 files changed, 344 insertions(+), 120 deletions(-)
- touches: generated runtime docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/docs/regenerate-runtime-docs | head -50):

```text
2fbe726 (origin/docs/regenerate-runtime-docs, docs/regenerate-runtime-docs) docs: regenerate runtime docs and MOCs — reflect current codebase state
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 10 files changed, 344 insertions(+), 120 deletions(-)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
_MOCs/BY_PHASE.md
_MOCs/BY_TOPIC.md
_MOCs/BY_TYPE.md
_MOCs/CODE_BY_LAYER.md
_MOCs/CODE_MODULES.md
_MOCs/HOME.md
_MOCs/RECENT.md
_MOCs/REPO_BY_FOLDER.md
docs/current_runtime/CURRENT_RUNTIME_STATE.md
docs/current_runtime/RUNTIME_FINGERPRINT.md
```

### docs/regenerate-runtime-docs-post-openclaw-hardening

- latest: 1f2e8ca0b09f / 2026-05-11
- merged into main: no
- unique commits: 1
- diff summary:  1 file changed, 57 insertions(+), 7 deletions(-)
- touches: governance/status docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/docs/regenerate-runtime-docs-post-openclaw-hardening | head -50):

```text
1f2e8ca (origin/docs/regenerate-runtime-docs-post-openclaw-hardening) docs: add runtime doc regeneration todo
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 1 file changed, 57 insertions(+), 7 deletions(-)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
docs/todo/ACTIVE_TODO.md
```

### docs/shopify-pod-business-intelligence-plan

- latest: da47d2b188fc / 2026-05-11
- merged into main: no
- unique commits: 3
- diff summary:  2 files changed, 573 insertions(+)
- touches: governance/status docs, future docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/docs/shopify-pod-business-intelligence-plan | head -50):

```text
da47d2b (origin/docs/shopify-pod-business-intelligence-plan) docs: add creator-led Shopify POD intelligence model
fb42a21 (origin/docs/work-style-enforcement-lock, docs/work-style-enforcement-lock) docs: patch work-style enforcement lock — 5 ChatGPT second-pass fixes
2934717 docs: add work style enforcement lock
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 2 files changed, 573 insertions(+)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
docs/future/NOVA_CREATOR_LED_SHOPIFY_POD_MODEL_2026-05-11.md
docs/status/WORK_STYLE_ENFORCEMENT_LOCK_2026-05-11.md
```

### docs/stage-6-truth-sync

- latest: c2011e3c3b1f / 2026-05-03
- merged into main: no
- unique commits: 10
- diff summary:  9 files changed, 259 insertions(+), 330 deletions(-)
- touches: governance/status docs, future docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/docs/stage-6-truth-sync | head -50):

```text
c2011e3 (origin/docs/stage-6-truth-sync) docs: add missing stage guide and google foundation references
74b56fa docs: clarify implemented subsets vs future specs
a78d0bd docs: align commands with memory and planning reality
91ba552 docs: align first five minutes with memory and routine truth
953dfa2 docs: update start_here brutal truth and reflect Stage 3-6 substrate
5ec2543 docs: fix duplicate Step 6 header and clarify Plan My Week proof wording
d130435 docs: correct stage guide plan my week status and next steps
030687e docs: sync what works today with Stage 3-6 truth
96d814f docs: remove capitalized Future Google connector duplicate
d208a58 docs: move Google read-only connector foundation to lowercase future path
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 9 files changed, 259 insertions(+), 330 deletions(-)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
START_HERE.md
docs/INDEX.md
docs/future/GOOGLE_READ_ONLY_CONNECTOR_FOUNDATION_2026-05-03.md
docs/future/README.md
docs/product/FIRST_5_MINUTES.md
docs/product/TRY_THESE_COMMANDS.md
docs/product/WHAT_WORKS_TODAY.md
docs/reference/HUMAN_GUIDES/CURRENT_STAGE_GUIDE.md
docs/todo/ACTIVE_TODO.md
```

### docs/sync-after-web-news-stress-fixtures

- latest: 2860896c9923 / 2026-05-07
- merged into main: no
- unique commits: 1
- diff summary:  2 files changed, 41 insertions(+), 14 deletions(-)
- touches: governance/status docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/docs/sync-after-web-news-stress-fixtures | head -50):

```text
2860896 (origin/docs/sync-after-web-news-stress-fixtures, docs/sync-after-web-news-stress-fixtures) docs: sync status after web news stress fixtures
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 2 files changed, 41 insertions(+), 14 deletions(-)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
docs/status/CURRENT_WORK_STATUS.md
docs/todo/ACTIVE_TODO.md
```

### docs/sync-agents-and-active-todo-after-pr159

- latest: 0dd507899e88 / 2026-05-12
- merged into main: no
- unique commits: 2
- diff summary:  2 files changed, 41 insertions(+), 4 deletions(-)
- touches: governance/status docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/docs/sync-agents-and-active-todo-after-pr159 | head -50):

```text
0dd5078 (origin/docs/sync-agents-and-active-todo-after-pr159) docs: sync active todo after PR159
866330b docs: sync AGENTS current priority after PR159
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 2 files changed, 41 insertions(+), 4 deletions(-)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
AGENTS.md
docs/todo/ACTIVE_TODO.md
```

### docs/sync-approval-gate-coverage-status

- latest: d8dfcefdad13 / 2026-05-17
- merged into main: no
- unique commits: 1
- diff summary:  3 files changed, 76 insertions(+), 29 deletions(-)
- touches: governance/status docs
- classification: D. Active PR branch
- action: keep / review PR #173
- reason: Current conservative approval-gate status sync PR; merge through PR only if accepted.
- open PR: PR #173: docs: sync approval gate coverage status (https://github.com/christopherbdaugherty96/NovaLIS/pull/173); draft=True

- required log check (git log --oneline --decorate origin/main..origin/docs/sync-approval-gate-coverage-status | head -50):

```text
d8dfcef (origin/docs/sync-approval-gate-coverage-status, docs/sync-approval-gate-coverage-status) docs: sync approval gate coverage status
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 3 files changed, 76 insertions(+), 29 deletions(-)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
.agent_context/current_priority.md
docs/status/CURRENT_WORK_STATUS.md
docs/todo/ACTIVE_TODO.md
```

### docs/sync-current-priority-after-runtime-doc-todo

- latest: ce9cb2209f9e / 2026-05-11
- merged into main: no
- unique commits: 4
- diff summary:  4 files changed, 125 insertions(+), 55 deletions(-)
- touches: governance/status docs, future docs, proof/audit docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/docs/sync-current-priority-after-runtime-doc-todo | head -50):

```text
ce9cb22 (origin/docs/sync-current-priority-after-runtime-doc-todo) docs: label audit roadmap as historical and update status
a3dddcf docs: label workflow roadmap as historical snapshot
7b0a556 docs: sync current work status to runtime doc regeneration
147c6f5 docs: sync current priority to runtime doc regeneration
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 4 files changed, 125 insertions(+), 55 deletions(-)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
.agent_context/current_priority.md
docs/audits/PATCH_ROADMAP_2026-05-11.md
docs/status/CURRENT_WORK_STATUS.md
docs/status/WORKFLOW_STAGE_ROADMAP_2026-05-02.md
```

### docs/sync-current-status-after-direction-updates

- latest: 97f7f2ae13c5 / 2026-05-11
- merged into main: no
- unique commits: 4
- diff summary:  4 files changed, 247 insertions(+), 470 deletions(-)
- touches: governance/status docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/docs/sync-current-status-after-direction-updates | head -50):

```text
97f7f2a (origin/docs/sync-current-status-after-direction-updates) docs: sync active todo after PR 144-148
b42c47d docs: sync current work status after PR 144-148
b9b3f9a docs: sync current priority after PR 144-148
623f516 docs: sync agent current priority after recent closeouts
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 4 files changed, 247 insertions(+), 470 deletions(-)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
.agent_context/current_priority.md
AGENTS.md
docs/status/CURRENT_WORK_STATUS.md
docs/todo/ACTIVE_TODO.md
```

### docs/sync-everyday-ux-closeout-status

- latest: 6d5830971344 / 2026-05-11
- merged into main: no
- unique commits: 1
- diff summary:  3 files changed, 61 insertions(+), 43 deletions(-)
- touches: governance/status docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/docs/sync-everyday-ux-closeout-status | head -50):

```text
6d58309 (origin/docs/sync-everyday-ux-closeout-status, docs/sync-everyday-ux-closeout-status) docs: sync continuity files to reflect Everyday UX Friction closeout
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 3 files changed, 61 insertions(+), 43 deletions(-)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
.agent_context/current_priority.md
docs/status/CURRENT_WORK_STATUS.md
docs/todo/ACTIVE_TODO.md
```

### docs/sync-post-openclaw-audit-hardening-status

- latest: dfb3c02d58f1 / 2026-05-11
- merged into main: no
- unique commits: 3
- diff summary:  3 files changed, 208 insertions(+), 101 deletions(-)
- touches: governance/status docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/docs/sync-post-openclaw-audit-hardening-status | head -50):

```text
dfb3c02 (origin/docs/sync-post-openclaw-audit-hardening-status) docs: sync active todo after audit hardening
e2f7650 docs: sync current work status after audit hardening
94231b3 docs: sync current priority after OpenClaw audit hardening
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 3 files changed, 208 insertions(+), 101 deletions(-)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
.agent_context/current_priority.md
docs/status/CURRENT_WORK_STATUS.md
docs/todo/ACTIVE_TODO.md
```

### docs/sync-proof-library-progress

- latest: d10d9db3be71 / 2026-05-07
- merged into main: no
- unique commits: 2
- diff summary:  2 files changed, 59 insertions(+), 25 deletions(-)
- touches: governance/status docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/docs/sync-proof-library-progress | head -50):

```text
d10d9db (origin/docs/sync-proof-library-progress) docs: sync status with proof library progress
2016118 docs: sync todo with proof library progress
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 2 files changed, 59 insertions(+), 25 deletions(-)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
docs/status/CURRENT_WORK_STATUS.md
docs/todo/ACTIVE_TODO.md
```

### docs/sync-trust-review-card-lock-status

- latest: 64e724f16ef8 / 2026-05-06
- merged into main: no
- unique commits: 2
- diff summary:  2 files changed, 71 insertions(+), 25 deletions(-)
- touches: governance/status docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/docs/sync-trust-review-card-lock-status | head -50):

```text
64e724f (origin/docs/sync-trust-review-card-lock-status) docs: sync active todo with trust review card lock
eee2dbc docs: sync current status with trust review card lock
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 2 files changed, 71 insertions(+), 25 deletions(-)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
docs/status/CURRENT_WORK_STATUS.md
docs/todo/ACTIVE_TODO.md
```

### docs/trust-review-card-priority-lock

- latest: 1092665a6fc6 / 2026-05-06
- merged into main: no
- unique commits: 2
- diff summary:  2 files changed, 127 insertions(+), 17 deletions(-)
- touches: governance/status docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/docs/trust-review-card-priority-lock | head -50):

```text
1092665 (origin/docs/trust-review-card-priority-lock) docs: add trust review card MVP priority lock
6aa6967 docs: clarify local capability matrix accepted scope
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 2 files changed, 127 insertions(+), 17 deletions(-)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
docs/status/ACTIVE_PRIORITY_LOCK_2026-05-06_TRUST_REVIEW_CARD_MVP.md
docs/status/LOCAL_CAPABILITY_SIGNOFF_MATRIX_2026-05-06.md
```

### docs/ui-simplification-inventory

- latest: dede4bca94a1 / 2026-05-09
- merged into main: yes
- unique commits: 0
- diff summary: empty
- touches: other/docs
- classification: A. Already merged / safe delete
- action: delete after human approval
- reason: Tip is contained in origin/main; no unique commits remain.

- required log check (git log --oneline --decorate origin/main..origin/docs/ui-simplification-inventory | head -50):

```text
empty
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
empty
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
empty
```

### docs/web-news-proof-priority-lock

- latest: fb2d3d63a256 / 2026-05-06
- merged into main: no
- unique commits: 7
- diff summary:  6 files changed, 537 insertions(+), 124 deletions(-)
- touches: governance/status docs, proof/audit docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/docs/web-news-proof-priority-lock | head -50):

```text
fb2d3d6 (origin/docs/web-news-proof-priority-lock) docs: sync todo with ui command proof lock
9f73291 docs: sync status with ui command proof lock
b4947bc docs: expand proof lock to full ui command verification
8d49c4c docs: add ui commands proof scaffold
69cea98 docs: add web news reporting proof folder scaffold
1a13782 docs: add web news reporting proof stress test lock
be8fe99 docs: pause trust review card lock
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 6 files changed, 537 insertions(+), 124 deletions(-)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
docs/PROOFS/UI-Commands/README.md
docs/PROOFS/Web-News-Reporting/README.md
docs/status/ACTIVE_PRIORITY_LOCK_2026-05-06_TRUST_REVIEW_CARD_MVP.md
docs/status/ACTIVE_PRIORITY_LOCK_2026-05-06_WEB_NEWS_PROOF_STRESS_TEST.md
docs/status/CURRENT_WORK_STATUS.md
docs/todo/ACTIVE_TODO.md
```

### docs/web-news-ui-proof-lock-closeout-review

- latest: 1375f8bb0df5 / 2026-05-07
- merged into main: no
- unique commits: 1
- diff summary:  5 files changed, 296 insertions(+), 93 deletions(-)
- touches: governance/status docs, proof/audit docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/docs/web-news-ui-proof-lock-closeout-review | head -50):

```text
1375f8b (origin/docs/web-news-ui-proof-lock-closeout-review, docs/web-news-ui-proof-lock-closeout-review) docs: add web news ui proof lock closeout review
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 5 files changed, 296 insertions(+), 93 deletions(-)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
.agent_context/current_priority.md
docs/status/ACTIVE_PRIORITY_LOCK_2026-05-06_WEB_NEWS_PROOF_STRESS_TEST.md
docs/status/CURRENT_WORK_STATUS.md
docs/status/WEB_NEWS_UI_PROOF_LOCK_CLOSEOUT_REVIEW_2026-05-07.md
docs/todo/ACTIVE_TODO.md
```

### docs/work-style-enforcement-lock

- latest: fb42a219339f / 2026-05-10
- merged into main: no
- unique commits: 2
- diff summary:  1 file changed, 375 insertions(+)
- touches: governance/status docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/docs/work-style-enforcement-lock | head -50):

```text
fb42a21 (origin/docs/work-style-enforcement-lock, docs/work-style-enforcement-lock) docs: patch work-style enforcement lock — 5 ChatGPT second-pass fixes
2934717 docs: add work style enforcement lock
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 1 file changed, 375 insertions(+)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
docs/status/WORK_STYLE_ENFORCEMENT_LOCK_2026-05-11.md
```

### feature/trust-review-card-mvp

- latest: db10b5f7ece8 / 2026-05-07
- merged into main: no
- unique commits: 1
- diff summary:  21 files changed, 538 insertions(+), 72 deletions(-)
- touches: runtime code, tests, generated runtime docs, governance/status docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/feature/trust-review-card-mvp | head -50):

```text
db10b5f (origin/feature/trust-review-card-mvp, feature/trust-review-card-mvp) feat: add trust review card MVP
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 21 files changed, 538 insertions(+), 72 deletions(-)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
Nova-Frontend-Dashboard/dashboard-chat-news.js
Nova-Frontend-Dashboard/dashboard-surfaces.css
_MOCs/BY_TOPIC.md
_MOCs/BY_TYPE.md
_MOCs/HOME.md
_MOCs/RECENT.md
_MOCs/REPO_BY_FOLDER.md
docs/current_runtime/CURRENT_RUNTIME_STATE.md
docs/current_runtime/RUNTIME_FINGERPRINT.md
docs/status/ACTIVE_PRIORITY_LOCK_2026-05-06_TRUST_REVIEW_CARD_MVP.md
docs/status/CURRENT_WORK_STATUS.md
docs/status/TRUST_REVIEW_CARD_MVP_STATUS_2026-05-07.md
docs/todo/ACTIVE_TODO.md
nova_backend/src/brain_server.py
nova_backend/src/conversation/general_chat_runtime.py
nova_backend/src/websocket/session_handler.py
nova_backend/static/dashboard-chat-news.js
nova_backend/static/dashboard-surfaces.css
nova_backend/tests/conversation/test_request_understanding_review_card.py
nova_backend/tests/phase45/test_brain_server_trust_status.py
nova_backend/tests/phase45/test_dashboard_trust_review_widget.py
```

### fix/everyday-ux-friction-slice-9

- latest: 1ef59e44796c / 2026-05-10
- merged into main: no
- unique commits: 2
- diff summary:  4 files changed, 337 insertions(+), 16 deletions(-)
- touches: runtime code, tests
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/fix/everyday-ux-friction-slice-9 | head -50):

```text
1ef59e4 (origin/fix/everyday-ux-friction-slice-9, fix/everyday-ux-friction-slice-9) fix: add 'i want help' to HELP_ORIENT_RE; add positive + negative pipeline tests
fe319b9 fix: everyday UX friction slice 9 — RC-7 normalization, dead code, pipeline tests
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 4 files changed, 337 insertions(+), 16 deletions(-)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
nova_backend/src/conversation/response_style_router.py
nova_backend/src/governor/governor_mediator.py
nova_backend/src/websocket/intent_patterns.py
nova_backend/tests/websocket/test_session_layer_pipeline.py
```

### fix/openclaw-freeform-goal-governance-patches

- latest: abb848cf6c44 / 2026-05-11
- merged into main: no
- unique commits: 6
- diff summary:  16 files changed, 647 insertions(+), 71 deletions(-)
- touches: runtime code, tests, generated runtime docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/fix/openclaw-freeform-goal-governance-patches | head -50):

```text
abb848c (origin/fix/openclaw-freeform-goal-governance-patches, fix/openclaw-freeform-goal-governance-patches) docs: regenerate runtime docs for final merged state
f82233c Merge remote-tracking branch 'origin/main' into fix/openclaw-freeform-goal-governance-patches
d7c3081 docs: regenerate runtime docs for governance patches branch state
3c364a5 fix: pre-existing lint and adversarial test failures
c94394c fix: second-pass — RunBudgetMeter URL-gating with empty allowed_hostnames
156db77 fix: PATCH A–D — enforce read-only allowlist and network budget on freeform goal path
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 16 files changed, 647 insertions(+), 71 deletions(-)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
_MOCs/BY_TOPIC.md
_MOCs/BY_TYPE.md
_MOCs/CODE_BY_LAYER.md
_MOCs/CODE_MODULES.md
_MOCs/HOME.md
_MOCs/RECENT.md
_MOCs/REPO_BY_FOLDER.md
docs/current_runtime/CURRENT_RUNTIME_STATE.md
docs/current_runtime/RUNTIME_FINGERPRINT.md
nova_backend/src/actions/action_request.py
nova_backend/src/api/openclaw_agent_api.py
nova_backend/src/openclaw/agent_runner.py
nova_backend/src/openclaw/tool_registry.py
nova_backend/tests/adversarial/test_no_direct_network_imports_outside_network_mediator.py
nova_backend/tests/openclaw/test_agent_runner_goal.py
nova_backend/tests/openclaw/test_freeform_goal_governance.py
```

### fix/ui-web-news-proof-blockers

- latest: f44a31982aff / 2026-05-07
- merged into main: no
- unique commits: 1
- diff summary:  17 files changed, 1111 insertions(+), 65 deletions(-)
- touches: runtime code, tests, proof/audit docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/fix/ui-web-news-proof-blockers | head -50):

```text
f44a319 (origin/fix/ui-web-news-proof-blockers, fix/ui-web-news-proof-blockers) fix: harden UI and web news proof blockers
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 17 files changed, 1111 insertions(+), 65 deletions(-)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
docs/PROOFS/UI-Commands/BLOCKERS.md
docs/PROOFS/UI-Commands/FRICTION_LOG.md
docs/PROOFS/UI-Commands/REGRESSION_RECOMMENDATIONS.md
docs/PROOFS/UI-Commands/REPORT.md
docs/PROOFS/UI-Commands/VERIFICATION_MATRIX.md
docs/PROOFS/UI-Commands/evidence/2026-05-07/raw/focused_pytest_results.txt
docs/PROOFS/UI-Commands/evidence/2026-05-07/raw/ui_blocker_fix_probe.json
docs/PROOFS/Web-News-Reporting/BLOCKERS.md
docs/PROOFS/Web-News-Reporting/FRICTION_LOG.md
docs/PROOFS/Web-News-Reporting/REGRESSION_RECOMMENDATIONS.md
docs/PROOFS/Web-News-Reporting/REPORT.md
docs/PROOFS/Web-News-Reporting/evidence/2026-05-07/raw/focused_pytest_results.txt
docs/PROOFS/Web-News-Reporting/evidence/2026-05-07/raw/web_news_blocker_fix_probe.json
nova_backend/src/brain/search_synthesis.py
nova_backend/src/websocket/session_handler.py
nova_backend/tests/brain/test_search_synthesis.py
nova_backend/tests/websocket/test_session_handler_proof_blockers.py
```

### fix/ui-web-news-proof-followups

- latest: e5166ca4e19c / 2026-05-07
- merged into main: no
- unique commits: 1
- diff summary:  22 files changed, 318 insertions(+), 41 deletions(-)
- touches: runtime code, tests, proof/audit docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/fix/ui-web-news-proof-followups | head -50):

```text
e5166ca (origin/fix/ui-web-news-proof-followups, fix/ui-web-news-proof-followups) fix: close UI web news proof followups
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 22 files changed, 318 insertions(+), 41 deletions(-)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
docs/PROOFS/UI-Commands/BLOCKERS.md
docs/PROOFS/UI-Commands/FRICTION_LOG.md
docs/PROOFS/UI-Commands/REGRESSION_RECOMMENDATIONS.md
docs/PROOFS/UI-Commands/REPORT.md
docs/PROOFS/UI-Commands/VERIFICATION_MATRIX.md
docs/PROOFS/UI-Commands/evidence/2026-05-07/raw/browser_screenshot_followup_attempt.txt
docs/PROOFS/UI-Commands/evidence/2026-05-07/raw/followup_combined_pytest_results.txt
docs/PROOFS/UI-Commands/evidence/2026-05-07/raw/followup_pytest_results.txt
docs/PROOFS/UI-Commands/evidence/2026-05-07/raw/ui_followup_probe.json
docs/PROOFS/Web-News-Reporting/BLOCKERS.md
docs/PROOFS/Web-News-Reporting/FRICTION_LOG.md
docs/PROOFS/Web-News-Reporting/REGRESSION_RECOMMENDATIONS.md
docs/PROOFS/Web-News-Reporting/REPORT.md
docs/PROOFS/Web-News-Reporting/evidence/2026-05-07/raw/followup_combined_pytest_results.txt
docs/PROOFS/Web-News-Reporting/evidence/2026-05-07/raw/followup_pytest_results.txt
docs/PROOFS/Web-News-Reporting/evidence/2026-05-07/raw/story_tracker_temp_store_proof.json
nova_backend/src/executors/story_tracker_executor.py
nova_backend/src/utils/web_target_planner.py
nova_backend/src/websocket/session_handler.py
nova_backend/tests/executors/test_story_tracker_executor.py
nova_backend/tests/utils/test_web_target_planner.py
nova_backend/tests/websocket/test_session_handler_proof_blockers.py
```

### fix/web-news-weak-query-confidence-current-main

- latest: 447ec4143dad / 2026-05-11
- merged into main: no
- unique commits: 1
- diff summary:  1 file changed, 1 deletion(-)
- touches: runtime code
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/fix/web-news-weak-query-confidence-current-main | head -50):

```text
447ec41 (origin/fix/web-news-weak-query-confidence-current-main, fix/web-news-weak-query-confidence-current-main) fix: remove "nonexistent" from _QUERY_STOPWORDS in search_synthesis
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 1 file changed, 1 deletion(-)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
nova_backend/src/brain/search_synthesis.py
```

### proof/cap-16-certification-lock

- latest: 677f3cded53d / 2026-05-10
- merged into main: yes
- unique commits: 0
- diff summary: empty
- touches: other/docs
- classification: A. Already merged / safe delete
- action: delete after human approval
- reason: Tip is contained in origin/main; no unique commits remain.

- required log check (git log --oneline --decorate origin/main..origin/proof/cap-16-certification-lock | head -50):

```text
empty
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
empty
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
empty
```

### proof/dashboard-stale-degraded-rendering

- latest: b84ae9b2fd08 / 2026-05-07
- merged into main: no
- unique commits: 1
- diff summary:  26 files changed, 586 insertions(+), 70 deletions(-)
- touches: tests, generated runtime docs, governance/status docs, proof/audit docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/proof/dashboard-stale-degraded-rendering | head -50):

```text
b84ae9b (origin/proof/dashboard-stale-degraded-rendering, proof/dashboard-stale-degraded-rendering) test: prove dashboard stale degraded rendering
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 26 files changed, 586 insertions(+), 70 deletions(-)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
Nova-Frontend-Dashboard/dashboard-chat-news.js
Nova-Frontend-Dashboard/dashboard-surfaces.css
_MOCs/BY_TOPIC.md
_MOCs/BY_TYPE.md
_MOCs/HOME.md
_MOCs/RECENT.md
_MOCs/REPO_BY_FOLDER.md
docs/PROOFS/UI-Commands/BLOCKERS.md
docs/PROOFS/UI-Commands/FRICTION_LOG.md
docs/PROOFS/UI-Commands/MASTER_UI_VERIFICATION_MATRIX_2026-05-07.md
docs/PROOFS/UI-Commands/REGRESSION_RECOMMENDATIONS.md
docs/PROOFS/UI-Commands/REPORT.md
docs/PROOFS/UI-Commands/cases/DASHBOARD_STALE_DEGRADED_RENDERING_PROOF_2026-05-07.md
docs/PROOFS/UI-Commands/evidence/2026-05-07/raw/dashboard_stale_degraded_rendering_contract.json
docs/PROOFS/UI-Commands/evidence/2026-05-07/raw/dashboard_stale_degraded_rendering_pytest_results.txt
docs/PROOFS/Web-News-Reporting/BLOCKERS.md
docs/PROOFS/Web-News-Reporting/FRICTION_LOG.md
docs/PROOFS/Web-News-Reporting/PROOF_LIBRARY_INDEX.md
docs/PROOFS/Web-News-Reporting/REPORT.md
docs/current_runtime/CURRENT_RUNTIME_STATE.md
docs/current_runtime/RUNTIME_FINGERPRINT.md
docs/status/CURRENT_WORK_STATUS.md
docs/todo/ACTIVE_TODO.md
nova_backend/static/dashboard-chat-news.js
nova_backend/static/dashboard-surfaces.css
nova_backend/tests/phase45/test_dashboard_search_widget_followups.py
```

### proof/everyday-ux-live-workflow-baseline

- latest: a087d58d184b / 2026-05-10
- merged into main: no
- unique commits: 3
- diff summary:  1 file changed, 646 insertions(+)
- touches: proof/audit docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/proof/everyday-ux-live-workflow-baseline | head -50):

```text
a087d58 (origin/proof/everyday-ux-live-workflow-baseline, proof/everyday-ux-live-workflow-baseline) proof: add capability workflow test results to UX baseline evidence
751dbc0 docs: patch email fix recommendation in UX baseline evidence
f894fee proof: add everyday UX live workflow baseline evidence
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 1 file changed, 646 insertions(+)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
docs/PROOFS/Everyday-UX/LIVE_WORKFLOW_BASELINE_EVIDENCE_2026-05-10.md
```

### proof/stale-provider-credibility-fixtures

- latest: 5bf33463cfe3 / 2026-05-07
- merged into main: no
- unique commits: 1
- diff summary:  22 files changed, 791 insertions(+), 76 deletions(-)
- touches: runtime code, tests, generated runtime docs, governance/status docs, proof/audit docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/proof/stale-provider-credibility-fixtures | head -50):

```text
5bf3346 (origin/proof/stale-provider-credibility-fixtures, proof/stale-provider-credibility-fixtures) test: add stale provider credibility fixtures
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 22 files changed, 791 insertions(+), 76 deletions(-)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
_MOCs/BY_TOPIC.md
_MOCs/BY_TYPE.md
_MOCs/HOME.md
_MOCs/RECENT.md
_MOCs/REPO_BY_FOLDER.md
docs/PROOFS/Web-News-Reporting/BLOCKERS.md
docs/PROOFS/Web-News-Reporting/FRICTION_LOG.md
docs/PROOFS/Web-News-Reporting/PROOF_LIBRARY_INDEX.md
docs/PROOFS/Web-News-Reporting/REGRESSION_RECOMMENDATIONS.md
docs/PROOFS/Web-News-Reporting/REPORT.md
docs/PROOFS/Web-News-Reporting/cases/SOURCE_CREDIBILITY_MATRIX_PROOF_2026-05-07.md
docs/PROOFS/Web-News-Reporting/cases/STALE_CACHE_PROVIDER_FAILURE_PROOF_2026-05-07.md
docs/PROOFS/Web-News-Reporting/evidence/2026-05-07/raw/stale_provider_credibility_payload.json
docs/PROOFS/Web-News-Reporting/evidence/2026-05-07/raw/stale_provider_credibility_pytest_results.txt
docs/current_runtime/CURRENT_RUNTIME_STATE.md
docs/current_runtime/RUNTIME_FINGERPRINT.md
docs/status/CURRENT_WORK_STATUS.md
docs/todo/ACTIVE_TODO.md
nova_backend/src/brain/search_synthesis.py
nova_backend/src/executors/web_search_executor.py
nova_backend/tests/brain/test_search_synthesis.py
nova_backend/tests/executors/test_web_search_executor.py
```

### proof/ui-malformed-rapid-click-stress

- latest: df0fec389cb8 / 2026-05-07
- merged into main: no
- unique commits: 1
- diff summary:  21 files changed, 405 insertions(+), 55 deletions(-)
- touches: tests, generated runtime docs, governance/status docs, proof/audit docs
- classification: B. Superseded / stale
- action: do not merge; keep until human delete approval
- reason: Historical workstream branch with unique/parallel diff; current main has later continuity and proof status. Extract only after manual review if a specific note is still current.

- required log check (git log --oneline --decorate origin/main..origin/proof/ui-malformed-rapid-click-stress | head -50):

```text
df0fec3 (origin/proof/ui-malformed-rapid-click-stress, proof/ui-malformed-rapid-click-stress) test: add malformed widget and rapid click proof
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
 21 files changed, 405 insertions(+), 55 deletions(-)
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
Nova-Frontend-Dashboard/dashboard-chat-news.js
_MOCs/BY_TOPIC.md
_MOCs/BY_TYPE.md
_MOCs/HOME.md
_MOCs/RECENT.md
_MOCs/REPO_BY_FOLDER.md
docs/PROOFS/UI-Commands/BLOCKERS.md
docs/PROOFS/UI-Commands/FRICTION_LOG.md
docs/PROOFS/UI-Commands/MASTER_UI_VERIFICATION_MATRIX_2026-05-07.md
docs/PROOFS/UI-Commands/REGRESSION_RECOMMENDATIONS.md
docs/PROOFS/UI-Commands/REPORT.md
docs/PROOFS/UI-Commands/cases/MALFORMED_WIDGET_PAYLOAD_PROOF_2026-05-07.md
docs/PROOFS/UI-Commands/cases/RAPID_CLICK_DOUBLE_SUBMIT_PROOF_2026-05-07.md
docs/PROOFS/UI-Commands/evidence/2026-05-07/raw/ui_malformed_rapid_click_contract.json
docs/PROOFS/UI-Commands/evidence/2026-05-07/raw/ui_malformed_rapid_click_pytest_results.txt
docs/current_runtime/CURRENT_RUNTIME_STATE.md
docs/current_runtime/RUNTIME_FINGERPRINT.md
docs/status/CURRENT_WORK_STATUS.md
docs/todo/ACTIVE_TODO.md
nova_backend/static/dashboard-chat-news.js
nova_backend/tests/phase45/test_dashboard_auto_widget_dispatch.py
```

### test/dashboard-event-replay-harness

- latest: c3fe766e538e / 2026-05-09
- merged into main: yes
- unique commits: 0
- diff summary: empty
- touches: other/docs
- classification: A. Already merged / safe delete
- action: delete after human approval
- reason: Tip is contained in origin/main; no unique commits remain.

- required log check (git log --oneline --decorate origin/main..origin/test/dashboard-event-replay-harness | head -50):

```text
empty
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
empty
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
empty
```

### test/non-search-widget-fuzzing

- latest: 2543aff2dec3 / 2026-05-09
- merged into main: yes
- unique commits: 0
- diff summary: empty
- touches: other/docs
- classification: A. Already merged / safe delete
- action: delete after human approval
- reason: Tip is contained in origin/main; no unique commits remain.

- required log check (git log --oneline --decorate origin/main..origin/test/non-search-widget-fuzzing | head -50):

```text
empty
```

- required diff stat (git diff --stat origin/main...origin/<branch>):

```text
empty
```

- required diff names (git diff --name-only origin/main...origin/<branch>):

```text
empty
```


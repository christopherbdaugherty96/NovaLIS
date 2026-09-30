# Open Pull Request Disposition

Read-only classification from live GitHub on 2026-09-30. No pull request was closed, merged,
or edited.

| PR | Exact head | Disposition | Reason |
| --- | --- | --- | --- |
| #335 `feat: add Google Workspace connection foundation` | `befb69ef75881a9f418472549b64243219c138f9` | `CLOSE-CANDIDATE` / owner decision | Draft historical foundation; later Google work exists on current `main`. Preserve until its unique diff is explicitly reconciled. |
| #432 `Beta readiness: align user-facing capability truth` | `484b0f5ae2171e72ff30d9619ebc097116ad18d6` | `SUPERSEDED`, `CLOSE-CANDIDATE` | Its beta-readiness truth work was materially superseded by merged follow-up work. Do not merge this stale head. |
| #435 `docs: refine post-beta governed capability expansion strategy` | `f6ad489823b11f60fab26d14475ed8005f639959` | `DEFERRED` | Draft future strategy; non-authorizing and outside the current sanitation/beta blockers. |
| #443 `docs: present Nova workflow and maturity before proof history` | `cc307093d7dfc254a3a2e122e2cf483ef8edd009` | `REQUIRES-OWNER-DECISION` | Presentation-only README work. Re-review/rebase after sanitation because every historical head changes. |

The history rewrite candidate changes all four PR head identities and all GitHub pull refs.
GitHub Support cleanup and fresh PRs/rebases may be preferable to preserving the existing PR
objects after an approved rewrite.

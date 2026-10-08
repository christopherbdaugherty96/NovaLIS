# Main merge-identity and required-check controls — 2026-10-08

Status: Issue #457 repository-hygiene record. Not a new architecture lane and not runtime
authority. Prospective only: accepted history is not rewritten.

## Observed state (verified 2026-10-08 against main `210c00855bf18ed2896b9bca42c924d2ea3f5388`)

```text
ruleset "NovaLIS main public baseline" (id 24226099): active, no bypass actors
  deletion blocked; non-fast-forward blocked
  pull request required; review-thread resolution required; 0 required approvals
  allowed merge methods in ruleset: squash, merge, rebase
  required status checks: NONE
repository merge setting: squash only; auto-merge off; branch deletion on merge
hosted Actions: executing again; all seven jobs green on main 210c0085
identity on main, PRs #447 through #456 (8 squash commits):
  author:    NOT a GitHub noreply address (personal address restamped at squash merge)
  committer: GitHub noreply (web-flow)
identity on main through 34b8adc6 and earlier: author and committer noreply
```

The required-status-check gap was deliberate while hosted Actions were unreliable
(`PUBLIC_EXPOSURE_REMEDIATION_PLAN_2026-09-30.md`; Issue #354, now closed). That reason no longer
holds.

Root cause of the author restamping: a GitHub squash merge creates a new commit whose author is the
merging account, using that account's selected commit email. The pull-request commits themselves
were noreply; the merge step replaced the identity.

## Controls and where each one lives

### 1. Owner account actions (outside any PR)

```text
GitHub Settings > Emails > Keep my email addresses private: ON
GitHub Settings > Emails > Block command line pushes that expose my email: ON
```

With the first setting on, web-UI squash merges stamp the account's noreply address. This is the
preventive control for the merge-time commit; no repository workflow can see that commit before
it exists.

### 2. In Issue #457 (this PR)

- `.github/workflows/commit-identity.yml`, stable check name `commit-identity`:
  - on `pull_request`: checks only the commits the PR introduces (`base.sha..head.sha`);
  - on `push` to `main`: audits only the newly pushed range (`before..after`), which is where a
    restamped squash commit would appear;
  - author and committer must both be `*@users.noreply.github.com` or `noreply@github.com`;
  - violations name the commit and field, never the address; an unresolvable range fails closed.
- `scripts/check_commit_identity.py` and `nova_backend/tests/test_commit_identity.py`, including a
  personal-address commit that is rejected and historical commits that are not re-checked.
- This record and the post-merge ruleset target below.

No exact-head-review workflow is added. Exact-head review continues as the existing review process.

### 3. After #457 merges and every listed job is green on `main`

Update ruleset 24226099 to add required status checks. Do not add a required check before it
exists and passes on `main`. Target: `GITHUB_MAIN_RULESET_2026-10-08_REQUIRED_CHECKS.json`.

```text
required checks (GitHub Actions):
  lint-and-test (3.10)      CI
  test-windows (3.10)       CI
  governance                NovaLIS Governance Check
  runtime-docs              Runtime Docs
  check-invariants          Phase-3.5 Invariants
  verify-phase35            Phase-3.5 Verification
  fingerprint-clean         Fingerprint Clean (Main PR)
  commit-identity           Commit Identity
kept unchanged: PR required, review-thread resolution, deletion block, force-push block,
  no bypass actors
merge method: squash only (the ruleset list is narrowed to match the existing repository setting)
rebase merging: NOT enabled (it can rewrite committer identity and is not an identity workaround)
```

`strict_required_status_checks_policy` stays `false`: requiring the branch to be up to date would
push contributors toward "Update branch" merge commits, and exact-head review already pins the
reviewed head.

## Verification after the ruleset update

1. `gh api repos/christopherbdaugherty96/NovaLIS/rulesets/24226099` shows the eight required
   contexts and the unchanged PR, thread, deletion, and non-fast-forward rules.
2. The next PR shows all eight checks as required.
3. After that PR merges, the `commit-identity` push audit on `main` passes; if it fails, the
   merging account email setting is not in effect.

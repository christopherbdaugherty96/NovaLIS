# Release Integrity #409 — Active Contract and Evidence

Date: 2026-09-18
Baseline: `main@0a036eafd0022b3509bfff488d749d85735b590d`

## Scope

Issue #409 is a non-runtime release-control lane. It covers only:

1. hosted-CI execution truth;
2. the strongest practical `main` controls under the current GitHub plan;
3. one canonical release/version identity; and
4. Windows beta-support truth.

It does not authorize recovery, migration, backup, provider, capability,
Continuity, OpenClaw, model-routing, governed-harness, or other runtime work.

## Hosted CI truth

On the baseline commit, all six push-triggered hosted workflows concluded
`failure` before executing their configured steps. The CI run exposed two jobs,
both with empty `steps` arrays; another inspected workflow exposed no jobs. The
failed-job log endpoint had no retrievable log. This is hosted release-control
infrastructure evidence, not a Nova runtime regression or a behavioral test
result.

| Workflow | Run |
| --- | --- |
| Phase 3.5 invariants | `35302414592` |
| Governance check | `35302415430` |
| Fingerprint clean | `35302415275` |
| Runtime docs | `35302415361` |
| Phase-3.5 verification | `35302415276` |
| CI | `35302415384` |

The repository keeps the workflow definitions and now makes release-identity
validation part of its ordinary CI and local Windows verification path. Until
the external hosting/account condition changes, hosted workflow failure must be
reported as **not executed**, not as a behavioral pass or failure.

## Main control truth

The repository is private. GitHub returned HTTP 403 for both branch protection
and repository rulesets, stating that the feature requires GitHub Pro or a
public repository. This lane does not change repository visibility.

The controls available on the current plan are configured as follows:

```text
web commit signoff required: enabled
auto-merge: disabled
merge method: squash only
merged-branch deletion: enabled
```

These controls improve merge hygiene but do not enforce PR-only merging or
block direct pushes to `main`. That limitation remains explicit until an owner
chooses a plan or visibility change.

## Canonical release identity

`pyproject.toml` `[project].version` is the canonical release version.
`scripts/check_release_identity.py` validates the active projections in runtime
metadata, the Windows installer version and artifact name, the root README, and
the installer README. The check is part of CI and `scripts/verify_windows.ps1`.

This contract validates declaration consistency; it does not build, publish, or
certify an installer.

## Windows beta-support truth

Windows x64 is Nova's primary beta-support target. The installer path exists,
but clean-machine certification is not complete. macOS and Linux source paths
remain developer-only and unverified for beta support.

The later clean-Windows proof is the certification gate for an exact candidate;
this #409 contract does not claim that certification early.

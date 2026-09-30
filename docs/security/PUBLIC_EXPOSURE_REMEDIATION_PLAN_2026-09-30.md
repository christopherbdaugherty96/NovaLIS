# Public Exposure Remediation — Prepared Plan

Status: rewrite candidate prepared and verified; remote history replacement is **not
authorized and has not occurred**.

## Exact identity

- Original remote `main`: `4a48bfcee2d90c73d5e7b09704c479364e183440`
- Sanitized history-only `main` before the public-source hygiene commit:
  `2a8e82bcb75722eac107ad4a056f64e1bef0a65d`. The final prepared head is the hygiene commit
  immediately above it and is recorded in the owner-facing execution report.
- Original forensic mirror:
  `%USERPROFILE%\.codex\forensics\NovaLIS-public-exposure-20260930.git`
- Sanitized candidate mirror:
  `%USERPROFILE%\.codex\forensics\NovaLIS-sanitized-candidate-20260930.git`
- Original mirror inventory: 108 heads, 56 tags, 395 pull refs; 559 total refs;
  22,278 packed objects; 120.67 MiB.
- Private current-main migration archive:
  `%USERPROFILE%\.codex\forensics\NovaLIS-private-material-main-4a48bfcee2d9.zip`
- Migration archive SHA-256:
  `1377b4b6b03bb7963519a7a74c0900659ccce7e707ee60d67e1c40516c365888`

## Confirmed exposure

| Category | Evidence | Disposition in candidate |
| --- | --- | --- |
| Personal/account export | Historical `OLD_VISION.md.html` variants contained email, IP/location, account/workspace/device/session identifiers, and an expired OpenAI access token. | Export and companion asset paths removed from all rewritten refs. |
| Runtime user data | `nova_backend/src/data/ledger.jsonl` contained 979 runtime events; `nova_backend/memory/quick_corrections.jsonl` was also historically tracked. | Both paths removed from all rewritten refs. |
| Private business data | Auralis/Website LLC pricing, funnel, intake, operating, sales, website-service, and business-vault planning. | Exact private paths removed; public-safe source/design/tests retained. |
| Personal commit metadata | Personal email occurred in author/committer metadata. | Mapped to the repository owner's GitHub noreply address in the candidate. |
| Developer-local paths | Tracked source/docs named a specific Windows user profile. | Replaced with a neutral example in history; active source uses `Path.home()` in the hygiene branch. |

The detected OpenAI token was an RS256 token issued by `https://auth.openai.com`, scoped to
the OpenAI API, and expired on 2025-12-31. It is sensitive historical session material but is
not an active credential requiring rotation in September 2026. A second JWT-shaped match was
not decodable and is classified as a false positive. Token values are intentionally omitted.

## Rewrite mechanics

- Tool: `git-filter-repo` 2.47.0, installed in an isolated local virtual environment.
- Mode: sensitive-data removal across every locally mirrored ref, without pushing.
- Removed paths: `PUBLIC_HISTORY_REWRITE_PATHS_2026-09-30.txt`.
- Content transform: developer-local Windows paths replaced by neutral example paths.
- Metadata transform: personal author/committer email mapped to GitHub noreply.
- First changed commits and complete changed/ref maps are preserved under
  `docs/security/history-rewrite-2026-09-30/`.
- First changed original commits reported by `git-filter-repo`:
  `fe56ccfc63901536013dd76e49d71a325a193554`,
  `9e19f8166f664ff2918afc8919138cbca0557bb5`,
  `5db4a12b64cde3b91ae58833c8aa693e8c8b9cd6`, and
  `c9e1b141e4bb147563a1ebc5047012bf1e00a434`.

All 559 refs changed: 108 heads, 56 tags, and 395 pull-request refs. GitHub does not permit
ordinary client pushes to replace `refs/pull/*`; GitHub Support will be required after an
approved heads/tags replacement to purge affected pull-request references and cached views.

## Verification

### Original mirror

- Gitleaks 8.30.1: five findings across 2,202 commits and about 74.78 MB.
  - Three generic-key findings are intentionally non-working test values.
  - Two JWT findings are the same historical HTML export across two commits.
- TruffleHog 3.97.9 with verification disabled: zero findings.

### Sanitized candidate

- Gitleaks 8.30.1: three findings across 2,167 commits and about 70.28 MB; all three are
  intentional non-working test values.
- TruffleHog 3.97.9 with verification disabled: zero findings.
- Removed paths have no reachable rewritten history.
- Known personal email, IP, account, device, session-export, and developer-path markers have
  zero rewritten-history hits.
- Author/committer emails remaining are GitHub/Copilot/Anthropic noreply addresses only.

## Installer and release

The historical `NovaSetup-0.1.0.exe` matched SHA-256
`54502089ae24122bda006e1f27d24863f6641844bab51a7b437cbbfafe391579`, was unsigned, and
could not be unpacked by 7-Zip 26.03 or innoextract 1.9. Static inspection remains
`INCONCLUSIVE`. The GitHub prerelease and asset were deleted with owner authorization on
2026-09-30. The Git tag `v0.1.0-test` remains preserved.

## Repository controls

Enabled on GitHub:

- secret scanning;
- push protection;
- Dependabot vulnerability alerts;
- Dependabot security updates and automated security fixes.

Non-provider pattern scanning and validity checks remained unavailable/disabled after the API
request. The proposed post-rewrite `main` ruleset is
`GITHUB_MAIN_RULESET_PROPOSAL_2026-09-30.json`. It intentionally has no required hosted status
checks while Actions execution is unreliable. Applying it before the sanitation push would
block the required non-fast-forward replacement, so it remains unapplied.

## Owner decision required

No remote history has been rewritten. Before any force update, review the removal list,
metadata mapping, all changed refs, the 395 affected pull refs, and the preserved backup paths.
If approved, the execution plan must specify exact heads/tags push commands, temporary ruleset
state, collaborator/reclone instructions, GitHub Support cleanup, and post-push rescan.

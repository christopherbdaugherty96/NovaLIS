# Web / News / Reporting Proof Library Index - 2026-05-07

Status: active evidence library / review required

This index turns the raw WebSocket and regression evidence into reviewer-readable proof cases. It does not approve new authority, new capabilities, browser/computer-use expansion, external writes, autonomous workflows, or direct Cap 63 shortcut use.

## Evidence Roots

- Raw 2026-05-06 evidence: `docs/PROOFS/Web-News-Reporting/evidence/2026-05-06/raw/`
- Raw 2026-05-07 evidence: `docs/PROOFS/Web-News-Reporting/evidence/2026-05-07/raw/`
- UI command evidence: `docs/PROOFS/UI-Commands/evidence/2026-05-07/raw/`

## Case Library

| Proof Case | Status | Primary Evidence | Boundary Result | Remaining Gap |
| --- | --- | --- | --- | --- |
| Governed web search | pass | `cases/GOVERNED_WEB_SEARCH_PROOF_2026-05-07.md` | Governed search returns sources, evidence, confidence, and caveats without action leakage. | Add more provider-failure/stale-cache fixtures. |
| Open website / article behavior | pass / screenshot blocked | `cases/OPEN_WEBSITE_ARTICLE_BEHAVIOR_PROOF_2026-05-07.md` | Invalid URL fails before confirmation; valid website open remains confirmation-bound. | Visual screenshot proof blocked by Browser Use asset setup. |
| Headline summaries | pass | `cases/HEADLINE_SUMMARY_PROOF_2026-05-07.md` | Summaries bind to loaded headline state or truthfully report no context. | Add stale/duplicate/conflicting feed fixtures. |
| Multi-source reporting + intelligence brief | partial pass | `cases/MULTI_SOURCE_REPORTING_AND_BRIEF_PROOF_2026-05-07.md` | Existing evidence proves source labeling/caveats and intelligence brief rendering. | Needs direct contradiction/timeline-drift report fixtures. |
| Topic map + story tracking | pass / follow-up needed | `cases/TOPIC_MAP_STORY_TRACKER_PROOF_2026-05-07.md` | Topic map and story tracker have direct evidence; temp-store proof avoids workspace contamination. | Add duplicate/merged/split-topic fixtures. |
| Governance/adversarial/degraded behavior | pass / blocked screenshot | `cases/GOVERNANCE_ADVERSARIAL_DEGRADED_PROOF_2026-05-07.md` | Coercion refusals and quoted prompt-injection handling are bounded and explicit. | Add UI click-path coercion proof after browser capture works. |
| Deterministic stress fixtures | pass / fixture hardening ongoing | `cases/STRESS_FIXTURE_PROOF_2026-05-07.md` | Contradictory reporting, duplicate topic state, and split-topic comparison now have deterministic executor proof. | Stale-cache/provider-failure, credibility, malformed widget, and rapid-click proof still needed. |
| Stale cache / provider failure | pass / UI fixture follow-up needed | `cases/STALE_CACHE_PROVIDER_FAILURE_PROOF_2026-05-07.md` | Stale timestamps lower confidence; degraded/malformed provider output remains truthful. | Add dashboard/WebSocket rendering proof for stale/degraded states. |
| Source credibility matrix | pass / taxonomy hardening ongoing | `cases/SOURCE_CREDIBILITY_MATRIX_PROOF_2026-05-07.md` | Search evidence now emits conservative credibility rows and lowers confidence for weak/untrusted sources. | Add broader reviewed source taxonomy and UI rendering proof. |

## Regression Evidence

- `docs/PROOFS/UI-Commands/evidence/2026-05-07/raw/focused_pytest_results.txt`: `65 passed`
- `docs/PROOFS/UI-Commands/evidence/2026-05-07/raw/followup_pytest_results.txt`: `20 passed`
- `docs/PROOFS/UI-Commands/evidence/2026-05-07/raw/followup_combined_pytest_results.txt`: `75 passed`
- `docs/PROOFS/Web-News-Reporting/evidence/2026-05-07/raw/stress_fixture_pytest_results.txt`: `24 passed`
- `docs/PROOFS/Web-News-Reporting/evidence/2026-05-07/raw/stale_provider_credibility_pytest_results.txt`: `24 passed` search evidence/web search slice; `28 passed` adjacent news/story slice

## Current Verdict

The current Web/News/Reporting proof library now contains concrete raw evidence, case-level summaries, and regression references for the primary active-lock surfaces.

The lock is not fully closed yet because screenshot/click-path proof, dashboard-rendered stale/degraded state proof, malformed-widget proof, rapid-click/double-submit proof, and broader UI/button coverage still need more evidence.

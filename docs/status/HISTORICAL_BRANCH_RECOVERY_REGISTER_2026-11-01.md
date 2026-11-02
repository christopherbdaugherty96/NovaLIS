# Historical Branch Recovery Register — 2026-11-01

Status: maintained recovery evidence; not runtime truth, work authorization, or a replacement for
the owner operating sequence.

Baseline inspected: `main@9444a513f9b262a9cb904c744171ad883d7d8f82`.

## Purpose and authority boundary

This register preserves useful work from historical branches without treating branch divergence
as proof that implementation is missing. It distinguishes:

- **code recovery** — current functionality is demonstrably absent and may need a new,
  separately authorized implementation;
- **knowledge recovery** — requirements, acceptance criteria, tests, or procedures remain useful;
- **absorbed or superseded** — later work contains or replaces the historical result;
- **preserve only** — the material is useful provenance but its lane is paused or unauthorized.

This register authorizes no merge, cherry-pick, implementation, capability, provider, branch
deletion, or branch closure. Recovery work must start from current `main`, preserve current truth
and authority boundaries, and receive lane-specific owner authorization.

## Audit summary

The inspected repository had 111 non-`main` remote branches. Git ancestry against the baseline
classified 38 as fully contained and 73 as divergent. The prior PR-aware audit divided the 73
divergent branches into 55 merged-history/equivalence checks and 18 direct recovery reviews.
Squash merging can leave a source branch graph-divergent after its content reaches `main`, so the
55 merged-history branches are not 55 unfinished projects.

No branch is approved for deletion. Worktree attachment, automation references, protected-ref
state, provenance needs, and content disposition remain separate checks.

## Direct recovery register

| Source branch | Head inspected | Historical PR | Finding on baseline | Disposition | Authorization state |
| --- | --- | ---: | --- | --- | --- |
| `codex/consumer-north-star` | `8defd40aa3adc3501defbe1605be82549a5b52f8` | #459, open | The consumer acceptance contract is absent. It defines Today/Waiting/Done/Ask Nova, ten acceptance proofs, low-friction capture safeguards, and product measures. | **Knowledge recovery candidate:** reconcile still-valid acceptance requirements on a fresh documentation branch. Do not claim the target surfaces exist. | Separate documentation authorization required; Continuity runtime remains paused. |
| `codex/morning-4-checklist` | `b230ede22cf1e5f7b10081aaa9f5ff594d4028eb` | none | `docs/observation/MORNING_04_CHECKLIST.md` is absent. It contains pre-registered natural weather, calendar, news, follow-up, stop-recovery, latency, and falsification probes. | **Preserve for later:** reuse when Morning Brief/Topic Watch acceptance is authorized. | Morning work remains later in the operating sequence. |
| `codex/beta-readiness-truth-cleanup` | `fdc0273da5fba8ad4b3950e401ae508de6807fea` | #432, closed/unmerged | Six of seven historical truth themes are represented by the newer 22-test suite. The exact regression requiring policy actions to remain draft/manual is not present in that suite, while the production strings remain present. | **Targeted test candidate:** verify adjacent policy tests, then add only a modernized missing regression if still absent. Do not recover the old frontend patch. | Separate test-only authorization required. |
| `docs/front-door-alpha0-truth-sync` | `a4193d4a4c5cfd929400c12e4311518270ff599c` | #446, closed/unmerged | Most security/front-door claims were superseded by T1, SEQ2, and Data-Out. Its `.agent_context/handoffs/README.md` is absent and contains useful exact-SHA, worktree, ownership, evidence, and secret-handling rules. | **Knowledge recovery candidate:** modernize the protocol for the current owner/ChatGPT/Codex/reviewer workflow; do not restore the Claude-specific layout verbatim. | Separate documentation authorization required. |
| `feat/ux-solidity-pass` | `7025086651774bb77357fac27d6c9c6b1a42c5e9` | none | Three historical commits address duplicated onboarding, card overlines, button hierarchy, status noise, and desktop layout. All touched frontend files have evolved. | **Deferred UX evidence:** preserve desired outcomes as later visual acceptance criteria; do not cherry-pick historical code. | Broader UI work remains paused. |
| `codex/presentation-first-screen` | `2eac2d0c54e2458ecc6da277f7208cf4529369c6` | #443, closed/unmerged | The old README led with a supported governed email-draft workflow, explicit draft/send outcome truth, maturity limits, and Nova's role alongside stronger models. Current README prioritizes status and security limitations. | **Deferred presentation candidate:** reuse the structure with current truth, not the stale September sequence or claims. | Front-door rewrite requires separate authorization. |
| `docs/post-beta-governed-capability-expansion-20260921` | `3bd2fe19e43eed607a3c65a573b304cac89e64f2` | #435, closed/unmerged | Historical additions cover a generalized connection/credential/permission broker, Data-Out/Data-In governance, governed-run consolidation, an isolated governed browser, and a selection rule. The exact sections are absent from the current strategy file; portions may be superseded by later Data-Out work. | **Requirements comparison candidate:** retain only requirements not already satisfied or superseded by current Data-Out plans and later slice contracts. | No runtime or architecture authority granted. |
| `codex/runtime-proof-entrypoint` | `75b7276eb9725d9c38f10df6e3dd33fa033ee283` | none | The proof script exists in a newer form, and current proof/runtime documents replace most historical material. Root `RUN_NOVA.md` operator guidance is absent. | **Low-priority knowledge check:** recover only operator instructions that remain accurate and are not covered by current quick-start/proof documentation. | Separate documentation authorization required. |
| `codex/google-workspace-foundation-slice1-20260810` | `6765a16eff9c93d3aa1487c50556cc2a5cd3b007` | #335, closed/unmerged | Google connector files exist on `main`; several historical files/tests are byte-identical and others evolved through the merged foundation. The historical implementation path is superseded. | **Preserve only:** design/provenance reference; no reconstruction or merge. | Google/provider expansion remains paused. |
| `docs/nova-product-platform-direction-20260817` | `52b0d38e867091dba95b98202a79b93434b7330f` | none | The validation protocol is byte-identical on `main`; direction and status documents evolved through later strategy reconciliation. | **Absorbed/superseded:** retain provenance; no recovery PR presently justified. | No action authorized. |
| `codex/start-here-post-wave-c-truth-fix-20260825` | `059065a0a9495932addcfa26ba5f1c3230bd5539` | none | Historical `START_HERE` reconciliation was followed by later closeout and current-sequence updates. | **Absorbed/superseded:** equivalence/provenance only. | No action authorized. |
| `codex/readme-front-door-truth-20260825` | `e470ba85e9196f70c4283efdb5801796114a00f6` | #367, closed/unmerged | Forms the base of a stacked narration series. Later merged narration/front-door closeout and newer operational ordering replace its changing status surfaces. | **Absorbed/superseded:** grouped equivalence only. | No action authorized. |
| `codex/start-here-truth-20260825` | `f1169707650bd835051f390a3c289dffd6833282` | #369, closed/unmerged | Stacked successor to PR #367; its unique `START_HERE` intent was later reconciled. | **Absorbed/superseded:** grouped equivalence only. | No action authorized. |
| `codex/current-stage-reference-banner-20260825` | `dcef2602ff498761061e48459c651823f55a902c` | #372, closed/unmerged | Its terminal Current Stage guide is byte-identical to `main`. | **Content recovered:** retain branch only as provenance pending later cleanup review. | No action authorized. |
| `codex/operating-model-narration-sync-20260825` | `db14f37b396d75ef8ad6874a9bd54b31d5cb2c97` | #373, closed/unmerged | Its terminal operating-model and Current Stage files are byte-identical to `main`. | **Content recovered:** no recovery PR. | No action authorized. |
| `codex/brain-overview-narration-sync-20260825` | `2710dc5822868912217213784d6129313ce6cfde` | #375, closed/unmerged | Its terminal `docs/brain.md`, operating-model, Current Stage, and capability-inventory files are byte-identical to `main`. | **Content recovered:** no recovery PR. | No action authorized. |
| `codex/brain-index-narration-sync-20260825` | `faa05c55cadbe00dec46935e932f4d8bb78e884f` | #377, closed/unmerged | Its terminal `docs/brain.md`, `docs/brain/README.md`, operating-model, Current Stage, and capability-inventory files are byte-identical to `main`. | **Content recovered:** no recovery PR. | No action authorized. |
| `dependabot/pip/python-multipart-0.0.31` | `dcf6f5c48ca50bfc7df3cba1521cdc67856d27ca` | #445, open | Superseded by merged PR #486, which updated both canonical dependency surfaces to `0.0.32`. | **No recovery:** later close as superseded only through an explicit maintenance decision. | No close/delete action authorized here. |

## Merged-history/equivalence pool

The 55 branches previously classified as merged-PR divergence require grouped semantic
equivalence checks, not merge recovery. They primarily cover:

- July product-awareness, news, routing, local-chat, and UI stabilization;
- August Waves A1 through C, runtime truth, narration, memory governance, reproducibility,
  strategy reconciliation, and bounded capability fixes;
- September durability, recovery, beta truth, and acceptance foundations;
- October T1, SEQ2, and Data-Out work.

A branch in this pool can be dispositioned only after its merged PR, current implementation,
current tests, and any later superseding work are reconciled. Different commit hashes after a
squash merge are not evidence of missing functionality.

## Fully contained pool

The 38 fully contained branches have no commits ahead of the inspected baseline. That proves
their commits are reachable from `main`; it does not by itself authorize deleting their refs.
Before any cleanup decision, verify:

1. no attached or protected worktree still depends on the ref;
2. no automation, documentation, or release process names it;
3. provenance retention requirements are satisfied;
4. any open PR has a deliberate disposition;
5. the owner separately authorizes the cleanup.

## Recovery order

This register does not alter the active provider-neutral Data-Out priority. When separately
authorized, the recommended knowledge-recovery order is:

1. reconcile PR #459's consumer acceptance contract without activating Continuity;
2. verify and, if absent, restore PR #432's policy-draft/manual-only regression;
3. modernize the historical handoff protocol;
4. preserve the Morning checklist for its later authorized acceptance lane;
5. preserve UX and first-screen outcomes for later product work;
6. compare PR #435's durable requirements with current Data-Out contracts;
7. record equivalence evidence for the merged-history pool in bounded groups.

Slice 5A remains on HOLD pending real elevated and cross-user Windows proof. This register does
not count as that proof and does not authorize production integration.

## Required fields for future updates

Every later register entry or disposition should identify:

- source branch and exact inspected SHA;
- current `main` SHA used for comparison;
- historical PR or absence of one;
- files, requirements, tests, or behavior examined;
- evidence of absorption, supersession, or a remaining gap;
- whether recovery is documentation, test, runtime, or provenance-only;
- dependencies and explicit exclusions;
- owner authorization state;
- final PR/merge provenance if recovery is later completed.


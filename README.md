# NovaLIS

**Version 0.5 Alpha — Current State**

> **Nova is a local-first personal AI built to keep your context and your authority on your own
> machine.** Models can help Nova think; Nova is being built so that it alone decides what they
> see, what is allowed to happen, and what is recorded about what actually happened. Governed
> paths already work this way; closing the remaining gaps is the current Alpha 0 work.

Nova separates intelligence from authority. Reasoning can be broad; real execution stays
bounded, approved, inspectable, and recorded.

```text
Awareness -> Decision -> Authority -> Execution -> Outcome
```

Intelligence proposes. Nova governs. You decide.

## What Nova does today

Nova runs locally on Windows as a Python backend with a browser dashboard. It uses a local model
through Ollama by default and can consult an external reasoning provider (DeepSeek) when a provider
key is configured.

> **Data-out note:** the Settings switch for external reasoning currently governs only the
> explicit second-opinion capability. Other reasoning paths can still send prompts to the provider
> while that switch is off. Making every provider setting block every matching outbound path is
> an Alpha 0 item. Until it lands, leave `DEEPSEEK_API_KEY` unset if no prompt should leave your
> machine.

- **Daily awareness:** weather, news, local calendar (ICS), headline summaries, daily briefs, and
  story tracking, with grounded follow-up questions about what was loaded.
- **Research and reasoning:** governed web search, multi-source reports, analysis documents,
  "explain anything", and an optional second opinion from an external reasoning provider.
- **Governed memory:** explicit saves with provenance, confidence, conflict handling, editing,
  locking, and deletion. Ordinary chat does not silently become durable memory.
- **Bounded local actions:** volume, media, brightness, opening a website or an approved folder,
  explicit screen capture and analysis, and email drafts that open in your own mail client.
  Nova does not send email.
- **Read-only business data:** Shopify intelligence reports. No Shopify writes.
- **Approval for sensitive actions:** single-use approvals bound to the session, the capability,
  and the exact action. A replayed, expired, or changed action is refused. The yes/no reply
  handling that issues an approval is being hardened for Alpha 0; answer confirmation prompts
  with a plain `yes` or `no`.
- **Receipts and outcome truth:** attempted, completed, failed, degraded (receipt failed), and
  unknown (timed out) outcomes are kept distinct.

The generated [Current Runtime State](docs/current_runtime/CURRENT_RUNTIME_STATE.md) lists the 27
active capabilities and their authority classes. Active is not the same as certified,
configured, or authorized for a particular request.

## What Nova does not do

- No autonomous goal pursuit, background outreach, purchases, posting, or financial writes.
- No broad browser or computer control. OpenClaw integration exists as bounded, manual-first
  infrastructure; its presence does not imply broad autonomy.
- No Gmail, Google Tasks, or other Google domain data. The Google connection foundation is
  identity infrastructure only.
- No supported remote access. Nova is local-only; do not expose it to a network.
- No recovery or restore feature for end users yet. Snapshot machinery exists internally.

## Current Status

Version 0.5 Alpha is a technical-user / early-adopter state, not a finished mainstream release.

Windows is Nova's primary beta-support target. The Windows installer path exists, but
clean-machine certification is still a later acceptance gate. macOS and Linux may be
used for source-based development only; they are not certified or supported beta
platforms.

**Current milestone: Alpha 0**, a deliberately limited first build for one external technical
Windows tester. Alpha 0 work in progress:

1. Close the local-only boundary so only this machine can reach Nova's interfaces.
2. Disable the remote bridge in code for this release.
3. Harden approval handling and timeout/receipt records.
4. Make every provider setting block every matching outbound connection.
5. Build the installer only from a clean, exact source export, with an automatic content scan.
6. Produce one attributable Windows build and test it on a machine that is not the developer's.

No installer is currently published. The exact ordering and boundaries live in
[`.agent_context/current_priority.md`](.agent_context/current_priority.md); older ordering
records further down are historical where they conflict with it.

## Future Directions

This is direction, not a description of current behavior, and it authorizes no work by itself.

Nova is moving toward being a **personal custody and authority layer** between your life and
the AI models you use:

- **Custody:** Nova keeps the durable understanding of you locally: a timeline of your context
  with provenance and sensitivity on every entry.
- **Disclosure you can inspect:** every request to an outside model is a minimal context
  packet, and Nova records exactly what left your custody, why, to which provider, and under
  what approval.
- **Models as consultants:** Claude, GPT, or local models contribute analysis under Nova's
  persona; vendor-side memory stays off; statements about what was verified, approved, or done
  come only from Nova's own records.
- **Governed tool access:** a read-only MCP gateway first, so agents reach your data and tools
  only through Nova's approvals and receipts.

The work after Alpha 0 is ordered in `.agent_context/current_priority.md`.

## Quick start

Requirements: Windows 10/11, Python 3.10 to 3.12, and [Ollama](https://ollama.com) with a local
model (default `gemma4:e4b`).

```bash
git clone https://github.com/christopherbdaugherty96/NovaLIS.git
cd NovaLIS
pip install -e .
nova-start
```

Then open `http://127.0.0.1:8000`. Keep Nova bound to loopback; do not set `NOVA_HOST` to a
network address. See [Quickstart](QUICKSTART.md) for details.

## How Nova is built

Every governed action takes the same path:

```text
User -> GovernorMediator -> Governor -> CapabilityRegistry -> SingleActionQueue
     -> LedgerWriter -> ExecuteBoundary -> Executor -> receipt and outcome
```

- **Governor** owns approval grants, dispatch, timeouts, and outcome records.
- **CapabilityRegistry** declares each capability, its authority class, and whether it needs
  confirmation.
- **NetworkMediator** carries governed outbound requests, with rate and budget limits.
- **Ledger** is an append-only record of attempts, completions, and degraded outcomes.
- **Runtime truth generator** writes the documents in `docs/current_runtime/` from the code.

Repository truth rules: code is authoritative for behavior; tests are evidence only for the
revision they ran on; generated runtime documents are authoritative only for what their
generators measure. See [Repo Map](REPO_MAP.md) and the
[Canonical Truth Index](docs/CANONICAL/00_INDEX.md).

## Core Principles

**Intelligence is not authority.**

**Visibility is not authority.**

**Capability is not permission.**

**Outcome learning may improve recommendations, never authority.**

Memory, conversation context, recommendations, model confidence, connection state, and past
approvals never authorize an action by themselves.

## Documentation

- [Start Here](START_HERE.md): shortest human path
- [Quickstart](QUICKSTART.md): install and first run
- [Current priority](.agent_context/current_priority.md): what is being worked on now
- [Current Runtime State](docs/current_runtime/CURRENT_RUNTIME_STATE.md): generated runtime truth
- [Capability Inventory](docs/capability_verification/CAPABILITY_INVENTORY.md): verification status
- [Product Definition](docs/product/PRODUCT_DEFINITION.md): identity and architecture
- [Known Limitations](docs/product/KNOWN_LIMITATIONS.md)
- [Daily Command Center](docs/status/DAILY_COMMAND_CENTER.md): detailed work chronology
- [Proof evidence index](docs/capability_verification/PROOF_EVIDENCE_INDEX_2026-09-28.md):
  what earlier proof packages do and do not cover
- [Security policy](SECURITY.md)

Screenshots and proof packages under `docs/demo_proof/` are dated historical captures. They do
not identify the current source revision and are not proof of the current build.

## AI Workflow Note

Nova is built with AI coding agents (currently Codex as implementer and Claude as independent
reviewer), coordinated through owner decisions and written handoffs. AI-generated work is
reviewed before it is treated as final, and GitHub remains the durable source of truth.

See [AI Tooling Workflow](docs/WORKFLOW_AI_TOOLING.md) and
[AI Tooling Boundaries](docs/AI_TOOLING_BOUNDARIES.md).

## License

See [LICENSE](LICENSE).

## Operational truth record (machine-checked)

The blocks below are kept verbatim because `scripts/check_operational_truth_consistency.py`
validates them. They record the beta-readiness ledger that preceded the Alpha 0 decision. For
current ordering, use `.agent_context/current_priority.md`.

<details>
<summary>Beta-readiness ledger and stabilization record</summary>

### Beta-readiness ledger (post-#405, 2026-09-20)

```text
BETA_READINESS_SEQUENCE_V1: ACTIVE
verified main after Lane 5A rollback/restore proof: 868de9d92c701834f1c4fba422ab9c47a01ea33f
#397 through #405: COMPLETE / MERGED
COMPLETE: #406 governed-memory ID collision correctness (PR #411; main `ca66a06d`)
COMPLETE: #408 durability/state-ownership decision (PR #412; main `2592ad91`)
COMPLETE: durability implementation lane 1 - canonical state registry/migration detection (PR #413; main `e74fdca0`)
COMPLETE: durability implementation lane 2 - corruption-safe readers (PR #416; main `80e1c86f`)
COMPLETE: durability implementation lane 3 - maintenance locking + mutation quiescence (PR #419; main `2bfe202e`)
COMPLETE: durability implementation lane 4 - versioned snapshot + manifest (PR #421; main `4e32b501`)
FRESH-MAIN CLOSEOUT: PASS (314 focused durability/operational-truth tests passed; 1 expected Windows POSIX-FIFO skip; runtime structural smoke PASS)
COMPLETE: #409 release integrity / repository control (PR #423; main `aa39515f`)
COMPLETE: #410 private-beta freeze criteria (PR #410; main `3ad3f544`)
AUTHORIZED / ACTIVE: Lane 5A recovery construction (owner authorization; base main `3ad3f544`)
COMPLETE: Lane 5A step 1 - inactive recovery candidate migration (PR #424; main `298b7731`)
MIGRATION PROOF: PASS (173 durability tests passed; 1 expected Windows POSIX-FIFO skip)
COMPLETE: Lane 5A step 2 - recovery candidate validation (PR #426; main `9de640cd`)
VALIDATION PROOF: PASS (184 durability tests passed; 1 expected Windows POSIX-FIFO skip)
COMPLETE: Lane 5A step 3 - controlled recovery activation (PR #427; main `678dda6c`)
ACTIVATION PROOF: PASS (192 durability tests passed; 1 expected Windows POSIX-FIFO skip)
COMPLETE: Lane 5A authority-foundation correction (PR #428; main `3a3e9d33`)
AUTHORITY FOUNDATION PROOF: PASS (201 durability tests passed; 1 expected Windows POSIX-FIFO skip)
RECOVERY AUTHORITY MODEL: dual-slot highest-valid-generation selection
COMPLETE: Lane 5A step 4 - rollback/restore proof (PR #430; main `868de9d9`)
ROLLBACK/RESTORE PROOF: PASS (208 durability tests passed; 1 expected Windows POSIX-FIFO skip; runtime structural smoke PASS)
COMPLETE: beta user-facing truth pass (PR #433; main `ad64048e`)
COMPLETE: rollback/restore operational-truth checker contract (PR #436; main `0003a2e`)
FRESH-MAIN PROOF: PASS (39 focused checker-contract tests; Ruff; operational-truth consistency; runtime structural smoke)
COMPLETE: first Synthetic Beta Cohort v1 (PR #438; test-only evidence, not product acceptance)
COMPLETE: connected-user cohort test-spec correction (PR #439; main `486ad3dddc3f75412085b968c28561ab57e25686`)
CONFIRMED P1 BEFORE BETA ACCEPTANCE: the local-only boundary is unsafe if `NOVA_HOST` accepts a non-loopback bind; repair and fresh proof are required before any Windows acceptance run.
NEXT REQUIRED ENGINEERING: bounded local-boundary P1 repair (no remote mode or authority expansion)
THEN: fresh-main security and truth proof
THEN: installer supply-chain and privacy/Data-Out/secrets audit
THEN: build a new exact Windows candidate artifact; the prior artifact is historical only
THEN: clean Windows operator proof against that exact artifact
THEN: freeze exact candidate identity
THEN: rerun #434 and remaining acceptance checks against that frozen candidate
THEN: owner acceptance/distribution decision
THEN: 3 real non-developer users
```

Google/provider expansion remains paused. Operational Continuity implementation remains paused.
New capabilities remain paused. Voice expansion remains paused. Broader UI work remains paused.
Other feature expansion remains paused. This current order supersedes older ordering language below and
grants no new capability or authority.

Current grounded status:

```text
- local-first governed awareness and decision-support system
- bounded execution infrastructure exists
- generated runtime state reports 27 active capability surfaces
- active != certified != locked != configured != authorized
- Cap 16 web search is P1-P5 certification-locked
- Cap 22 file-folder access is P1-P5 certification-locked
- Cap 64 email draft is P1-P5 certification-locked and remains local mailto draft only
- Cap 65 Shopify intelligence is P1-P5 certification-locked, read-only, not Shopify writes
- OpenClaw exists as bounded/manual-first runtime infrastructure; presence does not imply broad autonomy
- Wave A1, A2, B1, B2, B3, B4, and Wave C stabilization are complete and merged
- immutable Wave C validated_baseline_sha:
  ec20a7146f7d6d55b8983cb7d6d3918d5fad9915
- GitHub-hosted Wave C jobs remained NOT EXECUTED because of the external account/billing
  restriction tracked in Issue #354; the owner waived that source as mandatory exit evidence
  without classifying it as PASS
- POST-WAVE-C DOCUMENTATION CLOSEOUT: COMPLETE; truth/checker hardening is merged through PR #385
- PR #366 truth-hygiene provenance: MERGED
- PR #378 narration/front-door package: MERGED / VERIFIED
- #388: COMPLETE / TRUTH-CHECKER PREREQUISITE SATISFIED
- #368: COMPLETE
- #387: COMPLETE / DOCS-ONLY
- #394: GOOGLE WORKSPACE FOUNDATION COMPLETE / MERGED
- historical PR #335 implementation path: SUPERSEDED BY MERGED PR #394;
  retain it as historical reference only, not a reconstruction or merge lane
- the Foundation is identity/auth infrastructure, not permission for Google domain-data access
- Google Tasks and Gmail are not built as current Nova capabilities
- Operational Continuity is strategically accepted but implementation-inactive and non-authorizing
- no broad browser/computer-use, financial-write, autonomous outreach, contracting,
  autonomous-business, broad provider-routing, or expanded OpenClaw authority lane is active
```

</details>

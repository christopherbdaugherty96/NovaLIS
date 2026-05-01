# Nova Current Work Status

Last reviewed: 2026-05-01

This is a human-maintained continuity note for the current development slice.

It is not generated runtime truth. For exact runtime fingerprint, capability count, active capabilities, and generated invariants, use [`../current_runtime/CURRENT_RUNTIME_STATE.md`](../current_runtime/CURRENT_RUNTIME_STATE.md).

Generated runtime docs and actual code win if they conflict with this note.

---

## Current Truth

At this review baseline, the alignment branch includes:

- PR #64 Brain Planning Preview scaffold, merged earlier.
- PR #66 Search Evidence Synthesis, merged in this alignment pass.
- Free-first cost governance design docs, merged in this alignment pass.
- Auralis and YouTubeLIS planning docs already present on `main`.

Generated runtime truth still reports the authoritative capability inventory and governance invariants. This note should not be used as a replacement for generated runtime docs.

---

## Implemented Runtime / Code Truth

- Governance spine remains the strongest runtime truth: GovernorMediator, CapabilityRegistry, ExecuteBoundary, NetworkMediator, and ledger discipline are still the authority path.
- Cap 16 governed web search remains the active current-information lane.
- Search Evidence Synthesis is now implemented as a deterministic evidence-structuring module for Cap 16 search output.
- Search Evidence Synthesis does not add a new capability, does not authorize action, does not bypass NetworkMediator, and does not route through Governor as an authority path.
- Cap 64 remains confirmation-bound local `mailto:` draft only. It does not use Gmail API, SMTP, inbox access, or autonomous send.
- Cap 65 remains read-only Shopify intelligence. No Shopify writes are implemented.

---

## Merged Scaffold / Planning State

- Task Understanding, Task Envelope, and Simple Task Mode exist as planning-only Brain scaffolds.
- Conversation fallback can attach a planning-only Task Understanding preview for task-like requests.
- RunManager exists as an in-memory planning-only scaffold.
- Conversation fallback can create a session-local planning Run Preview.
- These Brain layers do not execute, authorize, call OpenClaw, add capabilities, or bypass Governor.

---

## Planning-Only / Future Direction

- Google connector work is future read/context connector planning. There is no Google OAuth, Gmail, Calendar, Drive, or Google account runtime connector unless generated runtime truth later proves it.
- Free-first cost governance is now a design policy and implementation plan. Runtime enforcement does not exist until registry metadata, generator output, tests, and UI/proof paths exist.
- Auralis Website Coworker is a future business workflow / production discipline layer. It is not an autonomous website builder and has no publish, deploy, domain, DNS, or client-send authority.
- YouTubeLIS is a planning-only tool folder. It has no upload, publish, account automation, or YouTube Studio control.
- OpenClaw remains governed/constrained and is not broad autonomy. Future expansion must require Run/Task Envelope/Governor/receipts.

---

## Active P1

Cap 16 current-information reliability and evidence quality remains the active P1.

Immediate continuation order:

1. Validate Search Evidence Synthesis after merge.
2. Re-run and record the conversation + search proof path.
3. Continue doc/status cleanup as needed.
4. Plan cost posture metadata as the next design-to-runtime step, without hard blocking first.
5. Plan Google read-only connector foundations only after cost posture and connector governance are clear.

Do not start new write/action capabilities from this status pass.

---

## Do Not Overstate

Do not claim these are finished unless verified against code/runtime truth:

- Full Task Environment Router.
- Governor-driven live contract lookup.
- Dry Run / Plan Preview API.
- Brain Trace UI.
- Google OAuth/Gmail/Calendar runtime connectors.
- Gmail send/write authority.
- Shopify write authority.
- Broad autonomous execution.
- OpenClaw Run-based execution.
- Free-first runtime enforcement.
- One-click consumer installer.

---

## Branch / Workstream Map

For the branch and workstream alignment snapshot from this pass, see [`REPO_BRANCH_AND_WORKSTREAM_STATUS_2026-05-01.md`](REPO_BRANCH_AND_WORKSTREAM_STATUS_2026-05-01.md).

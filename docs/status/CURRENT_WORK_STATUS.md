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
- PR #68 Daily Brief MVP, merged 2026-05-01.
- Free-first cost governance design docs, merged in this alignment pass.
- Auralis and YouTubeLIS planning docs already present on `main`.
- OpenClaw robust hardening audit added as a future implementation recommendation, not runtime truth.
- Governed Workflow Workspace Architecture added as a product/architecture planning note for everyday
  workflows, independent automation, and business-owner use cases.

Generated runtime truth still reports the authoritative capability inventory and governance invariants. This note should not be used as a replacement for generated runtime docs.

---

## Implemented Runtime / Code Truth

- Governance spine remains the strongest runtime truth: GovernorMediator, CapabilityRegistry, ExecuteBoundary, NetworkMediator, and ledger discipline are still the authority path.
- Cap 16 governed web search remains the active current-information lane.
- Search Evidence Synthesis is now implemented as a deterministic evidence-structuring module for Cap 16
  search output. It does not add a new capability, does not authorize action, and does not bypass
  NetworkMediator.
- Daily Brief MVP is implemented as a deterministic, on-demand session brief (PR #68). It synthesizes
  session state, memory, receipts, weather (live via WeatherService), calendar (local ICS via
  CalendarSkill), and email placeholder into 11 sections. Non-authorizing frozen dataclass;
  `execution_performed=False` and `authorization_granted=False` are enforced by `__post_init__`.
  No new capability, no LLM calls, no Governor path.
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
- The OpenClaw robust hardening audit recommends mandatory EnvelopeFactory issuance, disabling or preview-gating freeform goal execution, replacing action auto-allow, centralizing execution guards, adding boundary detection, and adding run/step receipts before any browser/computer-use expansion.
- Governed Workflow Workspace is product planning for everyday workflows, independent automation, and business-owner workflows. It does not mean workflow templates, object models, onboarding wizard, or complete personal SaaS behavior are implemented.

---

## Active P1

Cap 16 current-information reliability and evidence quality remains the active P1.

Immediate continuation order:

1. Re-run and record the conversation + search proof path with Search Evidence Synthesis active.
2. Memory loop and conversation continuity — session continuity state fields: `current_topic`,
   `session_goal`, `mode`, `last_decision`, `open_loops`, `recent_recommendations`.
3. Continue doc/status cleanup as needed.
4. Plan cost posture metadata as the next design-to-runtime step, without hard blocking first.
5. Plan Google read-only connector foundations only after cost posture and connector governance are clear.
6. Keep OpenClaw expansion frozen until envelope issuance, approval, execution-guard, and receipt gaps
   are closed.
7. Use the governed workflow workspace plan to guide product shell, object model, workflow template,
   and onboarding work after proof paths are stable.

Do not start new write/action capabilities from this status pass.

---

## Governed Workflow Workspace Direction

Canonical product planning note: [`../product/GOVERNED_WORKFLOW_WORKSPACE_ARCHITECTURE.md`](../product/GOVERNED_WORKFLOW_WORKSPACE_ARCHITECTURE.md).

The broadened product direction is:

```text
A governed AI workspace for everyday workflows and independent automation.
```

This includes everyday personal workflows, household/life admin workflows, creator workflows, independent contractor workflows, small business workflows, research and learning workflows, content/media workflows, local-first assistant workflows, and approved automation routines.

Independent business owners remain a major use case, but not the only use case.

---

## OpenClaw Hardening Priority

Canonical audit note: [`../future/OPENCLAW_ROBUST_HARDENING_AUDIT_2026-05-01.md`](../future/OPENCLAW_ROBUST_HARDENING_AUDIT_2026-05-01.md).

Current recommended order:

1. Make EnvelopeFactory mandatory for all OpenClaw runs.
2. Disable or strictly envelope-gate freeform goal execution.
3. Replace `/api/openclaw/approve-action` auto-allow with allow / pause / block decisions.
4. Add centralized OpenClaw execution guard for tool, network, file, action, and budget checks.
5. Add browser/computer-use boundary detection before any browser expansion.
6. Add run, step, boundary, failure, cancel, completion, and cleanup receipts.
7. Add visible active-run approval UI.
8. Only then implement a read-only isolated-browser slice.

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
- OpenClaw mandatory EnvelopeFactory enforcement.
- OpenClaw real human approval gate.
- OpenClaw browser/computer-use readiness.
- Governed workflow workspace runtime shell.
- Workflow object model.
- Workflow template system.
- First-run workspace onboarding wizard.
- Free-first runtime enforcement.
- One-click consumer installer.

---

## Branch / Workstream Map

For the branch and workstream alignment snapshot from this pass, see [`REPO_BRANCH_AND_WORKSTREAM_STATUS_2026-05-01.md`](REPO_BRANCH_AND_WORKSTREAM_STATUS_2026-05-01.md).

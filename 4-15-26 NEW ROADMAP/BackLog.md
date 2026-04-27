# BackLog.md

This file tracks follow-up work that is real, but not allowed to distract from the active close-out path in `Now.md`.

## HARD PAUSE — Auralis / Website Merger Work

Status: paused by owner direction on 2026-04-27.

The Auralis Digital / website / NovaLIS merger and commercial-integration planning work is now intentionally paused.

Do not delete the existing Auralis planning docs. They remain useful future references, but they must not drive the active Nova execution path right now.

Paused scope includes:

```text
Auralis/Nova merger planning
Auralis website-service expansion inside the NovaLIS repo
Nova Lead Console commercial planning
client-funnel/pricing/package expansion
website-to-Nova integration planning
Auralis as a near-term Nova commercial surface
```

Allowed while paused:

```text
preserve existing docs
reference them only when explicitly asked
avoid deleting or rewriting them
```

Blocked while paused:

```text
adding more Auralis merger docs
expanding Auralis pricing/funnel/client docs inside NovaLIS
shifting Claude/Codex work toward website merger strategy
letting Auralis work displace Cap 64, trust/action-history, OpenClaw governance, or runtime stabilization
```

Current active focus returns to NovaLIS runtime stabilization:

```text
Cap 64 P5 live signoff and lock
Windows installer/bootstrap validation
trust/action-history dashboard proof
OpenClawMediator / Business Follow-Up Brief proof after trust path is stable
```

## HARD PAUSE — Shopify / Cap 65 P5 Live Work

Status: paused by owner direction on 2026-04-27.

Cap 65 `shopify_intelligence_report` remains implemented and verified through P4, but P5 live Shopify signoff is intentionally paused for now.

Do not delete the Cap 65 implementation, tests, checklist, or blocker documentation. Preserve all completed evidence.

Current preserved truth:

```text
Cap 65 P1 unit: PASS
Cap 65 P2 routing: PASS
Cap 65 P3 integration: PASS
Cap 65 P4 API: PASS
Cap 65 P5 live: BLOCKED/PAUSED — requires Shopify credentials and owner unpause
Cap 65 P6 lock: NOT APPLIED
```

Paused scope includes:

```text
Shopify live P5 signoff
Shopify credential setup work
Shopify dev-store setup work
Cap 65 P6 lock
future Shopify write/operator planning
Shopify commercial expansion
```

Allowed while paused:

```text
preserve existing Cap 65 code/tests/docs
reference Cap 65 status only when explicitly asked
keep read-only safety conclusions documented
leave blocker status intact
```

Blocked while paused:

```text
running live Shopify P5 tests
requesting/adding Shopify credentials
locking Cap 65
expanding Shopify capability scope
adding Shopify write/mutation capabilities
letting Shopify work displace Cap 64, trust/action-history, installer validation, or OpenClaw governance work
```

Unpause condition:

```text
Owner explicitly unpauses Shopify/Cap 65 and provides or prepares Shopify dev-store credentials.
```

Until unpaused, the active NovaLIS path is:

```text
Cap 64 P5 live signoff and lock
Windows installer/bootstrap validation
trust/action-history dashboard proof
OpenClawMediator / Business Follow-Up Brief proof after trust path is stable
```

## Conversation Coherence Layer

Context: Nova already has a real conversation module with deterministic routing, `ConversationDecision`, response style routing, normalization, follow-up handling, and tests. The next coherence improvement should be incremental and test-backed, not a broad rewrite.

Reference: `docs/future/NOVA_CONVERSATION_COHERENCE_LAYER_PLAN.md`.

### Current Truth To Preserve

- Existing conversation surfaces include `conversation_router.py`, `conversation_decision.py`, `response_style_router.py`, `response_formatter.py`, `session_router.py`, `general_chat_runtime.py`, `websocket/session_handler.py`, and `skills/general_chat.py`.
- Existing tests cover conversation router, response style router, formatter, session router, and general chat runtime.
- Coherence work must not widen GovernorMediator, ExecuteBoundary, NetworkMediator, OpenClaw, Google connector, ElevenLabs, Auralis, or Shopify authority.
- This is a usability/context improvement, not an execution-authority project.

### Recommended Future Build Order

- [ ] Add tests for status/next-step/paused-work/memory-vs-doc/capability-signoff question types.
- [ ] Add a small task-state source for active, paused, blocked, and future-only work.
- [ ] Add runtime-truth labels such as `CURRENT_RUNTIME_TRUTH`, `PLANNED`, `PAUSED`, `BLOCKED`, and `DEFERRED`.
- [ ] Add coherence classification metadata without exploding or rewriting `ConversationMode`.
- [ ] Add response templates for project status, Claude/Codex direction, paused work, capability signoff, explanation, and governed action summaries.
- [ ] Wire the layer only into general-chat/project-status paths first.
- [ ] Add regression tests proving paused Auralis and paused Shopify are respected.

### Guardrail

Do not start this before Cap 64 P5 live signoff unless explicitly instructed. When started, do not replace the conversation router wholesale. Preserve existing behavior and add narrow, tested improvements.

## Governed Learning

Context: Nova should learn user corrections, preferences, recurring command meanings, and project context in a visible and reviewable way. Learning should improve conversation coherence, not action authority.

Reference: `docs/future/NOVA_GOVERNED_LEARNING_PLAN.md`.

### Current Truth To Preserve

- Governed learning is a future direction, not current runtime truth.
- Learning may shape wording, context selection, intent classification, and answer structure.
- Learning must not change action approval, capability signoff, capability locks, GovernorMediator, ExecuteBoundary, NetworkMediator, OpenClaw authority, or connector authority.
- All conversation/coherence learning should have `authority_effect = none`.

### Recommended Future Build Order

- [ ] Add learnable item categories: `USER_STYLE_PREFERENCE`, `PROJECT_GLOSSARY`, `COMMAND_MEANING`, `ACTIVE_TASK_STATE`, `PAUSED_SCOPE`, `CORRECTION`, `REJECTED_BEHAVIOR`, `ACCEPTED_RESPONSE_PATTERN`, `CAPABILITY_STATUS_HINT`, and `CONTEXT_DISAMBIGUATION_RULE`.
- [ ] Add learning states: `PROPOSED`, `USER_CONFIRMED`, `ACTIVE`, `SUPERSEDED`, `EXPIRED`, and `REJECTED`.
- [ ] Add visible review/delete/supersede behavior for learned items.
- [ ] Add tests for “save to memory” vs “add to docs”, “do not call Nova Jarvis”, “second pass means review for gaps”, and “forget that rule”.
- [ ] Add negative tests proving learning cannot mark capabilities passed, change locks, issue OpenClaw envelopes, call connectors, or change approval policy.

### Guardrail

Do not implement hidden self-training, background memory creation, or silent policy changes. Nova should learn how to understand the user better, not how to bypass the user.

## Background Reasoning, Not Background Automation

Context: Nova should eventually support background reasoning/processing while continuing to block background automation. This supports usefulness without giving Nova hidden external-world authority.

Reference: `docs/future/NOVA_BACKGROUND_REASONING_NOT_AUTOMATION_PLAN.md`.

### Current Truth To Preserve

- Background reasoning is a future direction, not current runtime truth.
- Nova may think, summarize, draft, analyze, and propose in the background.
- Nova must not send, post, delete, submit, book, purchase, modify accounts/files/customer records, or execute OpenClaw tasks in the background.
- Local-first means local control/trust anchor by default; it does not mean local-only forever.
- Cloud reasoning may expand intelligence, but it must not expand authority.

### Recommended Future Build Order

- [ ] Define explicit background reasoning job types such as `ANALYSIS_ONLY`, `SUMMARY_ONLY`, `DRAFT_ONLY`, `RECOMMENDATION_ONLY`, `STATUS_REVIEW`, `LOG_REVIEW`, `DOC_REVIEW`, `REPO_REVIEW`, `FOLLOWUP_SUGGESTION`, and `PROPOSED_ACTION_PREP`.
- [ ] Define provider lanes: `LOCAL_ONLY`, `LOCAL_FIRST_CLOUD_FALLBACK`, `CLOUD_ALLOWED`, and `CLOUD_REQUIRED_BY_USER`.
- [ ] Add visible status for reasoning jobs: provider/lane, data included, allowed outputs, blocked outputs, cancel/stop path.
- [ ] Add receipts and non-action statements proving nothing was sent, posted, changed, deleted, booked, purchased, or executed.
- [ ] First proof should be `Background Project Status Review`: read-only/local-simple, produces a status card, changes nothing.

### Guardrail

Do not implement broad background reasoning before Cap 64 P5/signoff or trust/action-history review surfaces unless explicitly reprioritized. Background reasoning may prepare drafts and proposed actions; it must not perform background automation.

## Trust Receipt Backend Hardening

Context: the minimum viable trust receipt backend/API was added, but a fresh review identified hardening work that should be tracked before treating the receipt system as durable. These are not known regressions; they are reliability, test, and defense-in-depth improvements.

### Highest Priority

- [x] Harden `receipt_store.py` for fresh-install and corrupted-ledger cases. *(done 2026-04-26, commit 83c7474)*
  - Missing ledger → `[]`; empty ledger → `[]`; malformed/non-dict JSON lines skipped; outer `try/except Exception` prevents propagation.

- [x] Add targeted unit tests for `receipt_store.py`. *(done 2026-04-26, commit 83c7474)*
  - 18 tests in `nova_backend/tests/trust/test_receipt_store.py` covering all scenarios.

### Medium Priority

- [x] Add prerequisite checks to `scripts/verify_windows.ps1`. *(done 2026-04-26, commit b1434e2)*
  - Python ≥ 3.10 check, project-root check, pytest importable check, Python/pip/pytest version printout.

- [x] Add a short `ci.yml` comment explaining why the Windows job runs specific suites rather than the full test suite. *(done 2026-04-26, commit b1434e2)*
  - Comment added above `test-windows:` job.

- [x] Add troubleshooting sections to the Cap 64 and Cap 65 live checklists. *(done 2026-04-26, commit b1434e2)*
  - Cap 64: mail client setup, `@` encoding, blank body, Trust page not built, confirmation gate, certify errors.
  - Cap 65: domain format, token scopes, NetworkMediator refusal, GraphQL/empty data, Test 3 restart, period defaults.
  - Cap 65 live P5 is now paused and must not be resumed without explicit owner unpause.

### Lower Priority / Design Follow-Up

- [x] Add router-level loopback dependency to the Trust Receipt API as defense-in-depth. *(done 2026-04-26, commit 83c7474)*
  - `APIRouter(dependencies=[Depends(require_local_http_request)])` applied in `trust_api.py`.
  - `/api/trust` added to `_LOCAL_ONLY_API_PREFIXES` in `local_request_guard.py` so the guard actually fires.

- [ ] Move receipt-worthy event classification out of ad hoc store logic.
  - Short-term acceptable: a named constant such as `RECEIPT_WORTHY_EVENT_TYPES`.
  - Longer-term preferred: event schema or capability metadata, for example `receipt_worthy: true`, derived from governance metadata such as `external_effect`, `persistent_change`, or `confirmation_required`.

## OpenClaw Alignment With Final Stack Direction

Context: the final future stack is now locked as **ElevenLabs speaks, Gemma reasons, OpenClaw acts, Nova governs**. Current OpenClaw code already has strong foundations, but it is still mostly governed home-agent templates plus transitional worker/tool paths. This backlog tracks what must change before OpenClaw can honestly be treated as Nova's full hands layer.

References:

- `docs/audits/2026-04-26/NOVA_OPENCLAW_DOCS_TO_CODE_ALIGNMENT_AUDIT_2026-04-26.md` — current truth and gap audit.
- `docs/future/NOVA_OPENCLAW_HANDS_LAYER_IMPLEMENTATION_PLAN.md` — build sequence, test gates, and done-means criteria.

### Current Truth To Preserve

- Cap 63 `openclaw_execute` is active today as a read-only/network home-agent template execution capability.
- OpenClaw has real foundations: `TaskEnvelope`, `EnvelopeFactory`, scheduler, runner, thinking loop, tool registry, robust executor, executor adapter, proposed action model, runtime store, and ledger events.
- Full Phase-8 governed envelope execution remains deferred in generated runtime truth.
- OpenClaw is not yet a fully general autonomous hands layer.

### Required Future Changes

- [ ] Add an `OpenClawMediator` as the single delegation boundary between Nova governance and OpenClaw worker execution.
  - Intended route: `GovernorMediator -> OpenClawMediator -> EnvelopeFactory -> EnvelopeStore -> OpenClaw runner/thinking loop -> approval queue if needed -> ledger/receipt`.

- [ ] Make `EnvelopeFactory` mandatory for all OpenClaw runs after tests cover manual, scheduler, bridge, and goal paths.
  - Remove or restrict legacy direct envelope construction to tests or migration-only code.

- [ ] Replace `/api/openclaw/approve-action` passthrough behavior with a real approval queue.
  - `READ` may be auto-allowed.
  - `LOCAL_MUTATION` may be auto-allowed only if reversible and allowed by settings.
  - `DURABLE_MUTATION`, `EXTERNAL_WRITE`, and financial/billing actions must become pending/approved/denied decisions, not auto-allow.

- [ ] Make OpenClaw thinking-loop and tool execution envelope-aware for every tool call.
  - Check `tools_allowed`, hostnames, budgets, action type, role policy, sensitive-data policy, and approval state before execution.

- [ ] Route executor-backed OpenClaw tools through Nova governance or an equivalent mediator-controlled boundary.
  - Avoid treating direct `ExecutorSkillAdapter` calls as sufficient governance for production worker actions.

- [ ] Add role-aware task envelope fields or a v2 envelope model.
  - Future fields: `nova_role`, `user_goal`, `task_type`, `risk_level`, `allowed_actions`, `blocked_actions`, `requires_approval_for`, `input_context`, `output_format`, `receipt_required`, `sensitive_data_policy`, and `voice_summary_required`.

- [ ] Split OpenClaw work into authority lanes or sub-capabilities.
  - Candidate lanes: read-only run, draft-only run, local reversible control, durable mutation proposal, external write proposal, owner-mode repo worker.

- [ ] Add OpenClaw run receipts and explicit non-action statements.
  - Examples: `Nothing was sent.`, `Nothing was posted.`, `No customer records were changed.`, `No files were deleted.`, `Two drafts are waiting for approval.`

- [ ] Build the first alignment proof: `Business Follow-Up Brief`.
  - Must be read-only/draft-only first.
  - Use sample or local customer data before any live CRM/email connector.
  - Show transcript, draft suggestions, approval queue item(s), receipt, and explicit “nothing sent/changed” output.

### Guardrail

Do not treat OpenClaw as full hands until Nova can prove:

> Nova can safely direct OpenClaw to do useful work without giving OpenClaw uncontrolled authority.

## Google Account And Connector Onboarding

Context: future Nova should support easy first-run Google sign-in and Google app connections, but Google access must not become hidden action authority. The guiding rule is: **Google connects data. Nova governs action.**

Reference: `docs/future/NOVA_GOOGLE_ACCOUNT_AND_CONNECTOR_ONBOARDING_PLAN.md`.

### Current Truth To Preserve

- Google connector onboarding is a future plan, not current runtime truth.
- First login should be identity-only: `openid`, `email`, `profile`.
- Gmail, Calendar, Drive, and Contacts should be connected incrementally by user choice.
- Local-only mode should remain available.
- Google tokens/scopes grant access, not permission to act without Nova governance.

### Recommended Future Build Order

- [ ] Google Sign-In identity only.
  - Create local Nova profile.
  - Show connected apps screen.
  - Request no Gmail/Calendar/Drive/Contacts access yet.

- [ ] Connector registry and Connected Apps page.
  - Track connector status, scopes, token status, last used/synced time, allowed actions, blocked actions, approval requirements, and disconnect/revoke support.

- [ ] Calendar read-only connector first.
  - Read today/upcoming events.
  - Summarize schedule.
  - No event creation/editing.
  - Receipt says calendar was read.

- [ ] Gmail read-only connector.
  - Summarize selected inbox/thread data.
  - Extract tasks.
  - No sending, deleting, labels, archive, or bulk actions yet.

- [ ] Gmail draft-only connector / Cap 64 alignment.
  - Prepare reply.
  - Ask approval to create draft.
  - User sends manually.
  - Receipt says draft created / not sent.

- [ ] Drive and Contacts read-only connectors.
  - Find/summarize selected files.
  - Find contacts for draft addressing.
  - No file/contact mutation.

- [ ] Connector receipts and non-action statements.
  - Examples: `Nova read today's calendar.`, `Nova summarized 3 email threads.`, `Nova did not send any emails.`, `Nova did not delete or modify files.`

### Guardrail

Do not start with:

```text
full Gmail access
full Drive access
send-email automation
calendar auto-booking
file moving/deleting
contact editing
bulk inbox changes
background connector sync without explicit permission
one-click all Google permissions
plain token storage
automatic connector actions without receipts
```

## Guardrail

Do not expand this into another broad audit. The active execution path remains:

1. Cap 64 P5 live signoff and lock.
2. Clean Windows VM installer validation and `C:\Program Files\Nova\bootstrap.log` review.
3. Trust receipt dashboard card after backend hardening.
4. OpenClaw hands-layer alignment only after the trust/action-history path is stable enough to prove bounded worker execution.
5. Conversation Coherence Layer, Governed Learning, and Background Reasoning only after Cap 64 P5 unless explicitly instructed.
6. Google connector onboarding only after identity, connector registry, token storage, approval queue, and receipts are designed clearly enough to avoid hidden authority.
7. Auralis / website merger work is paused and must not drive active NovaLIS work until the owner explicitly unpauses it.
8. Shopify / Cap 65 P5 live work is paused and must not drive active NovaLIS work until the owner explicitly unpauses it and provides/prepares credentials.

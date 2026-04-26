# BackLog.md

This file tracks follow-up work that is real, but not allowed to distract from the active close-out path in `Now.md`.

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
  - Cap 65: domain format, token scopes, NetworkMediator refusal, GraphQL/empty data, Test 3 restart, period defaults, certify errors.

### Lower Priority / Design Follow-Up

- [x] Add router-level loopback dependency to the Trust Receipt API as defense-in-depth. *(done 2026-04-26, commit 83c7474)*
  - `APIRouter(dependencies=[Depends(require_local_http_request)])` applied in `trust_api.py`.
  - `/api/trust` added to `_LOCAL_ONLY_API_PREFIXES` in `local_request_guard.py` so the guard actually fires.

- [ ] Move receipt-worthy event classification out of ad hoc store logic.
  - Short-term acceptable: a named constant such as `RECEIPT_WORTHY_EVENT_TYPES`.
  - Longer-term preferred: event schema or capability metadata, for example `receipt_worthy: true`, derived from governance metadata such as `external_effect`, `persistent_change`, or `confirmation_required`.

## OpenClaw Alignment With Final Stack Direction

Context: the final future stack is now locked as **ElevenLabs speaks, Gemma reasons, OpenClaw acts, Nova governs**. Current OpenClaw code already has strong foundations, but it is still mostly governed home-agent templates plus transitional worker/tool paths. This backlog tracks what must change before OpenClaw can honestly be treated as Nova's full hands layer.

Reference: `docs/audits/2026-04-26/NOVA_OPENCLAW_DOCS_TO_CODE_ALIGNMENT_AUDIT_2026-04-26.md`.

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

## Guardrail

Do not expand this into another broad audit. The active execution path remains:

1. Cap 64 P5 live signoff and lock.
2. Cap 65 P5 live Shopify checklist and lock.
3. Clean Windows VM installer validation and `C:\Program Files\Nova\bootstrap.log` review.
4. Trust receipt dashboard card after backend hardening.
5. OpenClaw hands-layer alignment only after the trust/action-history path is stable enough to prove bounded worker execution.

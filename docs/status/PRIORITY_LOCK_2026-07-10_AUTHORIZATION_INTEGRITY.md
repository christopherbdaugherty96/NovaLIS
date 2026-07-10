# Authorization Integrity Priority Lock - 2026-07-10

Status: LOCK ONLY. No implementation code. Explicitly POST-OBSERVATION —
this lane does not open until the seven-morning observation period produces evidence.

Scope: strengthen the Governor's authorization primitive so approval is verified
authority, not caller-supplied metadata. No new capabilities. No product-scope expansion.

## Product / Security Signal

A two-pass deep audit (2026-07-10) verified in source that the Governor's internal
contract is weaker than the documented authority claims. Nova's doctrine says:

```text
Intelligence proposes. Nova governs. You decide.
```

The current authorization primitive is closer to:

```text
A caller proposes an action and may attach a boolean claiming that you decided.
```

Three verified findings (checked against runtime source, not taken on trust):

```text
1. Confirmation is a caller-supplied boolean inside ordinary action params
   (governor.py: params.get("confirmed")). The Governor cannot independently
   verify that a live user approved this exact action.
2. A boundary timeout cannot force-cancel a started worker; the effect may still
   complete. (Timeout wording corrected in the 2026-07-10 truth-fix PR; real
   cancellation is deferred to this lane.)
3. A failed completion receipt previously returned silent success. (Corrected to
   completed_degraded in the same truth-fix PR; full effect/receipt reconciliation
   is deferred to this lane.)
```

## What the audit did NOT establish (bounds on the claim)

```text
- No verified live bypass through the current WebSocket UI.
- No evidence Nova acts without prompting in normal use — the session handler
  maintains real pending-confirmation state and injects the flag only after a
  genuine user answer. The boundary holds today by caller convention.
- No reason to stop or alter the read-only morning observation period.
- No permission for broad refactoring or capability work during the freeze.
```

The gap is that the Governor — the component intended to be the final authority —
does not itself possess proof of authorization. That is the whole of this lane.

## Decision

The first engineering lane after the seven-morning observation period is:

```text
Authorization integrity: trusted, action-bound, single-use approval grants,
truthful timeout outcomes, and effect/receipt reconciliation.
```

## Authorized scope when this lane opens

```text
1. Governor-owned ApprovalGrant record: session-bound, capability-bound,
   normalized-action-hash-bound, issued_at, expires_at, single-use (consumed).
2. Remove authorization booleans from ordinary capability parameters. Execution
   requires a trusted approval_id the Governor issued, not params["confirmed"].
3. Material parameter changes (recipient, path, subject, body, target) after a
   grant is issued invalidate that grant.
4. Timeout state machine: requested -> approved -> started -> commit_not_started
   -> committed -> verified. A timeout before "verified" yields outcome_unknown
   plus reconciliation, using cooperative cancellation or a killable child process
   for effectful capabilities.
5. Effect outcome and receipt-persistence outcome represented independently
   (build on the completed_degraded status already added).
6. End-to-end adversarial tests across multiple WebSocket sessions: changed-action
   refusal, replay/single-use refusal, cross-session refusal, expiry refusal.
   Source-text inspection is not accepted as primary certification evidence.
```

## Explicitly NOT authorized by this lock

```text
- Implementing any of the above now (lock only; this lane is post-observation).
- New confirmation-bound or effectful capabilities until this lane closes.
- capability_locks.json changes.
- Broad session_handler.py / brain_server.py refactoring beyond the minimum
  needed to relocate approval state (deeper decomposition is a separate lane).
- Any product-scope expansion, connector work, or autonomy expansion.
- Reopening or weakening the read-only observation period.
```

## Sequencing

```text
1. Seven real morning observation logs (docs/observation/) — in progress, unblocked.
2. Evidence-ranked product bottleneck from those logs.
3. THIS lane (authorization integrity) as the first hardening lane, unless a
   morning surfaces a higher-severity correctness or governance defect.
```

Authorization integrity is a correctness/security lane, not a product-usability
lane. It runs in parallel priority with whatever the mornings rank highest; it does
not require the mornings to justify it, but it does not preempt observation either.

## References

```text
Truth-fix PR (timeout wording, completed_degraded, harness reframe, version sync):
  fix/truthful-outcome-reporting (2026-07-10).
Verified findings: governor.py confirmation check, execute_boundary.py timeout,
  governor.py ACTION_COMPLETED receipt handling.
Doctrine: docs/product/PRODUCT_DEFINITION.md, AGENTS.md core rule.
```

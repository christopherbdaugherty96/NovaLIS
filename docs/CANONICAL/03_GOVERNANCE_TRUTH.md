# 03 — Governance Truth (what is enforced in code)

**Status: runtime-backed.** The governance spine is the strongest, most-tested part of the
system. Claims here map to named modules and generated matrices.

## Source of record

- [`../current_runtime/GOVERNANCE_MATRIX.md`](../current_runtime/GOVERNANCE_MATRIX.md) and
  [`../current_runtime/GOVERNANCE_MATRIX_TREE.md`](../current_runtime/GOVERNANCE_MATRIX_TREE.md)
  — generated governance mapping.
- [`../current_runtime/ROUTE_PROTECTION_COVERAGE.md`](../current_runtime/ROUTE_PROTECTION_COVERAGE.md)
  — per-route protection classification.
- [`../current_runtime/BYPASS_SURFACES.md`](../current_runtime/BYPASS_SURFACES.md) — declared
  surfaces that sit outside the normal path, with justification.
- Runtime state governance section:
  [`../current_runtime/CURRENT_RUNTIME_STATE.md`](../current_runtime/CURRENT_RUNTIME_STATE.md).

## Execution authority model (from the generated doc)

```text
User -> GovernorMediator -> Governor -> CapabilityRegistry -> SingleActionQueue
     -> LedgerWriter -> ExecuteBoundary -> Executor
```

| Component | Role | Location |
| --- | --- | --- |
| GovernorMediator | Invocation router + policy enforcement | `src/governor/governor_mediator.py` |
| CapabilityRegistry | Capability enablement control | `src/governor/capability_registry.py` |
| ExecuteBoundary | Final execution permission gate | `src/governor/execute_boundary/execute_boundary.py` |
| NetworkMediator | Enforced outbound HTTP control | `src/governor/network_mediator.py` |
| LedgerWriter | Append-only audit logging | `src/ledger/writer.py` |

(Paths are relative to `nova_backend/`.)

## Enforced boundaries

- Reasoning cannot execute directly — only the governed path can.
- Every outbound HTTP call must pass NetworkMediator; there is no approved direct network path.
- Every executed action is written to an append-only ledger.
- Confirmation-bound capabilities (Cap 22 open_file_folder, Cap 64 send_email_draft) block on an
  explicit approval before dispatch — certified 2026-05-19, see
  [06_TEST_AND_PROOF_TRUTH.md](06_TEST_AND_PROOF_TRUTH.md).

## Review guardrails (from `REPO_MAP.md`)

No change may introduce: hidden autonomy, background execution loops, silent persistence, direct
execution from reasoning, direct network paths outside mediation, or drift between explanatory
docs and runtime truth.

## Cost posture — visibility only, not enforcement

The registry carries a `cost_posture` field (free / free_tier / paid / unknown_cost) on every
capability and surfaces it in generated docs. **There is no runtime cost enforcement, quota
blocking, or billing guard yet** — this is metadata, labelled *unverified as an enforced
control*.

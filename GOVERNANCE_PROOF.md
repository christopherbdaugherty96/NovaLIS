# Governance Proof

Nova's governance claim should be checked in code, not trusted from prose.

Canonical truth navigation lives at `docs/CANONICAL/00_INDEX.md`; the governance-specific canonical map is `docs/CANONICAL/03_GOVERNANCE_TRUTH.md`.

## Main Runtime Paths

| Purpose | Path |
|---|---|
| FastAPI app | `nova_backend/src/brain_server.py` |
| Dashboard static files | `nova_backend/static` |
| WebSocket chat route | `nova_backend/src/brain_server.py` (`/ws`) |
| WebSocket session handler | `nova_backend/src/websocket/session_handler.py` |
| Capability registry | `nova_backend/src/governor/capability_registry.py` |
| Capability data | `nova_backend/src/config/registry.json` |
| Governor choke point | `nova_backend/src/governor/governor.py` |
| Execution boundary | `nova_backend/src/governor/execute_boundary/execute_boundary.py` |
| Single action queue | `nova_backend/src/governor/single_action_queue.py` |
| Ledger writer | `nova_backend/src/ledger/writer.py` |
| Local HTTP boundary | `nova_backend/src/utils/local_request_guard.py` |
| Route protection classifier | `nova_backend/src/utils/route_protection.py` |

## What The Registry Proves

`CapabilityRegistry` fails closed when:

- registry file is missing
- JSON is malformed
- schema version is unsupported
- phase is wrong
- capability fields are missing
- active capabilities lack governance metadata
- duplicate capability IDs exist
- runtime profile references unknown capabilities
- confirmation-risk capabilities disable confirmation

Useful generated view:

```text
docs/current_runtime/GOVERNANCE_MATRIX.md
```

## Example Allowed Shape

Cap 16:

```text
id: 16
name: governed_web_search
authority_class: read_only_network
requires_confirmation: false
external_effect: false
execution surface: Governor -> NetworkMediator
```

This is a read-oriented capability. It can still fail due to provider/network/model setup, but its authority class is not an external write.

## Example Blocked Shape

Cap 64:

```text
id: 64
name: send_email_draft
risk_level: confirm
requires_confirmation: true
external_effect: true
```

Calling the Governor for Cap 64 without `confirmed=true` returns a refusal before execution:

```text
This action requires confirmation before I can proceed.
```

Nova may open a local `mailto:` draft after confirmation. Nova does not send email.

## One-Command Check

Run:

```bash
python scripts/prove_runtime_truth.py
```

This checks:

- app import
- dashboard HTTP route
- `/phase-status`
- `/ws` connection
- capability registry load
- Cap 16 active/enabled
- Cap 64 confirmation metadata
- Governor refusal for unconfirmed Cap 64
- Governor refusal/failure for unknown capability
- current model trust status as machine-local info

## Related Tests

Representative tests:

```text
nova_backend/tests/certification/cap_16_governed_web_search/test_p4_api.py
nova_backend/tests/certification/cap_64_send_email_draft/test_p4_api.py
nova_backend/tests/certification/cap_64_send_email_draft/test_p3_integration.py
nova_backend/tests/governance/test_mediator_registry_enforcement.py
nova_backend/tests/test_route_protection_coverage.py
nova_backend/tests/test_dns_rebinding_block.py
```

Run focused examples:

```bash
pytest nova_backend/tests/certification/cap_64_send_email_draft/test_p3_integration.py
pytest nova_backend/tests/test_route_protection_coverage.py
```

## Boundary

This proof does not claim broad autonomy. It proves that important runtime routes and governance checks exist and are executable in the current repo.

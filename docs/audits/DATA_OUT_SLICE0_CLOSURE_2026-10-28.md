# Data-Out Slice 0 Closure Review

Date: 2026-10-28  
Reviewed baseline: `main@e7c742cc77ebb6cc5d3f20f5b14ebd3ddc9e47d8`  
Inventory baseline: `main@bab4a6cf1f200eebfad5af166b242d7e9ccdd963`  
Status: Slice 0 candidate; inventory closure and test-only characterization, no runtime change

## Decision

The frozen inventory remains a suitable implementation boundary for supported production/runtime
and setup egress. Every reviewed mechanism has a disposition below. No unresolved P0/P1 omission
or material misclassification was found after accounting for changes between the inventory and the
reviewed baseline.

This conclusion does not mean Data-Out enforcement exists. The default profile still has a
reproducible provider-policy bypass below the normal capability-62 caller gate. Slice 1 remains
unstarted.

## Review method

The closure pass:

1. compared all runtime/setup files changed since `bab4a6c`;
2. rescanned supported source and launch scripts for HTTP clients, sockets, `urllib`, browser/OS
   handoffs, process creation, executable discovery, temporary files, filesystem roots, and storage
   probes;
3. traced the provider-setting gate through `ExternalReasoningExecutor`, `DeepSeekBridge`,
   `DeepSeekReasoningProvider`, and `NetworkMediator`;
4. reran PR #462's network-evidence and redirect regressions; and
5. added strict-xfail transport-spy characterizations for the remaining provider-off gap.

Developer-only scripts, tests, archives/quarantine, inactive future code, and hypothetical
mechanisms remain outside closure unless they establish a supported reachable P0/P1 path.

## Closure matrix

| Mechanism class | Current disposition | Implementation owner |
| --- | --- | --- |
| External model prompts and credentials | Reproducible red baseline: the normal cap-62 executor honors `external_reasoning_enabled`, but `DeepSeekBridge` and `DeepSeekReasoningProvider` do not make that setting a final-boundary invariant. T1 separately blocks these paths only in trial. | Slices 2–3 |
| Governed external HTTP: search, source reads, news, weather, commerce | Inventory remains accurate. Requests are primarily mediated, but capability enablement is not disclosure permission and typed field/destination binding is absent. | Slices 2 and 4 |
| Provider setup, health, OAuth, and key operations | Direct health/setup calls remain separately identified. T1 added early trial rejection but did not create the default-profile Data-Out boundary. | Slice 4 |
| Model-local HTTP and startup probes | T1 disabled ambient Requests proxies and redirects for the runtime model mediator and tightened trial endpoints. Default/startup paths still need explicit effective-route/locality policy and uniform proof. | Slices 2 and 7 |
| Redirects and network failure evidence | PR #462 / closed issue #461 are green on current `main`: cross-origin redirects are rejected before the second request and raw/query credentials are sanitized from failure evidence. Same-origin next hops still need a fresh disclosure decision under the future common contract. | Preserve in Slice 2; extend, do not reopen fixed defect |
| Runtime, installation-relative, temporary, selected-file, and executable-search storage | Inventory remains accurate. Locality cannot be inferred by probing the untrusted target; trusted bootstrap evidence remains required. | Slice 5 |
| Browser, mail-client, application, subprocess, installer, and shell handoffs | Inventory remains accurate. Exact child environments and handoff-only outcomes are not yet governed by the common disclosure contract. | Slice 6 |
| Windows reminder delivery and startup registration added after the inventory baseline | Supported local OS handoffs are now explicitly dispositioned. Toast content crosses into the Windows notification subsystem; sign-in registration persists an executable command whose backing may be nonlocal. Treat toast as a typed local-OS disclosure/handoff and classify executable/install backing before registration or later launch. Do not claim Windows-owned downstream behavior is socket-controlled by Nova. | Slices 5–6 |
| Static enforcement and generated truth | Existing scanning is narrower than the frozen mechanism set and generated truth does not represent a complete disclosure decision. | Slice 8 |

## Red baseline evidence

`nova_backend/tests/governance/test_data_out_slice0_red_baselines.py` contains two strict expected
failures expressing the desired future invariant:

- provider-off must stop `DeepSeekReasoningProvider` before the fake transport; and
- provider-off must stop `DeepSeekBridge` before the provider adapter.

Both currently reach their spies in the default profile, so both desired assertions are red. The
tests make no external network request. When Slice 3 fixes the boundary, strict XPASS will fail the
suite until the characterizations are converted to ordinary passing regressions.

This evidence establishes a current policy/enforcement gap, not observed real-world transmission.

## Green baseline evidence

The PR #462 regressions remain green on the reviewed baseline:

- cross-origin 301/302/303/307/308 responses stop before a second request;
- malformed redirect targets produce sanitized evidence;
- query credentials and raw request exception text do not persist or propagate; and
- same-origin redirect behavior remains explicitly tested.

The T1 proof remains a separate trial-profile claim and cannot be generalized to the default
profile or machine-wide monitoring.

## Slice 0 exit assessment

- Closure matrix: complete for the frozen supported scope.
- P0/P1 omissions or material misclassifications: none unresolved after adding the Windows
  notification/startup disposition.
- Remaining known provider/model gap: reproducible with in-process spies and recorded as strict red
  characterizations.
- PR #462 regression baseline: green.
- Runtime behavior or authority changes: none.

Slice 0 may be accepted independently. Acceptance does not start Slice 1, repair the recorded red
gap, authorize external-model access, or establish Data-Out completion.

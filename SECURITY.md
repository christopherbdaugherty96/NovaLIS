# Security Policy

## Reporting a vulnerability

Report vulnerabilities privately through
[GitHub Security Advisories](https://github.com/christopherbdaugherty96/NovaLIS/security/advisories/new).
Do not open a public issue, and do not disclose publicly until a fix or mitigation is available.

Please include:

- a clear description of the vulnerability and its impact
- steps to reproduce
- environment: OS, Nova version, and the exact commit SHA
- a proof of concept, if you have one
- contact details for follow-up (optional)

We aim to acknowledge reports within 14 days and may ask for more information to reproduce
and triage the issue.

## Supported versions

Nova is alpha software. Only the current `main` branch is supported. No installer is currently
published; earlier installer artifacts are historical and unsupported.

## Security model

Nova is designed to run on, and be reachable only from, the user's own machine.

- **Local-only.** Nova binds to loopback by default. Exposing it to a network, tunnel, or
  reverse proxy is unsupported. Remote access is not supported in the current release.
- **Intelligence is not authority.** Model output, memory, conversation context, and connection
  state never authorize an action by themselves. Sensitive actions require a single-use approval
  bound to the session, the capability, and the exact action.
- **Governed outbound access.** Governed capabilities make outbound requests through Nova's
  network mediator. Known exceptions are tracked in the generated
  [Bypass Surfaces](docs/current_runtime/BYPASS_SURFACES.md) report.
- **Local data.** Memory, settings, ledger, and provider keys are stored locally. In a source
  checkout they live under `nova_backend/src/data/` and `nova_backend/src/secrets/`. Never commit
  them, and never build an installer from a working copy that contains them.

## In scope

- bypassing approval, confirmation, or capability boundaries
- reaching local-only interfaces from another machine
- data leaving the machine without the corresponding setting or approval
- secrets or personal data exposed in the repository, logs, receipts, or build artifacts
- installer or update integrity

## Out of scope

- attacks that require an already-compromised user account on the machine running Nova
- behaviour of third-party model providers once data has been deliberately sent to them
- findings in historical documents, branches, or artifacts that do not affect current `main`

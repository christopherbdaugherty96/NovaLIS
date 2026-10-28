# Provider-Neutral Data-Out Implementation Plan

Date: 2026-10-28  
Planning baseline: `main@a93637ddc41018156e325baec1b7d254004313f8`  
Status: approved implementation plan only; runtime implementation remains separately gated

## Outcome

Nova needs one provider-neutral disclosure decision at the last in-process point before data,
credentials, or sensitive filesystem evidence can leave the trusted local boundary. An enabled
capability, configured key, usage budget, or caller-side provider toggle is not Data-Out
permission.

The implementation is complete only when supported outbound paths either:

1. receive an `ALLOW` decision bound to the actual destination, route, fields, credential
   categories, purpose, and policy version; or
2. return an explicit local `DENY`/`UNKNOWN` result before DNS, connection, transport,
   delegation, or network-backed filesystem contact.

This plan refines the frozen inventory in
[`../audits/EGRESS_INVENTORY_2026-10-08.md`](../audits/EGRESS_INVENTORY_2026-10-08.md).
The inventory remains the detailed mechanism and regression checklist.

## Authority boundary

Data-Out permission is an additional necessary condition. It never replaces the Governor,
capability registry, confirmation requirements, execution boundaries, provider budgets, or
receipts. Memory and model reasoning do not grant disclosure authority.

This plan does not authorize runtime changes, provider onboarding, stronger-model integration,
Google expansion, Shopify writes, browser/computer-use expansion, autonomous execution, or public
distribution. Each implementation slice requires its own reviewed authorization and exact-head
acceptance.

## Common contract

Introduce immutable, typed structures owned by the governance boundary:

- `DisclosureRequest`: caller/capability and correlation IDs; purpose; actual transport class;
  boundary-derived provider, destination, destination class, and effective route; verified data
  and credential categories; user-initiation/approval state; policy version.
- `DisclosureDecision`: `ALLOW`, `DENY`, or `UNKNOWN`; bounded reason; policy version; safe
  destination identity; verified category names; correlation IDs.
- typed outbound adapters: derive categories from the actual outgoing URL, method, query, headers,
  body, files, child environment, or filesystem operation. Free-form caller labels are not proof.
- sanitized disclosure evidence: records decisions and structural metadata without payloads,
  credential values, userinfo, sensitive query values, or raw exception text.

Only `ALLOW` may continue. Any outgoing mutation after the decision invalidates it. Redirects,
effective proxies, prepared-request credential injection, delegated child environments, and
changed filesystem backing require a new decision.

## Ordered implementation slices

### Slice 0 — Closure review and red baselines

- Revalidate the frozen inventory against current `main` without widening it for hypothetical,
  archived, developer-only, or inactive paths.
- Confirm every supported runtime/setup egress mechanism has a disposition and no unresolved P0/P1
  omission or material misclassification remains.
- Record red tests for the known provider/model bypasses and failure-evidence leakage before
  changing the implementation.

Exit gate: reviewed closure matrix and reproducible red evidence. No runtime behavior changes.

### Slice 1 — Pure policy and evidence vocabulary

- Add the immutable request/decision types, policy evaluator, provider/destination and data-category
  vocabularies, trusted local bootstrap evidence sink, and sanitization rules.
- Default unclassified, mismatched, unavailable-policy, or unavailable-evidence cases to
  `UNKNOWN`; treat `UNKNOWN` like denial.
- Keep the policy pure: no DNS, URL fetch, target-path probe, provider call, or delegated action.

Exit gate: deterministic unit tests and durable secret-free decision evidence.

### Slice 2 — Final HTTP and model-network boundaries

- Enforce the decision inside `NetworkMediator.request`, `connection_request`, and
  `ModelNetworkMediator` immediately before URL validation, DNS, session/client construction, or
  send.
- Derive identity from the real transport URL; bind actual fields through typed adapters.
- Disable ambient netrc/CA/key-log behavior unless its backing and credential/session-secret
  categories are explicitly governed.
- Classify environment and platform proxies as additional destinations.
- Disable automatic redirects or reauthorize every exact next hop before send; strip origin-bound
  fields by default across origins.

Exit gate: denial proves zero DNS/client/socket attempt; redirect and proxy tests prove no policy
inheritance; evidence contains no secrets.

### Slice 3 — External-model leak closure

- Route general-chat escalation, capabilities 31/48/54/62, and the OpenAI fallback through the
  final-boundary decision.
- Preserve capability 62's existing `external_reasoning_enabled` caller gate as an additional
  requirement.
- Correct capability/runtime truth so nested provider calls are not described as local-only.

Exit gate: with provider disclosure denied, every supported model route returns a local result,
records a durable denial, and produces zero DNS, connection, payload, or credential attempts.
This gate is mandatory before governed stronger-model access may be declared ready.

### Slice 4 — Setup, health, and external read paths

- Replace direct provider health/setup requests with governed transport.
- Add typed provider/destination/category adapters for search, source reads, news, weather,
  commerce, provider-key operations, and Google OAuth setup.
- Constrain Shopify read-only destinations to approved Shopify Admin hosts before preparing tokens,
  headers, or bodies.

Exit gate: real-caller denial regressions for capabilities 16, 48, 49, 50, 55, 56, and 65 plus
credential/setup paths; no credential-bearing failure evidence.

### Slice 5 — Filesystem locality and trusted storage

- Classify effective runtime roots, installation-relative goal/story stores, temporary storage,
  calendar, Piper/audio, selected files, executable-search roots, and health-probe roots before the
  first target operation.
- Treat UNC, mapped/network drives, redirected folders, reparse points/symlinks, remote mounts, and
  unverifiable backing as external or `UNKNOWN`.
- Do not use `resolve`, `exists`, `stat`, enumeration, directory creation, read, write, or ambient
  share authentication to decide whether a target is safe.
- Keep denial evidence on a separately trusted local sink. Later storage migration is a separate
  implementation concern unless required to close a verified path.

Exit gate: `DENY`/`UNKNOWN` touches no target or fallback candidate and performs no network-backed
filesystem operation.

### Slice 6 — Delegated egress and child environments

- Gate browser, mail-client, application, subprocess, shortcut, Ollama, pip, winget, and supported
  shell/bootstrap handoffs before delegation.
- Build minimal exact child environments; never inherit unrelated provider keys, proxy/netrc/CA
  controls, or secrets by default.
- Use handoff-only outcome vocabulary. Do not claim Nova controlled child sockets or that a browser
  loaded, mail was sent, or a process completed an external action without evidence.

Exit gate: denial invokes no OS/process handoff; allowed-child tests prove exact environment
minimization and secret exclusion.

### Slice 7 — Local-model and startup closure

- Prove local/private model traffic has a direct, non-proxied route before granting the local class.
- Reject or govern origin userinfo; sanitize model URLs; reauthorize redirects.
- Apply equivalent fail-closed checks before launcher readiness probes, browser discovery/handoff,
  curl configuration, and provider-status probes.

Exit gate: public, proxied, DNS-rebound, redirected, or ambiguous model/startup routes make zero
attempts; independently tested direct-loopback operation remains available.

### Slice 8 — Static enforcement, generated truth, and complete proof

- Expand static scanning beyond `requests` to sockets, `urllib`, browser/OS handoffs, subprocesses,
  ambient configuration, executable discovery, temporary files, and network-backed storage roots.
- Require each supported mechanism to name the common boundary or appear as an unresolved failure.
- Regenerate runtime/capability/bypass truth and run the exact-head end-to-end proof package.

Exit gate: complete closure matrix, clean static scan, generated truth aligned with implementation,
and exact-head independent acceptance.

## Zero-attempt acceptance contract

For every supported denied path—and every `UNKNOWN` result—the proof must establish:

```text
policy evaluated before egress
-> no target-path probe or network client/session/socket creation
-> zero DNS lookup and zero connection attempt
-> zero delegated process/application handoff
-> zero payload or credential transmission
-> explicit local result
-> durable, secret-free disclosure-decision evidence
-> no transport-success receipt
```

The proof must include boundary-unit spies, real caller regressions, redirect/proxy/identity tests,
prepared-request binding, delegated-environment inspection, remote-filesystem cases, startup/setup
paths, evidence-hygiene tests, static mechanism detection, and a real session-route denial proof.
Each slice retains red-before-green evidence against the relevant pre-fix revision.

Instrumented Python tests are not machine-wide monitoring. Delegated child behavior must be stated
as outside Nova's socket-level proof after handoff unless separately measured.

## Completion and sequencing gates

Data-Out is complete only when all supported mechanisms in the frozen closure scope have passed
their slice gates and the final exact-head review returns PASS. Partial slice completion must be
reported as partial and must not be generalized to unsupported transports or machine-wide traffic.

Governed stronger-model work remains separately authorized and later in sequence. Its entry gate
requires, at minimum, completed Slice 3 on the same accepted Data-Out foundation, including
zero-attempt denial evidence—not merely a disclosure dialog or a distribution-time promise.

No downstream lane starts automatically when Data-Out completes.

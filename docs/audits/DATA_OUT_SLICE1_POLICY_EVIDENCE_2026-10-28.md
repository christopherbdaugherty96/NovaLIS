# Data-Out Slice 1 — Policy and Evidence Vocabulary

Date: 2026-10-28  
Implementation baseline: `main@da87f85df2b9fe1cc5c0f69fea105b29c551e55c`  
Status: candidate implementation; pure vocabulary/evaluator and explicit evidence sink only

## Implemented boundary

Slice 1 adds `src/governor/disclosure_policy.py` with:

- immutable disclosure request, grant, policy, decision, and evidence structures;
- provider-neutral transport, provider class, destination, data, credential, and initiation
  vocabularies;
- a deterministic evaluator returning only `ALLOW`, `DENY`, or `UNKNOWN`;
- exact grant matching for provider identity/class, normalized destination, effective route,
  destination class, transport, disclosed categories, purpose, caller, capability, and
  initiation state, with no empty-set wildcard scopes;
- URL normalization only for URL-bearing transports, while non-URL process/filesystem
  destination identities retain case for exact matching;
- fail-closed `UNKNOWN` results for missing policy/evidence, version mismatch, unclassified or
  malformed vocabulary, and evidence-write failure;
- identity-mismatch denial for caller-declared versus boundary-derived provider/destination data;
- a JSONL evidence sink that accepts only an explicitly pre-verified local target; and
- evidence projection that stores structural categories and sanitized identities, never payloads,
  credential values, URL userinfo, URL paths, query values, or fragments.

Pure evaluation never exposes executable permission. Only an `ALLOW` returned after its durable
evidence append succeeds exposes `may_proceed=True`; `DENY`, `UNKNOWN`, and unrecorded `ALLOW`
results are non-proceeding decisions.

## Deliberately not implemented

Slice 1 is not connected to `NetworkMediator`, `ModelNetworkMediator`, provider adapters,
filesystem operations, browsers, processes, setup flows, or capability execution. It performs no
DNS, HTTP, socket, target-path classification, provider call, or delegated action.

The `VerifiedLocalEvidenceTarget` is a bootstrap contract, not a locality detector. Callers cannot
construct the sink with `locality_verified=False`; Slice 5 owns trustworthy locality derivation and
revalidation. Until a later slice supplies a verified target, missing evidence returns `UNKNOWN`.

No provider is enabled and no Data-Out gap is repaired by this slice.

## Evidence semantics

An exact explicit policy grant can evaluate to `ALLOW` only after request vocabulary is complete
and typed, the destination is valid for its transport, every exact scope is populated, and the
initiation state matches. An allowance becomes executable only after the durable evidence append
succeeds; it is downgraded to `UNKNOWN` if the sink is unavailable or fails to write.

The evidence record contains:

- decision and bounded reason;
- policy version and correlation identifiers;
- caller, purpose, initiation, and capability identity;
- sanitized provider/destination class and transport;
- verified data- and credential-category names; and
- UTC record time.

Policy versions and correlation identifiers are stored as bounded SHA-256 fingerprints. Caller,
purpose, and provider labels are readable only for an exact allowed policy match; denied or
unknown untrusted labels are fingerprinted. Malformed capability identifiers are omitted so
arbitrary input cannot become a secret-bearing evidence field.

Evidence enum fields require their exact expected enum class. Foreign objects or unrelated enums
with a string-valued `value` attribute produce fixed `unclassified_*` markers rather than
persisting caller-controlled text.

It has no field for prompt text, document contents, tokens, keys, authorization values, child
environment values, or arbitrary exception strings.

Each record is explicitly a `disclosure_policy_evaluation` with `transport_observed=false`. It is
not a transport-success or execution receipt and cannot prove that a later operation occurred.

## Test evidence

`tests/governance/test_disclosure_policy.py` verifies:

- immutable contracts;
- exact allow matching, recorded-allow permission, and non-proceeding pure/deny/unknown states;
- provider and destination mismatch denial;
- missing/unmatched grants and rejection of empty wildcard scopes;
- exact initiation matching and transport-appropriate destination syntax;
- case-sensitive non-URL process/filesystem destination matching;
- policy/evidence unavailability and evidence-write failure;
- malformed request/policy vocabulary fail-closed behavior;
- explicit rejection of an unverified evidence target;
- durable JSONL persistence with secret and URL sanitization;
- bounded evidence for malformed input; and
- fixed evidence fallbacks for malformed or foreign enum values; and
- absence of transport/DNS/delegation imports from the policy module; and
- narrow scanner treatment of `urllib.parse` while retaining detection of network-capable
  `urllib.request` imports.

## Slice 1 acceptance boundary

Acceptance establishes vocabulary and deterministic policy/evidence behavior only. Slice 2 must
derive identity and categories from actual outgoing structures and enforce the decision at final
HTTP/model-network boundaries. Slice 1 does not authorize Slice 2 or stronger-model access.

# Data-Out Slice 3A — External-model denial closure

Date: 2026-10-30  
Baseline: `main@29bd4dc4770d0049041aea01cadca6aaf0e90aa9`  
Status: implementation candidate; deny-only; not full Slice 3 or Data-Out completion

## Scope

This bounded slice makes provider-off a final invariant for the currently
reachable DeepSeek and OpenAI model boundaries. It covers direct provider calls,
`DeepSeekBridge`, General Chat escalation, capabilities 31/48/54/62, and the
OpenClaw metered OpenAI fallback.

No external-model disclosure grant is added. No provider is enabled. Missing
policy, classification, grant, or evidence remains `UNKNOWN` and
non-proceeding at the merged Slice 2 transport boundary.

## Red-before-green evidence

The two Slice 0 strict expected failures reproduced on the baseline:

- provider-off direct `DeepSeekReasoningProvider` calls reached the transport
  spy; and
- provider-off `DeepSeekBridge` calls reached the provider spy.

A new direct-call regression reproduced the equivalent OpenAI gap: calling
`OpenAIResponsesLane.summarize_task_report` while the metered lane was disabled
reached its network spy without raising the settings denial.

## Correction

- `DeepSeekReasoningProvider.analyze` checks
  `external_reasoning_enabled` before API-key preparation, budgeting, payload
  construction, or transport invocation.
- `DeepSeekBridge.analyze` independently checks the same permission before the
  provider adapter, so nested callers cannot bypass the restriction.
- An explicitly enabled local reasoning fallback remains available without
  calling the external provider. No silent local or cloud fallback is added.
- `OpenAIResponsesLane.summarize_task_report` re-evaluates its settings,
  routing, key, and budget plan at the final provider method before preparing
  or sending the request.
- Provider-off remains an explicit settings denial. Missing disclosure
  authorization remains the separate `UNKNOWN` fail-closed result implemented
  by the transport boundary.
- Capabilities 31 and 54 classify the provider-paused response as unavailable
  instead of presenting it as malformed model output. Capability 48 continues
  to disable undeclared external-model enrichment on its approved report path.

## Evidence boundary

The provider-off check intentionally occurs before payload and credential
preparation. It does not fabricate disclosure evidence. Secret-free disclosure
evidence is recorded only when a legitimately verified sink is supplied to the
common boundary. Trustworthy production evidence-target locality remains a
later Data-Out obligation.

## Explicit non-claims

This slice does not establish:

- an external-model `ALLOW` path;
- stronger-model readiness;
- production disclosure classification, grants, or trustworthy evidence-root
  composition;
- setup, health, OAuth, filesystem, delegated-process, startup, or local-model
  closure;
- full Slice 3 or full Data-Out completion; or
- machine-wide network monitoring.

## Acceptance

The candidate must retain ordinary passing regressions for the two former
xfails and the direct OpenAI bypass, prove zero provider/network calls for all
covered provider-off routes, preserve explicit local-only fallback, pass the
focused and full suites plus repository truth checks, and receive hosted CI and
independent exact-head review before a separate merge decision.

## Candidate validation

Local validation on the final uncommitted candidate completed with:

- 70 focused caller, provider, policy-boundary, and runtime-truth tests passed;
- 389 adjacent provider and OpenClaw tests passed;
- 5,779 full-suite tests passed and 6 skipped;
- Ruff passed for the complete production source tree;
- dependency, release-identity, public-source, operational-truth, and
  runtime-document checks passed; and
- the structural runtime smoke proof passed.

Hosted CI and independent exact-head review remain required after the candidate
is committed and pushed.

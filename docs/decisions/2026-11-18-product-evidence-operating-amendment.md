# Product-Evidence Operating Amendment

Date: 2026-11-18  
Status: Owner-approved operating direction  
Baseline at decision: `ed0a533e6854abda6a1cfbdbdc5ef94dde7bbb5e`

## Decision

Nova remains governance-first, but release certification no longer blocks isolated,
non-authorizing product evaluation. Work proceeds on two bounded tracks:

```text
TRACK A — SAFE LOCAL OPERATION
Keep production-reachable startup, shutdown, execution, and disclosure paths safe.
Repair only reproduced local-operation defects needed by supported owner use.

TRACK B — PRODUCT EVIDENCE
Measure conversation, routing, context, memory, grounding, latency, and daily-use value.
Permit test-only evaluation that does not exercise unresolved external authority.

RELEASE GATE — EXTERNAL DISTRIBUTION
Full required Data-Out closure, Windows locality, installer, executable identity,
clean-artifact proof, and consolidated acceptance remain mandatory before distribution.
```

This amendment supersedes the 2026-10-27 sequence only where that sequence made all
product-evidence work wait for complete Data-Out certification. It does not weaken any
authority, disclosure, evidence, locality, or release requirement.

## Current evidence

- PR #518 is merged; the bounded Windows backend-startup repair is complete.
- A clean isolated environment at the decision baseline reached backend readiness.
- `gemma2:2b` identity and the owner-confirmed version lock were verified.
- The temporary lightweight configuration (`num_ctx=2048`, `num_predict=128`) produced
  one accurate local answer in about 13.7 seconds.
- That run reached 95.9% physical-memory use with only about 0.31 GB available.
- The five-turn context test and unchanged 31-turn benchmark have not passed.
- Hardware tiers are accepted product direction; their implementation is not yet earned.

## Immediate sequence

1. Complete one low-overhead, fixed-input five-turn lightweight acceptance run.
2. Score performance separately from conversational quality.
3. Decide whether `gemma2:2b` is viable for a provisional Lite workload.
4. If viable, run the unchanged 31-turn benchmark under the same recorded profile.
5. Prove one owner-use workflow: brief -> follow-up -> reminder -> correction -> recall
   -> truthful summary.
6. Repair only the highest-impact reproduced product failure, with separate review and
   merge authority.
7. Continue required release-security proof without treating it as a blocker for safe,
   isolated Track B evaluation.

## Product scorecard

Track B evidence must keep these measures separate:

- intent accuracy;
- context accuracy;
- groundedness;
- governed task reliability;
- usability, including latency and resource stability.

Test completion is not product acceptance. Governance-test totals do not substitute for
this scorecard.

## Authorized test-only boundary

The owner authorized a bounded low-overhead runner that may:

- apply process-scoped `gemma2:2b` / 2048 / 128 settings;
- use Nova's supported model-confirmation mechanism only for the exact verified identity;
- send the fixed minimal prompt and five fixed context prompts through Nova's real local
  WebSocket interface;
- record local latency, response, memory, and error evidence;
- stop its own Nova backend and unload its own model workload on safety failure or exit.

It may not terminate unrelated processes, enable providers, bypass the Governor or model
lock, change production defaults, download models, create persistent hardware profiles,
run the 31-turn benchmark automatically, or claim release acceptance.

## Deferred decisions

- A persistent Lite/Standard/Pro configuration mechanism requires evidence from the
  lightweight run and separate authorization.
- Smaller-model evaluation requires a separate model-identity decision.
- Stronger-model or external-provider access remains separately governed.
- Operational Continuity, provider expansion, voice expansion, and unrelated features
  remain paused.


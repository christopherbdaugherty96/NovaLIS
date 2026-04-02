# Nova Sovereignty Platform Phase Realignment
Date: 2026-03-18
Status: Planning packet only; runtime not authorized
Scope: Decomposes the March 2026 sovereignty-platform spec into phase-correct design plans aligned with the current repository state

## Purpose
This packet absorbs the supplied sovereignty-platform spec without letting design intent overwrite live runtime truth.

It exists because the source spec mixed three different layers:
- locked identity and constitutional language
- claims about the current runtime
- future-phase integration plans

Nova already has a runtime truth system for the second category.
This packet keeps the identity and roadmap value while relocating the work into the correct design phases.

## Runtime Grounding Corrections
Use these corrections when reading the source spec against the current repo:
- Runtime truth currently shows Phase 4, Phase 4.2, Phase 4.5, and Phase 5 as active in `docs/current_runtime/CURRENT_RUNTIME_STATE.md`.
- The current capability registry already uses capability `31` for `response_verification`, `60` for `explain_anything`, and `61` for `memory_governance`.
- The current runtime already has `screen_capture`, `screen_analysis`, `explain_anything`, memory governance, runtime audit endpoints, and a mediated local `llm_gateway`.
- The current repo also contains a practical pain-point note in `docs/design/Phase 8/node design.txt` saying screen-aware explain flows and the brief flow are not yet working reliably in real use.
- Therefore the source spec should be treated as a planning realignment packet, not as an overwrite of live status.

## Locked Identity Carried Forward
The following ideas from the source spec are preserved as the identity layer for future planning:
- Nova is a personal AI sovereignty platform.
- Nova is a governed agent node.
- Intelligence and authority must remain structurally separate.
- Nova remains Agent Under Law: reasoning may expand, but execution authority stays inside the Governor spine.
- No autonomy, background execution, or silent authority expansion is authorized unless a future phase is explicitly designed, verified, and unlocked.

## Section Relocation Map
| Source section | Correct location now |
| --- | --- |
| Core identity | Cross-phase identity layer in this packet |
| Source phase table | Normalized against `docs/current_runtime/CURRENT_RUNTIME_STATE.md` |
| Runtime architecture, execution pipeline, ledger contract, ActionResult contract | Phase 6 alignment and hardening plan |
| Authority class hierarchy | Phase 6 capability-topology and contract-hardening plan |
| Claude API integration | Phase 7 governed external reasoning plan |
| OpenClaw integration | Phase 8 governed execution plan |
| Email end-to-end flow | Phase 8 execution walkthrough, later Phase 9 node-scale use cases |
| Critical risks and mitigations | Shared gating criteria across Phases 6-9 |
| Known gaps to fix first | Phase 6 trust-loop and runtime-alignment plan |
| Future roadmap | Split into Phases 7, 8, and 9 |
| AI handoff summary | Preserved as cross-phase interpretation rule |

## New Phase Placement

### Phase 6 - Sovereignty Alignment and Trust Loop Completion
Phase 6 is the correct home for the work that must happen before any Anthropic or OpenClaw integration is allowed.

Moved here:
- runtime truth/doc alignment cleanup
- end-to-end capability audit
- explain-anything reliability fixes
- intelligence brief reliability fixes
- Recent Actions / Trust Review payoff loop
- authority-class metadata normalization
- ActionResult contract normalization
- four-event ledger completeness enforcement
- CI enforcement against direct network and direct LLM bypasses

Primary design artifact:
- `docs/design/Phase 6/PHASE_6_SOVEREIGNTY_ALIGNMENT_AND_TRUST_LOOP_PLAN.md`

### Phase 7 - Governed External Reasoning
Phase 7 is the correct home for Anthropic or any other external reasoning provider.

Moved here:
- provider abstraction for Anthropic
- gateway-mediated Claude access
- LLM output sanitizer layer
- explicit Governor-mediated routing for external reasoning
- bounded timeout, model, and audit controls

Important current correction:
- do not reuse capability IDs `31`, `60`, or `61`
- current candidate planning ID for external reasoning is `62`

Primary design artifact:
- `docs/design/Phase 7/PHASE_7_GOVERNED_EXTERNAL_REASONING_PLAN.md`

### Phase 8 - Governed External Execution
Phase 8 is the correct home for OpenClaw or any similar browser/app executor.

Moved here:
- governed OpenClaw capability definition
- strict confirmation and authority-class gating
- executor isolation and schema validation
- sanitizer path for untrusted executor output
- user-visible execution payoff loop for external actions

Important current correction:
- do not reuse capability ID `60`
- current candidate planning ID for governed OpenClaw execution is `63`

Primary design artifact:
- `docs/design/Phase 8/PHASE_8_OPENCLAW_GOVERNED_EXECUTION_PLAN.md`

### Phase 9 - Governed Node / Sovereign Platform Direction
Phase 9 is the correct home for the multi-device governed-node direction.

Moved here:
- Nova as local governed node
- device-to-node routing model
- unified trust and control surface across clients
- provider swap without daily-experience drift
- packaging of the sovereignty-platform identity at product scale

Primary design artifact:
- `docs/design/Phase 9/PHASE_9_GOVERNED_NODE_PLAN.md`

## Shared Gating Criteria Across Phases 6-9
The following remain mandatory regardless of phase:
- no direct execution outside the Governor spine
- no direct external HTTP outside the approved mediated path
- no direct external model calls outside the approved LLM gateway path
- no hidden background execution loops
- no silent authority expansion
- all execution attempts logged with a complete lifecycle
- trust-facing UI must show what happened, why it happened, and what changed

## AI Handoff Rule
When using this packet as context, apply it in this order:
1. runtime truth first
2. proof artifacts second
3. this packet third
4. phase-specific design docs fourth

If any phase-planning document conflicts with runtime truth, runtime truth wins.

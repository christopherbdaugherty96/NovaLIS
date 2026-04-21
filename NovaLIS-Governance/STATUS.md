# NOVA Governance Status

Updated: 2026-04-21
Status: Current runtime governance summary
Scope: Reflective status of the live repository state

## Purpose
This file is the short governance-facing status view for the current Nova runtime.

It replaces the older "Capability 16 only" staging snapshot.

Use this file when you want the concise answer to:
- what phase Nova is currently in
- what capability surface is active
- what remains intentionally disabled

If there is ever a conflict between this file and the runtime truth packet, the runtime truth packet wins:
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`
- `docs/current_runtime/RUNTIME_FINGERPRINT.md`

## Runtime Phase Status

| Phase | Status | Meaning now |
| --- | --- | --- |
| 3.5 | COMPLETE | Governance baseline sealed |
| 4 | ACTIVE | Governed execution runtime is live |
| 4.2 | ACTIVE | Explicit orthogonal cognition and structured analysis surfaces are live |
| 4.5 | ACTIVE | UX trust, screen/context, and daily snapshot surfaces are live |
| 5 | ACTIVE | Governed memory, continuity, scheduling, tone, and workspace surfaces are live |
| 6 | COMPLETE | Trust loop, policy review, capability topology, and manual policy execution review are complete |
| 7 | COMPLETE | Governed external reasoning, second-opinion review, provider transparency, and runtime settings controls are complete |
| 8 | ACTIVE | Manual OpenClaw home-agent runtime is live; strict preflight active; broad envelope-governed execution remains deferred |
| 9 | ACTIVE | OpenClaw intelligence layer active: dynamic tool registry, iterative thinking loop, goal-based execution, execution memory, error recovery, Gemma 4 personality |

## Current Authority Model

Nova remains:
- invocation-bound
- Governor-mediated
- capability-scoped
- ledger-audited
- fail-closed

Nova does not:
- act autonomously
- run delegated triggers in the background
- silently save memory
- widen execution authority through external reasoning

## Active Governed Capability Surface

Current active governed capability IDs:

`[16, 17, 18, 19, 20, 21, 22, 31, 32, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64]`

Capability count:
- 26 active governed capabilities

High-level categories:
- research and web intelligence
- local navigation and device control
- diagnostics and trust visibility
- news and structured intelligence
- screen/context explanation
- governed memory and continuity
- governed external reasoning review
- OpenClaw home-agent execution (cap 63)
- email draft composition (cap 64) — external_effect, confirmation-gated, user sends manually

## Required Execution Path

All governed capability execution must pass through:

`User -> GovernorMediator -> Governor -> CapabilityRegistry -> SingleActionQueue -> LedgerWriter -> ExecuteBoundary -> Executor`

This is the live runtime invariant for governed action.

## Intentionally Disabled or Not Yet Live

These remain intentionally unavailable as live runtime truth:
- wake word runtime (requirements file exists; no runtime module)
- delegated trigger runtime
- background policy execution
- autonomous agent execution
- OpenClaw broad envelope-governed execution (manual foundation is live; full envelope issuance path deferred — governance hardening plan in `docs/future/NOVA_OPENCLAW_GOVERNANCE_HARDENING_2026-04-21.md`)
- inbox_check template (visible in agent store; email connector not yet available)
- Cloud provider onboarding (BYOK / managed_cloud modes are selectable as preferences; onboarding flow not yet implemented)
- Shopify operator (caps 65–76): connector stub present; executor, registry entry, and connector_packages entry not yet implemented
- Social content operator (caps 77–82): design complete (`docs/future/NOVA_SOCIAL_CONTENT_OPERATOR_DESIGN_2026-04-21.md`); zero code

## Important Clarification About Code Structure

The session routing loop has been extracted from `brain_server.py` into `src/websocket/session_handler.py`. `brain_server.py` now handles app assembly, middleware, singleton wiring, and the WebSocket endpoint registration. All live command routing, governor invocation, and session state management lives in `session_handler.py`.

`brain_server.py` remains large due to inline payload-building helper functions (~35 identified). These are candidates for future extraction but are not architectural risk.

## Personality Layer

Nova has two personality components that coexist:
- `personality/core.py` — Phase 4.2 multi-agent deep cognition (prefix-triggered: `phase 4.2:` / `orthogonal:`)
- `personality/conversation_personality_agent.py` — Phase 8 Nova voice layer (default path for all normal turns and OpenClaw result presentation)

See `docs/reference/HUMAN_GUIDES/30_PERSONALITY_SYSTEM_ARCHITECTURE.md` for the full explanation.

## Operational Truth

What is true right now:
- execution is enabled
- the runtime is not Cap-16-only anymore
- policy review is manual-review-only
- external reasoning is advisory-only
- remote bridge access is bounded and token-gated
- wake word is still planned, not live

## Canonical Next-Layer Posture

Immediate (active sprint):
- Cap 64 P5 live signoff + lock — highest priority; first external-effect cap to be formally locked
- Installer clean-VM validation (Windows) — paused at bootstrap.log; resume when available

Next major architecture milestone:
- OpenClaw governance hardening (Steps 1–4, zero behavioral impact): `EnvelopeFactory`, `EnvelopeStore`, `OpenClawProposedAction` model, authority-rank headers — see `docs/future/NOVA_OPENCLAW_GOVERNANCE_HARDENING_2026-04-21.md`
- Steps 5–7 (approval endpoint, approval flow in robust_executor.py) must complete before Shopify Tier 4 (write) is activated

After hardening Steps 1–7:
- Shopify Tier 1 cap 65 (shopify_intelligence_report) — read-only; connector stub already present
- Social content caps 77–78 (research + draft; no publish) — reuses existing web search lane

Ongoing:
- Cleaner dependency/install truth
- Continued simplification of brain_server.py (~35 inline payload helpers are extraction candidates)

## Short Version

Nova is no longer a Cap-16 staging runtime.

It is now a governed local intelligence and home-agent system with:
- active Phases 4 through 9
- 26 active governed capabilities
- explicit settings and trust surfaces
- governed memory and continuity
- advisory-only external reasoning
- manual OpenClaw home-agent execution with strict preflight
- email draft (cap 64) as the first external-effect capability — confirmation-gated, user sends

And it still intentionally refuses:
- autonomy
- background trigger execution
- broad envelope-governed external execution without unified authority plane (hardening in progress)

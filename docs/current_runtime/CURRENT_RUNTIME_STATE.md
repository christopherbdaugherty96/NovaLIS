# NOVA - CURRENT RUNTIME STATE

Status: AUTHORITATIVE RUNTIME TRUTH
Authority Level: Runtime
Update Method: Auto-generated snapshot
Applies To: Nova Core Runtime

This document defines the exact operational state of Nova at the current commit.
All other documentation must defer to this file for runtime capability truth.
If any document conflicts with this file, this file is correct.

- Generated (UTC): 2026-03-07T04:03:27.621993+00:00
- Audit status: **FAIL**
- Execution gate enabled: True

## System Identity

Nova is a governed intelligence platform.
Execution authority exists only through the Governor Spine.
Nova is not autonomous and performs no background actions.

## Phase Status

- Current phase marker: Phase-4 runtime active
- Phase-3.5 baseline: sealed
- Future phases: design-only and not implemented in runtime

## Execution Authority Model

User -> Input Normalization -> Skill Router -> GovernorMediator -> ExecuteBoundary -> Capability Executor -> ActionResult -> Ledger

All execution authority passes through the Governor.
Conversation subsystems are text-only and non-authorizing.

## Active Capabilities

| Capability ID | Name | Description | Authority Level |
| --- | --- | --- | --- |
| 16 | governed_web_search | Governed runtime capability | read_only |
| 17 | open_website | Governed runtime capability | system_action |
| 18 | speak_text | Governed runtime capability | speech_output |
| 19 | volume_up_down | Governed runtime capability | system_action |
| 20 | media_play_pause | Governed runtime capability | system_action |
| 21 | brightness_control | Governed runtime capability | system_action |
| 32 | os_diagnostics | Governed runtime capability | system_action |

## Capability Restrictions

- No background execution
- No autonomous actions
- No persistent learning
- No scheduled task orchestration
- No multi-capability chaining inside one invocation

## Network Authority

- Outbound network access is permitted only through `NetworkMediator`.
- Skills and conversation modules may not bypass network mediation.
- Capabilities using NetworkMediator: [16, 48]

## Conversation Subsystem

- Provides formatting, clarification, escalation, and analysis.
- Cannot invoke executors directly.
- Cannot create ActionRequest objects.
- Direct LLM calls detected: deepseek_uses_ollama_chat_directly=False

## User Interface Behavior

- Orb visuals are non-semantic.
- UI may display system state but does not confer execution authority.

## Voice System

- Speech input: local STT pipeline (Vosk).
- Speech output: local invocation-bound TTS.
- No background listening.
- No unsolicited speech.

## Ledger & Audit

- Governed actions emit append-only ledger events.
- Ledger includes timestamps, capability ID, and execution result.
- Unknown ledger event types are rejected fail-closed.

## Runtime Safety Guarantees

- single_action_queue_enforced: True
- execution_timeout_guard_active: True
- dns_rebinding_protection_active: True
- ledger_logging_active: True
- execution_gate_enabled: True

## Verification Status

- Backend test suite must pass in CI (`python -m pytest -q`).
- Governance tests cover routing, mediation boundaries, and fail-closed behavior.

## Runtime Fingerprint

- Commit: e85bb68527cdcdd9b6151e128c045ab7219bacef
- Generated (UTC): 2026-03-07T04:03:27.746997+00:00
- Capabilities enabled: [16, 17, 18, 19, 20, 21, 32]
- Capabilities disabled: [22, 48]
- Execution gate: True

## Runtime Truth Discrepancies

- [hard_fail] ENABLED_ID_SET_MISMATCH: Enabled capability ID set differs between docs/current_runtime/CURRENT_RUNTIME_STATE.md and registry.json.

## Change Control

Update this document only when runtime capabilities, execution authority, or phase state changes.
Other documents must reference this file instead of redefining runtime behavior.

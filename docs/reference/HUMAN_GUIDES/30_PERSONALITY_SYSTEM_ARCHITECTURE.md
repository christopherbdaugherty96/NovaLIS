# Nova Personality System Architecture

Updated: 2026-03-30
Scope: How Nova's two personality layers coexist and which one governs normal operation

---

## Summary

Nova has two distinct personality system components. They serve different layers and are not in conflict, but the distinction is easy to miss when reading the codebase. This guide explains what each one does, when it runs, and how they relate.

---

## The Two Systems

### 1. `PersonalityAgent` — Phase 4.2 Deep Cognition Layer

**File:** `nova_backend/src/personality/core.py`

This is the Phase 4.2 multi-agent cognition personality layer. It orchestrates a set of specialist agents (adversarial, architect, assumption, builder, context, contradiction, deep_audit, memory) through `AgentOrchestrator`. It uses `DeepModeState` and `PersonalityValidator`.

**When it runs:**
- Only when a message is prefixed with `phase 4.2:` or `orthogonal:` in the WebSocket session
- Gated by `PHASE_4_2_ENABLED` (true when `BUILD_PHASE >= 5`)
- It is an expert surface, not the default conversation path
- Not invoked by ordinary user messages

**What it governs:**
- Deep structural analysis, adversarial critique, assumption auditing
- Multi-agent synthesis for complex reasoning requests
- Explicitly opt-in — the user must ask for it

---

### 2. `ConversationPersonalityAgent` — Phase 8 Nova Voice Layer

**File:** `nova_backend/src/personality/conversation_personality_agent.py`

This is the live presentation layer that shapes how Nova speaks in all normal runtime paths. It is used by:
- The OpenClaw `agent_personality_bridge.py` to present home-agent results
- The general conversation runtime for response shaping
- Any path that needs Nova's calm, direct voice applied to a result

**When it runs:**
- On every normal user turn where response shaping applies
- Inside the OpenClaw runner when presenting briefing results
- This is the default personality layer for all non-Phase-4.2 paths

**What it governs:**
- Tone: calm, direct, useful-first
- Opener phrasing by context (daily, research, agent)
- Stripping of internal worker language from agent results
- Nova-owned voice across all delivery surfaces

---

## Authority Rule

Neither personality system has execution authority. Both are presentation-only layers. They shape how Nova communicates but cannot invoke governed capabilities, write to memory, or trigger external effects.

The execution authority chain (`GovernorMediator → Governor → CapabilityRegistry → ExecuteBoundary`) is completely separate from both personality layers.

---

## Practical Guidance for Contributors

| Scenario | Which system |
|---|---|
| User sends a normal message | `ConversationPersonalityAgent` (via general_chat_runtime or session shaping) |
| OpenClaw home-agent result needs presenting | `ConversationPersonalityAgent` via `agent_personality_bridge.py` |
| User explicitly asks for deep structural analysis | `PersonalityAgent` (Phase 4.2, prefix-triggered) |
| Modifying Nova's default tone or phrasing | `ConversationPersonalityAgent` and `nova_style_contract.py` |
| Modifying multi-agent cognition behavior | `PersonalityAgent` in `core.py` and the `agents/` directory |

---

## Why Two Systems Exist

Phase 4.2 introduced a multi-agent cognition layer for deep, structured analysis. This was built as an orthogonal layer — explicitly invocation-bound and prefix-gated — so it would never interfere with normal conversation routing.

Phase 8 introduced `ConversationPersonalityAgent` as a lighter, cleaner voice layer specifically designed to work with the OpenClaw home-agent result presentation. It needed to be separate from the Phase 4.2 orchestrator because:
- OpenClaw results are pre-formed summaries, not raw LLM turns needing multi-agent critique
- The home-agent layer requires a simple, deterministic voice wrapper, not full agent orchestration
- The Phase 4.2 `PersonalityAgent` carries orchestration overhead that is unnecessary for result presentation

Both systems are correct for their respective contexts. The correct one is always `ConversationPersonalityAgent` for normal runtime and Nova voice, and `PersonalityAgent` for explicit Phase 4.2 deep cognition requests.

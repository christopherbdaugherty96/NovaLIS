# Source Directory Guide
Updated: 2026-03-13

## Purpose
This guide explains the top-level directories inside `nova_backend/src/`.

It is meant to help people find the right area of the codebase without guessing.

## Directory Guide

### `actions/`
Core request/result objects used across governed execution.

### `agents/`
Agent-related structures and older or supporting agent-layer code.

### `api/`
HTTP API route modules: bridge API, OpenClaw agent API, and related endpoint surfaces.

### `archive_quarantine/`
Quarantined or set-aside code that is not part of the primary clean runtime path.

### `audio/`
Audio-related support surfaces outside the newer `voice/` layer.

### `audit/`
Runtime audit and runtime-doc generation logic.
This is where the runtime truth generation path is anchored.

### `capabilities/`
Capability-related support structures and metadata surfaces.

### `cognition/`
Structured cognitive/reporting layer used for deeper analysis outputs.

### `config/`
Configuration files, including capability registry data.

### `connections/`
Connection management and connection-state support surfaces.

### `connectors/`
Connector package implementations and the governed connector rollout foundation.

### `context/`
Request-time environment/context snapshot services.
This is especially relevant for explain-anything and perception flows.

### `conversation/`
Conversation routing, deep-analysis bridges, style routing, and response-shaping logic.

### `debug/`
Developer/debugging support surfaces.

### `executors/`
The main capability execution layer.
Each executor handles a concrete runtime capability.

### `gates/`
Gate and boundary-related support logic.

### `governor/`
The authority spine: capability checks, execution path control, boundary enforcement, and mediation.

### `identity/`
Identity and authentication-related runtime surfaces.

### `ledger/`
Append-only event logging.

### `llm/`
Local model-management and model-network mediation surfaces.

### `memory/`
Governed memory storage and memory-related runtime logic.

### `models/`
Model-related local runtime support.

### `openclaw/`
OpenClaw home-agent integration logic: runners, runtime store, personality bridge, and diagnostics.

### `patterns/`
Pattern analysis and pattern-queue support surfaces.

### `perception/`
Screen capture, OCR, cursor-region logic, and explain-anything support modules.

### `personality/`
Presentation discipline layer for how Nova speaks and presents itself.

### `policies/`
Policy management, policy-review surfaces, and delegated trigger policy structures.

### `profiles/`
Runtime profile management and profile-switching surfaces.

### `prompts/`
Prompt-related assets and support text used by analysis paths.

### `rendering/`
Rendering logic for structured outputs such as intelligence briefs and speech formatting.

### `providers/`
Provider integration surfaces including the governed OpenAI lane and model provider routing.

### `routers/`
Request or service routing helpers outside the main conversation path.

### `services/`
Support services used by higher-level runtime behavior.

### `settings/`
Runtime settings store, settings API surfaces, and user-facing settings management.

### `skills/`
Deterministic and conversational skill handlers such as weather, news, calendar, and general chat.

### `system_control/`
The local OS-control boundary used by volume, media, brightness, and path-opening features.

### `tasks/`
Task-oriented support code.

### `tools/`
Auxiliary runtime tools and helper modules.

### `trust/`
Trust and governance support layers.

### `usage/`
Usage tracking and metered-budget accounting surfaces.

### `utils/`
Shared helper functions used across the runtime.

### `validation/`
Validation pipelines and boundary checks.

### `voice/`
Speech-to-text and text-to-speech runtime support.

### `websocket/`
WebSocket session handler and real-time connection management.

### `working_context/`
Session-scoped task understanding, project continuity, and thread-related logic.

## How To Use This Guide
If you know what kind of thing you are looking for, use this simple mapping:
- execution authority -> `governor/`
- concrete capability behavior -> `executors/`
- HTTP routes and API surfaces -> `api/`
- conversation handling -> `conversation/` and `skills/`
- OpenClaw home-agent logic -> `openclaw/`
- screen/context behavior -> `context/` and `perception/`
- continuity and project state -> `working_context/`
- durable memory -> `memory/`
- provider routing and AI lane -> `providers/`
- connector packages -> `connectors/`
- policy review -> `policies/`
- settings and runtime controls -> `settings/`
- real-time session handling -> `websocket/`
- UI-facing formatting -> `rendering/` and `personality/`
- validation and safety checks -> `validation/`, `audit/`, and tests

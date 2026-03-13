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

### `archive_phase4/`
Historical code kept for traceability from earlier Phase-4 work.

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

### `context/`
Request-time environment/context snapshot services.
This is especially relevant for explain-anything and perception flows.

### `conversation/`
Conversation routing, deep-analysis bridges, style routing, and response-shaping logic.

### `data/`
Local runtime data such as the append-only ledger.

### `debug/`
Developer/debugging support surfaces.

### `executors/`
The main capability execution layer.
Each executor handles a concrete runtime capability.

### `gates/`
Gate and boundary-related support logic.

### `governor/`
The authority spine: capability checks, execution path control, boundary enforcement, and mediation.

### `ledger/`
Append-only event logging.

### `llm/`
Local model-management and model-network mediation surfaces.

### `logs/`
Logging-related support surfaces.

### `memory/`
Governed memory storage and memory-related runtime logic.

### `models/`
Model-related local runtime support.

### `perception/`
Screen capture, OCR, cursor-region logic, and explain-anything support modules.

### `personality/`
Presentation discipline layer for how Nova speaks and presents itself.

### `prompts/`
Prompt-related assets and support text used by analysis paths.

### `rendering/`
Rendering logic for structured outputs such as intelligence briefs and speech formatting.

### `routers/`
Request or service routing helpers outside the main conversation path.

### `services/`
Support services used by higher-level runtime behavior.

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

### `utils/`
Shared helper functions used across the runtime.

### `validation/`
Validation pipelines and boundary checks.

### `voice/`
Speech-to-text and text-to-speech runtime support.

### `working_context/`
Session-scoped task understanding, project continuity, and thread-related logic.

## How To Use This Guide
If you know what kind of thing you are looking for, use this simple mapping:
- execution authority -> `governor/`
- concrete capability behavior -> `executors/`
- conversation handling -> `conversation/` and `skills/`
- screen/context behavior -> `context/` and `perception/`
- continuity and project state -> `working_context/`
- durable memory -> `memory/`
- UI-facing formatting -> `rendering/` and `personality/`
- validation and safety checks -> `validation/`, `audit/`, and tests

# Backend Runtime Guide
Updated: 2026-03-13

## Purpose
This guide explains the backend in human language.

## The Backend's Main Job
The backend is where Nova's real behavior lives.

It is responsible for:
- receiving requests
- routing them correctly
- deciding whether something is explanation-only or action-capable
- enforcing the Governor path for actions
- running analysis and reporting
- managing continuity and memory
- returning results to the dashboard or voice surface

## The Main Entry Point
The central orchestration file is:
- `nova_backend/src/brain_server.py`

At a high level, `brain_server.py` is where many different parts of Nova come together.
It coordinates:
- websocket interaction
- request routing
- continuity commands
- dashboard actions
- mediated capability calls
- output formatting

## Major Backend Areas

### `governor/`
This is the authority spine.
It includes the parts that decide whether a real action is allowed and how it should be executed safely.

### `executors/`
This is where individual capabilities actually perform their work.
There are executors for:
- search
- website opening
- local controls
- diagnostics
- reporting
- story tracking
- analysis documents
- screen capture
- screen analysis
- explain-anything
- governed memory

### `skills/`
These are the higher-level conversational and utility handlers.
They help Nova respond to common user requests such as:
- weather
- news
- calendar
- general chat

### `conversation/`
This is where conversation routing, style handling, deep analysis bridges, and higher-level response shaping live.

### `cognition/`
This is the structured analysis layer used for reports and deeper intelligence outputs.

### `working_context/`
This is where session-scoped task context and project continuity logic live.
It helps Nova understand ongoing work rather than treating every message like an isolated event.

### `memory/`
This is where governed memory storage and persistence logic live.
It is about explicit long-term preservation, not hidden passive learning.

### `perception/`
This is where screen capture, OCR, cursor-region logic, and explain-anything support modules live.

### `personality/`
This is Nova's presentation discipline layer.
It helps keep outputs readable and non-authoritarian.
It also now carries the manual Phase-5 tone profile store and response-style logic.

### `patterns/`
This is where the opt-in pattern-review queue lives.
It is advisory only and does not create a new authority path.

### `tasks/`
This is where calm scheduled updates and reminders live.
It includes explicit policy controls such as quiet hours and notification rate limits.

### `ledger/`
This is the append-only event logging surface.
It helps keep governed actions inspectable.

### `validation/`
This is where validation pipelines and output checks live.

### `voice/`
This is where speech-related support lives, including speech-to-text and text-to-speech support layers.

## Why The Backend Is Structured This Way
The backend is deliberately split so that:
- reasoning does not directly become execution
- presentation does not quietly become authority
- persistence is explicit instead of hidden
- perception remains bounded and request-time

That structure is one of Nova's biggest architectural strengths.

## Phase-5 In Code
If you want the Phase-5-specific code map, use:
- `docs/current_runtime/PHASE_5_RUNTIME_SURFACE.md`
- `docs/PROOFS/Phase-5/PHASE_5_IMPLEMENTATION_MAP_2026-03-13.md`

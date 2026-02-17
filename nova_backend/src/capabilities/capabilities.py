(active)



```
# CAPABILITY_SURFACE.md
Phase-3.5 Runtime Capability Boundary

**System:** NovaLIS  
**Phase:** 3.5 (Execution Disabled)  
**Status:** Canonical Proof Artifact  
**Purpose:** Define the complete runtime authority surface.  
**Rule:** Any capability not explicitly listed here DOES NOT EXIST in Phase-3.5.

---

## 1. System Authority Model

**Execution Authority:** Disabled  
**Execution Mechanism:** Not reachable  
**Runtime Flag:**
```

execute_action = None
```

**Consequence:**
- No tool execution
- No system actions
- No OS control
- No external command invocation
- No autonomous behavior

This is **structural prevention**, not policy restriction.

---

## 2. User Input Surface

### Primary Entry Point
| Endpoint | Type      | Authority              |
|----------|-----------|------------------------|
| `/ws`    | WebSocket | Interactive input only |

**Properties:**
- Single interactive command entry point
- All conversational input flows through this endpoint
- No alternative command interfaces exist

### Secondary Endpoints
| Endpoint        | Type     | Authority              |
|-----------------|----------|------------------------|
| `/phase-status` | HTTP GET | Read-only system state |

No modification capability.

---

## 3. Governance Layer

### GovernorMediator

Behavior:
```python
input → text.strip() → output
```

Capabilities:
- Trim whitespace
- Empty-input fallback

Restrictions:
- No routing decisions
- No tool selection
- No parameter inference
- No authority evaluation

Phase-3.5 Governor is **passive mediation only**.

---

## 4. Fast-Path Local Commands

Handled directly in `brain_server.py`.

| Command       | Action                    | Scope                     | Risk       |
|---------------|---------------------------|---------------------------|------------|
| `stop`        | `speech_state.stop()`     | Local TTS state           | Low        |
| `repeat`      | Return `last_spoken_text` | Read-only memory          | None       |
| `Correction:` | `record_correction()`     | Staged correction storage | Controlled |

**Constraints:**
- No skill invocation
- No external calls
- No execution
- Deterministic behavior
- Limited to local process state

---

## 5. Skill Capability Surface

Skills are evaluated in fixed priority order.

| Priority | Skill            | Capability Type                        |
|----------|------------------|----------------------------------------|
| 1        | SystemSkill      | Local system information (read-only)   |
| 2        | WeatherSkill     | External weather data (HTTP GET only)  |
| 3        | NewsSkill        | External RSS/news data (HTTP GET only) |
| 4        | GeneralChatSkill | LLM text response (advisory only)      |

### Skill Restrictions

All skills:
- No execution
- No file writes
- No OS control
- No subprocess creation
- No state modification
- No background tasks

External skills (Weather, News):
- Read-only HTTP requests only
- No data persistence
- No scheduled polling

GeneralChatSkill:
- Text generation only
- No tool calling
- No function execution
- No memory modification

---

## 6. External Communication Surface

| Component      | Direction | Capability           |
|----------------|-----------|----------------------|
| Weather API    | Outbound  | HTTP GET only        |
| RSS/News feeds | Outbound  | HTTP GET only        |
| LLM provider   | Outbound  | Text completion only |

No inbound connections.  
No webhooks.  
No background communication.

---

## 7. Process and System Interaction

Allowed subprocess usage:

| Component | Purpose                           |
|-----------|-----------------------------------|
| ffmpeg    | Audio conversion for STT pipeline |

Constraints:
- Deterministic invocation
- Fixed parameters
- No user-controlled command construction
- No system modification

No other subprocess usage exists.

---

## 8. Memory Surface

### Allowed
| Memory Type        | Behavior                              |
|--------------------|---------------------------------------|
| Speech state       | In-memory only                        |
| Last response      | In-memory only                        |
| Correction staging | Append-only, explicit prefix required |

### Not Present
- No persistent conversational memory
- No user profiling
- No learning
- No automatic storage
- No context inference across sessions

---

## 9. Inert / Placeholder Components (Phase‑3.5)

The following files exist in the active source tree but are **not used** in Phase‑3.5 runtime behavior. They are placeholders for future phases and do not enable execution.

| File                                     | Purpose                                                       | Why Inert in Phase‑3.5                                                              |
|------------------------------------------|---------------------------------------------------------------|--------------------------------------------------------------------------------------|
| `src/governor/single_action_queue.py`    | Single pending-action boundary container (Phase‑4+ design)    | No Phase‑3.5 component submits or executes actions; queue is not in active path.    |
| `src/governor/execution_gate.py`         | Constitutional refusal boundary for hypothetical ActionRequest| `EXECUTION_ENABLED = False`; gate always returns refusal; no ActionRequest created. |
| `src/governor/governor_mediator.py`      | Text mediation only (strip/empty fallback)                    | Pure text sanitization; no execution hooks or state.                                 |
| `src/skills/web_search_skill.py`         | Web search skill (Phase‑4 design)                             | Not imported or registered in Phase‑3.5; no runtime references.                      |
| `src/tasks/reminder_task.py`             | Reminder task placeholder (Phase‑5+ design)                   | Not imported; no background execution.                                               |

These components are **provably inert** and do not affect the capability surface.

---

## 10. Declarative Data Structures (Non‑Operational)

**Directory:** `src/actions/`

This directory contains pure data structures created during **GOV‑001** (Action Contract Integrity). These classes define the shape of future action requests and results but are **never instantiated** in Phase‑3.5 runtime.

- `action_request.py` – `ActionRequest` dataclass (with `id`, `action_type`, `title`, `payload`, `created_utc`)
- `action_result.py` – `ActionResult` dataclass with helper methods (`.refusal()`, `.failure()`, `.ok()`)
- `action_types.py` – Enumerations of action types (informational only)

**Constitutional rule:** No runtime code may instantiate these classes in Phase‑3.5. This is enforced by CI.

---

## 11. Declarative Capability Metadata (Non‑Operational)

**File:** `src/capabilities/capabilities.py`

This file defines static string identifiers representing potential future capabilities. These declarations:

- **Do not grant permission**
- **Do not enable execution**
- **Are not consulted by Phase‑3.5 runtime routing**
- **Have no runtime effect**

Example constants:
```python
CAN_OPEN_FILE = "can_open_file"
CAN_LAUNCH_APP = "can_launch_app"
CAN_CONTROL_DEVICE = "can_control_device"
CAN_VOICE_INPUT = "can_voice_input"
```

**Constitutional rule:** These strings must never be used as feature flags or branching conditions in Phase‑3.5 runtime code. Any such usage would be a violation and is blocked by CI.

---

## 12. Quarantined Execution Code (Unreachable)

All execution‑capable code is physically segregated under:

```
src/archive_quarantine/phase35_execution/
```

This directory contains:
- `execute_action.py`
- Handlers (`open_app.py`, `open_folder.py`, `volume_control.py`, etc.)
- Executor registry (`executor_registry.py`)

These files are **not importable** from the active runtime. Static CI scans confirm zero imports from this path.

**Status:** Structurally unreachable; preserved for historical reference and Phase‑4 design.

---

## 13. Explicitly Absent Capabilities

The following capabilities do **not exist** in Phase‑3.5:
- Action execution pipeline
- ActionRequest / ActionResult runtime use
- File system modification
- OS command execution
- Application launch
- Device control
- Automation or scheduling
- Background tasks
- Autonomous behavior
- Tool calling from LLM
- Parameter inference
- Intent expansion
- Self-modification
- Network listeners or inbound APIs

---

## 14. Capability Boundary Statement

Phase‑3.5 Nova is limited to:
- Receiving user text
- Deterministic routing
- Read-only information retrieval
- Advisory language generation
- Local speech state control
- Explicit correction staging

Nova **cannot** perform actions, modify the environment, or execute tools.

---

## 15. Verification Commands (CI‑Enforced)

The following static checks run in CI to maintain the Phase‑3.5 invariant boundary:

```powershell
# 1. No ActionRequest instantiation in runtime code (excluding tests/ and archive/)
Select-String -Path .\src\ -Recurse -Pattern "ActionRequest\(" | Where-Object { $_ -notmatch "tests|archive" }

# 2. No conditional branching on CAN_* constants
Select-String -Path .\src\ -Recurse -Pattern "if .*CAN_" | Where-Object { $_ -notmatch "tests|archive" }

# 3. No imports from quarantine
Select-String -Path .\src\ -Recurse -Pattern "archive_quarantine|phase35_execution" | Where-Object { $_ -notmatch "tests" }

# 4. No unexpected subprocess usage (only stt_engine.py allowed)
Select-String -Path .\src\ -Recurse -Pattern "subprocess\." | Where-Object { $_ -notmatch "stt_engine\.py|tests" }
```

All checks must return zero matches.

---

## 16. Final Boundary Declaration

**Phase‑3.5 Capability Surface: CLOSED**

- Authority Level: Read-only advisory system
- Execution Authority: None
- Autonomous Capability: None
- Environmental Impact: None

Any capability not explicitly listed in this document is constitutionally absent.

---

**Status:** Canonical  
**Phase Alignment:** 3.5  
**Purpose:** Phase‑4 unlock prerequisite
```


------------------------------------------------



"""
(phase 4 not active)

NovaLIS Capability Declarations

This file defines static capability names used to describe what an
executor *could* support in the future.

IMPORTANT:
- Capabilities do NOT grant permission
- Capabilities do NOT enable execution
- Capabilities are declarative metadata only

Phase-4 status:
- Used for documentation and future matching
- No runtime logic depends on this file
"""

# File system capabilities
CAN_OPEN_FILE = "can_open_file"
CAN_OPEN_FOLDER = "can_open_folder"

# Application control
CAN_LAUNCH_APP = "can_launch_app"

# Web / information
CAN_WEB_LOOKUP = "can_web_lookup"

# Media routing (where, not what)
CAN_ROUTE_MEDIA = "can_route_media"
CAN_STOP_MEDIA = "can_stop_media"

# Task / reminder introspection
CAN_LIST_REMINDERS = "can_list_reminders"
CAN_CANCEL_REMINDER = "can_cancel_reminder"

# Device / system control (DECLARED ONLY — NOT ENABLED)
CAN_CONTROL_DEVICE = "can_control_device"

# Voice I/O (DECLARED ONLY — NOT ENABLED)
CAN_VOICE_INPUT = "can_voice_input"
CAN_VOICE_OUTPUT = "can_voice_output"

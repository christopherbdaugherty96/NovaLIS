
---

# docs/PROOFS/phase 3.5-4/CAPABILITY_SURFACE.md

```
# CAPABILITY_SURFACE.md
Phase-3.5 Runtime Capability Boundary

System: NovaLIS
Phase: 3.5 (Execution Disabled)
Status: Canonical Proof Artifact
Purpose: Define the complete runtime authority surface.
Rule: Any capability not explicitly listed here DOES NOT EXIST in Phase-3.5.
```

---

## 1. System Authority Model

**Execution Authority:** Disabled
**Execution Mechanism:** Not reachable
**Runtime Flag:**

```
EXECUTION_ENABLED = False
execute_action = None
```

**Consequence**

* No tool execution
* No system actions
* No OS control
* No external command invocation
* No autonomous behavior

This is structural prevention, not policy restriction.

---

## 2. User Input Surface

### Primary Entry Point

| Endpoint | Type      | Authority              |
| -------- | --------- | ---------------------- |
| `/ws`    | WebSocket | Interactive input only |

**Properties**

* Single interactive command entry point
* All conversational input flows through this endpoint
* No alternative command interfaces exist

---

### Secondary Endpoints

| Endpoint        | Type     | Authority              |
| --------------- | -------- | ---------------------- |
| `/phase-status` | HTTP GET | Read-only system state |

No modification capability.

---

## 3. Governance Layer

### GovernorMediator

Behavior:

```
input → text.strip() → output
```

Capabilities:

* Trim whitespace
* Empty-input fallback

Restrictions:

* No routing decisions
* No tool selection
* No parameter inference
* No authority evaluation

Phase-3.5 Governor is **passive mediation only**.

---

## 4. Fast-Path Local Commands

Handled directly in `brain_server.py`.

| Command       | Action                    | Scope                     | Risk       |
| ------------- | ------------------------- | ------------------------- | ---------- |
| `stop`        | `speech_state.stop()`     | Local TTS state           | Low        |
| `repeat`      | Return `last_spoken_text` | Read-only memory          | None       |
| `Correction:` | `record_correction()`     | Staged correction storage | Controlled |

**Constraints**

* No skill invocation
* No external calls
* No execution
* Deterministic behavior
* Limited to local process state

---

## 5. Skill Capability Surface

Skills are evaluated in fixed priority order.

| Priority | Skill            | Capability Type                        |
| -------- | ---------------- | -------------------------------------- |
| 1        | SystemSkill      | Local system information (read-only)   |
| 2        | WeatherSkill     | External weather data (HTTP GET only)  |
| 3        | NewsSkill        | External RSS/news data (HTTP GET only) |
| 4        | GeneralChatSkill | LLM text response (advisory only)      |

---

### Skill Restrictions

All skills:

* No execution
* No file writes
* No OS control
* No subprocess creation
* No state modification
* No background tasks

External skills (Weather, News):

* Read-only HTTP requests only
* No data persistence
* No scheduled polling

GeneralChatSkill:

* Text generation only
* No tool calling
* No function execution
* No memory modification

---

## 6. External Communication Surface

| Component      | Direction | Capability           |
| -------------- | --------- | -------------------- |
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
| --------- | --------------------------------- |
| ffmpeg    | Audio conversion for STT pipeline |

Constraints:

* Deterministic invocation
* Fixed parameters
* No user-controlled command construction
* No system modification

No other subprocess usage exists.

---

## 8. Memory Surface

### Allowed

| Memory Type        | Behavior                              |
| ------------------ | ------------------------------------- |
| Speech state       | In-memory only                        |
| Last response      | In-memory only                        |
| Correction staging | Append-only, explicit prefix required |

### Not Present

* No persistent conversational memory
* No user profiling
* No learning
* No automatic storage
* No context inference across sessions

---

## 9. Explicitly Absent Capabilities

The following capabilities do **not exist** in Phase-3.5:

* Action execution pipeline
* ActionRequest / ActionResult runtime use
* File system modification
* OS command execution
* Application launch
* Device control
* Automation or scheduling
* Background tasks
* Autonomous behavior
* Tool calling from LLM
* Parameter inference
* Intent expansion
* Self-modification
* Network listeners or inbound APIs

---

## 10. Capability Boundary Statement

Phase-3.5 Nova is limited to:

* Receiving user text
* Deterministic routing
* Read-only information retrieval
* Advisory language generation
* Local speech state control
* Explicit correction staging

Nova cannot perform actions, modify the environment, or execute tools.

---

## 11. Verification Commands

Example static verification:

```
Select-String -Recurse -Pattern "execute_action"
Select-String -Recurse -Pattern "EXECUTION_ENABLED"
Select-String -Recurse -Pattern "@app.websocket"
Select-String -Recurse -Pattern "subprocess"
```

Expected results:

* Execution disabled
* Single WebSocket entry
* Only STT-related subprocess usage

---

## 12. Final Boundary Declaration

**Phase-3.5 Capability Surface: CLOSED**

* Authority Level: Read-only advisory system
* Execution Authority: None
* Autonomous Capability: None
* Environmental Impact: None

Any capability not explicitly listed in this document is constitutionally absent.

---

**Status:** Canonical
**Phase Alignment:** 3.5
**Purpose:** Phase-4 unlock prerequisite

```

---

# Architect Verdict

If you add this file, your Phase-3.5 proof set becomes **complete and auditor-grade**:

You will then have:

- Execution proof  
- Routing proof  
- Bypass proof  
- Static audit  
- Capability boundary  

That combination is what actually closes Phase-3.5.

---


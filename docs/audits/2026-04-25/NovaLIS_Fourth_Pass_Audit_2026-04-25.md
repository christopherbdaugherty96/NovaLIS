# NovaLIS Fourth Pass Audit — 2026-04-25

Scope: Security surface, LLM version locking, OpenClaw thinking loop internals, CI platform gap, pyproject.toml dependency correctness, remaining module survey.

Predecessor: [Third Deep Wide Audit (2026-04-25)](NovaLIS_Third_Deep_Wide_Audit_2026-04-25.md)

---

## Summary

The security surface is solid for the local trust model Nova has chosen. DNS rebinding protection is real and enforced at the HTTP middleware layer. There is no CORS and no API authentication — both intentional for a local-only application that binds to loopback. LLM version locking uses SHA256-based hash comparison with inference blocking on mismatch — a meaningful architectural control. The OpenClaw thinking loop is well-structured and appropriately bounded.

One real gap: **CI runs on ubuntu-latest only.** Nova is documented as Windows-primary. Platform-specific executors (brightness, media controls, file system paths) will silently pass or skip on Ubuntu, creating false confidence in test coverage for the platform that ships to users. This is a Tier 2 gap — not a launch blocker, but should be added to the known-gap register.

Piper is absent from `pyproject.toml` dependencies, which is correct and consistent with how Piper ships (separate binary), but it must remain clearly documented for users.

No new hot-path files found in the remaining module survey. Only 3 TODOs across the entire source.

---

## Security Surface

### DNS Rebinding Protection

**File**: `nova_backend/src/utils/local_request_guard.py` (88 lines)

Implemented and real. The guard enforces:

```python
_ALLOWED_LOOPBACK_HOSTS = {"localhost", "127.0.0.1", "::1", "testserver"}
_LOCAL_ONLY_API_PREFIXES = (
    "/api/memory", "/api/settings", "/api/workspace", "/api/openclaw/agent"
)
```

Sensitive API prefixes are rejected at HTTP middleware if the Host or Origin header is not in the allowed loopback set. `testserver` is included specifically for pytest's ASGI test client.

**Middleware wiring** — `brain_server.py` lines 180–188 registers `_enforce_local_http_boundary` as an HTTP middleware. Returns 403 on violation. This fires before any route handler.

### No CORS Middleware

Confirmed by source search: no `CORSMiddleware`, no `add_middleware` call with CORS in `brain_server.py`. This is intentional — cross-origin access from a browser on a different origin should not be possible.

### No API Authentication

Also intentional. Nova is a local single-user application binding to 127.0.0.1. There is no multi-user or network-exposed surface in the current design. The threat model is: attacker must already have local code execution, at which point API auth provides no meaningful barrier.

This choice is reasonable given the stated scope. It becomes a gap if Nova is ever run on a non-loopback interface — `NOVA_HOST` can override the default, and that override is currently undocumented in user-facing guides.

### WebSocket Rebinding Check

`brain_server.py` includes a `describe_websocket_rebinding_violation` helper. WebSocket upgrade requests also pass through the local request guard.

### main() Default Binding

```python
host = os.environ.get("NOVA_HOST", "127.0.0.1")
port = int(os.environ.get("NOVA_PORT", 8000))
```

Defaults are safe. `NOVA_HOST` and `NOVA_PORT` are real runtime overrides, but neither is mentioned in QUICKSTART.md. Not a security issue with default usage; worth adding as a Troubleshooting note for advanced users.

---

## LLM Version Locking

**File**: `nova_backend/src/llm/llm_manager.py`

The version lock uses a SHA256 hash computed over:
- model digest
- inference parameters
- system prompt

Hash is stored in `models/current_model_hash.txt`. On startup and before inference, the manager computes the hash and compares. If mismatched, `inference_blocked = True`. Inference calls will fail-closed rather than silently degrading.

This is a real architectural control. It prevents model substitution without developer awareness, and it catches unintentional model swaps (e.g., `ollama pull` updating a tag). The cost is that legitimate upgrades require an intentional hash update, which is the correct tradeoff for a governed system.

Fallback model support is present but also goes through the same locking mechanism.

---

## OpenClaw Thinking Loop

**File**: `nova_backend/src/openclaw/thinking_loop.py`

`ThinkingLoop` is a well-structured async class. Execution path:

```
async run(goal)
  → _reason()              # LLM reasoning step, produces plan
  → _select_tools()        # maps plan to available tool registry
  → _extract_params()      # validates and extracts arguments
  → execute                # dispatches through capability path
  → _should_terminate()    # checks stopping conditions
  → _synthesize()          # produces final answer
```

Supporting helpers:
- `_heuristic_done()` — early-exit if goal appears satisfied without full loop count
- `_parse_tool_list()` — parses LLM output into structured tool calls
- `_parse_json_object()` — extracts JSON from free-text LLM output

The loop is bounded (max iteration count), fails-closed on parse errors, and routes execution through the capability system rather than bypassing it. The separation of `_reason()` → `_select_tools()` → `_extract_params()` → execute is a correct factoring — it keeps the "what to do" step separate from the "how to invoke" step.

---

## CI Platform Gap

**File**: `.github/workflows/ci.yml`

Current configuration:
- Runner: `ubuntu-latest` only
- Python: `3.10` only
- Steps: ruff lint → pytest with `PYTHONPATH=nova_backend`

**Gap**: Nova is documented as Windows-primary. The following platform-specific surface areas exist in the codebase:
- Brightness control (Windows API calls)
- Media controls (Windows media key dispatch)
- File system paths (Windows path separator assumptions in some resolvers)
- Piper TTS (Windows binary expected by default)
- Voice STT (Vosk model path conventions)

These tests will either skip silently or pass trivially on Ubuntu. Platform-specific executors will not exercise their actual code paths in CI. This means CI can pass green while Windows-specific regressions accumulate.

**Classification**: Known gap, Tier 2 — not a launch blocker, but should be in the risk register.

**Recommendation**: Add a `windows-latest` runner job to the CI matrix. At minimum, the Windows job should run the adversarial test suite and any capability executor tests that invoke platform-specific paths. The ubuntu job can continue to cover lint and platform-agnostic tests.

---

## pyproject.toml Dependency Correctness

`vosk` is listed in dependencies — correct, it is the STT engine loaded at import time.

`piper` is **not** listed — also correct. Piper is a compiled binary distributed separately; it is not a Python package. This is consistent with the voice gap documented in prior passes. The absence from pyproject.toml does not indicate an oversight — it is the right representation of how Piper is distributed.

`pip install -e .` will not install Piper. This is documented in QUICKSTART.md (optional feature requirements table) and USER_READY_STATUS.md (voice setup section). Documentation is current and correct.

---

## Remaining Module Survey

Modules not previously reviewed:

| Module | Key File | Lines | Notes |
|---|---|---|---|
| `tasks/` | `notification_schedule_store.py` | 589 | Largest in tasks; notification scheduling state |
| `tasks/` | `reminder_task.py` | 34 | Simple reminder task wrapper |
| `usage/` | `provider_usage_store.py` | 267 | Provider usage tracking; normal size |
| `rendering/` | `intelligence_brief_renderer.py` | 522 | Daily brief rendering; appropriately sized |
| `rendering/` | `speech_formatter.py` | 42 | Speech output formatting; small |
| `connections/` | `connections_store.py` | 298 | Connection state management; normal size |
| `identity/` | `nova_self_awareness.py` | 229 | Self-description and capability surface; normal size |
| `patterns/` | `pattern_review_store.py` | 413 | Pattern review state; normal size |

No new hot-path candidates. The four already on the watch list (brain_server.py, session_handler.py, general_chat.py, path_resolver.py) remain the only files requiring careful handling before refactor.

`notification_schedule_store.py` at 589 lines is the largest newly-surveyed file. Worth monitoring if task scheduling grows in scope, but not a complexity risk at current size.

**TODO count**: 3 across entire source, all pre-existing. No new accumulation detected.

---

## Findings Summary

| Finding | Severity | Status | Home |
|---|---|---|---|
| CI runs ubuntu-latest only; Nova is Windows-primary | Medium | Known gap | `Now.md` active blockers |
| `NOVA_HOST` / `NOVA_PORT` overrides undocumented | Low | Documentation gap | `QUICKSTART.md` troubleshooting |
| DNS rebinding protection is real and enforced | Confirmed strength | N/A | `ARCHITECTURE.md` |
| LLM version locking via SHA256 is real | Confirmed strength | N/A | `ARCHITECTURE.md` |
| Piper absence from pyproject.toml is intentional | Confirmed correct | N/A | `QUICKSTART.md` already covers |
| No new hot-path files found | Clean | N/A | Watch list unchanged |
| Only 3 TODOs across source | Clean | N/A | — |

---

## What to Apply

1. Add CI Windows runner gap to `Now.md` active blockers (Tier 2, after Cap 64 and bootstrap.log).
2. Add `NOVA_HOST` / `NOVA_PORT` note to `QUICKSTART.md` troubleshooting section.
3. No changes needed to architecture or governance files — security surface findings are confirmations, not gaps.

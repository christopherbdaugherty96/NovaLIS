# NovaLIS Third Deep Wide Audit

**Date:** 2026-04-25
**Type:** Code-grounded read-only audit — executors, routing, tests, voice, connectors, skills, ledger, security surface
**Scope:** Areas not deeply examined in prior passes. Prior audits covered governance spine, registry, trust stub, hot-path size, OpenClaw hardening, installer, and roadmap.
**Authority:** Snapshot. Runtime truth docs and Now.md are authoritative for live status.

---

## 1. Executive Summary

This pass is the most positive of the three. Several prior audit concerns are confirmed stronger than implied. Three new findings are material. Nothing found that changes the overall verdict, but the picture is now substantially more complete.

**Confirmed stronger than previously implied:**
- Test-to-source ratio is excellent (1.11:1 by files, 1.10:1 by lines).
- Adversarial test suite is comprehensive, well-documented, and covers attack surfaces that most projects skip.
- Ledger is truly append-only with no delete paths in the source.
- Source code is extremely clean — only 3 TODO/FIXME comments across 8,132 lines.
- Network bypass exemptions are explicitly documented in tests, not silent holes.

**New material findings:**
1. The email connector (`src/connectors/email_connector.py`) is a stub — inbox reading is not implemented. Cap 64 (send_email_draft via `mailto:`) is real; inbox access is not.
2. Voice requires more setup than runtime docs imply — Piper binary and model file must be present and configured; STT requires a local Vosk model at a specific path.
3. `src/utils/path_resolver.py` at 876 lines is the largest utility file and was never flagged as a complexity watch point.

---

## 2. Test Suite — Stronger Than Prior Audits Implied

### File and line counts

| Dimension | Source | Tests | Ratio |
|---|---:|---:|---|
| Files (.py) | 255 | 284 | 1.11:1 test:source |
| Lines | 8,132 | 8,910 | 1.10:1 test:source |

The MasterRoadMap cited "234 test files vs 247 source files" at the 2026-04-15 audit. Both have grown. The ratio has stayed healthy.

### Adversarial suite (14 files, 828 lines)

`tests/adversarial/` covers attack surfaces that go well beyond standard unit tests:

| Test | What it enforces |
|---|---|
| `test_concurrency_one_enforced.py` | Max one execution at a time via ExecuteBoundary |
| `test_conversation_non_authorizing.py` | Conversation path cannot dispatch governed actions |
| `test_execute_boundary_timeouts_fail_closed.py` | Boundary closes on timeout, not returns partial |
| `test_executor_import_surface.py` | Executors cannot import governor, gates, or ActionRequest creation |
| `test_governor_bypass.py` | No path to execution bypassing GovernorMediator |
| `test_import_surface_integrity.py` | Module import graph integrity |
| `test_ledger_failure.py` | Ledger write failures do not surface to callers |
| `test_no_direct_network_imports_outside_network_mediator.py` | Network libs confined to NetworkMediator and documented exemptions |
| `test_no_dynamic_exec_eval.py` | No `eval`/`exec` in governor, executors, or gates |
| `test_no_multi_capability_chain.py` | One capability per request, no chaining |
| `test_recursive_action_request_is_impossible.py` | Executors cannot create new ActionRequests |
| `test_search_injection_no_escalation.py` | Search results cannot elevate to execution authority |
| `test_tts_spine_integrity.py` | TTS path integrity |

Each test file opens with a `"""Goal:"""` docstring stating exactly what it is protecting. This is well-maintained.

### Network bypass — documented exemptions, not holes

`test_no_direct_network_imports_outside_network_mediator.py` has an explicit `ALLOWED_NETWORK_IMPORT_FILES` set with inline comments for each exemption:

- `network_mediator.py` — the gatekeeper itself
- `llm/llm_manager.py`, `llm/llm_manager_vlock.py`, `llm/model_network_mediator.py` — local LLM inference
- `utils/local_request_guard.py` — uses `urllib.parse` for DNS rebinding check only, no outbound calls
- `api/connections_api.py` — user-initiated key health-check pings only, not intelligence calls
- `openclaw/task_envelope.py` — uses `urllib.parse` for URL hostname extraction, no outbound calls

All exemptions are documented with rationale. This is not a governance gap; it is an explicitly governed carve-out.

### Code cleanliness

Only **3 TODO/FIXME** comments in 8,132 lines of source — all in `src/base_skill.py` referencing a `DEBUG_MODE` check, not incomplete work. Extremely clean for a codebase of this complexity.

No `eval()` or `exec()` calls anywhere in the authority paths (`governor/`, `executors/`, `gates/`). Dynamic imports via `importlib.import_module` are confined to optional platform-specific dependencies (pygetwindow, pyautogui, pytesseract, pyttsx3, PIL) that fail gracefully when absent.

---

## 3. Ledger — Append-Only Confirmed

`src/ledger/writer.py` (39 lines):

```python
with open(self.path, "a", encoding="utf-8") as f:
    f.write(json.dumps(entry) + "\n")
```

Mode is `"a"` (append). No `os.remove`, `shutil.rmtree`, `unlink`, or `truncate` calls exist anywhere in `src/ledger/`. The reader (`reader.py`, 43 lines) is read-only. The append-only claim holds under code inspection.

---

## 4. Voice System — More Setup Than Implied

Runtime docs say "Voice System: Active." This is technically accurate but understates the dependency surface.

### Speech-to-text (input)

- Engine: Vosk (`src/services/stt_engine.py`, 227 lines)
- Required path: `models/vosk-model-small-en-us-0.15/` relative to `nova_backend/`
- If the model directory is absent: STT fails at import time — no graceful degradation at the language model load step
- `stt_pipeline.py` (16 lines) is a lightweight ack-payload builder, not the STT pipeline itself

### Text-to-speech (output)

- Primary engine: Piper CLI (`src/voice/tts_engine.py`, 417 lines)
- Required: Piper binary at `tools/piper/piper.exe` or in system PATH
- Required: `NOVA_PIPER_MODEL_PATH` env var pointing to a valid `.onnx` model file
- Fallback engine: pyttsx3 (lazy `importlib.import_module`) — available on Windows without config
- If neither is present: TTS degrades silently but speak_text capability produces no audio output

### Practical implication

The voice system requires:
1. Vosk model downloaded and placed at the correct path
2. Piper binary installed (not in pyproject.toml dependencies)
3. `NOVA_PIPER_MODEL_PATH` set to a valid model file

None of this is automated by the current installer. The Quickstart does not mention voice setup steps. A user who tries `speak_text` after a standard install will get either silent failure or pyttsx3 fallback without understanding why.

**Recommended:** Add a voice-setup section to the Quickstart, or add a `voice status` diagnostic command that reports which engines are found and what is missing.

---

## 5. Email Connector — Stub, Not Implemented

`src/connectors/email_connector.py` (174 lines) opens with:

```
Status: STUB — not yet connected.
The `inbox_check` template in the agent runner is currently blocked until a
compliant implementation of this interface is provided.
```

The file defines a clean abstract interface (`EmailConnector`, `EmailMessage`, `EmailInboxSummary`, `EmailConnectorError`) and a singleton registry (`get_email_connector`, `set_email_connector`). It is well-designed. Nothing is implemented.

**This is separate from cap 64 (`send_email_draft`).** Cap 64 uses `os.startfile` with a `mailto:` URI — it opens the system mail client, no email connector is involved. Cap 64 is real. Inbox reading is not.

The `inbox_check` OpenClaw home-agent template is explicitly blocked pending a real connector implementation.

**This finding should be surfaced in USER_READY_STATUS.md.** Currently that doc does not distinguish "email drafting works" from "email inbox access works."

---

## 6. Connectors — Actual State

Three connectors registered in `connector_packages.json`:

| ID | Integration mode | Auth | Capability | Status |
|---|---|---|---|---|
| `ics_calendar` | Local `.ics` file read | None — local file path | cap 57 | Real, requires ICS file path configured |
| `rss_news` | Read-only RSS feeds | None | caps 49, 50, 56 | Real, no credentials needed |
| `shopify` | Shopify GraphQL Admin API | `NOVA_SHOPIFY_SHOP_DOMAIN` + `NOVA_SHOPIFY_ACCESS_TOKEN` | cap 65 | Real, routes through NetworkMediator |

The email connector is **not** in `connector_packages.json` — consistent with its stub status.

`shopify_connector.py` confirmed routing all network I/O through `NetworkMediator`:
```python
from src.governor.network_mediator import NetworkMediator, NetworkMediatorError
...
mediator = NetworkMediator()
```

---

## 7. Skills Architecture

Five active skills (excluding `executor_adapter.py` bridge):

| File | Lines | Role |
|---|---:|---|
| `general_chat.py` | 1,891 | Primary conversation handler — imports memory, personality, LLM, NetworkMediator |
| `news.py` | 361 | RSS-backed headline surfaces |
| `calendar.py` | 287 | ICS calendar snapshot |
| `web_search.py` | 127 | Governed web search skill wrapper |
| `weather.py` | 127 | Weather snapshot |
| `system.py` | 75 | System status and diagnostics |

`general_chat.py` is 1,891 lines — the largest skill by a wide margin. It is the primary conversation handler and imports memory stores, personality layer, LLM gateway, and NetworkMediator directly. This is architecturally sound (skills are allowed to access these surfaces) but it is a growing file to watch. It is not yet a refactor candidate by the Tier 3 criteria, but it is approaching the size at which changes require care.

The adversarial test `test_no_skill_executes_capabilities.py` (in `tests/governance/`) enforces that skills do not execute capability dispatches directly.

---

## 8. Executor Coverage — All 27 Registry Caps Have Executors

Cross-check between registry capabilities and executor files:

All 27 active capabilities have a corresponding executor file in `src/executors/`. The two largest executors are:

| Executor | Lines | Notes |
|---|---:|---|
| `os_diagnostics_executor.py` | 1,546 | Largest executor — reads registry, topology, runtime docs for diagnostics |
| `news_intelligence_executor.py` | 1,545 | Second largest — multi-path news intelligence surface |

`os_diagnostics_executor.py` is in the `GOVERNOR_READ_ALLOWLIST` in the adversarial test — it reads from `capability_registry` and `capability_topology` for diagnostic reporting only, not for dispatch. This is explicitly documented.

---

## 9. Conversation Routing

`src/conversation/` is a well-decomposed 17-file module (2,708 total lines):

- `conversation_router.py` (367 lines) — deterministic pre-routing by pattern matching
- `meta_intent_handler.py` (696 lines) — handles meta-questions ("what can you do", "how do you work")
- `session_router.py` (171 lines) — routes between conversation modes
- `response_style_router.py` (271 lines) — determines response style
- `complexity_heuristics.py` (182 lines) — determines if a request needs deep analysis
- `escalation_policy.py` (104 lines) — controls when to escalate to the deep analysis bridge

The conversation layer is properly non-authorizing. The router uses regex pattern matching to classify intent before it reaches the governor. `test_conversation_non_authorizing.py` in the adversarial suite enforces this.

---

## 10. path_resolver.py — Unreviewed Complexity

`src/utils/path_resolver.py` at **876 lines** is the largest utility file and has not appeared in any prior audit. It is larger than the governor_mediator.py (1,424 lines) but approaches it in size for a utility module. Prior audits named only `brain_server.py` and `session_handler.py` as complexity watch points.

This file should be reviewed before Tier 3 refactor work begins to determine whether path resolution logic has accumulated in ways that affect testability or correctness.

---

## 11. NovaLIS-Governance/ — Duplication Risk

`NovaLIS-Governance/STATUS.md` (updated 2026-04-21) contains a governance-facing runtime summary: phase states, authority model, capability surface. This covers the same ground as `docs/current_runtime/CURRENT_RUNTIME_STATE.md`.

The STATUS.md itself says: "If there is ever a conflict between this file and the runtime truth packet, the runtime truth packet wins." The generated runtime docs are authoritative. But the NovaLIS-Governance/ folder is manually maintained and will drift as capabilities change.

This is not currently a problem because CURRENT_RUNTIME_STATE.md is generated and authoritative. It becomes a problem when someone reads NovaLIS-Governance/STATUS.md as current truth — which its format invites.

---

## 12. Complete Risk Register (Third Pass Additions)

New risks found in this pass, ordered by severity:

| Risk | Severity | Finding |
|---|---|---|
| Voice setup not documented in Quickstart | High | Users attempting voice features after standard install will get silent failure or pyttsx3 fallback without explanation |
| Email connector is a stub — inbox reading not implemented | Medium | USER_READY_STATUS.md does not distinguish send_email_draft (real) from inbox access (not implemented) |
| `general_chat.py` at 1,891 lines | Medium | Largest skill; approaching complexity threshold; not yet Tier 3 but worth tracking |
| `path_resolver.py` at 876 lines unreviewed | Medium | Largest utility file; never audited; should be reviewed before Tier 3 refactor |
| NovaLIS-Governance/STATUS.md manual drift risk | Low | Duplicates runtime truth; will diverge as capabilities change |
| ICS calendar requires explicit file path config | Low | Not documented in Quickstart or USER_READY_STATUS.md |

---

## 13. What Was Confirmed Solid This Pass

- **Ledger is truly append-only** — verified by code, no delete paths exist.
- **Adversarial test suite is comprehensive** — 14 tests covering attack vectors most projects skip, each with explicit goal documentation.
- **Network bypass exemptions are documented in tests** — not silent holes; each exemption has a rationale comment.
- **No eval/exec in authority paths** — confirmed by code scan and adversarial test.
- **Executor import surface is bounded** — executors cannot import governor, gates, or ActionRequest creation; enforced by adversarial test.
- **Shopify connector routes through NetworkMediator** — confirmed in source.
- **Only 3 TODOs in 8,132 source lines** — extremely clean.
- **Test-to-source ratio 1.11:1** — healthy and maintained as the codebase grows.
- **Email connector is a stub, not a silent failure** — explicitly documented with interface contract for future implementation.

---

## 14. Recommended Updates From This Pass

1. **USER_READY_STATUS.md** — distinguish `send_email_draft` (cap 64, real, via mailto:) from inbox reading (email connector, stub, not yet implemented).
2. **Quickstart or voice setup doc** — document the Piper binary, model file, and Vosk model requirements before voice features are reachable.
3. **Watch list addition** — add `general_chat.py` (1,891 lines) and `path_resolver.py` (876 lines) to the known hot-path watch list alongside `brain_server.py` and `session_handler.py`.
4. **NovaLIS-Governance/STATUS.md** — add a clear note that this file is manually maintained and may lag behind `docs/current_runtime/`; link directly to the generated docs for authoritative state.
5. **ICS calendar setup** — add a note to Quickstart or USER_READY_STATUS.md that calendar_snapshot requires a configured ICS file path.

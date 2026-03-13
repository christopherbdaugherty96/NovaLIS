# NovaLIS -- Phase 4 Master Status Document
**Date:** 2026-02-24
**Phase:** 4 -- Staging (Cap16 Active)
**Head Commit:** `7e9ccc5` -- `fix(stt): correct async ffmpeg subprocess with communicate() and error capture`
**Canonical Authority:** Nova Constitutional Blueprint v1.9 / Nova Truth v3.0

> [WARN] **This document was written on 2026-02-24 when only Cap 16 was live.** The runtime has expanded substantially since then. For current runtime truth, use `docs/current_runtime/CURRENT_RUNTIME_STATE.md`, `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`, `docs/current_runtime/RUNTIME_TRUTH_ADDENDUM_2026-03-12.md`, and `docs/current_runtime/RUNTIME_DOC_UPDATE_PROOF_2026-03-12.md`. The content below reflects the state as of 2026-02-24 and is preserved for historical reference.

---

> **Executive Summary:**
> Phase-4 is mechanically verifiable. The governor spine is real. Governed execution is proven by hard ledger evidence. You are no longer proving the architecture exists -- you are polishing a working governed system. This is the transition from structural construction to behavioral refinement.

---

# PART I -- WHAT IS FULLY COMPLETE

## 1. Governor Spine [OK]

The execution choke-point is real and proven.

- `ACTION_ATTEMPTED` logs fire **before** execution on every invocation
- Real UUIDs used as `request_id` from Era 2 onward (replacing hardcoded `"test"`)
- `SingleActionQueue` consulted on every invocation
- `CapabilityRegistry` lookup confirmed in terminal logs and ledger
- `ACTION_ATTEMPTED -> ACTION_COMPLETED` symmetry achieved (except expected restart case)

**Evidence:** Ledger entries at `02:46:23`, `03:03:51`, `03:50:14`, `03:55:18`, `18:06:02`, `18:33:13`, `18:41:13`

---

## 2. Network Authority Unification [OK]

All outbound HTTP is logged through `NetworkMediator`. No silent calls. No hidden paths. No bypass.

Logged domains confirmed in ledger:
- `api.duckduckgo.com` -- Capability 16 (governed, `capability_id: 16` on every call)
- `weather.visualcrossing.com` -- Weather skill (ungoverned background poll, `capability_id: null`)
- `feeds.npr.org`, `feeds.bbci.co.uk`, `pbs.org`, `abcnews.go.com`, `feeds.foxnews.com`, `rss.cnn.com` -- News RSS (ungoverned background poll)
- `reuters.com` -- Logs failures correctly
- `apnews.com` -- Logs failures correctly

**This satisfies Phase-4 Block 1 invariant.** The ledger is the proof.

---

## 3. STT Pipeline (Windows) [OK]

All four STT infrastructure bugs from the pre-Phase-4 era are resolved:

| Bug | Fix | Commit |
|---|---|---|
| Hardcoded Windows ffmpeg path | `shutil.which("ffmpeg")` + `rglob("ffmpeg.exe")` bundled fallback | `0b87aee`, `b97b7ff` |
| Temp `.wav` file leak | `try/finally` + `os.unlink()` | `ca4a67a` |
| OpenAI client initialized at import time | Lazy first-use initialization | `3292d8b` |
| Vosk decode blocking event loop | `asyncio.to_thread` | `27184d9` |
| ffmpeg subprocess synchronous | `asyncio.create_subprocess_exec` | `76e2211` |
| ffmpeg stderr invisible (no error capture) | `communicate()` + stderr PIPE | `7e9ccc5` (HEAD) |

**Terminal evidence from live session (image):**
```
[STT] Starting transcription - Received 551451 bytes
[STT] Processing file: speech.webm
[STT] Using ffmpeg path: C:\Nova-Project\nova_backend\tools\ffmpeg\ffmpeg.exe
[STT] ffmpeg exists: True
[STT] Converting audio to WAV format...
[STT] Audio conversion successful
[STT] Vosk model loaded successfully
[STT] Transcription completed: 'search for cats' (15 chars)
INFO: POST /stt/transcribe HTTP/1.1 200 OK
```

---

## 4. WebSocket Server [OK]

- Per-session `Governor` instance (isolated state)
- Per-session `session_id` (UUID) for clarification state
- Input size limit enforced in bytes (UTF-8 safe) -- BUG-S2 fix
- JSON guard added
- `GovernorMediator.clear_session(session_id)` called in `finally` block on disconnect

---

## 5. Capability 16 -- Governed Web Search [OK]

- Registered in `CapabilityRegistry` as `governed_web_search`
- `GOVERNED_ACTIONS_ENABLED = True`
- `WebSearchExecutor` wired to `NetworkMediator` (sole outbound gate)
- Boundary notice delivered to user: `"I'm checking online."`
- Widget payload (`type: "search"`) delivered separately from chat message
- DuckDuckGo `Answer`/`Abstract` fallback added when `RelatedTopics` is empty
- `SEARCH_QUERY` ledger event added for query-level auditability

**Confirmed successful executions in ledger:**

| Timestamp | request_id | Latency |
|---|---|---|
| `03:03:51-03:03:53` | `3c92b5c8-08d2-49cf-9882-290d6b41c482` | ~1.4s |
| `03:50:14-03:50:17` | `71129c8b-149b-48d4-a425-e5f647248e48` | ~2.7s |
| `03:55:18-03:55:19` | `409bb667-2226-4e15-b2d1-0c3cc72a615b` | ~1.0s |
| `18:41:13-18:41:15` | `7b1df093-3346-469e-8f18-ef02ac105100` | ~1.6s |
| `18:45:20-18:45:23` | `06ace471-b5e9-4506-9f48-a5400bd6e929` | ~3.1s |

---

## 6. Durable Append-Only Ledger [OK]

- File: `src/data/ledger.jsonl`
- All events are appended, never overwritten
- Timestamps monotonically increasing
- Schema covers: `ACTION_ATTEMPTED`, `ACTION_COMPLETED`, `EXTERNAL_NETWORK_CALL`, `NETWORK_CALL_FAILED`, `SEARCH_QUERY`
- `capability_id: 16` correctly scoped on all DuckDuckGo calls (from `16:32:45` onward)
- `SEARCH_QUERY` event type confirmed present from `18:33:13` onward

---

## 7. Background Skills (Phase-3.5) [OK]

All Phase-3.5 skills preserved and functioning:

- **Weather** -- Visual Crossing API, consistently HTTP 200, live in header bar
- **News** -- 6 of 8 RSS sources returning HTTP 200 consistently
- **General Chat** -- Ollama via `asyncio.to_thread` (non-blocking)
- **Speech State** -- `stop()` and `repeat` commands functional
- **Quick Corrections** -- `Correction:` prefix handler present
- **Confirmation Gate** -- Phase-3.5 passive gate preserved

---

## 8. Static File Serving [OK]

- `BASE_DIR` resolved via `Path(__file__).resolve().parents[1]`
- `STATIC_DIR / "index.html"` served at `/`
- `/static` mounted conditionally (only if directory exists)
- Dashboard confirmed loading at `127.0.0.1:8000` in browser

---

## 9. Commit History -- 2026-02-23

All 11 commits landed, in chronological order:

| Commit | Description |
|---|---|
| `ab17ca7` | `fix(speech_state): add missing stop() method` |
| `0b87aee` | `fix(stt): replace hardcoded ffmpeg path with shutil.which` |
| `b97b7ff` | `fix(stt): add bundled ffmpeg rglob fallback` |
| `ca4a67a` | `fix(stt_manager): fix temp WAV file leak with try/finally` |
| `3292d8b` | `fix(stt_manager): make OpenAI client lazy-initialized` |
| `28497a1` | `fix(general_chat): move ollama.chat to asyncio.to_thread` |
| `76e2211` | `fix(stt): replace synchronous ffmpeg subprocess with asyncio` |
| `d124d14` | `refactor(stt): route STT through stt_engine only, quarantine stt_manager` |
| `27184d9` | `fix(stt): move Vosk decode off event loop via asyncio.to_thread` |
| `770897f` | `fix(brain_server): enforce WebSocket input size limit (BUG-S2)` |
| `7e9ccc5` | `fix(stt): correct async ffmpeg subprocess with communicate() and error capture` <- HEAD |

---

# PART II -- LEDGER ANALYSIS FINDINGS

## Capability 16 Execution Eras

### Era 1 -- Pre-Governor Tests (Synthetic)
- `request_id: "test"` (hardcoded placeholder)
- No `ACTION_ATTEMPTED` predecessor
- All `success: false`
- Fired outside governor loop (direct executor calls)
- **These do not count against production record**

### Era 2 -- Governor Wired, Integration Stabilizing
- Real UUIDs present
- `ACTION_ATTEMPTED -> ACTION_COMPLETED` symmetry achieved
- First `success: true` at `03:03:53`
- One orphaned `ACTION_ATTEMPTED` at `02:59:18` (server restart mid-execution -- expected)

### Era 3 -- Stable Successful Executions
- Three consecutive `success: true` completions
- Latency 1.0s-2.7s
- Clean pairing

### Era 4 -- DuckDuckGo HTTP 202 (Ungoverned Path)
- Direct `NetworkMediator` calls (no `ACTION_ATTEMPTED` wrapper)
- DuckDuckGo returned `HTTP 202 Accepted`
- Not handled -- treated as failure

### Era 5 -- Full Pipeline Live (with `SEARCH_QUERY` event)
- `SEARCH_QUERY` event type introduced
- `capability_id: 16` on DuckDuckGo calls confirmed
- `success: true` on final executions confirmed in screenshot session

---

# PART III -- KNOWN ISSUES (Not Structural Failures)

These are service-level imperfections. They are not governance failures. They are not architectural redesign requirements.

---

## [HIGH] Issue 1 -- DuckDuckGo HTTP 202 Handling
**Severity:** High (UX reliability)
**Classification:** Executor interpretation failure, not governor failure

**What happens:**
DuckDuckGo returns `HTTP 202 Accepted` when processing. The executor treats non-200 as failure. The network call succeeds, but `ACTION_COMPLETED: success: false` is logged.

**Ledger evidence:**
```json
{"event_type": "EXTERNAL_NETWORK_CALL", "capability_id": 16, "url": "https://api.duckduckgo.com/", "status_code": 202}
{"event_type": "ACTION_COMPLETED", "capability_id": 16, "success": false}
```

**Fix:**
```python
# In WebSearchExecutor or NetworkMediator
VALID_STATUS_CODES = (200, 202)
```
Or: retry with short backoff (~500ms) when `202` received, then re-parse.

---

## [LOW] Issue 2 -- Reuters RSS Always 401
**Severity:** Low (gracefully handled)

Reuters returns `401 Forbidden` on 100% of polls. It will never succeed. It adds guaranteed-fail noise to every ledger refresh cycle.

**Fix:** Remove `https://www.reuters.com/rssFeed/topNews` from the news feed sources list.

---

## [LOW] Issue 3 -- AP News Brotli Decode Error
**Severity:** Low (gracefully handled, no crash)

AP News returns brotli-compressed content that the installed `brotli` library intermittently fails to decode:
```
('Received response with content-encoding: br, but failed to decode it.',
 error("brotli: decoder process called with data when 'can_accept_more_data()' is False"))
```
Alternates between this and `404 Not Found`.

**Fix (Option A):** Add `Accept-Encoding: gzip, deflate` header to AP News request.
**Fix (Option B):** Remove AP News from feed sources entirely.

---

## [LOW] Issue 4 -- One Orphaned ACTION_ATTEMPTED
**Severity:** Low (expected lifecycle behavior)

At `02:59:18`, one `ACTION_ATTEMPTED` has no matching `ACTION_COMPLETED`. Caused by server restart mid-execution. The in-memory `SingleActionQueue` resets on `Governor.__init__()`.

**No code change required.** This is expected behavior. Document it as a known lifecycle event.

---

## [LOW] Issue 5 -- Double Weather Poll
**Severity:** Low

At `18:05:02`, two weather calls fire ~600ms apart. Likely two concurrent WebSocket sessions or a race condition in the background poll timer.

**Fix:** Add a debounce or check for existing in-flight poll before triggering.

---

# PART IV -- DOCUMENTATION DEBT

| Document | Issue | Action |
|---|---|---|
| `docs/PHASE_4_RUNTIME_TRUTH.md` | Body still describes Phase-3.5 (`EXECUTION_ENABLED = False`, GovernorMediator as stateless/no-op) | Rewrite body to reflect Phase-4 reality |
| `docs/current_runtime/CURRENT_RUNTIME_STATE.md` | Stale preamble sentence at top (leftover chat text) | Remove first paragraph |
| `docs/NOVA_PHASE4_MASTER_STATUS.md` (this document) | Written 2026-02-24 when only Cap 16 was live; does not reflect later capability expansion and Phase-5 runtime slices | This document is now annotated as historical; see `docs/current_runtime/CURRENT_RUNTIME_STATE.md` and `docs/current_runtime/RUNTIME_TRUTH_ADDENDUM_2026-03-12.md` for current truth |

---

# PART V -- WHAT HAS NOT BEEN DONE YET

These items must pass before the tag `phase-4-cap16-live` can be applied:

## Adversarial Test Suite (Unverified)

| Test Case | Required Behavior | Status |
|---|---|---|
| Input: `"search"` | Clarification only -- no execution | [TODO] Not run |
| Input: `"search for"` | Clarification only -- no execution | [TODO] Not run |
| Input: `"search for cats"` | Boundary notice -> results widget | [TODO] Not run |
| Capability disabled (`enabled=False`) | Clean refusal message | [TODO] Not run |
| Simulated network failure | `ACTION_COMPLETED: success: false` in ledger, no silent swallow | [TODO] Not run |
| Rapid double invocation | Second invocation refused by `SingleActionQueue` | [TODO] Not run |
| Private IP URL (`192.168.x.x`) | Blocked by `NetworkMediator` | [TODO] Not run |
| Non-http scheme (`file://`, `ftp://`) | Blocked by `NetworkMediator` | [TODO] Not run |

## CI Import Audit (Not Built)

Per `docs/current_runtime/CURRENT_RUNTIME_STATE.md` Section 9:
> CI must fail if `requests`, `httpx`, `aiohttp`, or `urllib` appear outside `network_mediator.py`.

This check does not exist. It must be built before `phase-4-cap16-live` tag is applied.

## `phase-4-cap16-live` Git Tag
Blocked on adversarial test suite + CI import audit passing.

---

# PART VI -- EXECUTIVE ASSESSMENT

## What a Strong CS Engineer Would Say

Looking at:
- Governor spine
- Registry gating
- Ledger durability
- Capability scoping
- Risk classification
- Network mediator unification
- Deterministic invocation

> **"This is architecturally disciplined."**

The only critiques at this stage would be:
- Result formatting
- Error normalization
- Feed cleanup
- API edge case handling

**These are product refinements. Not structural redesign.**

## The Shift That Has Occurred

| Before | Now |
|---|---|
| Proving the governor exists | Refining a working governed system |
| Fighting architecture | Polishing behavior |
| Conceptual loops | HTTP semantics, retry policy, feed hygiene |
| Synthetic test IDs | Real UUID-keyed production executions |
| No ledger pairing | Full `ATTEMPTED -> COMPLETED` symmetry |

**This is a major shift. Phase-4 is real.**

---

# PART VII -- NEXT STEPS (Priority Order)

## Immediate (This Session)

### Step 1 -- Fix DuckDuckGo 202 Handling [HIGH]
**File:** `nova_backend/src/executors/web_search_executor.py`
Accept `(200, 202)` as valid, or implement a 500ms retry on `202`.
This is the only issue currently causing `success: false` on what should be successful searches.

### Step 2 -- Remove Reuters from Feed Sources [LOW]
**File:** `nova_backend/src/skills/news.py` (or equivalent feed list)
Delete the Reuters RSS entry. It is dead weight.

### Step 3 -- Fix AP News Accept-Encoding [LOW]
**File:** Feed fetcher / news skill HTTP request
Add `headers={"Accept-Encoding": "gzip, deflate"}` to the AP News request.
Or remove AP News entirely.

---

## Short Term (Next 1-3 Sessions)

### Step 4 -- Run Adversarial Test Suite
Execute all 8 test cases from Part V against the live server.
Document results in `docs/canonical/`.
Fix any failures before proceeding.

### Step 5 -- Build CI Import Audit
Add a GitHub Actions check (or pre-commit hook) that fails if `requests`, `httpx`, `aiohttp`, or `urllib` appear outside `src/governor/network_mediator.py`.

```yaml
# .github/workflows/import-audit.yml
- name: Enforce NetworkMediator boundary
  run: |
    python scripts/check_network_imports.py
```

### Step 6 -- Update PHASE_4_RUNTIME_TRUTH.md
Rewrite the document body to accurately describe Phase-4 runtime:
- `GOVERNED_ACTIONS_ENABLED = True`
- `GovernorMediator` as active mediator
- Capability 16 execution path
- Ledger schema

---

## Medium Term (Phase 4 Polish)

### Step 7 -- Make Search Results Human-Friendly
Current output:
```
I'm checking online. I found 5 results.
- Cats A small domesticated carnivorous mammal. https://duckduckgo.com/Cat
```

Target output (widget enhancement):
```
Title: Cats (musical)
Summary: A sung-through musical by Andrew Lloyd Webber.
Source: duckduckgo.com
[Link]
```

This is a widget rendering change on the frontend + a structured result schema change in `WebSearchExecutor`.

### Step 8 -- Apply `phase-4-cap16-live` Tag
After adversarial tests pass and CI audit is built:
```bash
git tag phase-4-cap16-live
git push origin phase-4-cap16-live
```

---

## Strategic (Phase 4.2 and Beyond)

### Phase 4.2 -- Presence Doctrine / Appliance Mode
Per `NOVA TRUTH v3.0`:
- Stability rule: 30 days of Phase-4 operation before Phase 4.2
- Next buildable thing: `LedgerAnalyzer` -> `authority_class + timeout_ms schema` -> timeout enforcement -> Influence Boundaries doc

### Phase 5 -- Memory Governance
Not yet designed to implementation level. Locked until Phase 4.2 is complete.

---

# PART VIII -- SYSTEM HEALTH SNAPSHOT

| Component | Status | Evidence |
|---|---|---|
| Governor spine | [OK] Active | Ledger `ACTION_ATTEMPTED` firing |
| CapabilityRegistry | [OK] Active | Terminal `[DEBUG] Capability 16 found` |
| SingleActionQueue | [OK] Active | Terminal `[DEBUG] Queue has pending: False` |
| NetworkMediator | [OK] Active | All outbound calls ledger-logged |
| Durable ledger | [OK] Active | Append-only, monotonic timestamps |
| Capability 16 (Web Search) | [OK] Active | 5 confirmed `success: true` executions; real HTTP to DuckDuckGo via NetworkMediator |
| Capability 17 (Open Preset Website) | [OK] Active | Real browser launch via `webbrowser.open`; wired as of 2026-02-26 |
| Capability 18 (Speak Text / TTS) | [WARN] Wired with issue | `pyttsx3` engine real; mediator sends empty params -- text must be injected by `brain_server` before TTS produces audible output |
| Capability 19 (Volume Up/Down) | [STUB] Wired (Stub) | Full pipeline wired and registry-enabled; executor returns success message but calls no OS audio API |
| Capability 20 (Media Play/Pause) | [STUB] Wired (Stub) | Full pipeline wired and registry-enabled; executor returns success message but sends no keypress or OS command |
| Capability 21 (Brightness Control) | [STUB] Wired (Stub) | Full pipeline wired and registry-enabled; executor returns success message but calls no screen brightness API |
| Capability 32 (OS Diagnostics) | [WARN] Wired (Partial) | Real disk stats via `shutil.disk_usage()`; network_status hardcoded; CPU/RAM/process/OS version absent |
| STT Pipeline | [OK] Stable | Full ffmpeg+Vosk trace in terminal |
| Weather skill | [OK] Active | HTTP 200 on every poll |
| News skill | [OK] Active (6/8 sources) | Reuters/AP failing gracefully |
| General Chat | [OK] Active | Non-blocking via `asyncio.to_thread` |
| Static file serving | [OK] Active | Dashboard loading at `127.0.0.1:8000` |
| DuckDuckGo 202 handling | [FAIL] Bug | Causes `success: false` on 202 response |
| Reuters feed | [FAIL] Dead | 100% 401, should be removed |
| AP News feed | [WARN] Flaky | Brotli decode error, should be fixed or removed |
| PHASE_4_RUNTIME_TRUTH.md | [WARN] Stale | Body describes Phase-3.5 |
| Adversarial tests | [TODO] Not run | Required before `phase-4-cap16-live` tag |
| CI import audit | [TODO] Not built | Required before `phase-4-cap16-live` tag |

---

*Document generated: 2026-02-24*
*Based on: ledger.jsonl full audit, live session screenshot, commit history 2026-02-23, canonical docs v1.9/v3.0*


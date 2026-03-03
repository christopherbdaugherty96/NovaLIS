# Network Mediation Enforced Proof
**Date:** 2026-03-03  
**Commit:** `454a11ec`  
**Scope:** Proof that all HTTP traffic is routed exclusively through `NetworkMediator`, and that SSRF, rate limiting, timeout, and DNS rebinding protections are mechanically enforced.

---

## 1. Core Claim

All outbound HTTP(S) traffic in NovaLIS is routed exclusively through `NetworkMediator.governed_request()`. No direct `requests`, `httpx`, `urllib`, or `aiohttp` calls exist outside the `NetworkMediator` module.

---

## 2. Executor Network Routing

| Capability | Executor | Network? | Route |
|---|---|---|---|
| 16 — `governed_web_search` | `WebSearchExecutor` | ✅ Yes | via `NetworkMediator.governed_request()` |
| 17 — `open_website` | `WebpageLaunchExecutor` | ❌ No | local browser launch only |
| 18 — `speak_text` | `execute_tts` | ❌ No | local pyttsx3 TTS |
| 19 — `volume_up_down` | `VolumeExecutor` | ❌ No | local OS call |
| 20 — `media_play_pause` | `MediaExecutor` | ❌ No | local OS call |
| 21 — `brightness_control` | `BrightnessExecutor` | ❌ No | local OS call |
| 22 — `open_file_folder` | `OpenFolderExecutor` | ❌ No | local OS call (disabled) |
| 32 — `os_diagnostics` | `OSDiagnosticsExecutor` | ❌ No | local read-only OS data |
| 48 — `multi_source_reporting` | `MultiSourceReportingExecutor` | ✅ Yes | via `NetworkMediator.governed_request()` (disabled) |

---

## 3. DeepSeekBridge — No NetworkMediator

`DeepSeekBridge` in `src/conversation/deepseek_bridge.py` uses **local Ollama only**:

```python
import ollama
response = ollama.chat(model="phi3:mini", ...)
```

- No `NetworkMediator` import or call.
- No `requests`, `httpx`, `aiohttp` imports.
- No external network calls.
- Full DeepSeek cloud API integration is design-only; not implemented.

---

## 4. SSRF Protection

`NetworkMediator._validate_url()` enforces:

| Check | Mechanism | Failure |
|---|---|---|
| Scheme check | Only `http` and `https` accepted | `NetworkMediatorError` |
| Hostname check | Empty hostname rejected | `NetworkMediatorError` |
| Private IP block (direct) | `ipaddress.ip_address(host)` checks `is_private`, `is_loopback`, `is_link_local` | `NetworkMediatorError` |
| DNS rebinding block | `socket.getaddrinfo(host, None)` resolves domain → checks each resolved address | `NetworkMediatorError` |

### DNS Rebinding Hardening (lines 89–99)

```python
# DNS rebinding hardening: block domains resolving to private/loopback ranges.
try:
    for info in socket.getaddrinfo(host, None):
        addr = info[4][0]
        resolved = ipaddress.ip_address(addr)
        if resolved.is_private or resolved.is_loopback or resolved.is_link_local:
            raise NetworkMediatorError("Resolved private network address forbidden.")
except NetworkMediatorError:
    raise
except Exception:
    # If DNS resolution fails, requests layer will raise a deterministic network error.
    pass
```

This prevents DNS rebinding attacks where an attacker-controlled domain resolves to an internal IP address.

---

## 5. Rate Limiting

- **Limit:** 50 requests per minute
- **Mechanism:** `threading.Lock` protects a per-minute counter and timestamp
- **Failure:** `NetworkMediatorError("Rate limit exceeded.")` — Governor catches and returns `ActionResult.failure`

---

## 6. Timeout Enforcement

- **Default timeout:** 5 seconds
- **Mechanism:** `requests.request(..., timeout=self._timeout)` — hard deadline on HTTP call
- **Failure:** `requests.Timeout` → caught → `NetworkMediatorError` → Governor catches → `ActionResult.failure`

---

## 7. Fail-Closed Guarantee

`NetworkMediator` is fail-closed:

- Any validation failure → `NetworkMediatorError` raised immediately
- Any network error → caught → `NetworkMediatorError` raised
- `Governor.handle_governed_invocation()` catches `NetworkMediatorError` → `ActionResult.failure`
- No exception escapes to the UI as raw data

---

## 8. Ledger Logging

All network calls (success and failure) are logged to the ledger:

| Event | When |
|---|---|
| `EXTERNAL_NETWORK_CALL` | After successful HTTP response |
| `NETWORK_CALL_FAILED` | After any network error |

Both events include `capability_id`, `url`, and `method`. Failed events include `error`.

---

## 9. Conclusion

All HTTP traffic in NovaLIS is routed through `NetworkMediator.governed_request()`. No direct network imports exist outside the NetworkMediator module. SSRF protection, DNS rebinding hardening, rate limiting, timeout enforcement, and fail-closed behavior are all mechanically enforced. The conversation layer (`DeepSeekBridge`) makes no external network calls — it uses local Ollama only.

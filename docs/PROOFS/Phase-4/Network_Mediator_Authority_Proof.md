# Network Mediator Authority Proof
**Date:** 2026-03-02
**Commit:** `6574a355f2db7fb00d7e0fb9451f60f9f16eac21`
**Scope:** Proof that all outbound HTTP traffic is exclusively mediated through `NetworkMediator`.

---

## 1. Sole Gateway Claim

`NetworkMediator.request()` in `nova_backend/src/governor/network_mediator.py` is the **only method** that calls `requests.request()` for governed capabilities.

`requests` is imported **only** in `network_mediator.py` among governor/executor modules.

---

## 2. Enforcement Stack

Every call to `NetworkMediator.request()` passes through this ordered enforcement stack:

```
1. Capability identity check     → CapabilityRegistryError if unknown
2. Capability enabled check      → NetworkMediatorError if disabled
3. Rate limit check              → NetworkMediatorError if >50 req/min per capability
4. URL validation (SSRF)         → NetworkMediatorError if scheme/host/IP fails
5. HTTP execution with timeout   → NetworkMediatorError on RequestException
6. Response parsing              → NetworkMediatorError on JSON parse failure
7. Success ledger logging        → EXTERNAL_NETWORK_CALL event
```

**Source:** `network_mediator.py` lines 88–181

---

## 3. SSRF Protection

`_validate_url()` (lines 60–86) enforces:

| Check | Blocked |
|---|---|
| Scheme not in `{http, https}` | ✅ `file://`, `ftp://`, `data://`, etc. |
| No hostname | ✅ Malformed URLs |
| Hostname is `localhost`, `127.0.0.1`, `::1` | ✅ Direct loopback |
| IP is private, loopback, or link-local | ✅ `10.x.x.x`, `192.168.x.x`, `169.254.x.x`, `fc00::`, etc. |

**Known gap (documented):** DNS rebinding is not defended. Domain names that resolve to private IPs are not blocked at validation time. This is accepted for the Phase-4 threat model.

**Source:** `network_mediator.py` lines 60–86

---

## 4. Rate Limiting

Thread-safe sliding window rate limiter:

```python
RATE_LIMIT_PER_MINUTE = 50
```

Per-capability tracking with `threading.Lock`. Requests older than 60 seconds are pruned from the window.

**Source:** `network_mediator.py` lines 49–58

---

## 5. Timeout Enforcement

```python
NETWORK_TIMEOUT = 5  # seconds (default)
```

Caller can override with `timeout=` parameter, but a timeout is **always** applied. No call can run without a timeout.

**Source:** `network_mediator.py` line 15, lines 131–139

---

## 6. Ledger Integration

| Event | When | Data Logged |
|---|---|---|
| `NETWORK_CALL_FAILED` | HTTP exception (line 143–147) | `capability_id`, `url`, `error` |
| `NETWORK_CALL_FAILED` | JSON parse failure (line 157–165) | `capability_id`, `url`, `error` |
| `EXTERNAL_NETWORK_CALL` | Successful response (line 171–179) | `capability_id`, `url`, `method`, `status_code` |

**No headers are logged** to avoid leaking secrets (documented at line 170).

---

## 7. Import Discipline

`requests` is imported at module level **only** in `network_mediator.py`. The adversarial test `test_no_direct_network_request_calls_outside_mediator_and_executors` scans the entire `src/` tree to verify no unauthorized `requests` usage exists.

**Source:** `tests/adversarial/test_governor_bypass.py` lines 24–46

---

## 8. Test Verification

| Test | File | What It Proves |
|---|---|---|
| `test_no_direct_network_request_calls_outside_mediator_and_executors` | `tests/adversarial/test_governor_bypass.py` | No `requests` usage outside allowed modules |
| `test_ledger_failure_denies_search` | `tests/adversarial/test_ledger_failure.py` | Network path is blocked if ledger fails first |

---

## 9. Conclusion

All outbound HTTP is funneled through `NetworkMediator.request()`, which enforces capability identity, enablement, rate limiting, SSRF protection, timeouts, and ledger logging. No alternate outbound path exists for governed capabilities.
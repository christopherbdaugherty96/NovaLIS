# Ledger Write Integrity Proof
**Date:** 2026-03-02
**Commit:** `6574a355f2db7fb00d7e0fb9451f60f9f16eac21`
**Scope:** Proof that the ledger is append-only, fail-closed at the authority boundary, and logs all governed actions.

---

## 1. LedgerWriter Implementation

**File:** `nova_backend/src/ledger/writer.py`

```python
class LedgerWriter:
    """Append‑only ledger with atomic write guarantees."""

    def __init__(self, path: Path = LEDGER_PATH):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log_event(self, event_type: str, metadata: Dict[str, Any]) -> None:
        entry = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            **metadata
        }
        try:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
                f.flush()
                os.fsync(f.fileno())
        except Exception as e:
            raise LedgerWriteFailed(f"Ledger write failed: {e}") from e
```

---

## 2. Write Guarantees

| Property | Mechanism |
|---|---|
| **Append-only** | File opened with `"a"` mode — no truncation, no overwrite |
| **Atomic flush** | `f.flush()` + `os.fsync(f.fileno())` — data reaches disk before method returns |
| **Structured entries** | Every entry is JSON with `timestamp_utc` and `event_type` |
| **Fail-loud** | Any write exception raises `LedgerWriteFailed` |

---

## 3. Fail-Closed Integration at Governor

`LedgerWriter.log_event("ACTION_ATTEMPTED", ...)` is called **before** `ActionRequest` creation (governor.py lines 103–111):

```python
try:
    self.ledger.log_event(
        "ACTION_ATTEMPTED",
        {"capability_id": capability_id, "capability_name": cap.name},
    )
except Exception as e:
    return ActionResult.failure("I can't do that right now.")
```

If the ledger write fails, **no ActionRequest is created and no executor runs**. This is the fail-closed guarantee.

---

## 4. Event Taxonomy

Events currently emitted in Phase-4 runtime:

| Event Type | Emitter | Blocking? | Data |
|---|---|---|---|
| `ACTION_ATTEMPTED` | `Governor.handle_governed_invocation` | **Yes** | `capability_id`, `capability_name` |
| `ACTION_COMPLETED` | `Governor._execute` | No (best-effort) | `capability_id`, `request_id`, `success` |
| `SEARCH_QUERY` | `Governor._execute` (cap 16 only) | No | `query` |
| `WEBPAGE_LAUNCH` | `WebpageLaunchExecutor.execute` | No | `requested_name`, `resolved_url`, `preset`, `success`, `request_id` |
| `EXTERNAL_NETWORK_CALL` | `NetworkMediator.request` | No | `capability_id`, `url`, `method`, `status_code` |
| `NETWORK_CALL_FAILED` | `NetworkMediator.request` | No | `capability_id`, `url`, `error` |

---

## 5. Known Gap

`event_type` is accepted as an unconstrained `str` argument. No allowlist is enforced at the write boundary. Any caller can pass any event type string. This is documented in `PHASE4_CONSTITUTIONAL_MISMATCH_AUDIT.md` as Major severity.

---

## 6. Ledger Storage

- **Format:** JSONL (one JSON object per line)
- **Path:** `nova_backend/src/data/ledger.jsonl`
- **Directory creation:** Automatic via `path.parent.mkdir(parents=True, exist_ok=True)`
- **No deletion:** No `truncate`, `unlink`, or prune operation exists in `writer.py`
- **No read interface:** `LedgerAnalyzer` / `reader.py` does not yet exist (task D3 pending)

---

## 7. Test Verification

| Test | File | What It Proves |
|---|---|---|
| `test_ledger_failure_denies_search` | `tests/adversarial/test_ledger_failure.py` | Simulated `IOError` in `log_event` → Governor returns `success=False`, no executor runs |

---

## 8. Conclusion

The ledger is append-only, atomically flushed, and fail-closed at the Governor boundary. Every governed action is logged before execution begins. Ledger write failure blocks all execution.
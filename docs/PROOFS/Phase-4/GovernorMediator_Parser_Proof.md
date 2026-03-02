# GovernorMediator Parser Proof
**Date:** 2026-03-02
**Commit:** `6574a355f2db7fb00d7e0fb9451f60f9f16eac21`
**Scope:** Proof that input parsing is deterministic, authority-free, and correctly routes to governed invocations.

---

## 1. Authority Boundary

`GovernorMediator` in `nova_backend/src/governor/governor_mediator.py`:

- ✅ Parses user text into structured `Invocation` / `Clarification` / `None`
- ❌ **Never** creates `ActionRequest`
- ❌ **Never** calls any executor
- ❌ **Never** accesses the ledger, registry, or network mediator
- ❌ **Never** modifies system state

**Source:** Module docstring lines 1–10 + full file review

---

## 2. Parsing Rules

### Capability 16 — Governed Web Search

**Pattern:** `^\s*(search(?: for)?|look up|research)\s+(?P<q>.+?)\s*$`

| Input | Result |
|---|---|
| `"search for climate change"` | `Invocation(capability_id=16, params={"query": "climate change"})` |
| `"look up python docs"` | `Invocation(capability_id=16, params={"query": "python docs"})` |
| `"research AI governance"` | `Invocation(capability_id=16, params={"query": "AI governance"})` |
| `"search"` (no query) | `Clarification(capability_id=16, message="What would you like to search for?")` |

### Capability 17 — Open Preset Website

**Pattern:** `^\s*open\s+(?P<name>\w+)\s*$`

| Input | Result |
|---|---|
| `"open youtube"` | `Invocation(capability_id=17, params={"target": "youtube"})` |
| `"open Google"` | `Invocation(capability_id=17, params={"target": "google"})` |

### Capability 18 — Speak Text (TTS)

**Pattern:** `^\s*(speak that|read that|say it)\s*$`

| Input | Result |
|---|---|
| `"speak that"` | `Invocation(capability_id=18, params={})` |
| `"read that"` | `Invocation(capability_id=18, params={})` |
| `"say it"` | `Invocation(capability_id=18, params={})` |

### No match

Any input not matching the above → `None` (no invocation detected).

---

## 3. One-Strike Clarification Protocol

If a search intent is detected but no query is provided:

1. Session ID is stored in `_pending_clarification[session_id] = 16`
2. `Clarification` is returned with `"What would you like to search for?"`
3. On the **next** call with the same session ID, the entire input becomes the query
4. Pending state is consumed (popped) — only one clarification attempt

**Source:** `governor_mediator.py` lines 78–85, 106–116

### Cleanup:

```python
@staticmethod
def clear_session(session_id: str) -> None:
    _pending_clarification.pop(session_id, None)
```

Called on WebSocket disconnect to prevent memory leaks.

---

## 4. Input Sanitization

Before parsing:
```python
t = (text or "").strip()
t = re.sub(r"[.?!]+$", "", t)    # Strip trailing punctuation
```

Empty input after sanitization → `None`.

---

## 5. Parsing Order

```
1. Check pending clarification (session-scoped)
2. Try full search pattern (SEARCH_RE)
3. Try open pattern (OPEN_RE)
4. Try TTS trigger pattern
5. Try incomplete search detection → Clarification
6. Return None
```

Order is deterministic. First match wins. No ambiguity.

---

## 6. Test Verification

| Test | File | What It Proves |
|---|---|---|
| `test_parse_speak_that_invocation` | `tests/test_governor_mediator_tts.py` | `"speak that"` → `Invocation(capability_id=18, params={})` |

---

## 7. Conclusion

`GovernorMediator` is a pure, deterministic, stateless (except ephemeral session clarification) parser. It holds no execution authority, creates no actions, and accesses no system resources. All parsing rules are regex-based and predictable.
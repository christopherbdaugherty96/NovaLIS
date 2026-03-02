# Capability 17 — Open Preset Website Proof
**Date:** 2026-03-02
**Commit:** `6574a355f2db7fb00d7e0fb9451f60f9f16eac21`
**Scope:** End-to-end proof for the governed preset website launch capability.

---

## 1. Full Execution Path

```
User: "open youtube"
  → GovernorMediator.parse_governed_invocation() → Invocation(17, {"target": "youtube"})
  → Governor.handle_governed_invocation(17, {"target": "youtube"})
    → [5 gates pass]
    → ActionRequest(capability_id=17, params={"target": "youtube"})
    → Governor._execute(req)
      → WebpageLaunchExecutor(ledger).execute(req)
        → PRESETS.get("youtube") → "https://www.youtube.com"
        → webbrowser.open("https://www.youtube.com")
        → Ledger.log_event("WEBPAGE_LAUNCH", {..., success: True})
      → ActionResult.ok("Opening https://www.youtube.com.")
      → Ledger.log_event("ACTION_COMPLETED", ...)
```

---

## 2. Preset Mapping

**File:** `nova_backend/src/executors/webpage_launch_executor.py`

```python
PRESETS = {
    "google":   "https://www.google.com",
    "facebook": "https://www.facebook.com",
    "pandora":  "https://www.pandora.com",
    "github":   "https://www.github.com",
    "twitter":  "https://www.twitter.com",
    "youtube":  "https://www.youtube.com",
}
```

**Static, hardcoded, no dynamic lookup.** The preset map is a module-level constant.

---

## 3. Failure Modes

| Failure | Handling |
|---|---|
| Unknown preset (`target` not in `PRESETS`) | `ActionResult.failure("I don't have a preset for '{target}'.")` |
| `webbrowser.open()` exception | `ActionResult.failure("Could not open the browser.")` + ledger event with `success: False` |

---

## 4. Ledger Events

The executor logs `WEBPAGE_LAUNCH` in both success and failure paths:

```python
self.ledger.log_event("WEBPAGE_LAUNCH", {
    "requested_name": target,
    "resolved_url": url,
    "preset": True,
    "success": True/False,
    "request_id": request.request_id
})
```

---

## 5. No Network Mediation Required

`webbrowser.open()` delegates to the OS browser. No `NetworkMediator` call is made. This is a **local effect** — the external effect is the browser opening, not a governed HTTP call.

---

## 6. Conclusion

Capability 17 is fully governed: registry-enabled, mediator-parsed, Governor-gated, ledger-tracked, static-preset-only, with deterministic failure handling for unknown presets and browser launch errors.
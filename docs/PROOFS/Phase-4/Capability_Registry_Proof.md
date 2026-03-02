# Capability Registry Proof
**Date:** 2026-03-02
**Commit:** `6574a355f2db7fb00d7e0fb9451f60f9f16eac21`
**Scope:** Proof that the capability registry enforces fail-closed identity and enablement for all governed capabilities.

---

## 1. Registry Schema Enforcement

`CapabilityRegistry._load_registry()` in `nova_backend/src/governor/capability_registry.py` enforces schema at load time:

| Check | Failure Mode |
|---|---|
| `REGISTRY_PATH.exists()` | `CapabilityRegistryError` — "Registry missing … Execution disabled." |
| JSON parse | `CapabilityRegistryError` — "Registry malformed (JSON error) … Execution disabled." |
| `schema_version == "1.0"` | `CapabilityRegistryError` — "Unsupported registry schema version." |
| `phase == "4"` | `CapabilityRegistryError` — "Registry phase mismatch." |
| Each entry has all required fields | `CapabilityRegistryError` — "Capability missing fields: {missing}" |
| `risk_level ∈ {low, confirm, high}` | `CapabilityRegistryError` — "Invalid risk_level" |
| `status ∈ {design, active, deprecated, retired}` | `CapabilityRegistryError` — "Invalid status" |
| `enabled` is boolean | `CapabilityRegistryError` — "enabled must be a boolean" |
| No duplicate IDs | `CapabilityRegistryError` — "Duplicate capability ID" |

**Source:** `capability_registry.py` lines 31–74

---

## 2. Required Fields

Every capability entry must include exactly:

```python
{"id", "name", "status", "phase_introduced", "risk_level", "data_exfiltration", "enabled"}
```

**Source:** `capability_registry.py` lines 51–52

---

## 3. Runtime State — `registry.json`

**File:** `nova_backend/src/config/registry.json`

| ID | Name | Status | Enabled | Risk | Exfiltration | Governor Route | Mediator Trigger |
|---:|---|---|---|---|---|---|---|
| 16 | `governed_web_search` | active | **true** | low | true | ✅ `WebSearchExecutor` | ✅ `search ...` |
| 17 | `open_website` | active | **true** | low | false | ✅ `WebpageLaunchExecutor` | ✅ `open <name>` |
| 18 | `speak_text` | active | **true** | low | false | ✅ `execute_tts` | ✅ `speak that`, `read that`, `say it` |
| 19 | `volume_up_down` | active | **false** | low | false | ❌ No route | ❌ No trigger |
| 20 | `media_play_pause` | active | **false** | low | false | ❌ No route | ❌ No trigger |
| 21 | `brightness_control` | active | **false** | low | false | ❌ No route | ❌ No trigger |
| 22 | `open_file_folder` | active | **false** | confirm | false | ❌ No route | ❌ No trigger |
| 32 | `os_diagnostics` | active | **false** | low | false | ❌ No route | ❌ No trigger |
| 48 | `multi_source_reporting` | active | **false** | low | true | ❌ No route | ❌ No trigger |

IDs 19–48 are **triple-locked**: disabled in registry, no parser trigger, no executor route.

---

## 4. Enablement Logic

```python
def is_enabled(self, capability_id: int) -> bool:
    cap = self.get(capability_id)
    return cap.status == "active" and cap.enabled
```

Both conditions must be true. `status == "active"` alone is insufficient. `enabled == True` alone is insufficient.

**Source:** `capability_registry.py` lines 83–86

---

## 5. Fail-Closed Behavior

| Scenario | Result |
|---|---|
| Registry file missing | `CapabilityRegistryError` raised at `__init__` → Governor cannot instantiate registry → all invocations fail |
| Registry file malformed JSON | Same |
| Unknown capability ID requested | `CapabilityRegistryError` → Governor returns `ActionResult.failure` |
| Known but disabled capability | `is_enabled()` returns `False` → Governor returns `ActionResult.failure("I can't do that yet.")` |

---

## 6. Immutability

`Capability` is `@dataclass(frozen=True)`. Fields cannot be modified after construction. The registry dict is populated once at `__init__` and never mutated.

**Source:** `capability_registry.py` line 14

---

## 7. Test Verification

| Test | File | What It Proves |
|---|---|---|
| `test_registry_missing_capability_fails` | `tests/test_registry_fail_closed.py` | Unknown ID 9999 → exception raised |
| `test_governor_refuses_disabled_capability` | `tests/test_governor_fail_closed.py` | Disabled ID 22 → `success=False` |

---

## 8. Conclusion

The capability registry is schema-validated, fail-closed, immutable, and double-gated (`status` + `enabled`). No capability can execute without being both `active` and `enabled` in the registry JSON.
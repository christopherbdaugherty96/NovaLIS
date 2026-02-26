Below is the **final authoritative document**, incorporating the consolidated Phase-4 staging state exactly as captured in  and aligned to your actual runtime, ledger events, and governance structure.

This version is formatted to be merge-ready with `/phase-status` and suitable for canonical storage.

---

# 🔒 NOVA PHASE-4 STAGING STATUS & GOVERNOR BYPASS PROOF

## Capability 16 — Governed Web Search

**Document ID:** `NOVA-PHASE4-STAGING-CAP16-v1.1`
**Status:** ACTIVE — Phase-4 Staging (Option B)
**Runtime Flag:** `GOVERNED_ACTIONS_ENABLED = True`
**Scope:** Capability 16 only
**Authority Model:** Agent Under Law — Governor Supremacy Absolute
**Non-Authorizing:** Reflective of runtime state only

---

# 1️⃣ CURRENT RUNTIME STATE

Nova has transitioned from Phase-3.5 seal to **Phase-4 staging**.

Installed and active:

* Governor spine (single choke-point authority)
* ExecuteBoundary active (`GOVERNED_ACTIONS_ENABLED = True`)
* CapabilityRegistry enforced
* NetworkMediator as sole outbound network gate
* SingleActionQueue concurrency control
* Deterministic invocation grammar
* One-strike clarification enforcement
* Explicit online boundary disclosure
* Durable append-only ledger

Execution authority exists but is:

* Explicit only
* Capability-scoped
* Deterministic
* Non-autonomous
* User-invoked only

Nova does not initiate actions.
Nova performs no background execution.
Nova performs no silent network access.

---

# 2️⃣ SCOPE OF AUTHORITY

Only **Capability 16 (Governed Web Search)** is enabled.

No additional governed capabilities are active.

All other system behavior remains Phase-3 style (read-only skills, deterministic routing).

---

# 3️⃣ REQUIRED EXECUTION PATH (Single Choke-Point)

A governed action must traverse this exact pipeline:

```
User input
 → GovernorMediator.parse_governed_invocation(session_id, text)
 → Governor.handle_governed_invocation(16, params)
 → ExecuteBoundary.allow_execution()
 → CapabilityRegistry validation
 → SingleActionQueue.try_begin()
 → WebSearchExecutor.execute()
 → NetworkMediator.request()
 → ActionResult
 → Ledger logging
 → UI delivery
```

There is no alternate execution path.

If any step fails → execution halts.

This enforces the Intelligence–Authority Split.

---

# 4️⃣ ONLINE BOUNDARY DISCLOSURE

When Capability 16 runs, Nova emits:

> “I’m checking online.”

This notice is sent **before** any external request is made.

This guarantees:

* No silent online access
* Explicit boundary crossing
* Calm, non-dramatic disclosure
* No retroactive narration

Boundary entry is visible. Boundary exit occurs implicitly upon result delivery.

---

# 5️⃣ ONE-STRIKE CLARIFICATION GUARANTEE

Malformed invocations:

* `search`
* `search for`
* `search for   `

Behavior:

1. Nova requests clarification once.
2. Clarification state stored per session.
3. Fallback routing is blocked.
4. No execution occurs.
5. No second clarification attempt.

After one clarification:

* If still malformed → refusal.
* No inference.
* No intent ranking.
* No recursive questioning.

---

# 6️⃣ LEDGER INTEGRITY (ACTUAL RUNTIME EVENTS)

Ledger file:

```
src/data/ledger.jsonl
```

Each entry:

```json
{
  "timestamp_utc": "...",
  "event_type": "...",
  "...metadata"
}
```

### Properties

✔ Append-only
✔ Durable (`flush` + `fsync`)
✔ Hardcoded `event_type` strings
✔ No user-derived event types
✔ No dynamic construction of event names

---

## Required Success Flow Events

| Event Type              | Source              | Meaning                           |
| ----------------------- | ------------------- | --------------------------------- |
| `ACTION_ATTEMPTED`      | governor.py         | Logged before execution begins    |
| `EXTERNAL_NETWORK_CALL` | network_mediator.py | Logged on successful HTTP request |
| `ACTION_COMPLETED`      | governor.py         | Logged after executor returns     |

---

## Required Failure Flow Events

| Event Type              | Source              | Meaning                   |
| ----------------------- | ------------------- | ------------------------- |
| `ACTION_ATTEMPTED`      | governor.py         | Attempt recorded          |
| `NETWORK_CALL_FAILED`   | network_mediator.py | Network failure logged    |
| (No `ACTION_COMPLETED`) | —                   | Absence indicates failure |

Ledger does **not** separately log boundary allow/deny events.
This document makes no unsupported claims.

---

# 7️⃣ BYPASS VECTORS CONSIDERED

### Direct Executor Invocation

Mitigated: Executors unreachable without Governor invocation.

### Direct Network Call

Mitigated: All outbound I/O restricted to NetworkMediator.

### Silent Online Access

Mitigated: Explicit boundary notice before request.

### Invocation Ambiguity

Mitigated: Deterministic grammar + one-strike clarification.

### Concurrency Exploit

Mitigated: SingleActionQueue enforcement.

### UI Auto-Trigger

Mitigated: No auto-fetch permitted.

---

# 8️⃣ ADVERSARIAL TEST REQUIREMENTS

Must pass before tagging live:

* `search` → clarification only
* `search for` → clarification only
* `search for cats` → boundary notice → results
* Disable capability → refusal
* Simulated network failure → no `ACTION_COMPLETED`
* Rapid double invocation → second refused
* Private IP URL → blocked
* Non-http scheme → blocked

---

# 9️⃣ CI IMPORT AUDIT REQUIREMENT

CI must fail if these appear outside `network_mediator.py`:

* `requests`
* `httpx`
* `aiohttp`
* `urllib`

No direct HTTP libraries permitted elsewhere.

---

# 🔟 PHASE-STATUS REFLECTION

`/phase-status` should now reflect staging:

```json
{
  "phase": "4 (staging)",
  "governed_actions_enabled": true,
  "active_capabilities": [16],
  "execution_mode": "explicit invocation only",
  "online_boundary_disclosure": true,
  "background_execution": false
}
```

Reflective only.
No runtime announcement.

---

# 11️⃣ ACTIVATION DISCIPLINE

Tag only when:

* Adversarial tests pass
* CI audit passes
* Bypass proof verified
* No debug scaffolding remains

Tag:

```
phase-4-cap16-live
```

No banner.
No ceremony.
No spoken announcement.

Execution simply works when invoked.

---

# 12️⃣ STABILITY RULE

After activation:

* No new governed capabilities
* No presence modifications
* No structural refactors
* No personality evolution

Minimum 30-day stability window before Phase-4.2 work.

---

# 13️⃣ CONCLUSION

Phase-4 staging is mechanically real.

Capability 16 is:

* Explicit
* Governed
* Logged
* Boundary-aware
* Non-autonomous
* Non-proactive
* Bypass-resistant

Nova remains:

> An agent under law.
> Authority constrained.
> Intelligence contained.

Execution works — but only when asked.

---


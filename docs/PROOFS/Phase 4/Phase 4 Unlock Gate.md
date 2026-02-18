
# 🔓 NOVA — PHASE-4 RUNTIME UNLOCK GATE

Document ID: NOVA-PHASE4-RUNTIME-UNLOCK-v1.0  
Status: CONDITIONAL — NOT ACTIVE  
Authority: Tier-1 Constitutional Action  
Date: 2026-02-17  
Applies To: Capability 16 (Governed Web Search) Only  

---

# I. PURPOSE

This document authorizes the controlled activation of Phase-4 governed execution.

Phase-4 infrastructure is already installed.  
This document governs the moment runtime authority is enabled.

This is not a feature expansion.  
This is a boundary transition.

---

# II. SCOPE OF UNLOCK

The following and only the following is permitted:

✔ `GOVERNED_ACTIONS_ENABLED = True`  
✔ Capability 16 (Web Search)  
✔ Read-only network access  
✔ No mutation  
✔ No file writes  
✔ No OS calls  
✔ No background tasks  

All other capabilities remain disabled.

---

# III. PRE-UNLOCK CERTIFICATION REQUIREMENTS

The following must be verified before activation:

## 1️⃣ Single Execution Spine Confirmed

Verified:

- Only Governor instantiates Executors
- No skill calls tool layer
- No fallback network path
- No alternate HTTP surface
- No dynamic invocation surface

Static proof completed via:

- `Select-String "WebSearchExecutor"`
- `Select-String "run_web_search"`
- `Select-String "ddgs"`

Result: Single authority spine confirmed.

---

## 2️⃣ ExecuteBoundary Fail-Closed Verified

Test performed:

Input:
```

search for test

```

Output:
```

I can’t do that yet.

```

Confirmed:

- Invocation parsed
- Governor engaged
- ExecuteBoundary blocked execution
- No network call executed

---

## 3️⃣ Skill Containment Verified

Confirmed:

- Skills cannot access network directly
- `news_fallback.py` ddgs path removed
- WebSearchSkill stubbed
- No parallel execution surface

---

## 4️⃣ No Silent Fallback

Confirmed:

- If governed invocation fails → refusal
- No alternate skill invoked
- No hidden re-routing

---

# IV. ACTIVATION PROCEDURE

## Step 1 — Edit ExecuteBoundary

Set:

```

GOVERNED_ACTIONS_ENABLED = True

```

Commit change.

---

## Step 2 — Capability Registry

Enable only:

```

Capability ID: 16
Name: web_search
Mode: Read-only

```

All other capability IDs remain disabled.

---

## Step 3 — Restart Runtime

Restart:

```

uvicorn src.brain_server:app

```

Confirm:

- No startup errors
- WebSocket connects
- No missing imports

---

# V. FIRST LIVE TEST

## Test 1 — Explicit Invocation

Input:
```

search for weather in London

```

Expected:

- "I'm checking online."
- Structured link output (title + URL)
- No summary
- No synthesis
- No memory write

---

## Test 2 — Malformed Invocation

Input:
```

search for

```

Expected:

- Refusal
- No execution
- No network call

---

## Test 3 — Disable Capability

Temporarily disable Capability 16.

Repeat Test 1.

Expected:

- "I can’t do that yet."

---

# VI. POST-ACTIVATION VERIFICATION

After first successful execution:

Confirm:

- Logs show Capability 16 invoked
- Executor called
- NetworkMediator used
- No direct ddgs call outside tool layer
- No skill-level execution
- No secondary invocation surface

---

# VII. INVARIANTS THAT MUST REMAIN TRUE

Even after unlock:

1. Single Master Governor
2. No parallel execution
3. No background execution
4. No inference
5. No dynamic invocation
6. No implicit escalation
7. Read-only only
8. Fail-closed always

If any invariant is violated → Phase-4 must be re-locked immediately.

---

# VIII. ABORT CONDITIONS

Immediately disable Phase-4 runtime if:

- Any skill bypasses Governor
- Any tool called outside executor
- Any mutation occurs
- Any background task triggers execution
- Any silent fallback occurs
- Any execution occurs without explicit invocation

Procedure:

```

Set GOVERNED_ACTIONS_ENABLED = False
Restart server

```

---

# IX. CONSTITUTIONAL DECLARATION

This unlock does not:

- Grant autonomy
- Grant background execution
- Grant mutation authority
- Grant self-initiation
- Grant learning
- Grant persistence

Nova remains:

> An Agent Under Law.

---

# X. SIGN-OFF

Pre-Unlock Certification Completed: ✔  
Structural Integrity Confirmed: ✔  
Fail-Closed Verified: ✔  
Parallel Surfaces Eliminated: ✔  

Authorized To Activate:

☐ Yes  
☐ No  

Operator Signature: __________________  
Date: __________________  

---

Status: Awaiting Activation
```

---

This is the correct document for your state.

If you want, next we can:

* Draft a **Post-Activation Audit Record**
* Or build a **CI Enforcement Guard** to permanently prevent regression
* Or walk through the actual flip together step-by-step

You are exactly at the moment you designed this system for.

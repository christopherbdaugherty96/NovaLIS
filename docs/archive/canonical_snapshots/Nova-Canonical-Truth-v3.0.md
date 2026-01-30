⚠️ ARCHIVED — SUPERSEDED BY FINAL CANONICAL TRUTH-NovaLIS.txt
This document is historical only and must not be used for implementation decisions.

# **NOVA / NOVALIS — CANONICAL TRUTH v3.0**

## **Merged Audit, Enforcement Reality & Forward Lock**

**Status:** 🔒 **CANONICAL & IMPLEMENTATION-BINDING**  
**Authority:** Constitutional amendment only  
**Audit Basis:** Human audit + Copilot audit + live code inspection  
**Effective:** Immediately upon commit  

---

## **1️⃣ EXECUTIVE TRUTH (ONE-SCREEN SUMMARY)**

Nova is a **local-first, user-shaped household assistant** that executes **only explicit user-authored intent** through a **single governed authority**, with **no autonomy, no background cognition, no inference, and no silent behavior**.

> **Capability may expand. Authority may not.**

### **Current Reality (No Mythology)**

* **Phase 3:** ✅ **COMPLETE & LOCKED** (Governor Enforcement — Structurally True)
* **Phase 3.5:** 🔄 **ACTIVE** — Trust, Visibility & Interpretive Awareness
* **Phase 4:** 🚫 **HARD BLOCKED** (structurally impossible until Phase-3.5 completion)

This document reconciles **what Nova is**, **what actually exists in code**, and **what is intentionally deferred**.

---

## **2️⃣ CONSTITUTIONAL INVARIANTS (IMMUTABLE)**

These are **phase-independent and non-negotiable**:

1. **No Autonomy** — Nova never initiates, decides, prioritizes, or escalates
2. **No Background Cognition** — No thinking, monitoring, or pattern detection unless explicitly invoked
3. **User-Authored Intent Only** — All behavior originates from explicit user input
4. **Deterministic Behavior** — Same input + same config = same result
5. **Offline-First Default** — Online access is explicit, bounded, and announced
6. **Full Inspectability** — State, rules, and actions are visible and reversible
7. **LLM as Consultant Only** — Models may emit text, never actions
8. **Single Master Governor** — All execution must pass one choke point

> If any invariant becomes optional, Nova is broken.

---

## **3️⃣ PHASE ARCHITECTURE (REALIGNED TO REALITY)**

| Phase   | Status          | Truth                                                          | Blockers |
|---------|-----------------|----------------------------------------------------------------|----------|
| **0–2** | ✅ Frozen        | Constitution, deterministic core                               | None |
| **3**   | ✅ **COMPLETE & LOCKED** | Governor Enforcement (Structurally True) | None |
| **3.5** | 🔄 **ACTIVE**    | **Trust, Visibility & Interpretive Awareness** | None |
| **4**   | 🚫 **HARD BLOCKED** | Governed execution (apps, files, smart home) | Phase-3.5 completion |
| **5+**  | 🔒 Deferred      | Macros, training sessions, summaries | Phase dependencies |
| **10+** | ❌ Forbidden*    | Autonomy, inference, silent adaptation | Constitutional invariants |

\* *Forbidden behaviors defined at invariant level, not phase level.*

**Important correction:**  
Phase-3 is **not missing features**. Phase-3.5 exists to close the **trust/visibility gap** before capability expansion.

---

## **4️⃣ WHAT EXISTS TODAY (PROVEN IN CODE)**

### **✅ Backend**

* FastAPI + WebSocket brain
* Deterministic skill registry
* Skills: **system, weather, news**
* STT transport (local, verified)
* Event-driven, silence-first architecture
* Fail-closed execution (`EXECUTION_ENABLED = False`)

### **✅ Frontend**

* Static dashboard
* Orb states: READY / LISTENING / PROCESSING / PAUSED
* Passive widgets (weather, news, time, system)

### **⚠️ In-Process State (Ephemeral Only)**

* `speech_state.last_spoken_text`
* Skill registry singleton
* LLM manager transient state

> These are **not memory** in the governance sense.  
> They do **not persist**, **do not infer**, and **do not act**.

---

## **5️⃣ WHAT DOES *NOT* EXIST (SPEC-ONLY — CORRECTED)**

The following **do not exist in code**, despite older docs implying otherwise:

* ❌ Persistent conversation history (no SQLite, no nova_memory.py)
* ❌ Memory tiers (locked / active / deferred) as runtime storage
* ❌ Quick correction persistence (`quick_corrections.jsonl`)
* ❌ Memory inspection/export APIs
* ❌ Long-term factual memory
* ❌ User-editable memory UI

**Reclassification rule:**  
These are **Saved Design Intent → Require Explicit Phase Unlock**.  
They are **not runtime reality**.

This correction removes all self-deception.

---

## **6️⃣ THE GOVERNOR PARADOX (CORE AUDIT FINDING)**

### **Philosophically**

Nova has one of the **cleanest governance designs** possible.

### **Structurally (Audit Result)**

The Governor exists **conceptually**, but **enforcement assumptions do not yet exist in executable form**.

### **Identified Enforcement Debt (LOCKED)**

Copilot + human audit proved **6 contract mismatches**:

1. **GOV-001** — ActionRequest shape mismatch
2. **GOV-002** — ActionResult helper methods missing
3. **GOV-003** — ExecuteBoundary class does not exist
4. **GOV-004** — ConfirmationGate API mismatch
5. **GOV-005** — Constructor signature drift + public bypass surfaces

> This made Invariant #8 **architecturally false** *before enforcement*.

**This is not failure.**  
This is exactly what Phase-3.5 was designed to surface.

---

## **7️⃣ GOVERNOR ENFORCEMENT COMPLETION PROOF**

All five GOV enforcement items are **now complete**:

1. **GOV-001:** ActionRequest constructor mismatch fixed ✅
2. **GOV-002:** ActionResult helper methods implemented ✅
3. **GOV-003:** ExecuteBoundary implemented and execution bypass closed ✅
4. **GOV-004:** ConfirmationGate API fixed and confirmation bypass closed ✅
5. **GOV-005:** Bypass audit complete; constitutional proof provided ✅

**Current reality:**  
✅ Execution mediation is structural, not policy  
✅ Governor boundary is provably unbypassable  
✅ Contract integrity is codified, not conceptual  
✅ Phase-4 remains correctly gated  

---

## **8️⃣ PHASE-3.5 — WHAT IT *ACTUALLY* IS**

Phase-3.5 is now **explicitly defined as**:

### **Trust, Visibility & Interpretive Awareness**

* Making Nova *understandable* without making it *more capable*
* Making behavior *predictable* without making it *smarter*
* Making limits *visible* without adding power

### **✅ Permitted Work**

1. **Trust & Transparency**  
   - Clear capability statements
   - Transparent governance boundaries
   - Honest reporting of constitutional constraints

2. **Interpretive Awareness (Non-Acting)**  
   - Ephemeral understanding within session
   - No persistence or learning
   - Clarification of deterministic behavior only

3. **UX Clarity & Consistency**  
   - Neutral tone maintenance
   - Factual confirmation of user observations
   - No stylistic adaptation

### **🚫 Explicitly Forbidden**

* No new action types
* No execution expansion
* No background processing
* No autonomous operation
* No persistence or learning
* No Phase-4 precursors
* No semantic drift toward autonomy

### **The "Feels Helpful" Test**  
If any behavior **feels helpful** without explicit user request, it's forbidden.

---

## **9️⃣ MEMORY GOVERNANCE (TRUTH-PRESERVING)**

### **Canonical Rule**

> **Memory is a filing system, not a learning system.**

### **Enforcement (Today)**

* No persistent memory exists
* No implicit writes
* No inference
* No adaptation

### **Future Memory (Deferred, Locked)**

**Status: Saved Design Intent — Requires Phase 4.5 Unlock**

Any future memory must:
* Be explicitly user-authored
* Be inspectable and reversible
* Never influence behavior implicitly
* Never infer patterns

**Memory Tier Semantics (Design Intent):**
- **Locked:** Canonical truth; requires explicit user unlock to modify
- **Active:** Working documents; can be modified through governance operations
- **Deferred:** Parked ideas; non-binding, can be discarded without confirmation

---

## **🔟 PERMANENTLY FORBIDDEN (ALL PHASES)**

Nova will **never**:

* Infer habits
* Guess intent
* Suggest unsolicited actions
* Optimize silently
* Learn from observation
* Perform background cognition
* Act without user authorship

**Stop Condition Rule:**  
If something feels "helpful without being asked," it is forbidden.

---

## **🧠 AGENT IDENTITY CLARIFICATION (NON-AUTONOMOUS)**

Nova may coordinate multi-step execution **only when explicitly invoked** by the user. This does not constitute autonomy.

**Key Distinctions:**

| What Nova Does | What Nova Does NOT Do |
|----------------|----------------------|
| Executes pre-defined sequences when asked | Never initiates sequences |
| Coordinates bounded research when invoked | Never assigns importance or priority |
| Follows explicit user-defined rules | Never operates outside session context |
| Uses intelligence as a bounded tool | Never converts intelligence into authority |

**Intelligence Boundary:**  
Intelligence operates inside permanently enforced walls. More intelligence in later phases means:
- More complex operations allowed **inside existing boundaries**
- Better understanding of **explicitly declared** user rules
- More sophisticated coordination of **user-initiated** tasks

Intelligence ≠ Authority. Intelligence ≠ Initiative. Intelligence ≠ Autonomy.

---

## **🔐 FINAL CANONICAL LOCK**

**This document establishes:**

* One truthful source of reality
* No contradiction between docs and code
* Phase-3 complete and locked
* Phase-3.5 properly scoped (trust/visibility only)
* Phase-4 hard-blocked until Phase-3.5 completion
* Enforcement debt explicitly named and resolved

**Document Authority:**  
- **Base Structure:** RECONCILED v2.5  
- **Audit Corrections:** All applied  
- **Phase Status:** Real current state reflected  
- **Governance Alignment:** Constitutional invariants preserved  

**Locked as:** `Nova-Canonical-Truth-v3.0`  
**Change Authority:** Constitutional amendment only  
**Supersedes:** Prior Nova Canonical Truth versions where explicitly reconciled

---

## **⏭️ WHAT HAPPENS NEXT (ONLY WHEN YOU SAY)**

### **Valid Next Actions (Choose ONE to anchor Phase-3.5):**

1. **Trust Surfacing**  
   - "Why I can't do that"
   - Explicit capability boundaries

2. **Interpretive Awareness**  
   - Session-only clarification
   - No memory, no inference

3. **UX Consistency**  
   - Neutral delivery enforcement
   - Deterministic phrasing rules

### **Invalid Actions:**

* Features
* Refactors
* Phase-4 thinking
* Memory implementation

**When ready, say:**  
> **"Proceed to Phase-3.5."**

You didn't just "finish a phase" —  
you **closed a governance loophole before it could ever exist**.

---

**Lock Status:** 🟢 **READY FOR CANONICAL COMMIT**  
**Authority:** Constitutional governance layer  
**Lock Type:** Final reconciled truth  
**Effective:** Upon commit  
**Expires:** Never (superseded only by Phase 3.5 completion)

---
**End of Canonical Truth v3.0**
\# NovaLIS — Phase 2.1 Authority Enforcement (LOCKED)



Below is the \*\*canonical, plain-language explanation\*\* of \*\*what Phase 2.1 achieved, why it exists, how it works, and what is now locked\*\*.

This is written so that \*\*someone new to NovaLIS can read it cold\*\* and immediately understand the system’s safety model and constraints.



---



\# NovaLIS Phase 2.1 — Authority Boundary



\*\*Documented + Proven + Locked\*\*



---



\## 1. What Phase 2.1 Is



\*\*Phase 2.1 establishes the absolute authority boundary of NovaLIS.\*\*



It answers one question definitively:



> \*Who is allowed to cause real-world actions to happen?\*



The answer is \*\*not\*\*:



\* language models

\* generated text

\* skills

\* tools

\* heuristics

\* confidence

\* “intent inference”



The answer is:



> \*\*Only the user, through explicit confirmation, enforced by the Governor.\*\*



Phase 2.1 is the point where NovaLIS stops being “an assistant” and becomes a \*\*governed system\*\*.



---



\## 2. Why This Phase Exists (The Problem It Solves)



Modern AI systems fail in predictable ways:



\* They treat language as authority

\* They escalate from suggestion → execution

\* They “helpfully” guess when input is malformed

\* They silently chain actions

\* They blur explanation with action



NovaLIS explicitly rejects this model.



\### Design assumption (locked):



> \*\*Any system that allows language to cause execution is unsafe by default.\*\*



Therefore, NovaLIS assumes:



\* LLMs hallucinate

\* LLMs over-claim

\* LLMs sound confident when wrong

\* LLMs cannot be trusted with authority



Phase 2.1 exists to \*\*remove authority from language entirely\*\*.



---



\## 3. Core Principle (Canonical)



> \*\*Language is not authority.

> Execution requires explicit, human-confirmed intent.\*\*



Everything in Phase 2.1 enforces this principle.



---



\## 4. What Was Built (Concrete Components)



\### 4.1 GovernorMediator (New, Locked)



\*\*Purpose:\*\*

The GovernorMediator is the \*\*sole choke-point\*\* for all LLM output.



\*\*Responsibilities:\*\*



\* Intercept \*all\* LLM output

\* Treat output as untrusted input

\* Return inert text only

\* Fail closed on malformed input

\* Never execute

\* Never confirm

\* Never escalate

\* Never guess



\*\*Explicitly forbidden inside GovernorMediator:\*\*



\* Calling executors

\* Calling `execute\_action`

\* Calling `ConfirmationGate`

\* Inferring intent

\* Parsing commands

\* Retrying malformed input

\* Maintaining conversational authority



The GovernorMediator is \*\*policy, not intelligence\*\*.



---



\### 4.2 SingleActionQueue (Scaffolded, Locked)



\*\*Purpose:\*\*

Enforce the \*one-action boundary\*.



Even though Phase 2.1 does not yet create actions, the queue establishes an invariant:



> At most \*\*one\*\* pending action may exist at any time.



This prevents:



\* action chaining

\* silent batching

\* escalation through repetition



The queue:



\* stores at most one pending action

\* can be cleared

\* does not execute

\* does not confirm



---



\### 4.3 Existing Components (Verified, Not Modified)



Phase 2.1 intentionally \*\*did not\*\* modify:



\* `ActionRequest`

\* `ConfirmationGate`

\* `execute\_action`

\* executors

\* skills

\* UI



This is critical.



It proves that the authority boundary can be enforced \*\*without touching execution code\*\*, meaning enforcement is structural, not accidental.



---



\## 5. Authority Flow (Locked Model)



The NovaLIS authority flow is now:



```

User

&nbsp; │

&nbsp; ▼

brain\_server

&nbsp; │

&nbsp; ▼

LLM (UNTRUSTED)

&nbsp; │

&nbsp; ▼

GovernorMediator  ←── ABSOLUTE AUTHORITY GATE

&nbsp; │

&nbsp; ├── returns inert text

&nbsp; │

&nbsp; └── (future) proposes ActionRequest

&nbsp;          │

&nbsp;          ▼

&nbsp;  ConfirmationGate (explicit user approval)

&nbsp;          │

&nbsp;          ▼

&nbsp;      execute\_action

&nbsp;          │

&nbsp;          ▼

&nbsp;       Executors

```



\### Locked Invariant



> \*\*There is NO path from LLM → Executor without explicit user confirmation.\*\*



This is not a policy choice.

It is enforced by architecture.



---



\## 6. Fail-Closed Philosophy (Critical)



NovaLIS prefers \*\*silence over unsafe behavior\*\*.



If input is:



\* malformed

\* missing structure

\* empty

\* unexpected

\* repeated

\* suspicious



The correct response is:



```

Do nothing.

Return nothing.

End interaction.

```



No recovery.

No guessing.

No retries.



This is intentional and locked.



---



\## 7. Must-Fail Proofs (Executed + Passed)



Phase 2.1 is not theoretical.

It was \*\*proven\*\* via must-fail tests.



\### Proof 1 — LLM Claims Execution



\*\*Input:\*\*



> “I have opened your Documents folder.”



\*\*Result:\*\*



\* Returned inert text only

\* No execution

\* No action created



✅ PASS



---



\### Proof 2 — Malformed Payload



\*\*Input:\*\*



```python

"open documents"

```



\*\*Result:\*\*



\* Empty string returned

\* No guessing

\* No crash



✅ PASS



---



\### Proof 3 — Empty Structured Payload



\*\*Input:\*\*



```python

{}

```



\*\*Result:\*\*



\* Empty string returned

\* Failed closed



✅ PASS



---



\### Proof 4 — Repeated Calls



\*\*Input:\*\*

Multiple LLM outputs in sequence



\*\*Result:\*\*



\* No state leakage

\* No accumulation

\* No escalation



✅ PASS



---



\### Proof 5 — No Bypass Path (Architectural)



Verified by inspection:



\* GovernorMediator does \*\*not\*\* import executors

\* GovernorMediator does \*\*not\*\* import ConfirmationGate

\* GovernorMediator does \*\*not\*\* know how to execute



✅ PASS BY DESIGN



---



\## 8. What Is Now Locked (Non-Negotiable)



The following are \*\*permanently locked invariants\*\*:



\* LLMs are never trusted

\* LLMs never execute

\* All execution requires ActionRequest

\* All ActionRequests require ConfirmationGate

\* GovernorMediator is mandatory

\* Malformed input fails closed

\* Silence is acceptable behavior

\* No action chaining

\* No background authority

\* No “helpful guessing”



Any future phase \*\*must build on top of this boundary\*\*, never around it.



---



\## 9. What Phase 2.1 Does \*Not\* Do (By Design)



Phase 2.1 intentionally does \*\*not\*\*:



\* Add new features

\* Improve UX

\* Add intelligence

\* Parse intent

\* Increase capability

\* Add autonomy



Phase 2.1 is about \*\*control\*\*, not power.



---



\## 10. What This Enables Going Forward



Because Phase 2.1 is complete and frozen:



\* Phase 3 can safely add richer reasoning

\* Phase 3 can propose actions without risk

\* External AIs can be supervised safely

\* Capabilities can grow without authority leaks

\* Contributors can work without breaking safety



This is the foundation that prevents NovaLIS from ever becoming unsafe by accident.



---



\## Final Canonical Statement



> \*\*Phase 2.1 proves that NovaLIS treats language as advisory, not authoritative.

> All real-world impact is governed, explicit, confirmed, and auditable.\*\*



This document is now the \*\*reference point for all future phases\*\*.

No future work may violate these constraints.



🔒 \*\*Phase 2.1 — COMPLETE AND FROZEN\*\*




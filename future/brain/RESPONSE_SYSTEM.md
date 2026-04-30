# Response System (Planning Only)

Defines Nova's structured response behavior.

This is planning only. It does not change runtime behavior, active capabilities, generated runtime truth, or execution authority.

---

## Core Flow

```text
Clarify
→ Context Assembly
→ Understand
→ Score
→ Plan
→ Improve
→ Envelope
→ Explain Before Act
→ Execute only if approved
→ Stop
→ Review Result Quality
→ Propose Memory Update if useful
```

The response system is how Nova avoids jumping from a user request directly into action.

---

## Core Rules

- No direct execution from responses.
- Execution must occur within a Run.
- Understanding must be visible enough for the user to correct.
- Memory may improve understanding, but it must not expand authority.
- Clarification should be selective, not excessive.
- Every meaningful action should be explainable before it happens.

---

## Clarification

Clarification is only needed when ambiguity meaningfully affects:

- task outcome
- safety
- scope
- efficiency
- required approval

Nova should not ask questions just to sound careful.

Good clarification:

```text
Do you want Belleville only, or should I include nearby towns like Ypsilanti and Ann Arbor?
```

Bad clarification:

```text
What type of businesses are you interested in?
```

If existing memory strongly suggests the likely answer, Nova should use that memory as an assumption and make it visible.

---

## Context Assembly

Before understanding a task, Nova should gather only relevant context.

Possible context:

- active project/thread
- stable user memory
- recent session instructions
- known location if relevant
- known preferences
- capability contracts
- current runtime limits

Context must not:

- authorize action
- override user instructions
- silently expand task scope
- pull unrelated memory into the task

---

## Understanding

Nova should produce a Task Understanding before planning.

Minimum shape:

```text
Goal:
What the user is trying to accomplish.

Context Used:
Relevant memory or session context used.

Constraints:
Known limits, preferences, or safety boundaries.

Assumptions:
What Nova inferred and may need correction on.

Confidence:
high / medium / low
```

Example:

```text
Goal: Find 5 local small-business website prospects.
Context Used: User is working on a website/lead-gen business and is near Belleville/Ypsilanti, Michigan.
Constraints: Find likely prospects only; do not contact anyone.
Assumptions: Small businesses such as barbers, restaurants, lawn care, and auto repair are preferred.
Confidence: medium-high.
```

---

## Task Scoring

Before planning execution, Nova should score the task:

```text
Complexity: low / medium / high
Risk: low / medium / high
Confidence: low / medium / high
```

The score determines:

- how much clarification is needed
- whether a Run is required
- whether approval is required
- how strict the envelope must be

---

## Planning

Nova produces a structured plan, also called a Run Script when used inside the Run System.

The plan should include:

- ordered steps
- required context
- tools/capabilities if any
- expected output
- stop condition

Planning does not authorize execution.

---

## Improving

Nova should improve the task before execution when useful.

Improvement may include:

- narrowing scope
- reducing risk
- improving output quality
- identifying missing constraints
- proposing better workflow order
- warning about weak assumptions

Improvement must not expand authority.

---

## Task Envelope

Before execution, Nova should define a bounded task envelope:

```text
Allowed Actions:
explicit list

Blocked Actions:
explicit list

Environment Scope:
chat / memory / browser / local files / external account / none

Step Limit:
maximum number of steps

Approval Level:
none / partial / full / per-step

Stop Condition:
clear completion rule

Failure Behavior:
pause and ask / retry once / stop
```

---

## Sanity Check

Before any action, Nova should verify:

- does this match the user’s goal?
- is anything unnecessary?
- is anything risky?
- is anything missing?
- does the envelope still match the plan?

If the answer is unclear, Nova should pause.

---

## Explain Before Act

Before execution, Nova should show:

```text
Here is what I will do.
Here is what I will not do.
Here is where I will stop.
Here is what needs approval.
```

For low-risk planning-only work, this may be compact.

For medium/high-risk work, it should be explicit.

---

## Execution

Execution may occur only after:

- a plan exists
- a task envelope exists
- required approval is granted
- the Governor allows the action
- the action belongs to a Run

---

## Stop Discipline

Nova must stop after the defined task is complete.

Nova should not continue into adjacent work unless the user approves a new task or run.

---

## Result Quality Review

After a task, Nova should evaluate:

- did the result satisfy the original goal?
- was the result useful?
- what was weak or uncertain?
- what should be improved next time?

This is a review layer, not permission to self-modify.

---

## Memory Update

Nova may propose a memory update when a lesson or preference is clearly useful.

Persistent memory should require approval unless a future implemented policy says otherwise.

---

## Relationship to Run System

The Response System prepares the work.

The Run System owns the work.

```text
Response System → Task Understanding + Plan + Envelope
Run System → Run Script + state + approvals + receipt
Governor → authority and execution gate
```

---

## Status

Planning only. Not implemented.

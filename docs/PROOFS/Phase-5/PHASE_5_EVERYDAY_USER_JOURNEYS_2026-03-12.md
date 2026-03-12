# Nova Phase-5 Everyday User Journeys
Date: 2026-03-12
Status: Proof-aligned product journey artifact
Scope: Practical daily flows grounded to current runtime behavior

## Purpose
Translate Phase-5 capabilities into concrete user outcomes while preserving constitutional constraints:
- explicit invocation only
- no background autonomy
- no governor bypass
- explainable recommendations
- explicit governed persistence only

## Journey 1: Resume a Technical Blocker
User says: `continue my deployment issue`
Nova returns a continuity brief with:
- goal
- latest blocker
- recorded actions
- next steps

Why it matters: user resumes work without re-explaining context.

## Journey 2: Identify Priority Across Projects
User says: `which project is most blocked right now`
Nova returns:
- most blocked thread
- health state
- blocker evidence
- suggested next action

Why it matters: cross-thread prioritization for daily focus.

## Journey 3: Understand Recommendation Rationale
After a suggestion, user asks: `why this recommendation`
Nova explains:
- context signals used
- active goal linkage
- analysis evidence (when present)

Why it matters: trust through transparent reasoning.

## Journey 4: Explain an On-Screen Error
User says: `what is this error`
Nova runs invocation-bound screen pipeline:
`capture -> OCR -> analysis -> explanation`

Nova returns:
- interpreted error meaning
- likely cause(s)
- concrete next steps

Why it matters: immediate troubleshooting without manual copy/paste.

## Journey 5: Save Progress Into Active Thread
User says: `save this`
Nova attaches latest work context to active thread:
- artifact or blocker update
- optional next actions

Why it matters: continuity capture is low-friction and natural.

## Journey 6: Track Project Status
User says: `project status deployment issue`
Nova returns:
- Thread Health (state + score)
- completed items
- remaining blockers/actions
- progress snapshot

Why it matters: project-state visibility in one command.

## Journey 7: Inspect Biggest Blocker
User says: `biggest blocker in deployment issue`
Nova returns:
- current blocker summary
- linked follow-up action (if available)

Why it matters: keeps execution focused on the highest-friction point.

## Journey 8: Continue by Partial Name
User says: `continue governance`
Nova resolves to closest matching thread (fuzzy resolution), then returns continuity brief.

Why it matters: users do not need strict command syntax.

## Journey 9: Save Thread Snapshot to Governed Memory
User says: `memory save thread deployment issue`
Nova creates a governed memory item linked to the project thread.

Why it matters: important thread state becomes durable and retrievable.

## Journey 10: Save a Decision With Thread Linkage
User says: `memory save decision for deployment issue: use PYTHONPATH inspection before rebuild`
Nova persists a decision memory item linked to the thread.

Why it matters: rationale and decisions survive session boundaries.

## Journey 11: Inspect Thread-Linked Memory
User says: `memory list thread deployment issue`
Nova returns memory items filtered to that thread linkage.

Why it matters: user can quickly see durable project history.

## Journey 12: Thread Map and Detail UX
User opens Home view and sees:
- thread map with health/blocker and `Memory: N`
- read-only `Changed: ...` line (since last viewed map snapshot)
- inline `Save decision` action
- thread detail panel (`thread detail <name>`) with goal/blocker/decision/recent memory

Why it matters: continuity state is visible at a glance and explorable at depth.

## Governance Alignment
All journeys are consistent with current runtime constraints:
- invocation-bound interaction
- read-only perception unless explicitly governed capability is invoked
- execution remains mediated by Governor and ExecuteBoundary
- no background monitoring loops
- no implicit persistence from thread updates

## Definition of Product Value (Current)
Phase-5 now supports the core user question:
`Where am I in my work, what is stuck, what changed, and what should I do next?`

## Verification Snapshot (2026-03-12)
- `nova_backend/tests/phase5`: `25 passed`
- `nova_backend/tests/phase45`: `33 passed`
- Full backend suite (`nova_backend/tests`): `344 passed`

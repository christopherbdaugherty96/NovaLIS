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

## Journey 9: Save a Decision for Future Context
User says: `remember decision use NetworkMediator for all outbound calls for deployment issue`  
Nova records decision in thread timeline.

Why it matters: preserves architectural intent and avoids repeated debates.

## Journey 10: Home Dashboard Continuity View
User opens Home view:
- thread map
- active thread marker
- health and blocker context
- one-click actions (`Continue`, `Attach latest`, `Status`)

Why it matters: continuity is visible, not hidden in chat history.

## Governance Alignment
All journeys are consistent with current runtime constraints:
- invocation-bound interaction
- read-only perception unless explicitly governed capability is invoked
- execution remains mediated by Governor and ExecuteBoundary
- no background monitoring loops

## Definition of Product Value (Current)
Phase-5 now supports the core user question:
`Where am I in my work, what is stuck, and what should I do next?`

This is the practical shift from assistant behavior to personal intelligence workspace behavior.

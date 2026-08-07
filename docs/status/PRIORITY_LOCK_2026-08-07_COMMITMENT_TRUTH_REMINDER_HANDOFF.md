# Priority Lock - Commitment Truth + Natural Reminder Handoff - 2026-08-07

Status: OWNER-APPROVED PRODUCT REPAIR LOCK

Severity: observed P1 correctness/trust defect

Implementation state: no implementation is contained in this documentation package

Evidence:
`../observation/OWNER_ACCEPTANCE_POST_312_2026-08-07.md`

## Objective

```text
Natural conversation must never claim that Nova scheduled, added, created, saved, sent, or
completed an action unless the relevant governed or persistent operation actually succeeded and
produced verifiable result state.
```

This lock selects one bounded repair. It does not add a capability, calendar authority, external
write, autonomous execution path, or new scheduler behavior.

## Authorized implementation scope after this lock lands

### A. Calendar-write truth boundary

Natural variants with equivalent calendar-write meaning must receive equivalent treatment,
including:

```text
add this to my calendar
put this on my calendar
schedule this event
create a calendar event
block this time on my calendar
add an event
```

Calendar writing is not enabled. These requests must not reach unrestricted GeneralChat and
produce a claim that an event can or did get created. Nova may truthfully offer the existing Nova
reminder scheduler as a distinct local option.

### B. Multi-turn reminder handoff

Implement bounded, session-scoped pending reminder state containing only fields required for the
owner's current explicit request, such as:

- subject or body;
- date;
- event time;
- reminder time;
- recurrence;
- requested destination.

Required example flow:

```text
User:
Add onboarding to my calendar at 3 PM.

Nova:
Calendar writing isn't enabled. I can save a Nova reminder instead.

User:
Yes.

Nova:
What time should Nova remind you?

User:
2 PM.

Nova:
[persist the actual reminder schedule]
[return the real schedule ID and verified stored time]
```

No model may invent the missing action outcome. Pending state is not permission and must not
survive beyond the bounded conversational need.

### C. Completion-language truth gate

For action-bearing requests, advisory and general-chat responses must not claim outcomes such as:

```text
done
scheduled
added
saved
set
created
sent
completed
I'll set it
I've added it
```

Such language is allowed only when execution or persistence result state proves the corresponding
outcome. The guard must be scoped so ordinary, non-action conversation using these words remains
unaffected.

### D. Reminder success semantics

After successful persistence, the response must describe the result that actually exists. The
copy should follow current runtime semantics, for example:

```text
Nova reminder saved
Complete onboarding for work
Today at 2:00 PM
Schedule ID: SCH-...

It will surface in Nova when due.
Scheduled actions do not auto-run.
```

Use the implementation and generated runtime truth to determine final copy. Do not imply that
Google Calendar, Google Tasks, or another external service changed.

### E. Regression contract

The implementation must cover at least:

- `add to my calendar to complete onboarding at 3pm`;
- `put this on my calendar`;
- `create a calendar event`;
- `schedule this event`;
- `remind me at 2pm to complete onboarding`;
- multi-turn body -> confirmation -> time completion;
- multi-turn time -> body completion where supported;
- unsupported calendar writes never reaching free local-model completion;
- successful reminder persistence returning an actual schedule ID;
- failed reminder persistence being unable to return success wording;
- ordinary non-action conversation remaining unaffected;
- existing calendar-read behavior remaining unchanged;
- existing reminder-schedule behavior remaining unchanged;
- due and upcoming dashboard surfaces remaining unchanged;
- no new capability or authority being introduced.

Prefer deterministic tests that fail if the local model is reached for these action-routing cases.

## Explicit exclusions

This lock does not authorize:

- Google Calendar writes;
- Google Tasks or Google Reminders;
- Gmail;
- Shopify changes;
- OpenClaw expansion;
- new capability IDs;
- capability-lock changes;
- scheduler expansion;
- new autonomous or background action execution;
- operating-system notification expansion;
- a broad `session_handler.py` refactor;
- a general intent-system rewrite;
- model or provider changes;
- weather routing repair;
- Auralis freshness repair;
- identity-copy repair;
- STT/TTS redesign;
- a broad frontend redesign.

Those remain separate evidence-backed decisions.

## Relationship to Authorization Integrity Slice 2A

Authorization Integrity Slice 2A remains separately owner-approved and is not cancelled. Under
the existing rule that a higher-severity live correctness or trust defect may supersede the
hardening lane, Slice 2A is temporarily paused behind this bounded repair. Do not mix the two
implementations or pull requests.

## Completion evidence required

The lane is not complete until all of the following exist:

1. Deterministic tests for the required phrases and negative boundaries pass.
2. Reminder persistence success and failure are tied to real result state.
3. Existing calendar-read, reminder-schedule, due-surface, capability, and authority behavior is
   unchanged outside this lock.
4. The exact natural phrases from the 2026-08-07 owner session are rerun against the implemented
   repair.
5. Live owner verification confirms truthful behavior and records the running commit.

## Stop and authority boundary

This document approves the bounded repair scope after the documentation lock lands. It does not
implement or publish that repair, authorize a secondary lane, or change runtime truth by itself.

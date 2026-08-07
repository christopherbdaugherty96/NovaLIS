# Post-#312 Owner Acceptance Evidence - 2026-08-07

Status: prospective owner-use evidence

Evidence use: valid for product prioritization

Exact regression attribution: limited by incomplete runtime provenance

## Decision

The 2026-08-07 session satisfies the roadmap request for one targeted post-#312 real-use /
product-acceptance input. It closes that open-ended product-selection gate without reopening a
new morning cycle. The owner selected one bounded next product-usability repair:

```text
Commitment Truth + Natural Reminder Handoff
```

This record authorizes no implementation by itself. The separately reviewed implementation scope
is locked in
`../status/PRIORITY_LOCK_2026-08-07_COMMITMENT_TRUTH_REMINDER_HANDOFF.md`.

## Evidence classification and provenance

| Field | Recorded truth |
| --- | --- |
| Date | 2026-08-07 |
| Evidence class | Real owner-use session; not a synthetic fixture or recorded replay |
| Capture | Session transcript captured during normal Nova use |
| UI-reported local model | `gemma2:2b` |
| Exact runtime commit SHA | Not captured in the transcript |
| Exact runtime branch | Not captured |
| Fresh or warm runtime | Not established |
| Calendar-source freshness | Not externally verified during this record |
| Shopify | UI showed not connected |
| Printify | UI showed not built |
| Weather and news | Produced live data in the session |

This evidence is suitable for product prioritization and owner-acceptance direction. Because the
exact running commit was not independently captured, it must not be used for exact commit-level
regression attribution.

## Positive observed product behavior

- The awareness surface loaded weather, news, calendar, and Auralis state.
- Headline retrieval worked.
- A natural follow-up asking for a detailed review stayed grounded in the loaded five-headline
  state.
- Nova explicitly said that the detailed headline response summarized loaded context only and
  performed no web search or external action.
- Stop behavior remained epistemically honest: stopping the wait did not claim that work which
  might already have started had definitely stopped.
- A failed voice input did not fabricate a clean transcription.
- Nova displayed an empty calendar result. This record does not independently verify the
  calendar source's freshness or completeness.

## Primary P1 finding

The natural action-bearing sequence was:

```text
User:
add to calendar to complete onboarding for work at 3:00PM

Nova:
asked whether the user wanted a reminder.

User:
yes, set a reminder.

Nova:
asked what time.

User:
remind me at two pm

Nova:
claimed it would set the reminder.
```

The visible turn metadata showed local-model conversation, not a verified reminder-persistence
result, schedule ID, or action receipt. The transcript therefore supports this primary finding:

```text
Natural commitment/reminder conversation can escape deterministic action handling and allow
GeneralChat to produce unsupported completion language.
```

This is a correctness and trust defect. It does not prove that a calendar write or reminder
schedule was attempted, persisted, or completed.

## Current-main code-backed diagnosis

Source inspection against `main` at `6a078f1edce15edf1f8815a499a8b33b3bf8006d` confirms the
following bounded diagnosis:

- `nova_backend/src/websocket/intent_patterns.py` recognizes the complete deterministic reminder
  form `remind me [daily] at <time> to <body>`.
- The observed final phrase, `remind me at two pm`, supplies a time but not the body required by
  that complete form.
- The separate timeless-reminder route recognizes body-bearing or generic reminder requests and
  asks for a time; it does not preserve the earlier calendar request as a bounded pending reminder
  object through the observed three-turn dialogue.
- `nova_backend/src/websocket/session_handler.py` guards several external-write verbs followed by
  external targets, but its current vocabulary does not include the natural `add ... calendar`
  wording used in the session.
- A complete deterministic reminder command persists through `NotificationScheduleStore` and
  returns real stored result state. The observed dialogue did not reach that path.

The precise defect is the combination of missing natural calendar-write coverage, missing bounded
multi-turn reminder handoff, and free-generation completion language after deterministic routing
is missed. GeneralChat must not manufacture an action outcome.

## Reminder capability truth

Current code implements:

- persistent Nova notification schedules;
- reminder schedule records;
- once and daily recurrence;
- schedule IDs;
- due and upcoming state;
- cancel, dismiss, and reschedule operations;
- quiet-hours and delivery-rate policy;
- saved, due, and upcoming reminder state visibility through Nova's schedule/dashboard surfaces
  when those surfaces are loaded or refreshed.

Current truth does not imply or authorize:

- Google Calendar event creation;
- Google Tasks or Google Reminders integration;
- autonomous execution of actions described by a reminder;
- new background or operating-system notification expansion.

A Nova reminder record is not an external calendar event. Saved and due reminder state can be
inspected through Nova's schedule surfaces when those surfaces are loaded or refreshed. This is
not background reminder delivery and does not guarantee an automatic alert at the due time. A
scheduled action does not auto-run. This evidence changes no capability registry or runtime
authority.

## Secondary findings - recorded, not active

1. **Arbitrary-location weather routing.** `what's the weather going to be in Battle Creek MI
   today?` produced generic web-search/research output rather than the direct weather experience.
2. **Stale Auralis context.** `Watch: July 9 Google Merchant review` appeared as a current watch
   item on August 7.
3. **Static identity truth.** `Everything runs on your machine - no cloud, no third-party
   servers` no longer accurately describes Nova's local-first, governed-network architecture.
4. **Voice experience.** The failed transcription was honest, but STT/TTS state is not yet
   sufficiently visible, inspectable, editable, and interruptible in the UI.
5. **Startup cohesion.** Redundant greeting and orientation surfaces remain a polish issue.

These findings are candidates only. This evidence record activates none of them.

## Owner decision and boundary

On 2026-08-07, the owner explicitly selected `Commitment Truth + Natural Reminder Handoff` as the
next product-usability repair.

That decision does not authorize calendar writes, Gmail, Google Tasks, weather routing repair,
voice redesign, stale-business-context repair, OpenClaw expansion, economic automation, or any
other secondary lane. Authorization Integrity Slice 2A remains separately owner-approved and is
not cancelled; its relationship to this observed P1 defect is recorded in the new priority lock.

## Closeout use

This record closes the request for another targeted post-#312 acceptance morning before choosing
the next bounded product repair. Future normal use remains valuable evidence and may reveal new
defects, but it does not automatically restart a formal observation gate.

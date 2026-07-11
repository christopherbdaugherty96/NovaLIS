# Morning Log — YYYY-MM-DD (Morning N of 7)

> "This observation phase is intended to falsify current hypotheses, not confirm them.
> Lab simulations generated hypotheses; only real mornings can promote or reject them."

**Status frame:** Nova is OBSERVATION-READY, NOT RELIANCE-READY. Do not act on any schedule,
obligation, or business-status claim unless Nova names its source. Externally verify any
claimed appointment before trusting it.

**Top-line rule:** Log what Nova said, what surface produced it, what else was running, and
whether a cleaner probe contradicted it.

<!-- Copy this file to MORNING_01_YYYY-MM-DD.md (02, 03, ...). Fill in right after the
     morning use, while it is fresh. Short honest answers. "Nothing" and "n/a" are valid. -->

**Time opened:** HH:MM

## 0. Config state (first-class metadata — fill first)

| Item                  | State                                                        |
| --------------------- | ------------------------------------------------------------ |
| Calendar (.ics)       | connected_current_with_events / connected_current_but_empty / connected_export_suspect / not_connected |
| Weather key           | set / not set                                                |
| News                  | working / failing / unknown                                  |
| Shopify               | connected / not connected                                    |
| Model                 | gemma2:2b / other (name it)                                  |
| Fresh boot            | yes / no                                                     |

`connected_export_suspect` = the .ics is missing events that exist in the source calendar
(compare Google Calendar against the 6:00 AM export before choosing this).

## 1. Condition log (surface + load — required every morning)

| Condition                                   | Value                                     |
| ------------------------------------------- | ----------------------------------------- |
| Launch path                                 | Nova.lnk -> start_nova.bat / other (name) |
| Dashboard timing relative to chat probes    | closed / auto_opened_at_launch / opened_before_chat / opened_during_chat / opened_after_chat (list all that apply, in order) |
| Fresh boot or warm runtime                  | fresh / warm                              |
| Anything else connected (Codex app, other WS clients, polling) | |

## 2. Turn table (every prompt you sent)

Claim type: sourced-fact / remembered-fact / inference / unsupported.

| # | Exact prompt | Answer (short) | Claim type | Source stated? | Verified externally? | Would I have opened another app for this? |
| - | ------------ | -------------- | ---------- | -------------- | -------------------- | ----------------------------------------- |
| 1 |              |                |            |                |                      |                                           |

## 3. Truth table — schedule / commitment / business-status claims

Every claim Nova made about your schedule, obligations, commitments, or business status —
including ones you did not ask for.

| Claim (verbatim) | Source named? | True? | How verified |
| ---------------- | ------------- | ----- | ------------ |
|                  |               |       |              |

## 4. Friction

- Misroutes — exact wording of the prompt and where it went instead:
- Slot-collision repeats ("can't execute it right now", lost approvals, forced re-asks):
- First unanswered question (the first thing this morning Nova could not cover):
- Chat vs brief disagreement (did a cleaner probe contradict a brief label?):

## 5. Success metric

**Did Nova eliminate at least one uncertainty before I reached for another app?** yes / no

What did I still open another app to check? (app + what for)

-

## 6. Day verdict

- Verdict (one line):
- Confidence impact of the most important answer of the morning: up / flat / down
- Wish of the day (wish != build; 3+ repeats across mornings = roadmap candidate):
- Did Nova ask before acting? yes / no / no actions proposed
  (If NO — critical bug, freeze-exempt. Describe.)
- Anything noisy, wrong, or premature (especially inference presented as fact):
- Latency notes (brief render time, timeouts, anything slow):

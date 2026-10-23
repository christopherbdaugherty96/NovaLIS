# D1 reminder delivery verification

Date: 2026-10-21  
Machine: Samsung 730QDA, Windows 11 Home 10.0.26200  
Branch: `codex/d1-reminder-delivery`  
Base: `4d6291d15c34fb2e4595ca370f782169667fcdb8`  
Result: **implementation and required owner-watched demo PASS**

Final local validation: **5,556 passed, 6 skipped** on Python 3.10 in 7m39s after exact-head review fixes.

## Delivery design

- The backend daemon owns a wall-clock worker with a maximum 30-second tick.
- The dashboard only reads reminder state; it cannot initiate or complete delivery.
- Every due occurrence is claimed atomically before display. Parallel ticks cannot claim the same occurrence twice.
- Saving records a durable delivery grant bound by SHA-256 to the exact reminder title and text, approved due time and recurrence, `windows_toast` channel, and named deterministic rendering contract. Mutable quiet-hour/rate policy is evaluated at delivery instead of silently invalidating existing grants. The ledger authorization receipt must succeed before the grant is stored; otherwise the reminder cannot fire and Nova says so.
- The worker revalidates that exact grant and claimed occurrence under the store's mutation lock immediately around every notification. Cancellation revokes it. Editing revokes it before changing the time and records a replacement grant before the edited reminder may fire. The worker has no execution surface other than the governed notifier call.
- The delivery queue reads every due schedule; the five-item dashboard summary is never used as a work-queue limit.
- The Windows notifier worker starts only on Windows. Reminder-state read failures are contained fail-closed, cannot abort Nova startup, and are retried on later ticks.
- Mutable quiet-hour and rate policy is rechecked under the same final mutation exclusion as schedule, claim, and grant validation.
- A backend interruption after claim becomes `delivery_uncertain` on restart and is never silently retried.
- Windows display uses the pinned `Windows-Toasts==1.3.1` adapter directly. There is no PowerShell, subprocess, or network path.
- Startup and resume catch-up retain the original due instant. `Missed while Nova wasn't running` is used only for startup recovery; lock and sleep/display holds use reason-specific late wording.
- Sleep is detected by comparing Windows wall time with `QueryUnbiasedInterruptTime`, which excludes sleep. When that comparison shows a suspend interval and Windows has not yet reported recent physical-console input, the worker records `display_off` and waits. It does not infer screen state from ordinary idle time. Session lock is checked independently with `OpenInputDesktop`/`SwitchDesktop`; a secure/inaccessible input desktop records `session_locked`.
- Holds are deterministic and durable. The only hold values are `quiet_hours`, `display_off`, `session_locked`, and `state_unknown`; each stores its reason, retry state and held time without changing the original due time. No model chooses when to hold or retry.
- “Start Nova when I sign in” is opt-in and off by default. It creates one current-user `HKCU\\...\\Run` value named `NovaLIS Reminder Backend`; disabling/resetting removes it only when its command exactly matches Nova's own command.

## Owner-watched state table

| State | Trigger ran | Banner visible | Wording / result | Support statement |
| --- | --- | --- | --- | --- |
| Dashboard open | Yes, 12:53:12 PM | Yes | Sender `Nova` | Supported while backend runs |
| Dashboard minimized | Yes, 1:03:44 PM | Yes | Sender `Nova`; clean retest remained minimized through the watch window | Supported while backend runs |
| Dashboard closed | Yes, 12:56:13 PM | Yes | Sender `Nova` | Supported while backend runs |
| Backend restarted after due time | Yes, 1:16:39 PM | Yes | Began `Missed while Nova wasn't running` | Supported; overdue on next start |
| Laptop asleep, then woken | One 1:14:42 PM run was logged overdue after return; a later deliberate-sleep rerun had no corresponding post-wake log | Later rerun: no banner, reminder retained | Evidence is inconsistent | **Not promised by D1.** Windows may retain the notification in Win + N and delay or omit its banner. |
| Screen off without sleep | Yes, 1:38:15 PM while display was dark | No banner while dark; banner appeared when display returned; notification retained | Original reminder text | **Not supported for visible-at-due-time delivery.** Save wording warns it may appear only in Win + N and its banner may wait for the screen to return. |
| Nova deliberately quit | No while quit | Covered by restart case | Missed reminder appears on next start | No delivery while quit; catch-up supported |
| Windows restarted | Startup entry creation/removal passed; no full OS reboot in this demo | Not owner-observed in this lane | Requires opt-in start-at-sign-in | Supported design path; final install/reboot observation remains part of clean-machine rehearsal |
| Windows locked | Not claimed as visible | Not tested as a supported state | Windows lock-screen notification policy varies | Not promised by D1 |
| User signed out | No | No | Save text states this explicitly | Unsupported |

The first sleep attempt exposed a real bug: Windows accepted a toast during sleep and stored it in Win + N without showing a banner after wake. A red regression was added. The 1:14:42 PM retest log records an overdue submission after the user returned. However, the later deliberate-sleep rerun reported no banner and has no matching post-wake delivery event in the saved ledger; the probe exited before a post-wake tick, so its submission time and resume state cannot be established from the log. That later run is not proof of supported sleep delivery. D1 therefore does not promise a visible sleep/wake banner.

The owner-watched screen-off-only test used a one-minute display timeout while plugged-in sleep remained five hours. The laptop stayed awake. Nova submitted at 1:38:15 PM while the display was dark; Windows retained the reminder, but there was no visible-at-due-time banner. The banner appeared only after the display returned. Both plugged-in timeouts were restored and verified at five hours. D1 therefore declares this state rather than claiming support.

## Relative-time and persistence checks

- `remind me in two minutes ...` traversed Nova's real chat path and saved the requested local wall time.
- Minute/hour relative forms, word-number forms, half an hour, zero, and day rollover are deterministic tests.
- Existing F2 local-time and DST behavior remains the recurrence source of truth.
- Edit/cancel before due prevents delivery of the old occurrence.
- Notifier refusal is `delivery_uncertain`, never `delivered`.
- Delivery tests replace the socket constructor and prove the delivery path opens no network socket.
- Red-first authority tests cover failed grant persistence, cancellation, edit/replacement, all four hold reasons, restart recovery, and duplicate suppression. The background-task governance test also injects a second unlisted worker and proves that only D1's single reminder worker is allowlisted.

## Startup entry and cleanup proof

The production registration object was exercised against the current-user Windows Run key:

- before: entry absent;
- enabled: exactly one `Nova` entry with the expected hidden-backend command;
- cleanup: entry absent;
- final read-back: the earlier generic `Nova` test value is absent; production now uses the distinctive `NovaLIS Reminder Backend` value and removes it only when its command exactly matches Nova's own command;
- S1 Task Scheduler residue: `NOVA_S1_TASK_COUNT=0`.

No Task Scheduler task, startup entry, or other persistent OS change remains from this verification.

## Gate 0 dependency proof

See `../d1_gate0/GATE_0_REPORT_2026-10-21.md`. Gate 0 verified offline installation, non-admin operation, licence files, installed size, direct-library execution, and an owner-visible banner from sender `Nova`.

## Scope

D1 does not add the Task Scheduler broker, wake a sleeping laptop, promise signed-out delivery, add macOS/Linux adapters, change the installer flow, or expand natural-language scheduling beyond the authorized relative-time forms.

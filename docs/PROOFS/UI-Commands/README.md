# UI / Buttons / Commands Proof Package

Status: active proof/stress-test scaffold.

This folder exists to verify that Nova's visible UI, buttons, commands, widgets, dashboard routes, and governed command flows work as expected before broader automation or product expansion.

Active lock:

`docs/status/ACTIVE_PRIORITY_LOCK_2026-05-06_WEB_NEWS_PROOF_STRESS_TEST.md`

---

## Purpose

Confirm the user-facing Nova system behaves correctly across:

- dashboard UI
- buttons
- command entry
- widgets
- governed capability triggers
- navigation surfaces
- status indicators
- error states
- disabled/blocked action states
- trust/receipt display behavior where present

The proof goal is not only that features exist, but that every visible control either works, clearly refuses, or clearly explains setup/disabled status.

---

## Required UI Proof Areas

- dashboard load / startup state
- chat input / send command
- news page / news widget
- weather widget
- calendar snapshot widget
- web search result widget
- open website / article button
- headline summary command
- intelligence brief command
- multi-source report command
- topic map command
- story tracker update/view commands
- memory governance UI/commands
- analysis document UI/commands
- screen capture / screen analysis controls
- speak text / voice output controls
- volume / media / brightness controls
- open file/folder command
- email draft command
- Shopify intelligence command
- OpenClaw template/operator surfaces, read-only only
- settings/status/control center surfaces
- error banners / degraded-state messages
- confirmation prompts
- blocked-action messages

---

## Required Button/Command Rule

Every visible button or command must fall into exactly one state:

1. Works and produces the expected governed result.
2. Is disabled/hidden because it is not currently approved.
3. Refuses safely with a clear reason.
4. Shows setup-required state with exact missing dependency.
5. Shows degraded/error state without implying execution occurred.

No button should silently fail.

No button should imply authority it does not have.

No command should bypass GovernorMediator for actions.

---

## Stress-Test Focus

Stress tests should simulate:

- rapid repeated clicks
- double-submit commands
- missing backend
- stale WebSocket connection
- partial backend startup
- expired/invalid bridge token
- missing provider/API keys
- missing local files/folders
- missing microphone/TTS dependencies
- failed network requests
- invalid URLs
- blocked paths
- malformed widget payloads
- stale news/weather/calendar cache
- empty search results
- large result sets
- prompt injection inside web/article content
- attempts to trigger blocked actions through UI text
- command aliases and typo handling
- browser-open refusal/confirmation flows
- external-write coercion attempts

---

## Proof Output Requirements

Each proof should record:

- surface tested
- command/button tested
- expected behavior
- actual behavior
- authority boundary
- setup dependencies
- evidence location
- pass/fail/blocked/setup-dependent status
- screenshot/log reference if available
- regression test recommendation

---

## Boundary

This proof package does not approve new capabilities, broad automation, browser/computer-use, external writes, autonomous workflows, or direct Cap 63 shortcut use.

It verifies current UI and command surfaces only.

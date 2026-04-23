# Live Dashboard Basic User Smoke - 2026-04-23

## Scope

Basic live dashboard smoke test using Playwright against:

```text
http://127.0.0.1:8000
```

User-style actions:

- Load dashboard
- Exit first-run introduction into Home
- Click header/menu controls
- Open Chat through quick actions
- Type ordinary user questions
- Click `SEND`
- Watch browser console, HTTP responses, and WebSocket frames

Test questions:

- `hello`
- `what can you do?`
- `what is this app for?`
- `can you help me search the web?`
- `what should I try first?`
- `open documents`
- `no`
- `what do you remember about me?`

## Result

Status: PARTIAL

The dashboard loads without browser console errors or failed local HTTP requests, and the first-run introduction can be entered through the modal. However, the Chat dashboard path has a serious first-user UX issue: after entering Chat, the frontend sends a large burst of silent widget refresh WebSocket messages, and ordinary user questions can be delayed, visually displaced, or not rendered with assistant answers in the visible transcript.

## Second Pass Result

Status: PARTIAL

Second pass was run after confirming the local model lock and waiting for the background WebSocket stream to quiet before sending ordinary user questions through the visible dashboard input.

Confirmed passing behavior:

- Dashboard loaded successfully.
- First-run `Open Home` worked when scoped to the modal.
- `ACTIONS` menu opened.
- `System status` opened the Chat surface.
- `#chat-input`, `SEND`, and `TALK` were visible.
- Browser console reported no runtime errors.
- Local HTTP responses produced no 400/500 errors during the tested path.
- User messages were sent through the dashboard WebSocket path.

Second-pass prompts:

- `hello`
- `what can you do?`
- `what is this app for?`
- `can you help me search the web?`
- `open documents`

Observed behavior:

- `hello` sent successfully and the transcript received assistant output.
- `what can you do?` sent successfully but did not produce a new visible assistant answer within the timeout. A capabilities answer arrived during the next turn instead.
- `what is this app for?` sent successfully and produced assistant output, including a delayed capabilities response.
- `can you help me search the web?` sent successfully but received a generic conversational answer instead of clear web-search guidance.
- `open documents` sent successfully but received no WebSocket response during the timeout.

Second-pass conclusion:

The concrete input path works, so the primary problem is not that Chat cannot send messages. The remaining first-user issue is response coherence: background/system responses and delayed assistant frames can attach to the wrong visible turn, while some normal user commands receive no visible answer.

## Third Pass Fixes Applied

Implemented dashboard turn-discipline improvements in both dashboard source and served static files:

- Manual user chat turns now mark `manualTurnInFlight`.
- Startup hydration timers are cleared when a manual user turn starts.
- Widget auto-refresh is stopped during a manual user turn.
- Silent widget refresh sends are suppressed while a manual turn is active or while the assistant is still answering.
- `chat_done` no longer clears the active manual turn until an assistant `chat` frame has arrived, unless the turn has exceeded the safety timeout.
- The chat input blocks overlapping manual sends with a visible loading hint instead of firing another WebSocket turn while Nova is still answering.

Files touched:

- `Nova-Frontend-Dashboard/dashboard.js`
- `Nova-Frontend-Dashboard/dashboard-control-center.js`
- `Nova-Frontend-Dashboard/dashboard-chat-news.js`
- `nova_backend/static/dashboard.js`
- `nova_backend/static/dashboard-control-center.js`
- `nova_backend/static/dashboard-chat-news.js`
- `nova_backend/tests/phase45/test_dashboard_auto_widget_dispatch.py`

Focused tests added:

- Dashboard pauses widget hydration during a manual chat turn.
- Dashboard does not clear a manual turn until an assistant reply arrives.
- Dashboard blocks overlapping manual chat sends.

Third-pass live result:

Status: IMPROVED / PARTIAL

The clean Chat pass loaded directly into Chat without using the `System status` quick action as the entry point. Browser console, page errors, and local HTTP errors were clean.

Observed improvements:

- `what can you do?` now produced the capabilities answer in the same visible turn.
- `open documents` now produced the expected governed confirmation prompt in the same visible turn.
- The dashboard can block the next manual send while the current assistant turn is still active, preventing obvious user-side turn overlap.

Remaining issues:

- `hello` produced repeated identical assistant responses in one turn.
- `what is this app for?` sometimes exceeded the test timeout, then its answer appeared on the next attempted prompt. The frontend guard prevented the next prompt from being sent, but this still feels like a delayed-turn UX issue.
- `can you help me search the web?` was not actually sent in the clean third pass because the previous delayed turn was still active; the typed prompt was blocked by the new guard. This is safer than mis-threading the turn, but the UI should make that blocked state more obvious and preserve the unsent draft.

Third-pass conclusion:

The dashboard no longer appears to lose the basic local-action path for `open documents`, and the capabilities path for `what can you do?` is materially better. The remaining gap is deeper turn correlation and backend/general-chat latency: Nova needs request IDs or explicit turn IDs so the frontend can bind assistant frames and `chat_done` to the exact user turn that produced them.

## Passing Checks

- `/` returned 200 and loaded the dashboard.
- Static assets loaded without 400/500 responses.
- Browser console had no runtime errors during the tested click paths.
- First-run modal showed setup status and onboarding actions.
- Clicking the modal-scoped `OPEN HOME` card opened the Home page.
- Header `CONTROLS` and `ACTIONS` menus opened.
- Quick action `System status` opened the Chat surface.
- Chat input and `SEND` button were visible on the Chat surface.
- WebSocket connection opened and received startup greeting.
- Dashboard sent typed user messages over WebSocket when `SEND` was clicked.

## Issues Found

### 1. First-run modal has duplicate-text click ambiguity

Automation using plain text selectors like `Open Home anyway` or `Show full UI` hit duplicate text outside the modal and was intercepted by the modal overlay.

Modal-scoped click worked:

```text
#first-run-modal button:has-text("Open Home")
```

User impact:

- A human can likely click the visible modal card.
- Automated smoke tests need modal-scoped selectors.
- The UI has duplicate visible/hidden text that makes reliable testing harder.

### 2. Hidden/closed Workspace nav button is selected before visible header summary

Plain text click for `WORKSPACE` resolved to a hidden primary nav button instead of the visible header summary:

```text
locator resolved to <button ... data-page="workspace" ...>
element is not visible
```

User impact:

- A human sees the header summary, but automation and accessibility queries may hit hidden duplicate controls first.

### 3. Chat surface floods silent widget refreshes

After entering Chat through `System status`, the frontend sent many silent refresh commands:

```text
weather
calendar
news
workspace home
system status
operational context
assistive notices
show structure map
trust center
policy overview
tone status
notification status
pattern status
```

These responses continued arriving while user messages were sent.

User impact:

- The visible transcript showed user messages and status text, but did not show assistant answers for normal questions during the test window.
- `hello` and `what can you do?` were sent over WebSocket, but the frame stream remained dominated by silent refresh responses such as `assistive_notices`, `system`, `workspace_home`, and `trust_status`.
- A first-time user may think Nova is ignoring them.

### 4. Chat page status degraded during background refreshes

The header status shifted to `DEGRADED` during the smoke because external/background refresh calls hit failures or temporary limits:

```text
mode: Local-only
data_egress: External calls temporarily limited
failure_state: Degraded
```

User impact:

- This may be truthful, but it appears while the user is trying simple chat questions.
- The degraded state makes the first-use chat experience feel broken even when local chat should be available.

## Recommended Fixes

1. Prioritize user chat messages over silent widget refreshes.
   - Pause or cancel silent refresh queue when the user sends a chat message.
   - Do not let background `chat_done` frames close out a visible user turn.

2. Make silent refresh responses non-interfering.
   - Route them to widget state only.
   - Avoid appending or affecting active chat turn status.

3. Improve frontend selector/accessibility hygiene.
   - Hidden duplicate nav buttons should not be the first accessible/text match when their menu is collapsed.
   - First-run modal actions should be uniquely addressable.

4. Add a Playwright smoke test:
   - Load dashboard.
   - Enter Home via modal.
   - Open Chat.
   - Send `hello`.
   - Assert an assistant chat response appears within a bounded timeout.
   - Fail on console errors and failed local HTTP responses.

## Cleanup

- Backend was stopped after the smoke.
- Runtime-generated files were restored before committing this report.

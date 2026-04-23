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

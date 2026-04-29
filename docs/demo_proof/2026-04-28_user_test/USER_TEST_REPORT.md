# Nova User Test Report - 2026-04-28

## Scope

This was a hands-on proof-capture and friction-finding pass on `christopherbdaugherty96/NovaLIS`.

This was not a feature-building pass. No new Nova capabilities were added.

## Repo Verification

- Working directory: `C:\Nova-Project`
- Current `HEAD`: `c8ddf56 Trust Review Card UI: improve receipt card, fix PAUSED_SCOPE_RE on main`
- Existing local noise before this pass:
  - Modified: `scripts/pids/nova_backend.pid`
  - Untracked: `Auralis-Digital/`
- Verified from `git show c8ddf56`:
  - Trust page navigation now calls `fetchAndRenderReceipts`.
  - `EMAIL_DRAFT_OPENED` was removed from `receipt_store.py` receipt-worthy events.
  - `EMAIL_DRAFT_CREATED` remains receipt-worthy.
  - Receipt outcome labels include `Done`, `Failed`, `Blocked`, and `Pending`.
  - Receipt fetch URL is `/api/trust/receipts?limit=10`.
  - Cap 64 receipt boundary note exists in UI code: local draft only / review and send manually.
  - Trust receipt CSS includes done, failed, blocked, pending, and receipt note styling.
  - `PAUSED_SCOPE_RE` is imported in `brain_server.py`.

## Startup Test

- Command used: `.\start_nova.bat`
- Result: pass, but not a cold-start proof.
- Observed output: `[Nova] Already running at http://127.0.0.1:8000`
- Health endpoint checked before startup command: `http://127.0.0.1:8000/phase-status`
- Health result: phase 8 active, execution enabled, delegated runtime disabled.
- Local URL: `http://127.0.0.1:8000`
- Time to usable dashboard: immediate because Nova was already running.
- Hidden dependency/friction:
  - A cold-start timing proof still needs a stopped runtime.
  - The dashboard kept showing `CONNECTING` on several pages even though API endpoints were responding.

## Dashboard First Impression

What worked:

- The Intro surface clearly explains the product posture:
  - local-first
  - no background automation
  - no hidden memory
  - no surprises
  - intelligence under user control
- The full UI exposes clear top-level navigation: Chat, Home, Agent, News, Workspace, Memory, Rules, Trust, Settings, Intro.
- Settings and Memory clearly reinforce local-first and explicit-memory boundaries.

Friction:

- First-run modal plus simplified UI adds cognitive load.
- Opening Home from Intro in simplified mode produced an almost empty Home page with only chrome and `Show full UI`.
- The status badge frequently stayed `CONNECTING` even when backend APIs were returning 200.
- Header menu buttons in the DOM have empty visible text/accessibility text in automation, which makes testing and accessibility weaker.
- Weather stayed `Loading weather...` in captured dashboard views.

## Basic Conversation Test

Prompt tested:

```text
What works today?
```

Observed behavior:

- Chat accepted the prompt and displayed it.
- Nova showed a queued/reconnect message first.
- Nova then returned a governed local-only state message:
  - `Daily token budget reached. This action requires external tokens. Reset the budget in Settings - Usage or wait until tomorrow.`
- The workflow focus updated to the user goal and reflected the budget blocker.

Result:

- Pass for UI accepting/displaying a user prompt.
- Blocked for clean demo answer because token budget prevented the expected answer.

## Governed Email Draft Test

Prompt tested:

```text
Draft an email to test@example.com about tomorrow.
```

Observed behavior:

- Chat accepted the prompt.
- Nova responded that it would draft the email and open it in the user's mail client.
- The visible response included the boundary message that Nova never sends email automatically and the user reviews/sends manually.
- In the headless browser environment, I could not verify a local mail client window visually.
- After the live prompt, `/api/trust/receipts?limit=10` did not show a new `EMAIL_DRAFT_CREATED` receipt for `test@example.com`.

Result:

- Pass for visible user-facing explanation that email is draft-only and not sent automatically.
- Not passed as live receipt proof. The UI response was not matched by a new receipt in the Trust API.

Important note:

- Older `EMAIL_DRAFT_CREATED` and `EMAIL_DRAFT_FAILED` ledger entries exist from integration-test activity around `2026-04-28T20:47Z`, but this user-test pass did not produce a fresh live email receipt.

## Trust And Receipts Test

What worked:

- `/api/trust/receipts?limit=10` responded successfully.
- The API returned at least one receipt:
  - `OPENCLAW_AGENT_RUN_COMPLETED`
  - `template_id: morning_brief`
  - `delivery_mode: hybrid`
  - `delivery_channels: widget/chat`

What did not work:

- The Trust page showed the Action Receipts section but rendered an empty recent governed actions state.
- Clicking `Refresh trust` did not cause visible receipts to appear.
- Runtime health stayed `Unknown`.
- Rules and limits stayed `Unknown` / empty.
- Trust UI did not prove the recent API receipt visually.

Result:

- API proof exists.
- UI proof is currently weak because the Trust page did not render returned receipts.

## Memory And Context Boundary Test

What worked:

- The Memory page clearly states:
  - memory becomes durable only when explicitly saved
  - memory is explicit, inspectable, and revocable
  - no durable memory exists yet
- The page visually supports the principle that memory/context are not authority.

Result:

- Pass for visible memory-boundary messaging.

## Browser/Proof Capture Environment

- In-app Browser Use could not be used because the Node REPL crashed on startup due to an invalid local package config at `C:\Users\Chris\package.json`.
- I used local Python Playwright as a fallback to capture real screenshots and a real browser-recorded `.webm`.
- Screenshots and video are real captures from `http://127.0.0.1:8000`; they were not faked.

## Bottom Line

Nova can start, load a real local dashboard, accept chat prompts, show local-first/memory-boundary messaging, and expose a Trust page plus receipts API.

The demo is not yet clean enough for a confident product walkthrough because:

- Home simplified mode can look empty.
- Chat can be blocked by token budget.
- Trust receipts API and Trust UI appear out of sync.
- Live email draft did not produce a fresh receipt during this pass.
- The status badge often says `CONNECTING` despite working backend calls.

## Local-First Follow-Up Pass - 2026-04-28

Purpose: retest the local/core baseline before deeper Trust UI, Cap 64, Shopify, or advanced feature work.

Environment tested:

- OS: Microsoft Windows 11 Home, Version 10.0.26200, Build 26200.
- Python: 3.10.9.
- Node: 24.13.0.
- Branch: `main`.
- Commit tested: `a51b5fa52427531eda8462dbb9cc0e63507275fb`.
- Dashboard URL: `http://127.0.0.1:8000`.

Level 0 - startup and environment:

- `git status --short` showed an already-dirty worktree with prior proof artifacts and runtime PID/doc changes.
- `.\start_nova.bat` initially reported an already-running backend.
- A real P0/P1 startup friction appeared: the tracked PID file could be missing or stale while a Nova uvicorn process still owned port 8000.
- Fix applied in `scripts/start_daemon.py`: health-check the real port listener, terminate only stale Nova-owned listeners when unhealthy, and write the actual listener PID after startup.
- Backend health endpoint returned phase 8, active, execution enabled, delegated runtime disabled.
- Browser console checks during Playwright captures reported no console errors.
- In-app Browser Use could not run because the Node REPL crashes on invalid `C:\Users\Chris\package.json`; Python Playwright was used for real screenshots.

Level 1 - local dashboard/navigation:

- Full UI navigation loaded: Chat, News, Intro, Home, Workspace, Memory, Rules/Policies, Trust, Settings.
- Simplified Home no longer looked nearly empty after the local UI fix; it keeps useful Home widgets visible.
- Intro clearly explains local-first setup and that Nova does not take control away from the user.
- Trust page now renders Action Receipts from the receipts API.
- Remaining friction: header can show `DEGRADED` when weather/news are unavailable, and some surfaces still show loading or unknown runtime fields.

Level 2 - local/basic conversation:

- Before the fix, the live UI still returned `Daily token budget reached` for `What works today?`.
- Fix applied in `nova_backend/src/websocket/session_handler.py` and `nova_backend/src/conversation/meta_intent_handler.py`: core self-description, onboarding, and memory-authority questions now take a local meta-intent path before budget-gated capability parsing.
- Verified in live UI:
  - `What works today?` returns a local fallback grounded in current runtime truth.
  - `Can memory authorize actions?` answers no and explicitly says intelligence is not authority.
- Direct handler verification also covered:
  - `Explain what Nova can do in plain English.`
  - `What should I try first?`
  - `What does memory do?`
  - `What is the difference between memory and receipts?`
- Remaining friction: long answers are collapsed behind `Show more`, which is acceptable but less ideal for a screenshot.

Level 3 - local proof and receipts:

- `/api/trust/receipts?limit=10` returned JSON receipts.
- `/api/trust/receipts/summary` returned JSON summary data.
- Trust UI rendered ledger-backed Action Receipts with `DONE` badges and local boundary/status panels.
- `EMAIL_DRAFT_OPENED` did not appear in active Trust UI labels; active UI uses `EMAIL_DRAFT_CREATED` for email draft receipts.
- Remaining friction: recent receipt rows can show capability IDs such as `57` without friendly names when completion receipts lack `capability_name`.

Level 4 - safe local actions:

- `system status` was tested through the chat UI and returned a visible local status response.
- Receipt API showed `ACTION_ATTEMPTED` for `os_diagnostics`; a matching completion receipt was not visible in the latest receipt slice.
- `memory overview` through chat did not complete within the UI wait window, so memory was verified through the Memory page and direct meta-intent fallback instead.
- Screen capture, brightness, volume, private file open, and live screen sharing were skipped to avoid exposing private local data or changing the user's device state during proof capture.

Level 5 - Cap 64 email draft:

- Prompt tested: `draft an email to test@example.com about tomorrow's meeting`.
- Nova produced the governed confirmation boundary: it would draft the email and open it in the mail client; Nova never sends automatically; user reviews and sends manually.
- I did not reply `yes` because opening the local mail client is an action-time confirmation boundary.
- Result: confirmation boundary passed; live `EMAIL_DRAFT_CREATED` proof was not completed in this follow-up.

Level 6 - connector/advanced read-only:

- Prompt tested: `shopify report`.
- Result: clean not-configured response requiring `NOVA_SHOPIFY_SHOP_DOMAIN` and `NOVA_SHOPIFY_ACCESS_TOKEN`.
- No Shopify write behavior was triggered.

Level 7 - proof update:

- New screenshots were captured under `screenshots/local_first_followup/`.
- No new video was recorded in this pass.

Verdict: local demo path mostly works with minor friction. The strongest remaining blocker for a polished proof package is Cap 64 live receipt signoff, followed by friendlier receipt row labels and a cleaner demo status story for optional weather/news degradation.

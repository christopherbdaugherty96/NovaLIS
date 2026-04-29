# Friction Log - 2026-04-28 User Test

## P0/P1 Demo Blockers

### Trust UI does not render receipts returned by the API

- Evidence: `/api/trust/receipts?limit=10` returned an `OPENCLAW_AGENT_RUN_COMPLETED` receipt.
- Evidence: Trust page screenshots `07_trust_receipts.png` and `08_trust_after_refresh.png` show empty recent governed actions.
- Impact: The demo cannot visually prove "what Nova did" from the Trust page.
- Suggested next step: Debug `fetchAndRenderReceipts` render path against the actual API response shape.

### Live email draft did not create a fresh visible receipt

- Evidence: Chat showed a draft-only email response for `test@example.com`.
- Evidence: API response after the prompt did not include a new `EMAIL_DRAFT_CREATED` receipt.
- Impact: Cap 64 cannot be treated as live-proof-complete from this pass.
- Suggested next step: Trace whether the chat route invokes the Cap 64 executor or only returns conversational text.

### Token budget blocked the basic demo prompt

- Evidence: `What works today?` returned `Daily token budget reached`.
- Impact: A first-time demo cannot show Nova's normal explanatory answer.
- Suggested next step: Add a demo-safe local answer for known product-status prompts or reset budget before capture.

## P2 Usability Friction

### Simplified Home can look empty

- Evidence: `03_workspace_home.png`.
- Impact: A new user may think the app failed after clicking `Open Home`.
- Suggested next step: Put a useful default Home panel in simplified mode or keep first-run users on Intro/Chat.

### Status badge stays `CONNECTING`

- Evidence: multiple screenshots show `CONNECTING` while API calls succeed.
- Impact: Trust is reduced because the runtime appears unhealthy while parts of the app work.
- Suggested next step: Separate websocket status from backend/API status and explain degraded states.

### Runtime health and rules stay unknown

- Evidence: Trust page shows Governor, Boundary, Network, Voice, Memory, Model as `Unknown`.
- Impact: Trust Center appears unfinished during proof capture.
- Suggested next step: Populate health values or explicitly label them unavailable in current build.

### Header menu controls have empty accessible text in automation

- Evidence: Playwright-visible controls included many header buttons with empty text.
- Impact: Harder automated testing and likely accessibility friction.
- Suggested next step: Add stable `aria-label` or visible text for icon/header menu controls.

### Weather remains loading

- Evidence: dashboard screenshots show `Loading weather...`.
- Impact: Looks broken during demo even if weather is optional.
- Suggested next step: Show an optional/unconfigured state instead of indefinite loading.

## Environment Friction

### In-app Browser Use failed because Node REPL crashed

- Evidence: Node REPL error reported invalid package config at `C:\Users\Chris\package.json`.
- Impact: The requested computer-use/browser-use path could not be used for capture.
- Workaround used: Python Playwright screenshots and video.
- Suggested next step: Fix or remove the invalid user-level `package.json`, or make node_repl start outside that package boundary.

## P3 Documentation/Proof Gaps

### Startup docs are enough for a running developer checkout, but not enough for cold proof

- Evidence: `.\start_nova.bat` succeeded because Nova was already running.
- Impact: This pass did not prove dependency installation or cold startup timing.
- Suggested next step: Add a cold-start proof checklist that begins with `stop_nova.bat` and records time to dashboard.

### Video proof exists but does not yet show a clean success path

- Evidence: `video/nova_user_test_demo_flow.webm`.
- Impact: Useful internal proof, not yet a polished external demo.
- Suggested next step: Re-record after Trust receipt and token-budget blockers are fixed.

## Local-First Follow-Up Pass - 2026-04-28

### P1 - stale or missing backend PID can leave Nova already running but not controllable

- Evidence: `stop_nova.bat` reported no PID file while a Nova uvicorn process still owned port 8000.
- Evidence: the listener command line was `python -m uvicorn src.brain_server:app --host 127.0.0.1 --port 8000 --app-dir C:\Nova-Project\nova_backend`.
- Fix applied: `scripts/start_daemon.py` now detects the actual port listener, clears unhealthy stale Nova-owned listeners, refuses unknown port owners, and writes the real listener PID after startup.
- Status: fixed for startup path; keep watching because tracked PID files are still noisy runtime artifacts.

### P1 - core local questions were blocked by daily token budget

- Evidence: live UI screenshot `screenshots/local_first_followup/level2_prompt_1_error.png` showed `Daily token budget reached` for `What works today?`.
- Fix applied: local self-description and memory-authority meta intents now run before budget-gated governed parsing in `session_handler.py`.
- Evidence after fix: `screenshots/local_first_followup/level2_what_works.png` and `screenshots/local_first_followup/level2_memory_authority.png`.
- Status: fixed for the tested core prompts.

### P1 - Trust UI receipt rendering now works, but receipt labels are still incomplete

- Evidence: `screenshots/local_first_followup/level1_surface_trust.png` shows Action Receipts rendering from the Trust page.
- Remaining issue: completion receipts may display only capability IDs such as `57` because the ledger completion event does not always include `capability_name`.
- Impact: proof exists, but a non-technical viewer may not understand what action completed.
- Suggested next step: enrich receipt rendering with registry names when receipt payload lacks `capability_name`.

### P2 - in-app Browser Use remains blocked by invalid user-level package config

- Evidence: Node REPL startup failed with invalid package config at `C:\Users\Chris\package.json`.
- Impact: requested computer-use/browser-use path could not be used for screenshot capture.
- Workaround used: Python Playwright, with real local screenshots.
- Suggested next step: fix/remove the invalid user-level `package.json` or launch node_repl outside that package boundary.

### P2 - `rg.exe` failed with access denied during this pass

- Evidence: `rg -n ...` failed with `Access is denied`.
- Impact: code search fell back to PowerShell `Select-String`, which is much slower and can accidentally scan huge ledger files.
- Suggested next step: repair local ripgrep executable/path permissions.

### P2 - optional network widgets can make the runtime look degraded

- Evidence: screenshots show `DEGRADED` and weather unavailable while core local chat and dashboard work.
- Impact: demo viewers may read optional weather/news failure as whole-system failure.
- Suggested next step: make optional connector/network degradation visually distinct from local runtime health.

### P2 - `memory overview` through chat did not complete in UI wait window

- Evidence: Level 4 UI test timed out waiting for the memory overview prompt.
- Impact: Memory page works, but chat-driven local memory inspection was not clean proof in this pass.
- Suggested next step: trace whether the prompt remained pending, was blocked by focus/input state, or routed to a slower governed path.

### P2 - Cap 64 was tested only to confirmation boundary

- Evidence: `screenshots/local_first_followup/level5_cap64_confirmation_boundary.png`.
- Impact: boundary messaging is visible, but live `EMAIL_DRAFT_CREATED` proof still needs an action-time approved run on a machine with a safe mail client setup.
- Suggested next step: run Cap 64 P5 live signoff separately with explicit approval to open the mail client, then close the draft without sending.

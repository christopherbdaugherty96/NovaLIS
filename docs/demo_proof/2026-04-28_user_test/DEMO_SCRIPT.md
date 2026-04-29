# Nova Demo Script - 2026-04-28 User Test

## Goal

Show Nova as it exists today: a governance-first local AI system where intelligence helps, but authority stays bounded, visible, and reviewable.

## Demo Flow

### 1. Start Nova

Command:

```powershell
.\start_nova.bat
```

Expected:

- Nova reports the local URL.
- If already running, Nova reports: `Already running at http://127.0.0.1:8000`.
- Open `http://127.0.0.1:8000`.

Narration:

> Nova runs locally first. The important thing is not that it can do everything; it is that real action is supposed to stay governed and reviewable.

### 2. Intro Surface

Show:

- `WELCOME TO NOVA`
- `Offline-first`
- `No background automation. No hidden memory. No surprises.`
- guided setup checklist

Narration:

> The first screen explains the safety posture. Nova can reason and help plan, but that does not automatically grant authority to act.

### 3. Full Dashboard

Action:

- Click `Show full UI`.
- Open `Home`.

Show:

- navigation: Chat, Home, Agent, News, Workspace, Memory, Rules, Trust, Settings, Intro
- home focus
- operational context
- assistive notices

Narration:

> The dashboard is the operator surface. It shows context, current focus, and bounded help instead of hiding work in the background.

### 4. Basic Chat

Prompt:

```text
What works today?
```

Observed in this pass:

- Nova accepted the prompt.
- Token budget blocked the full answer.
- The UI showed a local-only budget message.

Narration:

> This is not the ideal demo answer, but it is real governance behavior: Nova exposes that a budget boundary stopped the request instead of silently using more external tokens.

### 5. Governed Email Draft Boundary

Prompt:

```text
Draft an email to test@example.com about tomorrow.
```

Observed in this pass:

- Nova explained that it would draft and open the email in a mail client.
- Nova stated that it never sends email automatically and the user must review/send manually.
- A fresh `EMAIL_DRAFT_CREATED` receipt was not visible in the Trust API after this run.

Narration:

> Email is the cleanest principle demo when the receipt works: Nova can prepare a draft, but sending stays manual. This pass shows the UI boundary message, but the receipt proof still needs repair.

### 6. Trust Center

Action:

- Open `Trust`.
- Click `Refresh trust`.

Show:

- operating state
- action receipts section
- blocked conditions
- runtime health
- reasoning transparency
- remote bridge boundary

Observed in this pass:

- API returned a receipt.
- Trust UI did not render that receipt visually.

Narration:

> This page is supposed to answer "what did Nova do?" The API is alive, but the visual receipt surface needs work before this can be a reliable demo anchor.

### 7. Memory Boundary

Action:

- Open `Memory`.

Show:

- `Memory becomes durable only when you explicitly save it.`
- `No durable memory saved yet.`
- `Memory is explicit, inspectable, and revocable.`

Narration:

> Conversation and memory can help Nova understand. They do not authorize execution. Durable memory has to be explicit and inspectable.

## Short Demo Clip Captured

Captured video:

```text
docs/demo_proof/2026-04-28_user_test/video/nova_user_test_demo_flow.webm
```

Recorded flow:

- Intro
- full UI
- Chat
- email draft prompt
- Trust
- Memory

## Clean Demo Preconditions

Before using this as a public demo:

- Reset or raise the token budget so `What works today?` can answer cleanly.
- Fix Trust UI rendering of receipts returned by `/api/trust/receipts`.
- Ensure live email draft produces a fresh receipt visible in Trust.
- Make Home useful in simplified mode or route first-time users to Intro/Chat instead.
- Fix persistent `CONNECTING` status when backend APIs are reachable.

## Local-First Follow-Up Pass - 2026-04-28

Use this revised local-first flow for the next internal demo recording:

### 1. Start Nova

Command:

```powershell
python .\scripts\start_daemon.py --no-browser
```

Show:

- Local URL: `http://127.0.0.1:8000`
- Header settles to `LOCAL-ONLY`
- Phase status is active

Narration:

> Nova starts as a local-first system. Optional connectors can be degraded or missing without giving Nova broader authority.

### 2. Show Intro And Home

Action:

- Open `Intro`.
- Open `Home`.

Show:

- Nova explains it helps understand and continue work without taking control.
- Home has visible local widgets rather than an empty shell.

Narration:

> The first useful proof is local: can a user see where to begin before any advanced connector is involved?

### 3. Ask What Works Today

Prompt:

```text
What works today?
```

Expected:

- Nova answers from local runtime truth even if daily metered budget is exhausted.
- It should mention local chat, dashboard surfaces, memory visibility, receipts, safe local actions, and the email draft boundary.

Narration:

> The metered model budget is not authority. Nova can still explain current local truth without hiding that budget exists.

### 4. Prove Memory Is Not Authority

Prompt:

```text
Can memory authorize actions?
```

Expected:

- Nova answers no.
- It should explicitly state that intelligence is not authority.
- It should explain that real actions require governed capability paths, confirmation when required, and receipts/proof where expected.

Narration:

> Memory can help Nova understand, but memory cannot approve real action.

### 5. Show Trust And Receipts

Action:

- Open `Trust`.
- Show direct API proof if needed:

```text
http://127.0.0.1:8000/api/trust/receipts?limit=10
http://127.0.0.1:8000/api/trust/receipts/summary
```

Expected:

- Trust page renders Action Receipts.
- Receipt badges use readable states such as Done.
- Boundary/blocked-condition panels stay visible.

Narration:

> Receipts are evidence. They do not grant permission, but they let the user audit what happened or what was blocked.

### 6. Run One Safe Local Action

Prompt:

```text
system status
```

Expected:

- Nova returns local status.
- The action remains local/read-only.
- Any receipt or ledger evidence is shown if available.

Narration:

> Local actions should either work or fail visibly and safely.

### 7. Cap 64 Confirmation Boundary

Prompt:

```text
draft an email to test@example.com about tomorrow's meeting
```

Expected:

- Nova asks for confirmation before opening the local mail client.
- Nova states it never sends email automatically.
- Stop here unless the tester explicitly approves opening the mail client.

Narration:

> Email draft is governed: Nova may prepare a local draft, but sending remains manual.

### 8. Shopify Missing-Credentials Check

Prompt:

```text
shopify report
```

Expected:

- If credentials are missing, Nova says the Shopify connector is not configured.
- It should not crash or imply write access.

Narration:

> Advanced connectors should fail cleanly and never imply broad autonomy.

Remaining preconditions for final public demo:

- Run Cap 64 live signoff with explicit approval to open the mail client, then close the draft without sending.
- Improve receipt row labels when completion receipts only carry capability IDs.
- Re-record the final `.webm` after Cap 64 receipt proof is visible.

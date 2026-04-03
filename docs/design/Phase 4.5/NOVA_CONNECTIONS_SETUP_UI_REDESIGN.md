# Nova — Setup UI Redesign: User Profile + Connections
Status: PLANNED — not yet started
Updated: 2026-04-02
Effective status: profile and connection cards are shipped; remaining work is setup/readiness polish

---

## Goal

## Grounded Shipping Note

The original redesign packet was written before implementation. As of 2026-04-02:

- the User Profile surface is live in Settings
- profile saves persist locally and write a protected `user_identity` memory record
- the Connections surface is live as interactive in-app cards
- users can save, test, disconnect, and reset provider connections from the UI
- connection cards now replace the old read-only provider chip model

What remains open from this redesign is not the card system itself. The remaining Phase 4.5 polish gap is:

- making the Intro / readiness flow reflect the live connection-card state cleanly
- tightening setup copy so Nova feels guided instead of half-manual
- finishing the broader first-run setup feel around the shipped profile plus connection surfaces

Build a proper first-run and ongoing setup experience covering two areas:

1. **User Profile** — who the user is, what they want to be called, how they want Nova to behave
2. **Connections** — connect, test, and disconnect every provider from within Nova's UI, no manual `.env` editing

---

## PART A — User Profile & Preferences

### What This Is

A personal setup section where the user tells Nova who they are and how they want to be treated.
This feeds directly into Nova's personality layer, memory system, and response style.

---

### Zone A1 — Identity

```
┌──────────────────────────────────────────────────┐
│  About You                                        │
│                                                   │
│  Your name                                        │
│  ┌────────────────────────────────────────────┐  │
│  │  Chris                                     │  │
│  └────────────────────────────────────────────┘  │
│                                                   │
│  What Nova calls you  (nickname / leave blank)    │
│  ┌────────────────────────────────────────────┐  │
│  │  e.g. "Boss", "C", leave blank for name   │  │
│  └────────────────────────────────────────────┘  │
│                                                   │
│  Email  (used to detect connected services)       │
│  ┌────────────────────────────────────────────┐  │
│  │  email@example.com                   [✓]   │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

**Fields:**
- `name` — user's real name or preferred name. Nova uses this in greetings and memory.
- `nickname` — optional. If set, Nova uses this instead of name in conversation (e.g. "Hey Boss").
  If blank, falls back to name.
- `email` — identity anchor for provider detection and future OAuth (see Part B).

**Storage:** persisted to backend settings store AND written into Nova's governed memory store as a permanent
first-class memory entry. This means Nova carries name, nickname, and email as active context in every
conversation — not just as a config value the backend reads, but as something Nova actually "knows" about
the user the same way she knows anything she has been told to remember.

**Memory write on save:**
- When the user saves their profile, the backend writes a governed memory record with a reserved key
  (e.g. `user_identity`) into `governed_memory_store`.
- This record is loaded at session start alongside other memory and injected into Nova's working context.
- Result: Nova greets the user by name/nickname naturally, references their preferences without being told,
  and treats the user rules as persistent known context rather than a one-time instruction.

---

### Zone A2 — Preferences

Light preference toggles that shape Nova's default behavior without needing to edit governance docs.

```
┌──────────────────────────────────────────────────┐
│  Preferences                                      │
│                                                   │
│  Response style                                   │
│  ◉ Concise   ○ Balanced   ○ Detailed             │
│                                                   │
│  Morning brief                                    │
│  ◉ On   ○ Off      Time: [ 08:00 ]               │
│                                                   │
│  Proactive suggestions                            │
│  ◉ On   ○ Off                                    │
│                                                   │
│  Use my name in responses                         │
│  ◉ Yes  ○ No                                     │
│                                                   │
└──────────────────────────────────────────────────┘
```

**Preference fields (expandable — add more as needed):**
- `response_style` — "concise" | "balanced" | "detailed". Injects a style hint into the system prompt.
- `morning_brief_enabled` + `morning_brief_time` — surfaces to the scheduler (already exists in Nova).
- `proactive_suggestions` — whether Nova offers follow-up suggestions after responses.
- `use_name_in_responses` — whether Nova addresses the user by name/nickname in conversation.

---

### Zone A3 — User Rules

A free-text area where the user writes their own rules for how Nova should behave.
These are appended to the system prompt or personality layer as user-defined constraints.

```
┌──────────────────────────────────────────────────┐
│  Your Rules for Nova                              │
│                                                   │
│  Write anything you always want Nova to do,      │
│  avoid, or remember about how you work.           │
│                                                   │
│  ┌────────────────────────────────────────────┐  │
│  │  - Always give me bullet points first      │  │
│  │  - Don't ask clarifying questions if       │  │
│  │    you can make a reasonable assumption    │  │
│  │  - I prefer metric units                  │  │
│  │  - Don't use filler phrases like          │  │
│  │    "Certainly!" or "Great question!"      │  │
│  │                                            │  │
│  │  (free text, one rule per line)            │  │
│  └────────────────────────────────────────────┘  │
│                              [Save rules]         │
└──────────────────────────────────────────────────┘
```

**Behavior:**
- Rules are stored in the settings store as a raw string.
- At runtime, the personality/prompt builder prepends these rules to the system prompt.
- Rules are user-owned — Nova cannot override them through normal operation.
- Governor does NOT gate these — they are user expression, not a governed capability.
- Character limit: suggested 2000 chars to prevent prompt bloat.

---

### Backend Work for Part A

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/settings/profile` | Return current name, nickname, email, preferences, rules |
| `POST` | `/api/settings/profile` | Save name, nickname, email |
| `POST` | `/api/settings/preferences` | Save preference toggles |
| `POST` | `/api/settings/rules` | Save user rules string |

Storage: extend the existing settings store (or create `user_profile_store.py`) AND write a protected
`user_identity` record into `governed_memory_store` on every profile save. The memory store is the
runtime source of truth; the settings store is the persistence/edit layer.

Runtime injection: the personality/prompt builder reads these at conversation start and injects:
- Nickname/name into the greeting and memory layer
- Response style hint into the system prompt prefix
- User rules block into the system prompt (after governance rules, before conversation)

**Core memory integration (key design decision):**
Profile data does not live only in a settings file — it is written into Nova's governed memory store
so Nova carries this knowledge as active conversational context, not just background config.

Memory record structure (written on profile save):
```json
{
  "key": "user_identity",
  "type": "core",
  "content": {
    "name": "Chris",
    "nickname": "Boss",
    "email": "...",
    "response_style": "concise",
    "use_name": true,
    "rules": "- Always give bullet points first\n- Prefer metric units"
  },
  "protected": true,
  "source": "user_profile_setup"
}
```

- `protected: true` means Nova cannot overwrite or forget this via normal `remember` / `forget` commands
- The record is always loaded first in the memory recall stack — highest priority context
- If the user updates their profile in settings, the memory record is updated in place (same key)
- The rules field in memory is what Nova actually sees at prompt time — not a separate config path

---

### Open Questions for Part A

- [ ] Should "user rules" be shown to Nova as hard constraints (prefixed "You MUST...") or soft preferences?
- [ ] Should nickname/name already be surfaced somewhere in Nova's existing personality system — or is this entirely new?
- [ ] What is the character/line limit for user rules before prompt injection becomes a problem?
- [ ] Should preferences like response_style also be changeable mid-conversation via chat command (e.g. "be more concise")?
- [ ] Should there be a "reset to defaults" button for preferences?
- [ ] Should the profile section be part of the main Settings page or a separate first-run onboarding page?
- [ ] How does the `user_identity` memory record interact with Nova's existing memory recall — does it always load first, or is it injected directly into the system prompt regardless of recall?
- [ ] Should Nova be able to suggest updates to the profile ("I noticed you always prefer bullet points — want me to save that as a rule?") or is the profile strictly user-edited only?

---

---

## PART B — Connections & Provider Setup

### Current State (what exists now)

- `#settings-connection-grid` — read-only chip grid, populated from `trustReviewState.connectionRuntime`
- `#intro-checklist-grid` — setup readiness checklist (also read-only)
- No `<input>` fields for API keys anywhere in the frontend
- No connect/disconnect action flows
- Users must manually edit `.env` and restart to add/remove keys
- The note currently reads: "Most provider keys and connector logins are still configured manually today"

Relevant files:
- `Nova-Frontend-Dashboard/index.html` — lines ~186–203 (setup readiness), ~909–919 (connections section)
- `Nova-Frontend-Dashboard/dashboard.js` — connection grid rendering ~8358–8388, connection button ~9085–9090
- `nova_backend/src/api/settings_api.py` — where new save/test/disconnect endpoints will go
- `nova_backend/src/connectors/email_connector.py` — email connector stub (Phase 10)
- `nova_backend/.env.example` — canonical list of all 17 env vars to expose in UI

---

### Proposed Design

#### Zone 1 — Identity (Email)

A single email input at the top of the setup/connections page.

```
┌──────────────────────────────────────────────────┐
│  Your Nova Identity                               │
│  ┌────────────────────────────────────────────┐  │
│  │  email@example.com                   [✓]   │  │
│  └────────────────────────────────────────────┘  │
│  Used to pre-fill provider sign-ins and match    │
│  your connected services. Stays on this device.  │
└──────────────────────────────────────────────────┘
```

**Behavior:**
- Email stored locally (backend settings store or localStorage — NOT transmitted externally)
- On entry, auto-detect provider suggestions:
  - `@gmail.com` → surface Gmail connector card + Google Calendar card
  - `@outlook.com` / `@hotmail.com` → surface IMAP / Outlook card
  - Any other domain → show generic IMAP option
- Pre-fills email field when OAuth popups open in future
- Shows "Linked" indicator on any card that matches the detected provider

---

#### Zone 2 — Provider Connection Cards

Each provider gets a card. Cards replace the current read-only chip grid.

**Three card states:**

```
╔═══════════════════╗   ╔═══════════════════╗   ╔═══════════════════╗
║  🟢 CONNECTED     ║   ║  🟡 KEY NEEDED    ║   ║  ⚪ NOT SET UP    ║
║  OpenAI           ║   ║  Weather          ║   ║  Email / Gmail    ║
║  GPT-4o active    ║   ║  ┌─────────────┐  ║   ║  [Connect →]      ║
║  Last check: now  ║   ║  │ Paste key…  │  ║   ║                   ║
║  [Disconnect]     ║   ║  └─────────────┘  ║   ║                   ║
║                   ║   ║  [Save & Test]    ║   ║                   ║
╚═══════════════════╝   ╚═══════════════════╝   ╚═══════════════════╝
```

**State: Connected (green)**
- Shows provider label, model or plan in use if known, timestamp of last successful health check
- Single action: `Disconnect` — clears the key, disables the governed capability, flips card to grey
- No key visible (masked for security)

**State: Key Needed (amber)**
- Key field is missing or failed last health check
- Inline `<input type="password">` for pasting the key
- `Save & Test` button — POSTs key to backend, runs health check, shows inline pass/fail
- On pass: card flips to green
- On fail: shows error message inline (bad key, quota exceeded, network error)

**State: Not Set Up (grey)**
- Opt-in only — user clicks `Connect` to expand the card into Key Needed state
- No noise for services the user doesn't want

**Providers to card-ify (maps to `.env.example` vars):**

| Card Label | Env Var | Governed Cap(s) | Notes |
|---|---|---|---|
| OpenAI / GPT-4o | `OPENAI_API_KEY` | 63 (OpenClaw), reasoning lane | Primary cloud reasoning |
| Web Search (Brave) | `BRAVE_API_KEY` | 16 | Also `WEB_SEARCH_ENABLED` toggle |
| News | `NEWS_API_KEY` | 48, 49, 50 | |
| Weather | `WEATHER_API_KEY` | 55 | Also `WEATHER_UNITS` selector |
| Calendar (ICS) | `NOVA_CALENDAR_ICS_PATH` | 56 | File path picker, not an API key |
| Email / Gmail | `NOVA_EMAIL_*` vars | inbox_check (Phase 10) | EmailConnector stub ready |
| Voice / Piper TTS | `NOVA_PIPER_MODEL_PATH` | TTS | File path picker |
| Remote Bridge | `NOVA_OPENCLAW_BRIDGE_TOKEN` | OpenClaw remote | Token field |

---

#### Zone 3 — Disconnect All / Reset

At the bottom of the connections page, a governed reset option.

```
┌──────────────────────────────────────────────────┐
│  ⚠ Reset All Connections                         │
│  Removes all provider keys and resets Nova to    │
│  local-only mode. This cannot be undone without  │
│  re-entering your keys.                          │
│                                                  │
│                        [Reset all connections]   │
└──────────────────────────────────────────────────┘
```

- Clicking `Reset all connections` shows a confirmation step (inline, not a browser alert)
- On confirm: sends `DELETE /api/settings/connections/all` → backend clears all key env vars → all cards flip to grey
- Consistent with Nova's governed design — no destructive action without a confirmation step

---

### Backend Work Required (Part B)

New API endpoints needed in `nova_backend/src/api/settings_api.py`:

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/settings/connections/{provider}/key` | Save a provider key, run health check, return pass/fail |
| `DELETE` | `/api/settings/connections/{provider}` | Clear a single provider key |
| `DELETE` | `/api/settings/connections/all` | Clear all provider keys (Reset All) |
| `GET` | `/api/settings/connections` | Return all provider connection statuses (replaces current trust status polling) |
| `POST` | `/api/settings/identity/email` | Save the identity email to settings store |

Health check logic per provider:
- **OpenAI**: hit `/v1/models` with the key, expect 200
- **Brave**: hit a cheap search endpoint, expect 200
- **NewsAPI**: hit `/v2/top-headlines` with `pageSize=1`, expect 200
- **Weather (Visual Crossing)**: hit a minimal forecast endpoint, expect 200
- **Email**: call `EmailConnector.health_check()` when implemented
- **ICS Calendar / Piper / Bridge token**: validate file exists or token format — no network call needed

---

### Frontend Work Required (Part B)

- Replace `#settings-connection-grid` chip rendering with card component renderer
- Add identity email input above the card grid
- Add inline key input + Save & Test flow per card
- Add Disconnect button per connected card
- Add Disconnect All zone at bottom
- Handle WebSocket or REST response for health check result (show inline feedback)
- Update `#intro-checklist-grid` / setup readiness to reflect new card states

---

### What Does NOT Change (Part B)

- Keys are never stored in localStorage or sent to any third party
- All governed capability paths still go through the Governor — connecting a key in the UI does not bypass governance
- The `.env` file remains the source of truth at the OS level; the UI writes through the backend settings API which updates the running config and optionally persists to `.env`
- The `Disconnect` action disables the relevant governed cap at runtime immediately — no restart required

---

### Open Questions / Things to Add (Part B)

- [ ] Should the UI support OAuth flows (Google sign-in button) for Gmail/Calendar, or key-only for now?
- [ ] Where exactly does the email field live — Settings page only, or also on the intro/onboarding panel?
- [ ] Should `Save & Test` update the `.env` file on disk, or only update the running config until next restart?
- [ ] Should there be a "Test connection" button on already-connected cards (re-run health check on demand)?
- [ ] Card ordering — alphabetical, or grouped by category (Reasoning / Search / Data / Connectivity)?
- [ ] Mobile/compact layout for the card grid?
- [ ] Should the identity email field be tied to the Nova personality/profile system?

---

## Implementation Order (when ready to build)

1. Backend: `GET /api/settings/connections` — connection status per provider
2. Frontend: Replace read-only grid with card components (three states, no actions yet)
3. Backend: `POST /api/settings/identity/email` + store
4. Frontend: Identity email field + provider detection logic
5. Backend: `POST /api/settings/connections/{provider}/key` + health check
6. Frontend: Key Needed state — inline input + Save & Test flow
7. Backend: `DELETE /api/settings/connections/{provider}`
8. Frontend: Connected state — Disconnect button
9. Backend + Frontend: Reset All (with confirmation)
10. Update `#intro-checklist-grid` to reflect card-based connection states

---

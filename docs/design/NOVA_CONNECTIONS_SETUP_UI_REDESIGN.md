# Nova — Connections & Setup UI Redesign
Status: PLANNED — not yet started
Updated: 2026-04-02

---

## Goal

Replace the current read-only connection status grid with a fully interactive setup experience.
Users should be able to connect, test, and disconnect every provider entirely from within Nova's UI —
no manual `.env` editing required.

Add an email identity field as the anchor for provider detection and future OAuth flows.

---

## Current State (what exists now)

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

## Proposed Design

### Zone 1 — Identity (Email)

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

### Zone 2 — Provider Connection Cards

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

### Zone 3 — Disconnect All / Reset

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

## Backend Work Required

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

## Frontend Work Required

- Replace `#settings-connection-grid` chip rendering with card component renderer
- Add identity email input above the card grid
- Add inline key input + Save & Test flow per card
- Add Disconnect button per connected card
- Add Disconnect All zone at bottom
- Handle WebSocket or REST response for health check result (show inline feedback)
- Update `#intro-checklist-grid` / setup readiness to reflect new card states

---

## What Does NOT Change

- Keys are never stored in localStorage or sent to any third party
- All governed capability paths still go through the Governor — connecting a key in the UI does not bypass governance
- The `.env` file remains the source of truth at the OS level; the UI writes through the backend settings API which updates the running config and optionally persists to `.env`
- The `Disconnect` action disables the relevant governed cap at runtime immediately — no restart required

---

## Open Questions / Things to Add

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

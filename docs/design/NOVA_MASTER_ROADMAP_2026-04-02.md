# Nova — Master Roadmap
Updated: 2026-04-02
Status: Living document — add to this as new work is identified

This is the single prioritized backlog for everything planned but not yet built.
Each item links to its full design doc where one exists.

---

## How to Read This

- **P0** — Do this next. High value, unblocks other things.
- **P1** — Do this soon. Core product improvement.
- **P2** — Do this when P1 is done. Good features, not urgent.
- **P3** — Future. Good ideas, complex, not yet scoped.

Status tags: `[ ]` not started · `[~]` in progress · `[x]` done

---

## P0 — Intelligence Layer (Do This First)

The current ceiling: every conversation goes through `gemma2:2b` (2 billion parameters).
The cloud lane exists but is not wired to conversation. This is the single biggest unlock.

### 0.1 — Add DeepSeek V3 as Tier 2 Provider
Design doc: `NOVA_AGENT_NODE_ARCHITECTURE_2026-04-01.md`

- [ ] Add `DEEPSEEK_API_KEY` and `DEEPSEEK_BASE_URL=https://api.deepseek.com/v1` to `.env.example`
- [ ] Make `openai_responses_lane.py` accept a configurable base URL (not hardcoded to OpenAI)
- [ ] Add `MODEL_PROVIDER=deepseek` as a recognized routing option in `nova_config.py`
- [ ] Add DeepSeek pricing constants to `provider_usage_store`
- [ ] Test: conversation routed to DeepSeek V3, response returns, budget tracked

**Why first:** OpenAI-compatible API — one URL change away. ~$0.07/1M tokens.
Nearly free intelligence upgrade with minimal code change.

---

### 0.2 — Wire Conversation Loop to Provider Routing
Design doc: `NOVA_AGENT_NODE_ARCHITECTURE_2026-04-01.md`

Currently `general_chat.py` always calls `llm_manager.generate()` (local Ollama).
The routing logic in `runtime_settings_store.py` exists but is never consulted for conversation.

- [ ] Build a `conversation_router.py` that checks routing mode before calling local model
- [ ] Add a complexity classifier (heuristic: query length + question words + topic signals)
      → simple queries stay local · complex queries route to Tier 2 (DeepSeek) or Tier 3 (OpenAI)
- [ ] Wire `general_chat.py` / `run_general_chat_fallback()` to call conversation router
- [ ] Update `MODEL_PROVIDER` env var to recognize `"auto"` properly
- [ ] Budget gate applies to cloud tier calls (Phase 9 gate already exists — just extend it)
- [ ] Test: simple question → local · complex question → DeepSeek · agent task → OpenAI

**Tiered routing target:**
```
Tier 1 — local gemma2:2b      free, private, instant   simple queries
Tier 2 — DeepSeek V3 API      ~$0.07/1M tokens         complex reasoning
Tier 3 — OpenAI GPT-4o-mini   ~$0.15/1M tokens         agent/OpenClaw tasks
Tier 4 — OpenAI GPT-4o        ~$2.50/1M tokens         heavy analysis (on-demand only)
```

---

### 0.3 — Update BUILD_PHASE to 9
- [ ] Set `BUILD_PHASE = 9` in `nova_backend/src/build_phase.py`
- [ ] Update `registry.json` phase field to match
- [ ] Update any runtime docs that reference current phase

---

## P1 — Setup & Profile

Design doc: `NOVA_CONNECTIONS_SETUP_UI_REDESIGN.md`

### 1.1 — User Profile Setup
- [ ] Backend: `GET /api/settings/profile` + `POST /api/settings/profile`
- [ ] Backend: `POST /api/settings/preferences` (response style, morning brief, proactive suggestions)
- [ ] Backend: `POST /api/settings/rules` (user rules free-text)
- [ ] On save: write protected `user_identity` record to `governed_memory_store`
      (name, nickname, email, preferences, rules stored as permanent memory)
- [ ] Frontend: profile form — name, nickname, email fields
- [ ] Frontend: preferences panel — response style picker, toggles
- [ ] Frontend: user rules textarea with save button

### 1.2 — Connection Cards (replace read-only grid)
- [ ] Backend: `GET /api/settings/connections` — status per provider
- [ ] Backend: `POST /api/settings/connections/{provider}/key` — save + health check
- [ ] Backend: `DELETE /api/settings/connections/{provider}` — clear key
- [ ] Backend: `DELETE /api/settings/connections/all` — reset all (with confirmation)
- [ ] Backend: `POST /api/settings/identity/email` — save identity email
- [ ] Frontend: replace `#settings-connection-grid` chips with interactive cards
- [ ] Frontend: three card states — connected (green) / key needed (amber) / not set up (grey)
- [ ] Frontend: inline key entry + Save & Test per card
- [ ] Frontend: Disconnect button per connected card
- [ ] Frontend: Disconnect All zone at bottom with confirmation step
- [ ] Frontend: email field at top with provider auto-detection logic

---

## P1 — Memory Tiers

Design doc: `NOVA_MEMORY_TIERS_DESIGN.md`

### 1.3 — Rolling Memory with Auto-Purge
- [ ] Add `recall_count` and `last_recalled_at` fields to memory record schema
- [ ] Add `purge_old_active()` method to `governed_memory_store.py`
      (purge oldest active items when count > 100, spare recently-recalled items)
- [ ] Call `purge_old_active()` at session start in `brain_server.py`
- [ ] Expose `ROLLING_MEMORY_LIMIT` as a configurable setting (default 100)

### 1.4 — Permanent Memory (always injected)
- [ ] Update `_select_relevant_memory_context()` in `brain_server.py`:
      always load ALL locked items + top 5 scored active items per query
- [ ] Add `promote` action to `memory_governance_executor.py`
      (moves active item to locked tier)
- [ ] Backend: `POST /api/memory/{id}/promote` endpoint
- [ ] Backend: `DELETE /api/memory/rolling/clear` endpoint

### 1.5 — Memory Panel UI
- [ ] Frontend: "Saved Memories" section — shows locked items, always visible
- [ ] Frontend: "Session Memory" section — shows active items with count (42 / 100)
- [ ] Frontend: promote-to-permanent button per rolling memory card
- [ ] Frontend: Clear All session memory button (with confirmation)
- [ ] Frontend: Add permanent memory free-text form

---

## P1 — Automations

Design doc: `NOVA_AUTOMATIONS_DESIGN.md`

### 1.6 — User-Created Templates
- [ ] `POST /api/openclaw/agent/templates` — save custom template
- [ ] `DELETE /api/openclaw/agent/templates/{id}` — remove custom template
- [ ] Frontend: template builder form (name, step picker, schedule, delivery mode)
- [ ] Persist custom templates in `agent_runtime.json` alongside defaults

### 1.7 — Extended Recurrence
- [ ] Extend recurrence field in `notification_schedule_store.py`:
      `"weekdays"`, `"weekends"`, `"weekly:monday"`, `"every_2h"`, `"every_4h"`
- [ ] Update `due_scheduled_templates()` in `agent_scheduler.py` to evaluate new patterns
- [ ] Frontend: recurrence picker (human-readable, not cron syntax)

### 1.8 — RSS / Research Digest Template
- [ ] `nova_backend/src/openclaw/feed_store.py` — RSS URL list store
- [ ] New executor step: `rss_fetch` — fetch and parse RSS feeds
- [ ] New OpenClaw template: `research_digest`
      (fetch → filter last 24h → score relevance → summarize top N → deliver)
- [ ] Frontend: feed list manager in Settings (add/remove RSS URLs)

---

## P2 — Email & Calendar Automations

Design doc: `NOVA_AUTOMATIONS_DESIGN.md`

### 2.1 — IMAP Email Connector
- [ ] `nova_backend/src/connectors/imap_email_connector.py`
      (concrete implementation of existing `email_connector.py` stub)
- [ ] Env vars: `NOVA_EMAIL_PROVIDER`, `NOVA_EMAIL_HOST`, `NOVA_EMAIL_PORT`,
      `NOVA_EMAIL_USER`, `NOVA_EMAIL_SECRET`
- [ ] New trigger type: `on_email_received` in scheduler (IMAP poll every 5–10 min)
- [ ] New template: `email_triage`
      (fetch → classify urgent/actionable/noise → route urgent to chat, batch others to widget)

### 2.2 — Meeting Prep Automation
- [ ] New trigger type: `on_calendar_event_upcoming` (check for events starting in N min)
- [ ] New template: `meeting_prep`
      (fetch event → search memory for context → summarize → deliver widget card)

### 2.3 — File Watch / Document Ingest
- [ ] `nova_backend/src/tasks/file_watcher.py` — Python watchdog-based file watcher
- [ ] New trigger type: `on_file_created` in configured watch directory
- [ ] New template: `document_ingest`
      (detect file → extract text → summarize → save to permanent memory)
- [ ] Env var: `NOVA_WATCH_DIR`
- [ ] Frontend: watch directory picker in Settings

---

## P2 — Trading Connector

Design doc: `NOVA_TRADING_CONNECTOR_DESIGN.md`

### 2.4 — Alpaca Paper Trading (Phase 1)
- [ ] `src/connectors/trading_connector.py` — abstract base class
- [ ] `src/connectors/alpaca_trading_connector.py` — Alpaca Markets implementation
- [ ] `src/tasks/trading_rules_store.py` — user trading rules + dollar limits store
- [ ] `src/usage/trading_budget_store.py` — dollar budget gate (mirrors token budget gate)
- [ ] Cap 64: `src/executors/trade_executor.py`
      (rules check → API call → ledger write)
- [ ] New OpenClaw template: `market_trader`
      (fetch price → fetch news signal → LLM signal score → governor rules check → execute)
- [ ] Env vars: `TRADING_PAPER_MODE=true`, `ALPACA_API_KEY`, `ALPACA_API_SECRET`,
      `TRADING_ACCOUNT_FLOOR`, `TRADING_DAILY_SPEND_LIMIT`, `TRADING_SINGLE_TRADE_MAX`,
      `TRADING_MAX_TRADES_PER_DAY`, `TRADING_ALLOWED_ASSETS`
- [ ] Frontend: trading widget card (balance, P&L, last trade, signal, pause button)
- [ ] Update `.env.example` with all trading vars

### 2.5 — Coinbase Crypto Connector (Phase 2)
- [ ] `src/connectors/coinbase_trading_connector.py`
- [ ] Env vars: `COINBASE_API_KEY`, `COINBASE_API_SECRET`
- [ ] Sandbox mode support

### 2.6 — Live Trading Opt-In Flow
- [ ] UI confirmation flow to flip `TRADING_PAPER_MODE=false`
      (requires explicit multi-step confirmation, not just an env change)

---

## P3 — Agent / Node Architecture

Design doc: `NOVA_AGENT_NODE_ARCHITECTURE_2026-04-01.md`

### 3.1 — Webhook Trigger
- [ ] Governed endpoint: `POST /api/webhooks/trigger`
- [ ] New trigger type: `on_webhook`
- [ ] Auth: shared secret token per webhook source
- [ ] Governor handles external effect gate

### 3.2 — Two-Model Pipeline per Template Step
- [ ] Add `model_preference` field per template step
      (`"local"` | `"deepseek"` | `"openai"` | `"auto"`)
- [ ] Conversation router respects per-step preference

### 3.3 — Node Protocol (Phase 10+)
- [ ] WebSocket → REST bridge for external callers
- [ ] Node discovery protocol
- [ ] Governor-to-governor trust handshake between Nova instances

---

## Open Items — Add As You Think of Them

- [ ] Should Nova suggest promoting rolling memories to permanent automatically?
- [ ] Should trading P&L summary appear in the evening digest template?
- [ ] Should there be a "explain your last trade" chat command from the ledger?
- [ ] Should the DeepSeek routing note data-goes-to-China in the UI like OpenAI keys do?
- [ ] Should user rules be changeable mid-conversation via chat ("be more concise")?
- [ ] Should connection card health checks run on a schedule (not just on save)?
- [ ] Live trading mode: should it require a UI confirmation step beyond flipping the env var?
- [ ] Max drawdown rule for trading: pause if account drops X% from peak?

---

## Design Docs Index

| Doc | Topic |
|---|---|
| `NOVA_AGENT_NODE_ARCHITECTURE_2026-04-01.md` | Intelligence tiers, provider routing, node roadmap |
| `NOVA_CONNECTIONS_SETUP_UI_REDESIGN.md` | Setup page, user profile, connection cards |
| `NOVA_MEMORY_TIERS_DESIGN.md` | Rolling memory, permanent memory, purge logic |
| `NOVA_AUTOMATIONS_DESIGN.md` | Templates, triggers, RSS, email triage, file watch |
| `NOVA_TRADING_CONNECTOR_DESIGN.md` | Auto-trading, Alpaca, rules gate, dollar budget |
| `NOVA_AUDIT_TODO_2026-03-28.md` | Code-level audit remediation backlog |

---

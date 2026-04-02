# Nova — Automations Design
Status: PLANNED — not yet started
Updated: 2026-04-02

---

## What Already Exists

| Capability | Status |
|---|---|
| Morning Brief (weather + calendar + news) | Template exists, paused by default |
| Evening Digest | Template exists, paused |
| Inbox Check | Template stub — waiting on email connector |
| Market Watch | Manual only |
| Time-based scheduling (HH:MM daily) | Live — 30s polling loop |
| Quiet hours + rate limiting | Live |
| Once or daily recurrence | Live |

The execution foundation is solid. Gaps: no event-based triggers, no user-created templates,
no RSS/research digest, no document processing, no chaining beyond the 4 hardcoded templates.

---

## What Real People Build (Research Findings)

### Most Common Workflows People Automate

1. **Morning brief / daily digest** — calendar + news + weather compiled into one delivery
2. **Email triage** — classify on arrival, surface urgent, batch noise
3. **RSS / research digest** — aggregate 20+ sources, score relevance, deliver top N
4. **Meeting prep** — pull context 30 min before a calendar event
5. **Document drop processing** — drop a file, get a summary saved to memory
6. **Alert aggregation** — multiple services → one webhook → AI classifies urgency
7. **Home automation with context** — presence/sensor events + LLM reasoning + action

### Trigger Types People Use
- **Time-based** — most common starting point. Cron at 7:00 AM.
- **Event-based** — new email, calendar event upcoming, file dropped in folder
- **Webhook** — external service posts to a single endpoint, AI routes it
- **Voice command** — wake word → STT → LLM → action

### Patterns That Appear Everywhere
- Two-model pattern: fast/cheap model for classification, stronger model for synthesis
- Loop with memory: fetch → filter seen items → summarize → store → repeat
- Structured JSON output enforced on LLM so results are always parseable
- Config stored outside code (Google Sheets equivalent) so rules can be edited without rebuilding

---

## Automations to Add — Prioritized

### Tier 1 — High value, fits Nova's architecture cleanly

#### 1. RSS / Research Digest Template
New OpenClaw template: `research_digest`

- User maintains a list of RSS feed URLs in the UI (new: feed list store)
- Template runs daily at user-set time
- Steps: fetch feeds → filter last 24h → score relevance against user interest tags
  (drawn from profile rules) → summarize top N → deliver to widget or chat
- No new trigger type needed — uses existing time-based scheduler

**Files to create/modify:**
- `nova_backend/src/openclaw/feed_store.py` — RSS URL list store
- New OpenClaw template entry in `agent_runtime_store.py`
- New executor step: `rss_fetch` that pulls and parses feeds
- UI: feed list manager in Settings

---

#### 2. User-Created Templates
Let users build their own automation templates instead of only having 4 hardcoded ones.

A template is: name + ordered list of capability steps + schedule + delivery mode.
The `OpenClawAgentRunner` already executes any template — only creation needs to be user-driven.

**Files to create/modify:**
- `POST /api/openclaw/agent/templates` — save a custom template
- `DELETE /api/openclaw/agent/templates/{id}` — remove a custom template
- UI: template builder form (name, step picker, schedule, delivery mode)
- Persist custom templates alongside defaults in `agent_runtime.json`

---

#### 3. Smarter Recurrence
Currently only "once" or "daily." People need weekdays-only, weekly, every N hours.

Human-readable options (not cron syntax):
- Every day
- Weekdays only
- Weekends only
- Weekly (pick a day)
- Every N hours

**Files to modify:**
- `notification_schedule_store.py` — extend recurrence field values
- `agent_scheduler.py` — update `due_scheduled_templates()` to evaluate new patterns
- UI: recurrence picker in schedule editor

---

### Tier 2 — Medium value, needs a new trigger type

#### 4. Email Triage
New email arrives → classify (urgent / actionable / noise) → surface urgent immediately,
batch the rest into a daily digest.

The email connector stub (`src/connectors/email_connector.py`) is ready.
Needs a real IMAP or Gmail API implementation wired in.

Template: `email_triage`
- Steps: fetch inbox (email connector) → LLM classify each message → route urgent to chat,
  batch others to widget digest
- Trigger: `on_email_received` — IMAP polling every 5–10 minutes

**Files to create/modify:**
- `nova_backend/src/connectors/imap_email_connector.py` — concrete IMAP implementation
- New trigger type `on_email_received` in scheduler
- `email_triage` template in agent runtime store
- Env vars: `NOVA_EMAIL_PROVIDER`, `NOVA_EMAIL_HOST`, `NOVA_EMAIL_PORT`,
  `NOVA_EMAIL_USER`, `NOVA_EMAIL_SECRET`

---

#### 5. Meeting Prep
Calendar event starting in N minutes → pull relevant context from memory → surface a prep card.

Template: `meeting_prep`
- Steps: fetch upcoming calendar events → filter for events in next 30 min →
  search memory for relevant context on attendees/topic → summarize → deliver as widget card
- Trigger: `on_calendar_event_upcoming` — calendar poller checks for events starting in N minutes

**Files to create/modify:**
- New trigger type `on_calendar_event_upcoming` in scheduler
- `meeting_prep` template
- Calendar cap (56) already exists — no executor changes needed

---

#### 6. File Watch / Document Drop
User drops a file into a watched folder → Nova processes it and saves summary to memory.

Template: `document_ingest`
- Steps: detect file → extract text (PDF, .txt, .md, audio) → LLM summarize →
  save to governed memory as a permanent record
- Trigger: `on_file_created` in a configured watch directory

**Files to create/modify:**
- `nova_backend/src/tasks/file_watcher.py` — Python watchdog-based file watcher
- New trigger type `on_file_created`
- `document_ingest` template
- Env var: `NOVA_WATCH_DIR` — directory to monitor
- UI: watch directory picker in Settings

---

### Tier 3 — Future, more complex

#### 7. Webhook Trigger
External services post to one Nova endpoint → AI classifies urgency → routes or batches.

- New governed endpoint: `POST /api/webhooks/trigger`
- New trigger type: `on_webhook`
- Governor handles the external effect gate
- User maps webhook sources to templates in the UI

#### 8. Two-Model Pipeline per Step
Specify "use local for classification steps, use cloud for synthesis steps" per template.
`MODEL_PROVIDER=auto` + `openai_responses_lane.py` already enables this at the provider level.
Templates just need a per-step `model_preference` field.

---

## Architecture: How New Triggers Fit

Everything routes into the existing `OpenClawAgentRunner.run_template()`.
Only trigger detection is new:

```
Current:
  Trigger: time (HH:MM daily)
    └── agent_scheduler.py polls every 30s → runs template

Add:
  Trigger: time (extended recurrence)       ← same scheduler, new recurrence logic
  Trigger: on_email_received                ← IMAP poller every 5 min
  Trigger: on_calendar_event_upcoming       ← calendar poller checks N-min window
  Trigger: on_file_created                  ← watchdog file system watcher
  Trigger: on_webhook                       ← FastAPI endpoint fires template
  Trigger: manual                           ← already exists
```

No changes to execution layer. Only trigger detection is new per type.

---

## Build Order

1. User-created templates — unlocks everything; users can build their own immediately
2. Extended recurrence — quick win, big quality-of-life
3. RSS digest template — no new trigger needed, self-contained
4. Email connector (IMAP) + email triage — finishes the inbox_check stub
5. Calendar upcoming trigger + meeting prep — natural extension of cap 56
6. File watcher + document ingest — new input surface
7. Webhook receiver — opens Nova to external services in a governed way

---

## Open Questions / Things to Add

- [ ] Should custom user templates support conditional steps ("only run step 2 if step 1 returns X")?
- [ ] Should there be a template marketplace or share format so users can import templates?
- [ ] How many steps max per template before it becomes unwieldy?
- [ ] Should the two-model pattern be a first-class config option per template or per step?
- [ ] File watcher: which file types to support first — .txt/.md only, or also PDF and audio?
- [ ] Should email triage auto-reply be in scope or read-only classification only?
- [ ] Webhook: should incoming webhooks require a shared secret token for auth?

---

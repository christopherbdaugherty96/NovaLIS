# UI Simplification Inventory - 2026-05-09

Status: inventory / product-direction corrected 2026-05-09 / no runtime changes in this branch

## Product Direction Correction (2026-05-09)

The original inventory classified most pages as KEEP and the intro page as REMOVE.
That was wrong for the product direction.

The corrected target is:

```text
Start screen (Intro)
↓
Chat
News
CRM
Settings
```

Everything else folds in:

- Home → dissolve; useful status/morning pieces move into Chat or Settings
- Memory → not top-level; exposed through Chat and Settings
- Workspace → not top-level; business-facing pieces into CRM, diagnostics into Settings
- Trust → not top-level; fold into Settings / Governance
- Policy → not top-level; fold into Settings / Governance / Advanced
- Agent → not top-level; fold into Settings / Advanced
- CRM → new top-level; future-facing/read-only/setup-required

CRM must be future-facing and read-only unless an exact governed backend capability
exists. No CRM write actions. No Shopify writes. No email sends. No autonomous workflows.

This changes the classification of navigation entries and intro page buttons below.
All other section classifications remain valid.

## Purpose

Classify every visible dashboard control before the UI simplification
implementation branch. The rule is:

```text
visible by default = only what the user needs + what the backend truly supports
```

A visible primary action button implies authority in Nova. If there is no
governed backend path for the exact behavior, the button should not look like
a primary action.

## Classification Key

```text
KEEP      — required for normal use; backend-backed; stays visible
COLLAPSE  — useful for diagnostics/governance but too noisy for default view;
            hide behind Details/Advanced/Diagnostics drawer
REMOVE    — shortcut/demo/future-looking/duplicative/not directly backend-backed;
            confuses user expectation of capability
```

## Hard Constraints on This Inventory

This doc classifies. It does not:

- change any runtime code
- change any JavaScript
- add capabilities
- remove governance visibility entirely
- hide action/no-action status
- approve Browser Use or computer-use expansion
- approve OpenClaw expansion
- approve external writes or autonomous workflows

---

## Section 1 — Core Chat Interface

These are the non-negotiable user-facing controls. Nothing here should change.

| Element | ID / location | Current behavior | Backend-backed? | Classification | Rationale |
|---|---|---|---|---|---|
| Chat input | `#chat-input` | Accepts user text | Yes | **KEEP** | Core interaction |
| Send button | `#send-btn` | Sends message via `/ws` | Yes | **KEEP** | Core interaction |
| Assistant response area | `#chat-messages` | Displays responses | Yes | **KEEP** | Core output |
| Connection/status chip | `#header-connection-chip` | Shows connected/disconnected | Yes | **KEEP** | Truthfulness requirement |
| Loading hint | `#loading-hint` | Shows "Nova is answering…" | Yes | **KEEP** | Guard visibility |
| Thinking bar | orb/status indicator | Shows active turn in progress | Yes | **KEEP** | Guard visibility |

---

## Section 2 — Trust Receipt

| Element | ID / location | Current behavior | Backend-backed? | Classification | Rationale |
|---|---|---|---|---|---|
| Trust Review Card | inline in `#chat-messages` | Displays non-action planning receipt | Yes | **KEEP** | Core governance visibility |
| Trust strip / confidence badge | inline in responses | Shows "No action", confidence label | Yes | **KEEP** | Truthfulness requirement |
| Trust receipt expanded detail | trust card body | Shows authority_effect, execution fields | Yes | **COLLAPSE** | Default: "No action taken." / Expanded: full detail on click |

---

## Section 3 — Navigation: Target Product Hierarchy

The corrected product hierarchy reduces top-level pages to four plus a Start screen.
The current 10-tab structure is too wide and implies capabilities that are not top-level
user goals.

### Target top-level pages

| Page | Status | Notes |
|---|---|---|
| Start / Intro | **KEEP — new role** | Entry point; becomes a minimal welcome screen with one Start button and a Settings link |
| Chat | **KEEP** | Primary page; unchanged |
| News | **KEEP** | Core governed information feature; unchanged |
| CRM | **ADD (future-facing)** | New page; read-only/setup-required; Shopify read status if configured; no writes |
| Settings | **KEEP — expanded** | Absorbs governance, memory, voice, connections, policy, agent, diagnostics, advanced |

### Pages folded out of top-level navigation

| Current page | Disposition |
|---|---|
| Home (`page-home`) | Dissolve; morning/weather/status pieces move into Chat sidebar or Settings |
| Memory (`page-memory`) | Not top-level; memory access through Chat (ask/remember) and Settings |
| Workspace (`page-workspace`) | Not top-level; business-facing pieces into CRM; thread/structure into Settings / Advanced |
| Trust (`page-trust`) | Not top-level; fold into Settings / Governance section |
| Policy (`page-policy`) | Not top-level; fold into Settings / Governance / Advanced |
| Agent (`page-agent`) | Not top-level; fold into Settings / Advanced |

### Folded Page Destination Map

Where each non-top-level page's content and buttons go:

| Current page | New destination | Button fate |
|---|---|---|
| Home (`page-home`) | Chat sidebar / Settings | Morning/weather/calendar status → Chat contextual or Settings status section; diagnostic widgets → Settings / Diagnostics; shortcut chips → see Section 12 |
| Memory (`page-memory`) | Settings / Memory | All memory action buttons (list, filter, edit, lock, defer, delete) move into Settings / Memory sub-section |
| Workspace (`page-workspace`) | CRM (business-facing) + Settings / Workspace (diagnostic) | Board thread/architecture views → Settings / Workspace; business project context → CRM |
| Trust (`page-trust`) | Settings / Governance | All trust subsection buttons become Settings / Governance accordions; no separate nav page |
| Policy (`page-policy`) | Settings / Policy | Policy overview → Settings / Policy; policy create shortcuts → REMOVE |
| Agent (`page-agent`) | Settings / Agent / Advanced | Agent refresh and status → Settings / Agent section; agent-to-trust/home nav links → obsolete |
| Intro (`page-intro`) | Start screen | Becomes entry point; buttons reduced to Start + Settings link only |

---

### Settings Structure Map

Settings absorbs six folded pages. New Settings sub-section structure:

| Sub-section | Content | Source pages / buttons |
|---|---|---|
| General | Profile, identity, preferences, rules, accessibility, privacy, reset | Existing Settings buttons: profile-save-*, reset-defaults, accessibility, privacy |
| Connections | External connections, calendar setup, API status | btn-connections-refresh, btn-settings-open-connections, btn-morning-calendar-connect |
| Voice | Voice status, voice check | btn-settings-voice-status, btn-settings-voice-check |
| Memory | Memory list, filter, edit, lock, defer, delete, export | All btn-memory-* from current Memory page |
| Governance / Trust | Trust status summary, authority boundary, system/memory/bridge status | btn-trust-center-refresh + trust subsections (all as accordions) |
| Policy | Policy overview, capability readiness | btn-policy-refresh, btn-policy-capability-map; no creation shortcuts |
| Agent / OpenClaw | Agent and bridge status | btn-agent-refresh; read-only status only |
| Workspace / Project context | Thread structure, board views | btn-workspace-board-* views; diagnostic only |
| Diagnostics | Workflow steps, operational context, assistive notices, runtime refresh | btn-workflow-*, btn-operational-context-*, btn-assistive-*, btn-settings-refresh-runtime |
| Advanced / Proof | Proof surfaces, capability surface widget, operator health, bridge reasoning grids | Collapsed by default; operator/developer view only |

---

### CRM Stub (current-state definition)

CRM is future-facing. The stub page renders what exists today:

```text
CRM page (current state):

Title: CRM

Default state (no integrations configured):
  - "Business integrations coming soon."
  - One link: Settings / Connections (to configure)

Shopify (if configured):
  - Read-only store status / revenue summary from Cap 65
  - No write actions. No create/update/delete product or order.

Email (always):
  - Email draft creation through Chat only, user-initiated, confirmation-bound
  - User sends manually. No inbox access. No autonomous send.

Calendar / business context:
  - Read-only event list if calendar connected
  - Setup-required state if not connected
```

No buttons: "Add lead", "Send follow-up", "Create deal", "Sync customer",
"Assign task", or any CRM write action.

---

### Intro / Start screen buttons (corrected from Section 10)

The intro page is **KEEP** — it becomes the Start screen, not a page to remove.
Its buttons are reduced:

| Button ID | Classification | Rationale |
|---|---|---|
| Start / enter-chat button | **KEEP** | One primary action: enter Chat |
| `btn-intro-open-settings` | **KEEP** | Secondary link to Settings |
| `btn-intro-open-connections` | **COLLAPSE** | Inline setup prompt is enough |
| `btn-intro-daily-brief` | **REMOVE** | Specific action shortcut; not a launch button |
| `btn-intro-open-home` | **REMOVE** | Home is not top-level |
| `btn-intro-open-home-ready` | **REMOVE** | Same |
| `btn-intro-open-landing` | **REMOVE** | Redundant |
| `btn-intro-refresh-setup` | **COLLAPSE** | Surface inline; not a prominent button |

---

## Section 4 — Buttons: Chat Page

### Chat vs News: resolved decision

News has its own top-level page. Chat renders news widgets inline when the user
asks, but Chat should not duplicate the full News control cluster as persistent
shortcut buttons. Five news-specific buttons on the Chat page implies News is a
Chat sub-feature, not a peer page.

Decision: move persistent News controls to the News page. Remove them from the
Chat default view. The user navigates to News to browse; news results appear in
Chat when requested via natural language or a single chip ("Today's news").

| Button ID | Label | Current behavior | Backend-backed? | Classification | Rationale |
|---|---|---|---|---|---|
| `btn-news` | News | Requests news widget | Yes | **REMOVE from Chat** | News page owns this; one nav chip in Chat is enough |
| `btn-news-summary` | Summary | Requests news summary | Yes | **REMOVE from Chat** | Same |
| `btn-news-refresh` | Refresh | Refreshes news | Yes | **REMOVE from Chat** | Same |
| `btn-news-expand` | Expand | Expands news list | Yes | **REMOVE from Chat** | Same |
| `btn-news-search` | Search | Opens search input | Yes | **REMOVE from Chat** | Same; search chip in Chat covers this |
| `btn-morning-toggle` | Morning | Toggles morning panel | Yes | **KEEP** | Status/calendar/weather summary before Chat; stays in Chat |
| `btn-morning-calendar-connect` | Connect calendar | Opens calendar setup | Partial — setup-required | **COLLAPSE** → **Settings / Connections** | Show as Settings link when setup-required; not a Chat button |
| `btn-hints-toggle` | Hints | Toggles hint panel | No direct backend | **REMOVE** | Low-value in current form |
| `btn-live-help-start` | Live help start | Starts live help session | Unclear / limited | **REMOVE** | No clear governed path |
| `btn-live-help-stop` | Live help stop | Stops live help | Same | **REMOVE** | Same |
| `btn-live-help-explain` | Explain | Explain via live help | Same | **REMOVE** | Same |

---

## Section 5 — Buttons: Memory Page

| Button ID | Label | Current behavior | Backend-backed? | Classification | Rationale |
|---|---|---|---|---|---|
| `btn-memory-overview` | Overview | Memory overview | Yes | **KEEP** | Core |
| `btn-memory-list` | List | Memory list | Yes | **KEEP** | Core |
| `btn-memory-list-all` | All | All memories | Yes | **KEEP** | Core |
| `btn-memory-recent` | Recent | Recent memories | Yes | **KEEP** | Core |
| `btn-memory-list-active` | Active | Active-tier filter | Yes | **KEEP** | Useful filter |
| `btn-memory-list-locked` | Locked | Locked-tier filter | Yes | **KEEP** | Useful filter |
| `btn-memory-list-deferred` | Deferred | Deferred-tier filter | Yes | **KEEP** | Useful filter |
| `btn-memory-list-current-thread` | Thread | Thread-scoped filter | Yes | **KEEP** | Useful filter |
| `btn-memory-refresh` | Refresh | Silent refresh | Yes | **KEEP** | Core |
| `btn-memory-threads` | Threads | Thread-memory view | Yes | **KEEP** | Core |
| `btn-memory-review-list` | Review | Memory review list | Yes | **KEEP** | Core |
| `btn-memory-detail-edit` | Edit | Edit a memory | Yes | **KEEP** | Core action |
| `btn-memory-detail-lock` | Lock | Lock a memory | Yes | **KEEP** | Core action |
| `btn-memory-detail-unlock` | Unlock | Unlock a memory | Yes | **KEEP** | Core action |
| `btn-memory-detail-defer` | Defer | Defer a memory | Yes | **KEEP** | Core action |
| `btn-memory-detail-delete` | Delete | Delete a memory | Yes | **KEEP** | Core action |
| `btn-memory-detail-show-chat` | Show in chat | Opens chat with memory context | Yes | **KEEP** | Useful |
| `btn-memory-inline-confirm` | Confirm | Confirms inline edit | Yes | **KEEP** | Required for edit flow |
| `btn-memory-inline-cancel` | Cancel | Cancels inline edit | Yes | **KEEP** | Required for edit flow |
| `btn-memory-export` | Export | Exports memory | Partial — format unclear | **COLLAPSE** | Advanced; hide in details drawer |

---

## Section 6 — Buttons: Trust Center Page

| Button ID | Label | Current behavior | Backend-backed? | Classification | Rationale |
|---|---|---|---|---|---|
| `btn-trust-center-refresh` | Refresh | Refreshes trust data | Yes | **KEEP** | Core |
| `btn-trust-center-system` | System | Shows system section | Yes | **COLLAPSE** | Default: summary visible; sections behind expand |
| `btn-trust-center-memory` | Memory | Shows memory section | Yes | **COLLAPSE** | Same |
| `btn-trust-center-policy-map` | Policy map | Shows policy readiness | Yes | **COLLAPSE** | Same |
| `btn-trust-center-voice-check` | Voice check | Runs voice check | Partial — setup-required | **COLLAPSE** | Only relevant post-setup |
| `btn-trust-center-bridge-status` | Bridge | Shows bridge section | Yes | **COLLAPSE** | Diagnostic; collapse by default |
| `btn-trust-center-workspace` | Workspace | Shows workspace section | Yes | **COLLAPSE** | Diagnostic |
| `btn-trust-center-agent` | Agent | Shows agent section | Yes | **COLLAPSE** | Diagnostic |
| `btn-trust-center-settings` | Settings | Navigates to settings | Yes | **KEEP** | Navigation |

---

## Section 7 — Buttons: Policy Page

| Button ID | Label | Current behavior | Backend-backed? | Classification | Rationale |
|---|---|---|---|---|---|
| `btn-policy-refresh` | Refresh | Refreshes policy overview | Yes | **KEEP** | Core |
| `btn-policy-capability-map` | Capability map | Shows capability readiness | Yes | **COLLAPSE** | Advanced/diagnostic |
| `btn-policy-create-weather` | Create weather rule | Injects policy create command | Partial — policy path exists but limited | **REMOVE** | Looks like a capability; inject via chat if needed |
| `btn-policy-create-calendar` | Create calendar rule | Same | Same | **REMOVE** | Same |
| `btn-policy-create-status` | Create status rule | Same | Same | **REMOVE** | Same |
| `btn-policy-open-trust` | Open trust | Navigates to trust | Yes | **KEEP** | Navigation |
| `btn-policy-open-settings` | Open settings | Navigates to settings | Yes | **KEEP** | Navigation |

---

## Section 8 — Buttons: Settings Page

| Button ID | Label | Current behavior | Backend-backed? | Classification | Rationale |
|---|---|---|---|---|---|
| `btn-settings-refresh-runtime` | Refresh runtime | Refreshes runtime status | Yes | **KEEP** | Core |
| `btn-settings-voice-status` | Voice status | Shows voice status | Yes | **KEEP** | Core |
| `btn-settings-voice-check` | Voice check | Runs voice check | Partial | **COLLAPSE** | Only useful post-setup |
| `btn-settings-open-connections` | Connections | Navigates to connections | Yes | **KEEP** | Core navigation |
| `btn-settings-open-trust` | Trust center | Navigates to trust | Yes | **RECLASSIFY** → scroll to Governance sub-section | Trust folds into Settings; this becomes a same-page scroll link, not cross-page nav |
| `btn-settings-open-home` | Home | Navigates to home | Yes | **REMOVE** | Home is not top-level; no destination |
| `btn-settings-open-agent` | Agent | Navigates to agent | Yes | **RECLASSIFY** → scroll to Agent / Advanced sub-section | Agent folds into Settings; same-page scroll |
| `btn-settings-open-accessibility` | Accessibility | Opens accessibility settings | Yes | **KEEP** | Useful |
| `btn-settings-open-privacy` | Privacy | Opens privacy settings | Yes | **KEEP** | Useful |
| `btn-settings-open-intro` | Intro / Return to Start | Navigates to Start screen | Yes | **KEEP** | Intro is now the Start screen; return path is valid |
| `btn-settings-reset-defaults` | Reset defaults | Resets settings | Yes | **KEEP** | Core — requires confirmation |
| `btn-reset-confirm` | Confirm reset | Executes reset | Yes | **KEEP** | Required by reset flow |
| `btn-reset-cancel` | Cancel reset | Aborts reset | Yes | **KEEP** | Required by reset flow |
| `btn-profile-save-identity` | Save identity | Saves identity prefs | Yes | **KEEP** | Core |
| `btn-profile-save-prefs` | Save prefs | Saves preferences | Yes | **KEEP** | Core |
| `btn-profile-save-rules` | Save rules | Saves rule prefs | Yes | **KEEP** | Core |

---

## Section 9 — Buttons: Home, Workspace, Agent Pages (folded)

Home, Workspace, and Agent are no longer standalone top-level pages. Their buttons
do not KEEP on standalone pages — they fold into Settings sub-sections or CRM, as
defined in the Section 3 Folded Page Destination Map.

### Home page buttons

| Button ID | Label | New destination | Classification |
|---|---|---|---|
| `btn-home-threads` | Threads | Settings / Workspace or CRM context | **COLLAPSE** into destination section |

### Workspace page buttons

| Button ID | Label | New destination | Classification |
|---|---|---|---|
| `btn-workspace-home-refresh` | Refresh | Settings / Workspace | **KEEP** in Settings / Workspace |
| `btn-workspace-board-refresh` | Refresh board | Settings / Workspace | **KEEP** in Settings / Workspace |
| `btn-workspace-board-threads` | Threads view | Settings / Workspace | **KEEP** in Settings / Workspace |
| `btn-workspace-board-architecture` | Architecture view | Settings / Workspace | **KEEP** in Settings / Workspace |
| `btn-workspace-board-visual` | Visual view | Settings / Workspace | **KEEP** in Settings / Workspace |

### Agent page buttons

| Button ID | Label | New destination | Classification |
|---|---|---|---|
| `btn-agent-refresh` | Refresh agent | Settings / Agent / Advanced | **KEEP** in Settings / Agent section |
| `btn-agent-open-home` | Home | — | **REMOVE** — Home is not top-level |
| `btn-agent-open-settings` | Settings | Settings | **KEEP** — still a valid nav link to parent page |
| `btn-agent-open-trust` | Trust | Settings / Governance | **RECLASSIFY** — becomes section link within Settings |

---

## Section 10 — Buttons: Intro / Start Screen

**Corrected:** Intro page is KEEP as the Start screen (not REMOVE).
See Section 3 for the corrected button-level classification.

---

## Section 11 — Buttons: Workflow / Operational Context

| Button ID | Label | Current behavior | Backend-backed? | Classification | Rationale |
|---|---|---|---|---|---|
| `btn-workflow-show-steps` | Show steps | Shows workflow steps | Partial | **COLLAPSE** | Diagnostic; collapse by default |
| `btn-workflow-refine` | Refine | Workflow refine action | Partial | **COLLAPSE** | Implies capability; collapse |
| `btn-workflow-reset` | Reset | Resets workflow state | Yes | **COLLAPSE** | Diagnostic |
| `btn-operational-context-refresh` | Refresh context | Refreshes operational context | Yes | **COLLAPSE** | Diagnostic |
| `btn-operational-context-reset` | Reset context | Resets operational context | Yes | **COLLAPSE** | Diagnostic |
| `btn-assistive-notices-refresh` | Refresh notices | Refreshes assistive notices | Yes | **COLLAPSE** | Diagnostic |
| `btn-assistive-open-settings` | Settings | Navigates to settings | Yes | **KEEP** | Navigation |
| `btn-connections-refresh` | Refresh | Refreshes connections | Yes | **KEEP** | Core |

---

## Section 12 — Quick Action Chips (Per-Page)

Quick action chips are configurable shortcuts injected into the chat. The concern is
that many look like primary capability buttons to a user who doesn't know they only
inject text.

| Page | Chip label | Command injected | Backend-backed? | Classification | Rationale |
|---|---|---|---|---|---|
| Chat | Plan this goal | "help me do this" | Weak | **REMOVE** | Generic; no specific backend path |
| Chat | Build a page | "build me a landing page…" | Weak | **REMOVE** | Implies construction capability |
| Chat | Research a topic | "research latest technology news" | Yes — search | **COLLAPSE** | Useful but should be in chat input, not chip |
| Chat | Explain what I'm seeing | "explain this" | Partial | **COLLAPSE** | Useful when screen context exists |
| Chat | Plan my day | "daily brief" | Yes | **KEEP** | Backend-backed; common user goal |
| Chat | Continue a project | "show threads" | Yes | **KEEP** | Backend-backed |
| Chat | Check project status | "project status this" | Partial | **COLLAPSE** | Useful but context-dependent |
| Chat | Review project memory | "memory list thread this" | Yes | **KEEP** | Backend-backed |
| Chat | Review saved memory | "memory overview" | Yes | **KEEP** | Backend-backed |
| Chat | Review reminders | "show schedules" | Partial | **COLLAPSE** | Only useful if schedules exist |
| Chat | Review patterns | "pattern status" | Yes | **KEEP** | Backend-backed |
| Chat | System status | "system status" | Yes | **KEEP** | Backend-backed |
| Chat | Tone settings | "tone status" | Yes | **COLLAPSE** | Diagnostic; secondary |
| Chat | Create analysis doc | "create analysis report on…" | Partial | **REMOVE** | Implies document creation beyond current scope |
| Chat | Open analysis docs | "list analysis docs" | Partial | **COLLAPSE** | Secondary |
| News | Get headlines | "news" | Yes | **KEEP** | Core |
| News | Source brief | "today's news" | Yes | **KEEP** | Core |
| News | Daily brief | "daily brief" | Yes | **KEEP** | Core |
| News | Compare stories | "compare headlines 1 and 2" | Partial | **COLLAPSE** | Context-dependent |
| News | Explain this page | "what is this page" | Weak | **REMOVE** | Noise |
| Home | System status | "system status" | Yes | **MOVE to Chat chips** | Useful; keep as a Chat-page chip since Home dissolves |
| Home | Calendar | "calendar" | Yes | **MOVE to Chat chips** | Contextual; Chat renders calendar widget on request |
| Home | Weather | "weather" | Yes | **MOVE to Chat chips** | Contextual; Chat renders weather widget on request |
| Home | Home agent | "bridge status" | Yes | **MOVE to Settings / Agent** | Diagnostic; Settings / Agent section surfaces this |
| Home | Explain this | "explain this" | Partial | **REMOVE** | Context-dependent; better via natural language in Chat |
| Home | Analyze screen | "analyze this screen" | Partial — setup-required | **REMOVE** | Implies computer-use; setup-required and misleading |
| Home | Show threads | "show threads" | Yes | **MOVE to Chat chips** | Useful; keep as Chat-page chip |
| Home | Project status | "project status this" | Partial | **COLLAPSE** | Context-dependent; keep as secondary Chat chip if anything |
| Home | Most blocked | "which project is most blocked…" | Partial | **REMOVE** | Overpromises project management depth |
| Home | Memory overview | "memory overview" | Yes | **MOVE to Chat chips** | Useful; keep as Chat-page chip |
| Home | Tone settings | "tone status" | Yes | **REMOVE** | Diagnostic; available via natural language |
| Home | Schedules | "show schedules" | Partial | **REMOVE** | Secondary; not a default chip |
| Home | Pattern review | "pattern status" | Yes | **REMOVE** | Secondary; not a default chip |
| Policy | Create calendar rule | "policy create weekday calendar…" | Partial | **REMOVE** | Implies policy automation; no shortcut |
| Policy | Create weather rule | "policy create daily weather…" | Partial | **REMOVE** | Same |

---

## Section 13 — Suggested/Assistant Action Buttons (Per Response)

These appear after assistant responses and inject follow-up commands.

| Button label | Injected behavior | Backend-backed? | Classification | Rationale |
|---|---|---|---|---|
| "Follow-up analysis" | `phase42: follow up on this report…` | Partial | **REMOVE** | Internal command string visible to user; confusing |
| "Expand", "Track story", "Compare" | Inject news follow-up commands | Yes | **KEEP** | Backend-backed news actions |
| "Copy" | Copies response text | Client-only | **KEEP** | Useful utility |
| Suggested actions (derived) | Commands like "Today's brief", "3 bullet version" | Yes | **COLLAPSE** | Show one max; not the full set |
| "Sources and confidence" | Shows search source detail | Yes | **KEEP** | Governance visibility |
| "What matters most?", "Best next step" | Planning follow-ups | Yes | **COLLAPSE** | Secondary; one or zero per response |

---

## Section 14 — Diagnostic / Proof Surfaces

| Surface | Location | Classification | Rationale |
|---|---|---|---|
| Capability surface widget | Home page | **COLLAPSE** | Developer/operator view; not end-user |
| Operator health widget | Home page | **COLLAPSE** | Developer/operator view |
| Trust internals grid (provider, route, authority fields) | Trust page | **COLLAPSE** | Show summary; full grid behind expand |
| Bridge/reasoning runtime grids | Trust page | **COLLAPSE** | Diagnostic; collapse by default |
| Raw evidence chips (provider/freshness/source) | Search results | **KEEP** | Required for truthfulness; keep visible but compact |
| `Confidence: …` badge | Responses | **KEEP** | Required for truthfulness |
| `Evidence: …` / `Provider: …` / `Freshness: …` chips | Search widget | **COLLAPSE** | One-line summary visible; full detail behind expand |
| Usage/route chips in chat | After responses | **COLLAPSE** | Debug info; collapse by default |

---

## Summary Counts

Counts revised after product-direction correction and structural patch.
Original counts (KEEP ~55 / COLLAPSE ~30 / REMOVE ~18) were based on the 10-page
standalone-page hierarchy and are no longer accurate.

Revised approximate counts after folding non-top-level pages into Settings / CRM:

| Classification | Count (approx) | Notes |
|---|---|---|
| KEEP (as-is or in new destination) | ~50 | Core chat, memory actions, settings actions, news page, workspace board views in Settings, agent refresh in Settings |
| COLLAPSE (behind expand/accordion) | ~20 | Trust subsections, diagnostics, some quick-action chips |
| REMOVE | ~30 | Home nav, Policy create shortcuts, live-help, noisy chips, cross-page nav to dissolved pages, 5 Chat news buttons |
| MOVE (chip to different page) | ~5 | Home chips → Chat chips |
| RECLASSIFY (cross-page nav → section link) | ~4 | trust, agent, workspace nav links become same-page Settings section links |

---

## Recommended Implementation Order

### Branch 2: `ui/simplify-dashboard-core-navigation`

PR title: `ui: simplify dashboard to start plus core navigation`

Implement in this order to limit blast radius:

1. **Reduce nav to four tabs + Start** — Chat, News, CRM (setup-required stub), Settings; hide Home,
   Memory, Workspace, Trust, Policy, Agent from top-level nav bar

2. **Reduce intro/Start screen** — strip to: welcome text, one-line authority boundary, Start button,
   Settings link; remove `btn-intro-daily-brief`, `btn-intro-open-home`, `btn-intro-open-home-ready`,
   `btn-intro-open-landing`

3. **Expand Settings with sub-sections** (the largest step — break into sub-commits):
   - 3a: Add Memory sub-section — surface btn-memory-* buttons inside Settings
   - 3b: Add Governance / Trust sub-section — trust center as accordion inside Settings
   - 3c: Add Policy sub-section — policy overview only; no creation shortcuts
   - 3d: Add Agent / Advanced sub-section — agent refresh, bridge status
   - 3e: Add Workspace / Project sub-section — board views
   - 3f: Add Diagnostics sub-section — workflow, operational context, assistive, runtime refresh
   - 3g: Remove `btn-settings-open-home`, reclassify `btn-settings-open-trust` and
     `btn-settings-open-agent` as same-page section links, keep `btn-settings-open-intro`

4. **Add CRM stub** — setup-required placeholder per Section 3 CRM Stub definition;
   Shopify read status if configured; no write actions

5. **Remove Chat-page News button cluster** — remove `btn-news`, `btn-news-summary`,
   `btn-news-refresh`, `btn-news-expand`, `btn-news-search` from Chat; Chat renders news
   results inline when user asks; add one "Open News" navigation chip if needed

6. **Relocate Home chips to Chat** — move weather, calendar, system-status, show-threads,
   memory-overview chips to Chat page chips; remove analyze-screen, most-blocked, tone-settings,
   schedules, pattern-review, explain-this Home chips

7. **Remove live-help buttons**, **policy create shortcut buttons**, and remaining noisy chips
   (chat_plan_goal, chat_build_page, phase42 follow-up, policy create chips)

8. **Collapse trust card expanded detail** — default "No action taken."; expand on click

### Files likely affected

```text
nova_backend/static/index.html           — button removal, collapse wrappers
nova_backend/static/dashboard-config.js — quick action chip lists
nova_backend/static/dashboard-chat-news.js — suggested action button limits
nova_backend/static/dashboard-control-center.js — trust/diagnostic section collapse
Nova-Frontend-Dashboard/dashboard-chat-news.js — mirror of chat-news changes
```

### Verification after implementation

```text
node --check nova_backend/static/dashboard-chat-news.js
node --check Nova-Frontend-Dashboard/dashboard-chat-news.js

python -m pytest nova_backend/tests/phase45/test_dashboard_event_replay_harness.py \
  nova_backend/tests/phase45/test_dashboard_auto_widget_dispatch.py \
  nova_backend/tests/phase45/test_dashboard_no_auto_widget_dispatch.py \
  nova_backend/tests/websocket/test_session_handler_proof_blockers.py \
  nova_backend/tests/phase45/test_non_search_widget_fuzzing.py -q

Expected: 51 passed
```

### Risks

| Risk | Mitigation |
|---|---|
| Removing a button breaks a test assertion | Run full test suite before and after each removal batch |
| Collapse hides content the user actually needs | Start with clear-REMOVE items; review COLLAPSE list in PR |
| `dashboard-config.js` chip removal breaks chip rendering | Chip renderer degrades safely if the list is shorter |
| Frontend mirror drifts from backend | Mirror both `dashboard-chat-news.js` files in each commit |

# UI Simplification Inventory - 2026-05-09

Status: draft inventory / no runtime changes in this branch

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

## Section 3 — Navigation Tabs

The nav bar is appropriate. All 10 pages have some backend-backed content.
The issue is how full each page feels, not whether the tab exists.

| Tab | Page | Backend-backed content? | Classification | Rationale |
|---|---|---|---|---|
| Chat | `page-chat` | Yes | **KEEP** | Primary page |
| Home | `page-home` | Yes — system status, weather, calendar, threads | **KEEP** | Useful launch surface |
| News | `page-news` | Yes — governed news/search | **KEEP** | Core feature |
| Memory | `page-memory` | Yes — explicit memory store | **KEEP** | Core feature |
| Workspace | `page-workspace` | Yes — thread/structure map | **KEEP** | Useful |
| Trust | `page-trust` | Yes — trust/status surface | **KEEP** | Governance visibility |
| Policy | `page-policy` | Partial — policy overview backend exists; creation is limited | **KEEP** (with note below) | Keep but clean up policy page action buttons |
| Settings | `page-settings` | Yes — voice/runtime/connections | **KEEP** | Necessary |
| Agent | `page-agent` | Partial — bridge status; limited live capability | **COLLAPSE** (into Settings or Trust) | Low user utility as a standalone tab; mostly duplicates Trust + Settings |
| Intro | `page-intro` | Static onboarding content | **REMOVE** (or COLLAPSE to first-run only) | Not useful for ongoing sessions; should auto-dismiss after first use |

---

## Section 4 — Buttons: Chat Page

| Button ID | Label | Current behavior | Backend-backed? | Classification | Rationale |
|---|---|---|---|---|---|
| `btn-news` | News | Requests news widget | Yes | **KEEP** | Core |
| `btn-news-summary` | Summary | Requests news summary | Yes | **KEEP** | Core |
| `btn-news-refresh` | Refresh | Refreshes news | Yes | **KEEP** | Core |
| `btn-news-expand` | Expand | Expands news list | Yes | **KEEP** | Useful |
| `btn-news-search` | Search | Opens search input | Yes | **KEEP** | Core |
| `btn-morning-toggle` | Morning | Toggles morning panel | Yes | **KEEP** | Useful summary |
| `btn-morning-calendar-connect` | Connect calendar | Opens calendar setup | Partial — setup-required | **COLLAPSE** | Only relevant pre-setup; show inline in calendar widget when setup-required |
| `btn-hints-toggle` | Hints | Toggles hint panel | No direct backend | **REMOVE** | Adds noise; hints are low-value in current form |
| `btn-live-help-start` | Live help start | Starts live help session | Unclear / limited | **REMOVE** | Implies autonomy; unclear governed path |
| `btn-live-help-stop` | Live help stop | Stops live help | Same | **REMOVE** | Same as above |
| `btn-live-help-explain` | Explain | Explain via live help | Same | **REMOVE** | Same as above |

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
| `btn-settings-open-trust` | Trust center | Navigates to trust | Yes | **KEEP** | Core navigation |
| `btn-settings-open-home` | Home | Navigates to home | Yes | **KEEP** | Navigation |
| `btn-settings-open-agent` | Agent | Navigates to agent | Yes | **COLLAPSE** | Low-value if agent page collapses |
| `btn-settings-open-accessibility` | Accessibility | Opens accessibility settings | Yes | **KEEP** | Useful |
| `btn-settings-open-privacy` | Privacy | Opens privacy settings | Yes | **KEEP** | Useful |
| `btn-settings-open-intro` | Intro | Navigates to intro | Low | **REMOVE** | Intro page is low-value for ongoing sessions |
| `btn-settings-reset-defaults` | Reset defaults | Resets settings | Yes | **KEEP** | Core — requires confirmation |
| `btn-reset-confirm` | Confirm reset | Executes reset | Yes | **KEEP** | Required by reset flow |
| `btn-reset-cancel` | Cancel reset | Aborts reset | Yes | **KEEP** | Required by reset flow |
| `btn-profile-save-identity` | Save identity | Saves identity prefs | Yes | **KEEP** | Core |
| `btn-profile-save-prefs` | Save prefs | Saves preferences | Yes | **KEEP** | Core |
| `btn-profile-save-rules` | Save rules | Saves rule prefs | Yes | **KEEP** | Core |

---

## Section 9 — Buttons: Home, Workspace, Agent Pages

| Button ID | Label | Current behavior | Backend-backed? | Classification | Rationale |
|---|---|---|---|---|---|
| `btn-home-threads` | Threads | Shows threads | Yes | **KEEP** | Core |
| `btn-workspace-home-refresh` | Refresh | Refreshes workspace home | Yes | **KEEP** | Core |
| `btn-workspace-board-refresh` | Refresh board | Refreshes board | Yes | **KEEP** | Core |
| `btn-workspace-board-threads` | Threads view | Switches board view | Yes | **KEEP** | Core |
| `btn-workspace-board-architecture` | Architecture view | Switches board view | Yes | **KEEP** | Useful |
| `btn-workspace-board-visual` | Visual view | Switches board view | Yes | **KEEP** | Useful |
| `btn-agent-refresh` | Refresh agent | Refreshes agent/bridge status | Yes | **KEEP** (if page kept) | Core for agent page |
| `btn-agent-open-home` | Home | Navigates to home | Yes | **KEEP** | Navigation |
| `btn-agent-open-settings` | Settings | Navigates to settings | Yes | **KEEP** | Navigation |
| `btn-agent-open-trust` | Trust | Navigates to trust | Yes | **KEEP** | Navigation |

---

## Section 10 — Buttons: Intro Page

| Button ID | Label | Classification | Rationale |
|---|---|---|---|
| `btn-intro-daily-brief` | Daily brief | **REMOVE** (with intro page) | Part of page to remove/collapse |
| `btn-intro-open-connections` | Connections | **REMOVE** (with intro page) | Same |
| `btn-intro-open-home` | Open home | **REMOVE** (with intro page) | Same |
| `btn-intro-open-home-ready` | Home ready | **REMOVE** (with intro page) | Same |
| `btn-intro-open-landing` | Landing | **REMOVE** (with intro page) | Same |
| `btn-intro-open-settings` | Settings | **REMOVE** (with intro page) | Same |
| `btn-intro-refresh-setup` | Refresh setup | **REMOVE** (with intro page) | Same |

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
| Home | System status | "system status" | Yes | **KEEP** | Core |
| Home | Calendar | "calendar" | Yes | **KEEP** | Core |
| Home | Weather | "weather" | Yes | **KEEP** | Core |
| Home | Home agent | "bridge status" | Yes | **COLLAPSE** | Diagnostic |
| Home | Explain this | "explain this" | Partial | **COLLAPSE** | Context-dependent |
| Home | Analyze screen | "analyze this screen" | Partial — setup-required | **REMOVE** | Implies computer-use; only works with capture |
| Home | Show threads | "show threads" | Yes | **KEEP** | Core |
| Home | Project status | "project status this" | Partial | **COLLAPSE** | Context-dependent |
| Home | Most blocked | "which project is most blocked…" | Partial | **REMOVE** | Implies deep project management; overpromises |
| Home | Memory overview | "memory overview" | Yes | **KEEP** | Core |
| Home | Tone settings | "tone status" | Yes | **COLLAPSE** | Secondary |
| Home | Schedules | "show schedules" | Partial | **COLLAPSE** | Secondary |
| Home | Pattern review | "pattern status" | Yes | **COLLAPSE** | Secondary |
| Policy | Create calendar rule | "policy create weekday calendar…" | Partial | **REMOVE** | Implies policy automation |
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

| Classification | Count (approx) |
|---|---|
| KEEP | ~55 |
| COLLAPSE | ~30 |
| REMOVE | ~18 |

---

## Recommended Implementation Order

### Branch 2: `ui/simplify-dashboard-default-experience`

Implement in this order to limit blast radius:

1. **Remove intro page buttons** — lowest risk; intro page has no backend behavior
2. **Remove live-help buttons** — no clear governed path
3. **Remove policy create shortcut buttons** — misleading capability
4. **Remove noisy quick-action chips** (chat_plan_goal, chat_build_page, analyze screen, most_blocked, phase42 follow-up)
5. **Collapse trust center subsection buttons** — keep Refresh and Settings; put subsections behind expand
6. **Collapse workflow/operational buttons** — move to a Diagnostics section
7. **Collapse capability/operator health widgets** — keep on page but collapsed by default
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

# Technical Patterns Review — What to Adopt, What to Defer

**Status:** Design reference — updated as decisions are made
**Audience:** Christopher Daugherty / Core development
**Last reviewed:** 2026-04-15

---

## Guiding Principle

> *If it works, and it fits — use it. If not, discard it.*

Borrow patterns only when they solve Nova's real problems at the right time.
Do not add complexity ahead of the use case that demands it.

---

## Patterns Worth Adopting

### 1. Dynamic Prompt Assembly / Modular Rules

**What it is:** Context-specific instructions assembled at runtime instead of one giant static prompt.
Rules are injected only when relevant to the current capability or mode.

**Why it fits Nova:**
- Cleaner governance — each capability carries its own constraints.
- Prevents prompt bloat as Nova gains capabilities.
- Makes it easier to audit what rules applied to a given decision.

**Priority:** Mid-term. Do after core capabilities are stable.

---

### 2. Mailbox Pattern / Central Approval Coordinator

**What it is:** Workers route high-risk or uncertain requests to a central coordinator before acting.
The coordinator holds the decision, logs it, and either approves, rejects, or escalates.

**Why it fits Nova:**
- Natural extension of the existing Governor model.
- Enables multi-worker orchestration without losing control visibility.
- Audit trail is preserved at the handoff point.

**Priority:** Mid-term. Relevant when Nova has more than one active worker running simultaneously.

---

### 3. Analytics Dashboard over Raw Logs

**What it is:** Transform raw ledger entries into structured insights:
failure rates, escalation frequency, most-used capabilities, patterns over time.

**Why it fits Nova:**
- Moves the ledger from "audit proof" to "operational intelligence."
- Surfaces what's working and what isn't without manual log review.
- Aligns with the Cockpit Dashboard idea (see `2026-04-18_feature_ideation_review.md`).

**Priority:** Mid-term. Valuable once there's enough ledger data to make it meaningful.

---

## Patterns to Defer or Redesign

### 4. Autonomous Memory Consolidation ("AutoDream" style)

**What it is:** Background cycles that autonomously reorganize, merge, or purge memory without user involvement.

**Why it conflicts with Nova:**
Nova's values are explicitness and user control.
Silent memory changes — even well-intentioned ones — undermine trust.

**Nova's approach instead:**
- Manual "optimize memory" command the user invokes.
- Opt-in scheduled maintenance with a visible summary of what changed.
- Never hidden behavior changes.

**Status:** Redesign required before considering. Not a direct lift.

---

### 5. 24/7 Daemon Infrastructure

**What it is:** Always-running background processes that proactively monitor, trigger, and act.

**Why to defer:**
- Premature expansion before the core is packaged and demonstrable.
- Distracts from the immediate priority: making Nova's existing value visible and accessible.

**Status:** Defer. Revisit after Phase 1 is complete and the portfolio gap is closed.

---

### 6. Proactive Intelligence / Push Notifications

**What it is:** Nova surfaces insights, reminders, or suggestions without being asked.

**Why to defer:**
- Introduces notification complexity before user demand is established.
- Trust infrastructure (user preferences, opt-in controls, mute) must come first.
- Risk of feeling intrusive before the relationship with the user is earned.

**Status:** Defer. Wait for clear pull from real users, then design with bounded opt-in controls.

---

## Priority Roadmap

### Near-Term (Next 1–2 weeks)

| # | Action |
| :--- | :--- |
| 1 | Demo visible value — 30-second GIF or video |
| 2 | Complete ONE hero capability end-to-end |
| 3 | Rewrite README with Quickstart and "Why Nova?" |
| 4 | Surface test and CI badges |

### Mid-Term (Next 3–6 months)

| # | Action |
| :--- | :--- |
| 5 | Build one complete business intake workflow |
| 6 | Add ledger insights dashboard |
| 7 | Introduce modular context and rule injection |
| 8 | Implement manual memory maintenance controls (opt-in) |

### Later-Term (6+ months)

| # | Action |
| :--- | :--- |
| 9 | Multi-worker mailbox coordinator |
| 10 | Async messaging channels (SMS / Telegram) |
| 11 | Voice and call handling (governed) |
| 12 | Carefully bounded proactivity — opt-in only |

---

## One-Sentence Guardrail

**Add complexity only when the use case demanding it already exists and the simpler version is already working.**

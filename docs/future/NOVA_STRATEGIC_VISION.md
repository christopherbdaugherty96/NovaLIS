# Nova Strategic Vision — Governed Receptionist & Business OS

**Status:** Long-term direction (not current priority)
**Audience:** Christopher Daugherty / Core planning
**Last reviewed:** 2026-04-15

> *Use this document to understand where Nova is heading, then close it and return to the roadmap.*

---

## The Core Idea

Nova's long-term role is not to be a general chatbot.
It is to be a **trusted first-contact layer** that captures, filters, summarizes, and acts—
only within explicitly approved business rules, across multiple ventures.

A receptionist AI *without* governance is a liability.
A receptionist AI *with* Nova's audit trail and approval gates is a defensible, trustworthy system.

---

## The Layered Role Model

Nova should evolve as a layered system with clear, escalating authority boundaries.
Each layer has a defined ceiling. No layer acts beyond its ceiling without explicit permission.

| Layer | Role | Examples |
| :--- | :--- | :--- |
| **1. Front Desk** | Answers inbound calls, texts, and simple inquiries. | "Thanks for calling Pour Social. How can I help?" |
| **2. Triage Layer** | Classifies inquiry type and routes accordingly. | Lead request, support question, scheduling, urgent, spam. |
| **3. Governed Action Layer** | Only executes explicitly approved actions. | Log caller details, send summary, draft response, schedule callback. |
| **4. Escalation Layer** | Knows when to hand off to a human. | "That decision requires the owner. I'll have Christopher follow up." |

---

## Multi-Business Architecture

Nova should maintain a **shared governance spine** with **business-specific modes**.
The governance layer (ledger, permissions, approval gates) is shared.
The knowledge, scripts, and approved actions are isolated per business.

```
Shared Core (Governance · Ledger · Trust · Identity)
├── Pour Social Mode
│   ├── Event inquiries
│   ├── Approved pricing ranges
│   ├── Availability capture
│   └── Callback summary drafting
├── Website Business Mode
│   ├── Lead intake
│   ├── Project type / budget / timeline collection
│   └── Follow-up request drafting
└── Personal / Household Mode
    ├── Reminders
    ├── Approved contact outreach
    └── Home coordination
```

---

## Required Capabilities (When This Phase Begins)

### Capabilities

- Inbound call answering (speech-to-text + voice response)
- Caller classification and intent detection
- Business-specific knowledge bases (per mode)
- Lead intake form generation and summary
- Follow-up drafting (email / message)
- Full call and action logs in ledger
- Escalation and transfer logic
- Do-not-disturb awareness

### Controls

- Approved scripts and pricing language (per business)
- Escalation triggers and emergency bypass
- Business hours enforcement
- Caller allowlists and VIP routing
- Visible call and action history
- Revocation and mute controls

---

## Critical Boundaries — What Nova Must Never Do

These boundaries apply regardless of phase, business, or instruction.

- Promise services not offered by the business.
- Quote custom prices outside approved ranges.
- Make legal or financial statements outside approved templates.
- Impersonate the owner unless explicitly framed as such.
- Handle customer issues silently without an audit trail.
- Act on a request that has no approved pathway—route to escalation instead.

> *Nova represents your rules, not its own.*

---

## Phase Roadmap (5-Phase Expansion)

| Phase | Focus | Deliverable |
| :--- | :--- | :--- |
| **1** | Local Core Stability | Installable, calm, one strong verified capability, memory, basic trust. |
| **2** | Text-Based Business Intake | Form capture, lead summaries, approved responses, callback planning. |
| **3** | Async Messaging | SMS / WhatsApp / Telegram governed replies, routing, escalation. |
| **4** | Voice / Call Handling | Scripted greeting, intake, basic Q&A, escalation handoff. |
| **5** | Multi-Business Front Desk | Mode switching, shared trust center, reporting, lead dashboards, call analytics. |

**Phase 1 is the current priority.**
Do not start Phase 2 until Phase 1 is solid, repeatable, and easy to understand.

---

## One Sentence Truth

**Nova's next win should be practical usefulness and visible trust.
Not more autonomous complexity.**

Extend that same disciplined, governed approach tier by tier—and Nova evolves from a portfolio piece into a genuine competitive advantage.

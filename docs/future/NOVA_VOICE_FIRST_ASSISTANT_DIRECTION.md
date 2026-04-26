# Nova Voice-First Assistant Direction

Date: 2026-04-26

Status: Future product direction / TODO planning document

Related docs:

- [`NOVA_ROLE_BASED_ASSISTANT_CORE_VISION.md`](NOVA_ROLE_BASED_ASSISTANT_CORE_VISION.md)
- [`NOVA_ROLE_BASED_ASSISTANT_DECISION_RECORD_2026-04-26.md`](NOVA_ROLE_BASED_ASSISTANT_DECISION_RECORD_2026-04-26.md)
- [`NOVA_EVERYDAY_TASK_SERVICE_EXPANSION_2026-04-26.md`](NOVA_EVERYDAY_TASK_SERVICE_EXPANSION_2026-04-26.md)
- [`NOVA_SOLO_BUSINESS_ASSISTANT_PRODUCT_VISION.md`](NOVA_SOLO_BUSINESS_ASSISTANT_PRODUCT_VISION.md)

---

## Executive Summary

Nova should become a **voice-first, role-based governed assistant** for home, work, everyday tasks, and small business.

This does not mean text disappears.

The intended product model is:

```text
Primary interface: Voice
Secondary interface: Text/chat
Review interface: Dashboard
Trust interface: Approval queue, action history, and receipts
```

Nova should not feel like a chatbot with voice added later.

Nova should feel like:

> **A voice-first assistant that can be directed into roles, help with everyday tasks, prepare or automate safe workflows, and keep real-world actions approved, logged, and under user control.**

Short product phrase:

> **Nova is your voice-first assistant, under your rules.**

---

## Core Direction

The updated direction is:

> **Nova is a voice-first governed assistant for home, work, and small business. You can direct it into roles, ask it to help with everyday tasks, and let it prepare or automate safe workflows — while real-world actions stay approved, logged, and under your control.**

This extends the existing role-based assistant direction.

Updated hierarchy:

```text
Umbrella:
Voice-first role-based governed assistant

Core roles:
- Home Assistant
- Personal Assistant
- Work Helper
- Business Assistant
- Business Manager
- Research Assistant
- File Organizer
- Owner Mode

First product wedge:
Solo Business Assistant

Broader expansion:
Everyday Task Service + lightweight CRM

Interface principle:
Voice-first, text-supported, dashboard-reviewed

Governance principle:
Simple outside, governed inside
```

---

## Why Voice-First Matters

For everyday users, independents, and small-business owners, voice is often easier than typing.

The target users may not want to open dashboards, learn software, or write detailed prompts.

They want to say things like:

```text
Nova, what do I need to do today?
Nova, help me reply to this customer.
Nova, summarize this page.
Nova, fill out this form with what you know.
Nova, remind me to follow up with Mike tomorrow.
Nova, what did you do today?
Nova, act as my business manager for the next hour.
```

Voice-first makes Nova feel more natural for:

```text
home tasks
basic job workflows
small-business follow-ups
customer replies
forms
reminders
summaries
hands-free work
non-technical users
```

---

## Product Interface Model

Nova should be designed around four layers.

### 1. Voice Layer

Voice is the main control surface.

Examples:

```text
Ask a question
Switch role
Start a workflow
Request a summary
Draft a reply
Create a reminder
Ask what changed
Cancel or pause
```

### 2. Text Layer

Text remains available for:

```text
backup input
editing drafts
reviewing exact wording
copy/paste
long summaries
forms
settings
searchable history
```

### 3. Dashboard Layer

Dashboard is for review and control, not the main personality of the product.

Dashboard should show:

```text
current role
today's tasks
approval queue
action history
recent drafts
follow-ups
settings
voice mode
pause/stop controls
```

### 4. Trust Layer

Trust layer should show:

```text
what Nova did
what Nova did not do
what is waiting for approval
what was sent/post/published/changed, if anything
what remained draft-only
what automations are paused or active
```

This depends on trust receipt backend recovery and hardening before it should be treated as fully implemented.

---

## Voice-First Role System

Voice makes the role-based product easier to understand.

The user should be able to say:

```text
Nova, switch to Home Assistant.
Nova, switch to Work Helper.
Nova, act as my Business Assistant.
Nova, be my Business Manager today.
Nova, summarize this like my Research Assistant.
Nova, organize these files.
Nova, switch to Owner Mode.
```

Each role changes Nova’s focus, but not the authority model.

---

## Role Examples

### Home Assistant Voice Examples

```text
Nova, what needs to be handled around the house today?
Nova, remind me to pay the electric bill Friday.
Nova, help me understand this bill.
Nova, make a grocery list.
Nova, help me fill out this form.
```

### Work Helper Voice Examples

```text
Nova, summarize my work emails.
Nova, draft a professional reply.
Nova, turn this into a checklist.
Nova, what are my top tasks today?
Nova, summarize this policy in plain English.
```

### Business Assistant Voice Examples

```text
Nova, who do I need to follow up with today?
Nova, draft a reply to Sarah.
Nova, create a quote for lawn mowing and debris removal for $150.
Nova, what quotes are still open?
Nova, what did you do for the business today?
```

### Business Manager Voice Examples

```text
Nova, manage my business workflow for the next hour.
Nova, prioritize my customer follow-ups.
Nova, what is waiting for approval?
Nova, what should I handle first?
Nova, show me open leads and quotes.
```

---

## Text Still Matters

Nova should be voice-first, not voice-only.

Text is better for:

```text
editing drafts
reviewing quotes
checking exact wording
reading long summaries
copy/paste
forms
approval queue
action history
settings
business records
```

Voice is better for:

```text
quick commands
daily check-ins
reminders
hands-free workflows
home tasks
business follow-ups
summaries
assistant role switching
```

Final interface principle:

> **Voice-first, text-supported, dashboard-reviewed.**

---

## Voice Safety Rules

Voice-first must not weaken governance.

Nova still needs the same rules:

```text
Do not send without approval.
Do not post without approval.
Do not buy without approval.
Do not delete without approval.
Do not submit forms without approval.
Do not charge customers.
Do not change records without approval.
Show what changed.
Let me pause or stop.
```

Voice responses should make boundaries clear:

```text
I drafted the reply. I have not sent it.
Would you like to hear it, edit it, copy it, or open it as a draft?
```

```text
I can fill in the form fields I know, but I will not submit the form without your approval.
```

---

## Safety Voice Commands

Voice-first Nova needs reliable stop/cancel/control commands.

Required safety commands:

```text
Nova, stop.
Nova, pause all automations.
Nova, cancel that.
Nova, do not send.
Nova, do not submit.
Nova, do not post.
Nova, read that back.
Nova, what are you about to do?
Nova, what did you just do?
Nova, switch to local-only mode.
Nova, show what is waiting for approval.
```

These commands should be consistent across roles.

---

## Voice Modes

### 1. Push-To-Talk

This should be the first version.

```text
Hold button → speak → Nova responds
```

Why first:

```text
simpler
safer
less privacy concern
easier to test
less accidental activation
better MVP fit
```

### 2. Wake Word

Later version.

```text
“Nova...” → command
```

Needs:

```text
privacy controls
accuracy checks
local/offline preference
clear listening indicator
false activation handling
```

### 3. Conversation Mode

Later version.

```text
natural back-and-forth conversation
```

Needs:

```text
interruption handling
timeout behavior
stop command
context reset
approval boundaries
role awareness
```

### 4. Business Voice Mode

Specialized mode for small-business workflows.

```text
Nova reads follow-ups
Nova drafts replies
Nova asks for approval
Nova does not send automatically
```

---

## Voice Provider Strategy

Nova should support voice providers without making any cloud provider mandatory.

Recommended stack:

```text
Default:
Local STT + local TTS when possible

Premium optional:
ElevenLabs natural voice output

Fallback:
Text-only mode
```

User-facing setting:

```text
Voice quality:
[Private/local]
[Premium natural voice]
```

Plain explanation:

```text
Local voice = more private
Premium voice = more natural
```

ElevenLabs or any other external voice provider should be optional, governed, and network-mediated.

If cloud voice is used, Nova should disclose when text is sent out for voice generation.

Example:

```text
This will send the text of this response to the selected voice provider to generate speech.
Use local voice instead?
```

---

## First Voice-First MVP

Do not begin with full always-listening voice.

The smallest voice-first MVP should include:

```text
Push-to-talk
Role selection
Spoken response
Text transcript
Approval queue
Action history placeholder
Draft-only workflows
```

First demo:

```text
User presses talk:
“Nova, act as my business assistant. Who do I need to follow up with?”

Nova:
“You have two follow-ups. Mike has an open quote from two days ago. Sarah asked for pricing yesterday. I recommend replying to Sarah first. Would you like me to draft a reply?”

User:
“Yes.”

Nova:
“I drafted the reply. I have not sent it. You can review it on screen.”
```

This demonstrates:

```text
voice-first use
role switching
business workflow
safe drafting
approval boundary
dashboard review
```

---

## Voice-First UI Direction

The main screen should feel like a voice assistant control center, not a chat app first.

Example:

```text
Nova is listening

Current role:
Business Assistant

Today:
- 3 follow-ups
- 1 quote waiting
- 2 appointments
- 0 actions sent automatically

Say:
“Draft a reply”
“Show follow-ups”
“Create quote”
“What did Nova do?”
```

Buttons:

```text
Hold to Talk
Type Instead
Approval Queue
Action History
Switch Role
Settings
```

---

## TODO Roadmap

### Phase A — Document And Ground

- [x] Document voice-first direction.
- [ ] Link this document from `docs/INDEX.md`.
- [ ] Keep wording aligned with role-based assistant docs.
- [ ] Avoid fantasy-assistant terminology.

### Phase B — Protect Current Runtime Truth

- [ ] Recover trust receipt work from commit `e9c0187`.
- [ ] Apply follow-up correction commit `92baccd`.
- [ ] Verify files, tests, and certification state.
- [ ] Harden trust receipt store.
- [ ] Complete Cap 64 live signoff and lock.

### Phase C — Voice MVP

- [ ] Define voice provider interface.
- [ ] Keep local/private voice as default where possible.
- [ ] Add push-to-talk as first voice control.
- [ ] Show transcript after spoken input.
- [ ] Add spoken response output.
- [ ] Add role selection by voice.
- [ ] Add safety voice commands.
- [ ] Add approval queue visibility.
- [ ] Add action history placeholder.

### Phase D — First Product Workflow

- [ ] Implement Business Assistant voice demo.
- [ ] Support “who do I need to follow up with?”
- [ ] Support “draft a reply.”
- [ ] Support “create a quote.”
- [ ] Make all communication draft-only by default.
- [ ] Show “sent automatically: 0” style trust line.

### Phase E — Later Voice Expansion

- [ ] Evaluate optional premium voice provider.
- [ ] Add wake word only after push-to-talk is stable.
- [ ] Add conversation mode only after stop/cancel behavior is reliable.
- [ ] Add role-specific voice dashboards.
- [ ] Add voice budgets and usage limits for cloud voice.

---

## What Not To Do First

Do not start with:

```text
always-listening voice
cloud-only voice
unrestricted voice actions
autonomous sending/posting/submitting
voice cloning
deep SaaS billing before core workflows
complex role packs before one useful demo
```

Do not make external voice services required for Nova to feel usable.

Do not allow voice commands to bypass approval, ledger, capability checks, or network mediation.

---

## Final Direction

Nova should become:

> **A voice-first, role-based governed assistant for home, work, everyday tasks, and small business — with text as an optional control and review layer.**

The user should be able to talk naturally.

Nova should be able to help, draft, summarize, organize, and prepare actions.

But real-world authority remains:

```text
visible
bounded
approved
logged
reviewable
under user control
```

Final product rule:

> **Voice-first, text-supported, dashboard-reviewed, governed underneath.**

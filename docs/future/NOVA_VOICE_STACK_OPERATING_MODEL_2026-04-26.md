# Nova Voice Stack Operating Model

Date: 2026-04-26

Status: Future operating model / truth-and-goals document

Purpose: capture the corrected future architecture for Nova’s voice-first assistant stack after stabilization and testing. This is not a claim that all pieces are implemented today.

Related docs:

- [`NOVA_VOICE_FIRST_ASSISTANT_DIRECTION.md`](NOVA_VOICE_FIRST_ASSISTANT_DIRECTION.md)
- [`NOVA_ELEVENLABS_VOICE_INTEGRATION_PLAN.md`](NOVA_ELEVENLABS_VOICE_INTEGRATION_PLAN.md)
- [`NOVA_VOICE_FIRST_ELEVENLABS_FINAL_REVIEW_2026-04-26.md`](NOVA_VOICE_FIRST_ELEVENLABS_FINAL_REVIEW_2026-04-26.md)
- [`NOVA_ROLE_BASED_ASSISTANT_CORE_VISION.md`](NOVA_ROLE_BASED_ASSISTANT_CORE_VISION.md)
- [`NOVA_ROLE_BASED_ASSISTANT_DECISION_RECORD_2026-04-26.md`](NOVA_ROLE_BASED_ASSISTANT_DECISION_RECORD_2026-04-26.md)

---

## Executive Summary

The corrected future architecture is:

> **Nova is a voice-first governed assistant. Gemma provides local-first reasoning, ElevenLabs provides the standard natural voice experience when online, OpenClaw performs bounded work, and Nova governs every real-world action.**

Short operating model:

```text
Nova = governor / orchestrator / authority
Gemma = local-first reasoning / language brain
OpenClaw = hands / worker / action runner
ElevenLabs = standard high-quality online voice experience
Local TTS/STT = offline/private voice fallback
Dashboard/Text = review, editing, approvals, records, fallback
```

The clean rule is:

> **ElevenLabs speaks. Gemma reasons. OpenClaw acts. Nova governs.**

This is the preferred future path once the current runtime is stabilized, tested, and trust/action-history foundations are working.

---

## Correction To Prior Voice Direction

Earlier notes framed ElevenLabs as an optional premium provider.

The corrected direction is more precise:

> **ElevenLabs should be Nova’s standard high-quality online voice provider because it gives the best user experience.**

But:

> **ElevenLabs should not be Nova’s brain, authority layer, action controller, or required offline dependency.**

Gemma and ElevenLabs are not the same layer.

```text
Gemma = reasoning/language model
ElevenLabs = speech/voice experience
```

The correct framing is not:

```text
ElevenLabs is standard, Gemma is fallback.
```

The correct framing is:

```text
Gemma is the standard local-first reasoning lane.
ElevenLabs is the standard online voice experience.
Local voice is the offline/private voice fallback.
```

---

## Core Stack Roles

### 1. Nova — Governor / Orchestrator / Authority

Nova remains the center of the system.

Nova is responsible for:

```text
user intent
role selection
policy
authority
approval boundaries
capability checks
action envelopes
risk classification
network mediation
ledger/action history
trust receipts
pause/stop controls
user-facing explanation
```

Nova decides:

```text
what is allowed
what needs approval
what can be delegated
what must be blocked
what gets logged
what gets shown to the user
```

Nova must never surrender execution authority to:

```text
Gemma
ElevenLabs
OpenClaw
any external LLM
any external voice agent
any plugin system
any webhook system
```

Nova’s core rule remains:

> **Intelligence is not authority.**

---

### 2. Gemma — Local-First Reasoning / Language Brain

Gemma should be Nova’s standard local-first reasoning model/lane when capable for the task.

Gemma is responsible for:

```text
local reasoning
plain-language response generation
drafting messages
summarizing content
turning instructions into steps
extracting tasks
creating checklists
helping with forms
business/customer workflow reasoning
home/work assistant reasoning
```

Gemma fits Nova because it supports:

```text
local-first operation
privacy-first workflows
offline or reduced-cloud workflows
lower cost
non-dependence on one cloud provider
role-based assistant responses
basic work/home/business task reasoning
```

Gemma should not be responsible for:

```text
action authority
policy bypass
ungoverned execution
approving its own actions
making irreversible decisions without user/Nova approval
```

Gemma can think and draft.

Nova governs whether anything is allowed to happen.

---

### 3. ElevenLabs — Standard Online Voice Experience

ElevenLabs should be Nova’s standard high-quality online voice layer.

ElevenLabs is responsible for:

```text
natural spoken responses
assistant voice output
clean feedback for summaries
business follow-up readouts
home/work briefings
spoken approval prompts
role-appropriate voice tone
accessibility-friendly voice experience
possibly STT/transcription later
possibly voice-agent shell experiments later
```

ElevenLabs fits Nova because Nova is becoming voice-first.

The user experience goal is:

```text
Nova feels natural to talk to.
Nova can read summaries clearly.
Nova can speak business follow-ups cleanly.
Nova can guide non-technical users through tasks.
Nova can sound polished enough for everyday and business use.
```

ElevenLabs should not be responsible for:

```text
execution authority
policy decisions
ungoverned tool calls
direct CRM/email/calendar/payment actions
unrestricted webhooks
Nova's internal brain
Nova's approval system
```

ElevenLabs can improve how Nova speaks and listens.

It must not decide what Nova is allowed to do.

---

### 4. Local TTS/STT — Offline / Private Voice Fallback

Local TTS/STT remains important.

Local voice is used when:

```text
offline
privacy-first mode
sensitive content mode
cloud voice is disabled
ElevenLabs quota is exhausted
network is unavailable
user chooses local-only mode
```

Local voice may be less natural than ElevenLabs, but it protects Nova’s local-first identity.

The user-facing explanation should be simple:

```text
Standard voice = best natural experience when online.
Local/private voice = better for offline or sensitive tasks.
```

---

### 5. OpenClaw — Hands / Worker / Action Runner

OpenClaw should be Nova’s bounded worker layer.

OpenClaw is responsible for:

```text
bounded task execution
background jobs
scheduled tasks
browser/file/repo automation
worker agents
multi-step task flow
channel bridging
report generation
research execution
test runs
safe local automations
```

OpenClaw should receive structured Nova task envelopes:

```text
role
goal
allowed actions
blocked actions
time limits
file limits
network limits
output format
approval requirements
ledger/receipt expectations
```

OpenClaw should not directly own authority.

Allowed pattern:

```text
Nova receives request
→ Nova classifies role/risk
→ Nova creates governed task envelope
→ OpenClaw performs bounded work
→ OpenClaw returns result
→ Nova explains, logs, and asks for approval when needed
```

Blocked pattern:

```text
OpenClaw receives user request
→ OpenClaw decides and acts freely
→ email/social/calendar/CRM/payment/file changes happen directly
```

---

### 6. Dashboard / Text — Review, Editing, Approval, Records

Text and dashboard remain essential even in a voice-first product.

They are used for:

```text
editing drafts
reviewing exact wording
checking quotes
reviewing approval queue
showing action history
showing receipts
settings
business records
fallback input
long summaries
copy/paste
```

The product should not become voice-only.

Correct interface model:

```text
Voice-first
Text-supported
Dashboard-reviewed
Governed underneath
```

---

## Recommended Operating Modes

### 1. Standard Mode

Best user experience when online.

```text
Reasoning: Gemma local if capable, otherwise selected governed model lane
Voice: ElevenLabs standard online voice
Actions: OpenClaw through Nova task envelopes
Governance: Nova
Dashboard: approvals/action history
```

User experience:

```text
natural voice
fast spoken feedback
role-based responses
drafts and approvals
high-quality everyday assistant feel
```

---

### 2. Local / Private Mode

For offline, sensitive, or privacy-first use.

```text
Reasoning: Gemma local
Voice: local TTS/STT or text-only
Actions: local only or restricted
Governance: Nova
Dashboard: local review
```

User experience:

```text
more private
works offline where possible
less natural voice
no cloud voice usage
```

---

### 3. Sensitive Content Mode

Automatically suggested or triggered for:

```text
medical information
legal documents
financial records
passwords/secrets
private customer data
identity documents
full email threads
employment records
children/family private data
```

Default behavior:

```text
Gemma local reasoning
local voice or text-only
no ElevenLabs unless explicitly approved
no external voice provider by default
```

---

### 4. Business / Product Voice Mode

For polished everyday/business use.

```text
Reasoning: Gemma local if sufficient, or selected governed model lane
Voice: ElevenLabs standard
Actions: OpenClaw bounded tasks
Governance: Nova approval queue
Usage: budgeted and logged
```

This is the mode that best supports:

```text
business follow-ups
quote drafts
customer reply readouts
what did Nova do today?
home/work summaries
role-based assistant UX
```

---

## User-Facing Settings

Settings should be simple.

```text
Voice experience:
- Standard natural voice
- Local/private voice
- Text only

Reasoning mode:
- Local-first
- Auto-select governed model lane later
- Owner-controlled advanced settings

Privacy mode:
- Standard
- Sensitive/local-only

Actions:
- Draft only
- Ask before actions
- Approved low-risk automation
```

Plain-language explanations:

```text
Standard natural voice uses the online voice provider for the best sound.
Local/private voice keeps voice processing on your machine where possible.
Text only disables voice output.
```

---

## Transition Plan

This operating model should be treated as the **next route after stabilization and testing**, not as a shortcut around current close-out work.

### Stage 0 — Stabilize Current Runtime

Before this stack becomes the main build path:

```text
recover/verify trust receipt state
complete Cap 64 live signoff and lock
complete Cap 65 close-out if applicable
harden action receipts
validate runtime docs and drift checks
validate Windows installer path
keep current local voice stable
```

Do not move into full voice-stack work until the runtime truth and trust/action-history foundations are reliable.

---

### Stage 1 — Provider Abstractions

Build the transition surface first.

```text
VoiceOutputProvider interface
SpeechInputProvider interface
ReasoningProvider or ModelLane abstraction
OpenClawTaskEnvelope
OpenClawMediator
VoiceSessionController
VoiceGovernancePolicy
```

The goal is to make it easy to swap/configure providers without rewriting Nova’s product logic.

---

### Stage 2 — Standard Online Voice + Local Fallback

Add ElevenLabs as the standard online voice path, while keeping local fallback.

```text
ElevenLabs TTS provider
local TTS fallback provider
text-only fallback
cloud disclosure
usage budgets
sensitive-content detection/confirmation
voice provider ledger events
```

Important:

> Make the transition feel seamless for the user, but keep the authority boundary visible.

---

### Stage 3 — Gemma Local Reasoning Lane

Make Gemma the local-first standard reasoning lane where capable.

```text
local model configuration
model capability checks
fallback/upgrade path for tasks too large or complex
owner-visible model status
local/offline mode
sensitive-content routing to local reasoning
```

Gemma should power normal local reasoning, drafting, summaries, checklists, and role behavior where it performs well.

---

### Stage 4 — OpenClaw As Bounded Hands

Move OpenClaw into a governed worker model.

```text
Nova task envelope
OpenClaw worker role
allowed/blocked action lists
time/file/network limits
result return format
approval queue integration
ledger receipt integration
```

First OpenClaw proof:

```text
Business Follow-Up Brief
- read-only
- draft-only
- no sending
- no record changes
- result returned to Nova
- Nova speaks summary
- dashboard shows drafts/receipt
```

---

### Stage 5 — Voice-First Role-Based Shell

Build the first product shell:

```text
push-to-talk
role selection by voice
spoken response
text transcript
approval queue
action history
business assistant demo
```

First demo command:

```text
Nova, act as my business assistant. Who do I need to follow up with?
```

Expected behavior:

```text
Nova reasons with Gemma or selected governed lane.
Nova delegates bounded review to OpenClaw if needed.
Nova speaks through ElevenLabs when online.
Nova shows transcript/drafts/dashboard.
Nova sends nothing automatically.
```

---

### Stage 6 — Gradual Expansion

After the first role-based shell works:

```text
Home Assistant role
Work Helper role
Business Manager role
Research Assistant role
File Organizer role
lightweight CRM
form helper
email consolidation
website/social draft workflows
```

Expand role packs only after one useful workflow is stable.

---

## Easy Transition Principles

To ensure the transition is easy:

1. **Build abstractions before hardcoding providers.**
   - Voice provider
   - Reasoning/model lane
   - Worker/action runner

2. **Keep local fallback working at every step.**
   - If ElevenLabs fails, local voice/text works.
   - If cloud is disabled, Gemma/local path works.

3. **Make mode switching simple.**
   - Standard natural voice
   - Local/private mode
   - Text-only mode

4. **Do not merge voice quality with action authority.**
   - A better voice does not mean more permission.

5. **Do not let OpenClaw bypass Nova.**
   - OpenClaw gets envelopes, not broad authority.

6. **Do not let Gemma approve its own actions.**
   - Gemma can reason; Nova governs.

7. **Keep dashboard review available.**
   - Voice is primary, but review must be visual/textual.

8. **Log provider use.**
   - Cloud voice use should be visible.
   - Worker runs should be visible.
   - Real actions should create receipts.

9. **Guard sensitive content.**
   - Sensitive tasks default to local/private.

10. **Build one demo before broad platform work.**
    - Business Follow-Up Brief first.

---

## What Not To Do

Do not make:

```text
ElevenLabs the brain
ElevenLabs the authority layer
ElevenLabs required for offline/private mode
OpenClaw the governor
OpenClaw free to act without Nova envelopes
Gemma responsible for approval or authority
cloud voice required for sensitive content
voice cloning part of default onboarding
always-listening mode before push-to-talk is stable
SaaS billing before the core role workflow works
```

---

## Final Architecture Statement

Use this as the future truth/goals statement:

> **Nova is the governor. Gemma is the local-first reasoning brain. OpenClaw is the hands. ElevenLabs is the standard online voice experience. Local voice/text remains the offline and privacy fallback. Every real-world action stays visible, bounded, approved, logged, and reviewable.**

Short form:

> **ElevenLabs speaks. Gemma reasons. OpenClaw acts. Nova governs.**

This is the next route once the system is stabilized and tested.

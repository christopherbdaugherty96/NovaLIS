# Nova ElevenLabs Voice Opportunity Map

Date: 2026-04-27

Status: Future truth / opportunity map / voice design record

Purpose: capture the recommended ElevenLabs direction for Nova, grounded in Nova's current voice plans, current repo truth, and reviewed public ElevenLabs capabilities. This document is future planning only. It does not claim these workflows are implemented today.

---

## Active Priority Note

This document is **not** the current active implementation task.

Current active path remains:

```text
RequestUnderstanding trust/action-history review card
→ local capability signoff matrix
→ OpenClawMediator skeleton
→ first read-only OpenClaw workflow proof
→ Google/email connector direction before Cap 64 P5
→ voice provider implementation when the trust/action loop is ready
```

Do not use this opportunity map to skip directly into broad ElevenLabs, ElevenAgents, telephony, voice cloning, or always-listening voice work.

---

## Executive Summary

ElevenLabs should be Nova's standard high-quality online voice experience, not Nova's brain or authority layer.

The correct pattern is:

```text
Nova decides what is allowed
Gemma / governed model lane reasons
OpenClaw acts only inside Nova envelopes
ElevenLabs speaks the approved/allowed response
Trust/action history records what happened
```

The wrong pattern is:

```text
ElevenLabs Agent receives user request
→ ElevenLabs tool/webhook directly books, emails, edits, charges, submits, or changes data
→ Nova only hears about it later, if at all
```

Short product rule:

> **ElevenLabs speaks. Nova governs.**

Full stack rule:

> **ElevenLabs speaks. Gemma reasons. OpenClaw acts. Nova governs.**

---

## Current Nova Truth

The current Nova voice direction already says:

```text
ElevenLabs = standard high-quality online voice experience
Local TTS/STT = offline/private voice fallback
Dashboard/Text = review, editing, approvals, records, fallback
Nova = governor / orchestrator / authority
Gemma = local-first reasoning / language brain
OpenClaw = hands / worker / action runner
```

Current truth to preserve:

```text
ElevenLabs is not implemented as the full standard voice provider yet.
Existing local voice surfaces remain important.
Voice setup may still require local dependencies and manual validation.
ElevenLabs must not become Nova's control plane, authority layer, action controller, internal brain, or required offline dependency.
```

Primary references:

```text
docs/future/NOVA_ELEVENLABS_VOICE_INTEGRATION_PLAN.md
docs/future/NOVA_VOICE_STACK_OPERATING_MODEL_2026-04-26.md
docs/future/NOVA_VOICE_FIRST_ASSISTANT_DIRECTION.md
docs/future/NOVA_VOICE_FIRST_ELEVENLABS_FINAL_REVIEW_2026-04-26.md
```

---

## Source Hygiene / Evidence Boundary

This document uses public ElevenLabs documentation and public reports as planning inputs, not as authoritative implementation truth for Nova.

Use this distinction:

```text
Nova repo truth → authoritative for Nova current status.
Official ElevenLabs docs/pricing → useful for current product/API capabilities and cost planning.
Hands-on articles/community examples → useful for opportunity discovery.
News/security/ethics reporting → useful risk signals that must be rechecked before public/security claims.
```

Do not copy raw public claims into README, marketing, security docs, or implementation commitments without rechecking current sources.

Nova implementation truth must come from:

```text
live repo code
generated runtime truth docs
capability verification docs
tests
owner direction / priority override
```

---

## Public ElevenLabs Capability Snapshot

Reviewed public ElevenLabs docs describe an AI audio platform with:

```text
Text to Speech
Speech to Text
realtime TTS streaming via WebSockets
realtime STT via WebSockets
voice library / voice IDs
voice cloning
voice design
Conversational AI / Agents Platform
webhooks
tools / client-side or server-side integrations
phone/telephony-style assistant patterns
music / sound effects / dubbing / audio utilities
```

Key public capability notes:

```text
TTS supports lifelike audio, multiple voices/styles, and real-time streaming use cases.
Flash / Turbo models are positioned for low latency; Multilingual/v3 style models are positioned for higher-quality output.
TTS WebSocket streaming is designed for partial text input and low-latency audio generation from streamed LLM output.
STT supports speech-to-text, realtime transcription, word-level timestamps, and multilingual use cases.
Webhooks exist for certain platform/agent events such as post-call transcription and voice-removal notices.
ElevenLabs pricing is usage-based, so always-on voice or long readouts need budget controls.
```

Public references reviewed during planning:

```text
ElevenLabs docs overview
https://elevenlabs.io/docs/overview

Text to Speech docs
https://elevenlabs.io/docs/capabilities/text-to-speech
https://elevenlabs.io/docs/api-reference/text-to-speech

TTS WebSocket / realtime audio docs
https://elevenlabs.io/docs/api-reference/websocket
https://elevenlabs.io/docs/eleven-api/websockets

Speech to Text realtime docs
https://elevenlabs.io/docs/api-reference/speech-to-text/

Webhooks docs
https://elevenlabs.io/docs/eleven-api/resources/webhooks

ElevenLabs API pricing
https://elevenlabs.io/pricing/api
```

---

## What Nova Should Copy

Nova should copy the high-quality user experience and provider patterns, not the authority model.

Good patterns to adapt:

```text
natural spoken responses
low-latency spoken feedback
streamed TTS for LLM responses
high-quality voice for daily summaries
business-friendly voice readouts
role-appropriate voice tone
accurate online transcription as optional path
phone/website voice intake as later experiments
conversation analytics only if privacy/governance is clear
```

Nova should wrap these patterns in:

```text
VoiceOutputProvider interface
SpeechInputProvider interface
VoiceGovernancePolicy
RequestUnderstanding
sensitive-content routing
cloud voice disclosure
usage budgets
ledger events
trust/action-history visibility
local/private fallback
```

---

## What Nova Should Not Copy

Do not copy the risky pattern:

```text
ElevenLabs Agent as Nova's brain
ElevenLabs tool/webhook as direct action authority
cloud voice required for all use
always-on microphone before push-to-talk is stable
voice cloning as default onboarding
phone assistant that books/sends/charges directly
web widget that writes to CRM/calendar/email directly
unrestricted outbound calling
unreviewed conversation data retention
```

Why:

```text
Voice feels authoritative to users.
A natural voice can make an unsafe action feel more trustworthy than it is.
External voice agents with tools/webhooks can bypass Nova's governed action path if not designed carefully.
Cloud voice can expose sensitive content if routed blindly.
Voice cloning can create impersonation and consent risks.
Always-on microphone raises privacy and trust issues.
Usage-based voice can create hidden cost spikes.
```

Nova's product position should be:

> **High-quality voice, governed authority.**

---

## Voice Integration Ladder

Nova should not jump directly to full conversational agents or phone automation.

Build in this order:

```text
1. Text-only fallback remains reliable
2. Local/private TTS/STT remains available
3. Voice provider abstraction
4. ElevenLabs TTS provider for spoken output
5. Push-to-talk voice UX with transcript and stop/cancel
6. Cloud voice disclosure and budget controls
7. Optional ElevenLabs STT provider
8. Role-based voice presets
9. Website/phone intake experiments through Nova-governed endpoints only
10. Conversational AI / ElevenAgents research prototype, not authority layer
```

---

## Tier 1 — Best First ElevenLabs Workflows

### Spoken Nova Response

Purpose:

```text
Let Nova speak normal responses naturally when online.
```

Scope:

```text
text response already generated by Nova
non-sensitive content
within budget
user has standard online voice enabled
```

Required receipt/log state:

```text
Voice provider used: ElevenLabs
Characters used: <count>
Cloud voice allowed: yes
Action authority effect: none
```

### Daily / Project Brief Readout

Purpose:

```text
Read daily operator summaries and project status briefs aloud.
```

Good fit:

```text
morning brief
project foreman brief
repo status brief
what changed today
what should I work on next
```

Required boundary:

```text
Speaking a brief does not mean Nova acted.
```

### Approval Queue Readout

Purpose:

```text
Read pending approvals aloud while the dashboard/text view shows exact details.
```

Example:

```text
You have two proposed actions waiting: one draft email and one calendar proposal. Nothing has been sent or created yet.
```

Required boundary:

```text
Voice may describe approvals, but the approval control remains governed and reviewable.
```

### Error / Safety Readout

Purpose:

```text
Make failures and blocked actions understandable to non-technical users.
```

Examples:

```text
I could not do that because email sending is paused.
I prepared a draft only. Nothing was sent.
This content looks sensitive, so I am using local/private mode.
```

---

## Tier 2 — Optional STT / Voice Input Workflows

### Push-To-Talk Command Input

Purpose:

```text
Let the user speak a command, see the transcript, then let Nova classify/handle it.
```

Preferred first path:

```text
local STT where possible
ElevenLabs STT optional for online/high-quality mode
manual text fallback always available
```

Required boundary:

```text
Transcription is not permission.
A spoken command still passes through RequestUnderstanding and Nova governance.
```

### Meeting / Note Transcription

Purpose:

```text
Transcribe voice notes, meetings, or call notes for summary/draft generation.
```

Allowed output:

```text
transcript
summary
action items
draft follow-up suggestions
```

Blocked output:

```text
no automatic emailing
no calendar creation
no CRM update without approval
```

---

## Tier 3 — Role Voice Workflows

Role voices can improve user experience later.

Candidate roles:

```text
Home Assistant
Work Helper
Business Assistant
Business Manager
Research Assistant
Project Foreman
Voice Concierge
Owner Mode
```

Rules:

```text
A role voice is a presentation layer, not a permission layer.
Role voice must not change capabilities, approvals, or authority.
Role voice settings must be visible and editable.
```

Good initial approach:

```text
one default ElevenLabs voice
one local/private fallback voice
role-specific presets later
```

---

## Tier 4 — Website / Phone Intake Experiments

ElevenLabs conversational agents / phone-style assistants are tempting and useful later, especially for business use.

Potential safe uses:

```text
website voice intake widget
phone inquiry intake assistant
customer FAQ assistant
appointment inquiry assistant
lead capture assistant
business-hours information assistant
```

Required Nova-safe architecture:

```text
ElevenLabs handles voice conversation shell
Nova receives structured request/event
Nova classifies and governs
Nova decides what can be read, drafted, proposed, or blocked
Nova logs and receipts
Nova returns safe answer/draft/proposal
```

Blocked architecture:

```text
ElevenLabs agent directly books appointments
ElevenLabs agent directly sends email/SMS
ElevenLabs agent directly edits calendar/CRM/database
ElevenLabs agent directly charges/payment/purchases
```

---

## Tier 5 — Defer / Block Initially

Avoid early implementation of:

```text
voice cloning
voice changer
voice remixing
always-listening mode
wake word before push-to-talk is stable
unrestricted ElevenAgents tools
Twilio/SIP outbound calls
batch outbound calls
direct webhooks to email/calendar/CRM/payment
music/sound-effects/dubbing as core voice path
cloud-only voice with no fallback
sensitive-content cloud voice by default
```

These should only be considered after:

```text
Voice provider abstraction exists
local/private fallback is stable
cloud voice disclosure exists
usage budgets exist
sensitive-content routing exists
approval/trust/action-history surfaces are stable
Google/email connector direction is clear
OpenClaw mediation and approval boundaries are clearer
```

---

## Specific Nova Voice Opportunities

### 1. Natural Spoken Status

Best first ElevenLabs workflow.

User prompt:

```text
Nova, what is my current status?
```

Output:

```text
short spoken summary
matching text transcript
trust/action-history card if relevant
```

Receipt:

```text
Voice output generated. No external action performed.
```

### 2. Project Foreman Voice Readout

Purpose:

```text
Read the Project Foreman Brief aloud once OpenClaw can produce the read-only brief.
```

Boundary:

```text
Speaking the brief does not mean files were changed, tests were run, or commits were made.
```

### 3. Approval Queue Voice Assistant

Purpose:

```text
Let Nova say what is waiting for approval and what will not happen automatically.
```

Example:

```text
You have one email draft waiting. It has not been sent. Review it in the dashboard before approving.
```

### 4. Business Follow-Up Voice Readout

Purpose:

```text
Read follow-up opportunities and draft replies aloud for a small business owner.
```

Boundary:

```text
No messages sent. No customer records changed.
```

### 5. Sensitive Mode Voice Switch

Purpose:

```text
Automatically shift to local/private voice or text-only for sensitive content unless the user explicitly allows cloud voice.
```

Example:

```text
This looks sensitive, so I will keep this local/private unless you approve online voice.
```

### 6. Voice Error Explainer

Purpose:

```text
Explain blocked actions, missing dependencies, model lock, budget exhaustion, or connector pauses in plain speech.
```

Examples:

```text
I cannot run Cap 64 P5 because email signoff is paused.
I cannot use ElevenLabs because the API key is missing.
I switched to text-only because the voice budget is exhausted.
```

### 7. Accessibility Readout Mode

Purpose:

```text
Read docs, summaries, checklists, and approval states aloud for accessibility.
```

Boundary:

```text
Ask before long readouts to control cost and avoid surprise cloud usage.
```

### 8. Voice Setup Diagnostic

Purpose:

```text
Help the user understand current voice state.
```

Output:

```text
local voice available?
ElevenLabs key configured?
voice mode selected?
budget available?
private/sensitive mode active?
last voice error?
```

---

## Required UX Pattern

Every cloud voice response should have an internal or visible trust statement when relevant.

Examples:

```text
Spoken only. No action executed.
Cloud voice used for this response.
Local/private mode used because content looked sensitive.
Voice budget remaining: <summary>.
Nothing was sent or changed.
One draft is waiting for approval.
```

The user should never confuse a polished voice with action authority.

---

## Required Data Model Concepts

Future voice events should capture:

```text
voice_event_id
session_id
request_understanding_id or snapshot
voice_mode
provider
model_id
voice_id
character_count
audio_duration
cloud_allowed
sensitive_content_detected
fallback_used
budget_checked
budget_remaining
spoken_text_hash or safe summary
action_authority_effect
ledger_event_id
error_code
```

Do not log sensitive full spoken text unnecessarily.

---

## Budget / Cost Controls

ElevenLabs is usage-based, so Nova needs explicit controls.

Required controls:

```text
monthly character budget
daily character budget
per-response character limit
ask before long readouts
role-specific budget later
cloud voice off switch
local/text fallback when budget exhausted
usage display in settings/dashboard
ledger event for cloud voice use
```

Default behavior:

```text
short confirmations can use online voice if enabled
long docs/articles require confirmation
sensitive content defaults to local/private or text-only
budget exhaustion falls back gracefully
```

---

## Security / Privacy Controls

Required before broad ElevenLabs use:

```text
ELEVENLABS_API_KEY stored as environment/secret, not in repo
all outbound ElevenLabs calls route through NetworkMediator or governed network boundary
sensitive-content classifier before cloud voice
zero/minimal retention mode considered where available and applicable
voice usage ledger events
no voice cloning without consent record
no third-party/person voice cloning without verified rights
no direct ElevenAgents webhooks into business systems
```

---

## What To Build First

Do not start with ElevenAgents, phone calls, or cloning.

Recommended first ElevenLabs workflow after current trust/action visibility work:

```text
ElevenLabs TTS provider for natural spoken Nova responses.
```

Why first:

```text
high user-visible improvement
low authority risk if output-only
fits voice-first direction
can preserve local fallback
can be budgeted and logged
makes demos much better
```

Second workflow:

```text
Voice Setup Diagnostic / Settings visibility
```

Third workflow:

```text
Project Foreman Voice Readout
```

Fourth workflow:

```text
Optional ElevenLabs STT provider after push-to-talk is stable
```

Fifth workflow:

```text
ElevenAgents website/phone intake research prototype only through Nova-governed endpoints
```

---

## Implementation Order

Before treating ElevenLabs as the standard voice path:

```text
1. RequestUnderstanding trust/action-history visibility exists.
2. Local/private voice/text fallback remains available.
3. VoiceOutputProvider abstraction exists.
4. ElevenLabsTTSProvider is added behind settings/env flag.
5. Cloud voice disclosure exists.
6. Budget checks exist.
7. Sensitive-content routing exists.
8. Voice provider use is logged.
9. Stop/cancel behavior works for playback where possible.
```

Before ElevenLabs STT:

```text
push-to-talk UI exists
transcript review exists
manual text fallback exists
spoken command still passes through RequestUnderstanding
cloud STT disclosure and budget checks exist
```

Before ElevenAgents:

```text
Nova governed endpoint boundary exists
no direct write webhooks
approval queue exists for proposed actions
conversation data handling is documented
telephony/website use case is narrow and tested
```

---

## What To Add To The Existing Voice Plan

The existing plan is strong. Missing or under-emphasized additions:

```text
explicit active-priority warning so voice work does not jump ahead of trust visibility
voice event data model
cloud voice trust statements
voice setup diagnostic workflow
Project Foreman voice readout workflow
approval queue voice readout workflow
sensitive mode voice switch
budget exhaustion fallback behavior
ElevenAgents only through Nova-governed endpoints
role voice = presentation layer, not permission layer
```

---

## Final Recommendation

Nova should use ElevenLabs to sound natural, not to become less governed.

The opportunity is:

```text
A voice-first assistant that feels natural while staying honest about what it did, did not do, and cannot do without approval.
```

Final sequence:

```text
RequestUnderstanding trust/action-history card
→ local capability signoff matrix
→ voice provider abstraction
→ ElevenLabs TTS provider
→ voice setup diagnostic
→ Project Foreman voice readout
→ optional ElevenLabs STT
→ ElevenAgents website/phone intake research only through Nova-governed endpoints
```

Final rule:

> **ElevenLabs gives Nova a voice. Nova keeps the authority.**

# Nova Voice-First / ElevenLabs Final Review

Date: 2026-04-26

Status: Final review / product decision summary, corrected by [`NOVA_VOICE_STACK_OPERATING_MODEL_2026-04-26.md`](NOVA_VOICE_STACK_OPERATING_MODEL_2026-04-26.md)

Related docs:

- [`NOVA_VOICE_STACK_OPERATING_MODEL_2026-04-26.md`](NOVA_VOICE_STACK_OPERATING_MODEL_2026-04-26.md)
- [`NOVA_VOICE_FIRST_ASSISTANT_DIRECTION.md`](NOVA_VOICE_FIRST_ASSISTANT_DIRECTION.md)
- [`NOVA_ELEVENLABS_VOICE_INTEGRATION_PLAN.md`](NOVA_ELEVENLABS_VOICE_INTEGRATION_PLAN.md)
- [`NOVA_ROLE_BASED_ASSISTANT_CORE_VISION.md`](NOVA_ROLE_BASED_ASSISTANT_CORE_VISION.md)
- [`NOVA_ROLE_BASED_ASSISTANT_DECISION_RECORD_2026-04-26.md`](NOVA_ROLE_BASED_ASSISTANT_DECISION_RECORD_2026-04-26.md)

---

## Final Decision

Nova’s product direction is now:

> **Voice-first, text-supported, dashboard-reviewed, governed underneath.**

Corrected voice-stack decision:

> **ElevenLabs should be Nova’s standard high-quality online voice experience. Local voice/text remains the offline, private, and fallback path. Gemma remains the local-first reasoning lane.**

This means ElevenLabs is no longer framed as merely an optional premium novelty.

However, ElevenLabs must still not become:

```text
Nova's authority layer
Nova's action controller
Nova's internal brain
an unrestricted external agent layer
the required offline/private voice path
the required path for sensitive content
```

Nova remains responsible for:

```text
policy
authority
approval boundaries
capability checks
network mediation
ledger/action history
user control
```

Short architecture rule:

> **ElevenLabs speaks. Gemma reasons. OpenClaw acts. Nova governs.**

---

## Final Product Hierarchy

The current product hierarchy is:

```text
Umbrella product direction:
Voice-first role-based governed assistant

Primary interface:
Voice

Secondary interface:
Text/chat

Review/control surface:
Dashboard

Trust surface:
Approval queue, action history, receipts

First commercial wedge:
Solo Business Assistant

Broader expansion:
Everyday Task Service + lightweight CRM

Standard online voice experience:
ElevenLabs TTS, governed and budgeted

Offline/private fallback:
Local voice and text-only mode

Local-first reasoning lane:
Gemma

Bounded worker/action layer:
OpenClaw through Nova envelopes
```

---

## What ElevenLabs Should Add To Nova

### Add First

```text
ElevenLabs TTS provider
voice provider abstraction
push-to-talk compatibility
spoken response output
voice ID configuration
model setting
cloud voice disclosure
character/usage budget
ledger event for cloud voice use
sensitive-content warning
local fallback
```

### Add Later

```text
ElevenLabs STT provider
realtime transcription experiment
voice isolator for noisy audio
role-specific standard voices
streaming playback
usage dashboard
website/phone intake prototype through governed Nova endpoints
```

### Research Later, Do Not Ship First

```text
ElevenAgents
telephony
website voice widgets
client tools
webhooks
conversation analytics
```

These must route through Nova governance before touching business systems.

### Block Or Defer Initially

```text
voice cloning
voice changer
voice remixing
music generation
dubbing
image/video generation
unrestricted ElevenAgents tools
outbound batch calls
automatic phone calls
direct webhooks to email/calendar/CRM/payment systems
```

---

## Required Governance Rules

Cloud voice must not bypass Nova’s governance spine.

Allowed pattern:

```text
User voice/text request
→ Nova role/session controller
→ VoiceGovernancePolicy
→ GovernorMediator where action is involved
→ CapabilityRegistry
→ ExecuteBoundary
→ NetworkMediator for ElevenLabs request
→ LedgerWriter
→ spoken/text response
```

Blocked pattern:

```text
ElevenLabs agent/tool
→ direct email/calendar/CRM/payment/social action
```

---

## Required User-Facing Controls

Nova should expose simple settings:

```text
Voice mode:
- Off
- Push-to-talk
- Wake word later
- Conversation mode later

Voice experience:
- Standard natural voice
- Local/private voice
- Text only

Cloud voice permission:
- Never
- Ask each time
- Allow non-sensitive responses
- Allow within budget

Readout length:
- Short only
- Ask before long readouts
- Allow within budget
```

Plain-language explanation:

```text
Standard natural voice = best sound when online
Local/private voice = better for offline or sensitive tasks
Text only = no spoken output
```

---

## Required Safety Commands

Voice-first Nova should consistently support:

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

These commands matter more in a voice-first product because voice can feel immediate and invisible if not controlled.

---

## Sensitive Content Rule

Cloud voice should be blocked or require confirmation for sensitive content:

```text
medical information
legal documents
financial accounts
passwords/secrets
private customer information
full email threads
identity documents
children/family private data
employment records
```

Default behavior:

```text
Use local voice or text-only for sensitive content unless the user explicitly allows cloud voice.
```

---

## Recommended Build Order

Do not build voice-stack work before stabilization.

Correct order:

1. Recover / maintain current runtime truth and trust receipt work.
2. Complete Cap 64 live signoff and lock.
3. Keep existing local voice stable.
4. Build provider abstractions.
5. Build push-to-talk voice MVP.
6. Add transcript + spoken response + safety commands.
7. Add role selection by voice.
8. Add approval queue / action history visibility.
9. Add ElevenLabs TTS as the standard online voice path with local fallback.
10. Add usage budget and cloud disclosure.
11. Add Gemma local-first reasoning lane checks/status.
12. Add OpenClaw task-envelope worker path.
13. Add ElevenLabs STT only after the voice MVP is stable.
14. Research ElevenAgents only after Nova’s governed voice boundary is working.

---

## First Demo Target

The first voice-first demo should not be a broad assistant.

It should be one useful workflow:

```text
User presses talk:
"Nova, act as my business assistant. Who do I need to follow up with?"

Nova:
"You have two follow-ups. Mike has an open quote from two days ago. Sarah asked for pricing yesterday. I recommend replying to Sarah first. Would you like me to draft a reply?"

User:
"Yes."

Nova:
"I drafted the reply. I have not sent it. You can review it on screen."
```

This proves:

```text
voice-first control
role-based behavior
business workflow value
draft-only safety
approval boundary
dashboard review
```

---

## Final Recommendation

Proceed with the voice-first direction.

Proceed with ElevenLabs as the standard online voice experience.

Do **not** make ElevenLabs authoritative, required for sensitive/private/offline mode, or capable of direct ungoverned actions.

Best final wording:

> **Nova can use ElevenLabs for standard high-quality online voice, but Nova keeps authority, approvals, logs, and execution boundaries.**

Product rule:

> **Voice-first. Text-supported. Dashboard-reviewed. Governed underneath.**

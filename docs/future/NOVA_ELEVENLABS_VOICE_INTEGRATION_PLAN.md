# Nova ElevenLabs Voice Integration Plan

Date: 2026-04-26

Status: Future integration planning / second-pass research note

Related docs:

- [`NOVA_VOICE_FIRST_ASSISTANT_DIRECTION.md`](NOVA_VOICE_FIRST_ASSISTANT_DIRECTION.md)
- [`NOVA_ROLE_BASED_ASSISTANT_CORE_VISION.md`](NOVA_ROLE_BASED_ASSISTANT_CORE_VISION.md)
- [`NOVA_ROLE_BASED_ASSISTANT_DECISION_RECORD_2026-04-26.md`](NOVA_ROLE_BASED_ASSISTANT_DECISION_RECORD_2026-04-26.md)

Research references:

- ElevenLabs docs overview: https://elevenlabs.io/docs/overview
- ElevenLabs TTS docs: https://elevenlabs.io/docs/overview/capabilities/text-to-speech
- ElevenLabs STT docs: https://elevenlabs.io/docs/overview/capabilities/speech-to-text
- ElevenLabs ElevenAgents docs: https://elevenlabs.io/docs/eleven-agents/overview
- ElevenLabs tools help article: https://help.elevenlabs.io/hc/en-us/articles/34669011018257-How-do-I-use-tools-with-ElevenAgents
- ElevenLabs API pricing: https://elevenlabs.io/pricing/api

---

## Executive Summary

ElevenLabs is a strong candidate for Nova’s optional premium voice layer, especially now that Nova’s product direction is voice-first.

However, ElevenLabs should **not** become Nova’s core control plane, default required dependency, or unrestricted agent authority.

Correct integration direction:

> **ElevenLabs should be an optional governed voice provider for Nova — useful for premium natural voice, possible transcription, and future voice-agent experiments, while Nova keeps local/private voice as the default path where possible.**

Nova should remain:

```text
voice-first
text-supported
dashboard-reviewed
governed underneath
local-first by default
cloud-voice optional
```

---

## What ElevenLabs Provides

ElevenLabs currently provides a broad AI audio platform, including:

```text
Text to Speech
Speech to Text
Voice cloning
Voice design
Voice agents / ElevenAgents
Generative audio
Music
Sound effects
Dubbing
Voice changer
Voice isolator
Forced alignment
Voice remixing
```

Its documentation describes these as available through REST API, Python/TypeScript SDKs, and web/no-code tooling.

For Nova, not all of these should be added immediately.

---

## Capabilities Relevant To Nova

### 1. Text To Speech — Strong Fit

ElevenLabs TTS is the best first integration target.

Relevant features:

```text
lifelike spoken audio
nuanced intonation
pacing/emotion awareness
streaming real-time audio
multiple voice styles
low-latency Flash model
higher-quality Multilingual/v3 models
MP3/PCM/u-law/a-law/Opus output formats
```

Why it fits Nova:

```text
voice-first assistant output
natural spoken daily summaries
business follow-up readouts
home assistant reminders
work-helper briefings
premium role voices
better demos
accessibility
```

Nova recommendation:

> Add ElevenLabs TTS first as an optional premium `VoiceProvider` implementation.

Do not make it the only voice path.

---

### 2. Speech To Text — Useful, But Second Priority

ElevenLabs STT is useful, especially for accurate transcription and multilingual use.

Relevant features:

```text
Scribe v2 transcription
90+ languages
word-level timestamps
speaker diarization
keyterm prompting
entity detection
dynamic audio tagging
smart language detection
realtime STT over WebSockets
```

Why it fits Nova:

```text
voice-first command input
meeting/note transcription
customer call transcription later
business voice workflows
work-helper summaries
role-based voice sessions
```

Nova recommendation:

> Use local STT first where possible. Add ElevenLabs STT as optional premium or fallback for higher accuracy, realtime transcription, multilingual users, and business/paid tiers.

Do not route all microphone input to cloud by default.

---

### 3. ElevenAgents — Powerful, But High Risk For Nova

ElevenAgents can build, deploy, and monitor voice agents. Their docs describe configuration for prompts, voice/language, knowledge base, tools, personalization, authentication, deployment through web/mobile/server/telephony, Twilio/SIP, events, analytics, testing, and conversation analysis.

Relevant features:

```text
voice agents
turn-taking
interruptions
timeout settings
knowledge base/RAG
custom or supported LLMs
client tools
webhooks
authentication
web/mobile widgets
Twilio/SIP/telephony
batch outbound calls
conversation analytics
real-time monitoring
privacy/data retention settings
cost optimization
```

Why it is tempting:

```text
rapid voice agent setup
built-in conversation handling
phone/telephony path
web widget path
conversation monitoring
multi-role assistant demos
```

Why it is risky for Nova:

```text
could become an external agent control plane
could duplicate or bypass Nova governance
could call tools/webhooks outside GovernorMediator
could store conversation data externally
could confuse where authority lives
could create SaaS cloud dependency too early
```

Nova recommendation:

> Do not make ElevenAgents Nova’s internal brain or action controller.

Acceptable future use:

```text
customer-facing website voice widget
inbound phone assistant prototype
demo-only voice agent shell
telephony intake that sends requests into Nova for governed handling
```

Required rule:

> Any ElevenAgents tool/webhook action must call into Nova’s governed API boundary, not directly into business systems.

---

### 4. Tools / Webhooks — Must Be Gated

ElevenAgents supports Client Tools, Webhooks, and System Tools.

Examples from ElevenLabs docs/help:

```text
Client Tools:
- redirect users within a site
- send on-screen notifications
- guide users through website flows

Webhooks:
- booking meetings
- accessing or updating databases
- telling current time
- connecting to external APIs

System Tools:
- ending a call
- transferring a call
- switching languages
```

Nova rule:

> ElevenLabs tools must never directly execute real-world actions outside Nova governance.

Allowed pattern:

```text
ElevenLabs voice interaction
→ request sent to Nova governed endpoint
→ GovernorMediator
→ CapabilityRegistry
→ ExecuteBoundary
→ NetworkMediator if needed
→ LedgerWriter
→ result returned to voice layer
```

Blocked pattern:

```text
ElevenLabs agent
→ direct webhook to booking/database/email/payment/social system
```

---

### 5. Voice Library / Voice Design — Useful Later

ElevenLabs supports large voice libraries, voice design from text descriptions, community voices, and generated voices.

Nova use cases:

```text
choose a calm assistant voice
business/professional assistant voice
home assistant voice
accessibility-friendly voice
role-specific voice styles
```

Nova recommendation:

```text
Phase 1: use one safe default ElevenLabs voice ID if configured
Phase 2: allow user to choose from approved/saved voices
Phase 3: role-specific voice presets
```

Do not make voice browsing a core MVP feature.

---

### 6. Voice Cloning — Defer And Restrict

ElevenLabs supports Instant Voice Cloning and Professional Voice Cloning.

This is powerful but high-risk because of impersonation/scam potential.

Nova recommendation:

> Do not include voice cloning in the first Nova integration.

If added later:

```text
require explicit user consent
only allow cloning the authenticated user’s own voice or properly licensed voices
show clear warnings
store consent record
never clone public figures or third parties without verified permission
never use cloned voice to impersonate a person in outbound calls/messages
label cloned/generated voices clearly
```

Voice cloning should be an advanced setting, not a normal onboarding step.

---

### 7. Voice Isolator — Good Utility Later

Voice Isolator removes ambient sound, reverb, and interference.

Nova use cases:

```text
clean noisy voice commands
improve transcription before STT
clean meeting recordings
improve customer call transcription later
```

Nova recommendation:

> Useful later as an optional audio-processing helper, not first MVP.

---

### 8. Voice Changer / Voice Remixing — Mostly Defer

Voice changer and remixing can transform voice characteristics.

Nova use cases are limited:

```text
accessibility
role voice tuning
creative demos
```

Risks:

```text
identity confusion
impersonation concerns
unnecessary complexity
brand distraction
```

Nova recommendation:

> Defer. Do not include in core Nova voice assistant.

---

### 9. Sound Effects / Music / Dubbing / Image & Video — Not Core

These are available ElevenLabs platform capabilities, but they are not important for Nova’s first voice assistant path.

Possible future uses:

```text
sound effect for alerts
content creation workflows
marketing/video workflows
translation/dubbing for business content
```

Nova recommendation:

> Do not add to initial Nova voice integration. Track as future optional creative/content features only.

---

### 10. Forced Alignment — Niche But Useful Later

Forced alignment maps text to audio timing.

Possible Nova uses:

```text
highlight text while Nova reads it aloud
create transcript/audio sync
accessibility playback
training/tutorial content
```

Nova recommendation:

> Defer until Nova has stable voice readout and transcript UI.

---

## Pricing / Usage Considerations

ElevenLabs pricing is usage-based.

Current API pricing examples from ElevenLabs pricing page:

```text
TTS Flash / Turbo: about $0.05 per 1K characters
TTS Multilingual v2/v3: about $0.10 per 1K characters
Scribe STT: about $0.22 per hour
Scribe v2 Realtime STT: about $0.39 per hour
Voice Isolator: about $0.12 per minute
Voice Changer: about $0.12 per minute
Dubbing: about $0.33+ per minute depending on watermark/tier
Sound Effects: about $0.12 per generation/minute grouping depending on plan table
```

Nova implications:

```text
cloud voice can become expensive if always-on
long article readouts should be budgeted
background narration should be blocked by default
paid tiers may include premium voice quotas
free/local users should have local voice fallback
```

Required Nova controls:

```text
monthly character budget
daily character budget
max readout length before confirmation
per-role voice budget
usage warning before long readout
local fallback
admin/owner usage dashboard
ledger event for cloud voice use
```

---

## Recommended Nova Architecture

Add provider interfaces instead of hardcoding ElevenLabs.

### Voice Output Provider

```text
VoiceOutputProvider
- LocalPiperVoiceProvider
- ElevenLabsTTSProvider
- TextOnlyProvider
```

### Speech Input Provider

```text
SpeechInputProvider
- LocalSTTProvider
- ElevenLabsSTTProvider
- ManualTextInputProvider
```

### Voice Session Controller

```text
VoiceSessionController
- push-to-talk session
- transcript capture
- role context
- stop/cancel handling
- response playback
- approval boundary enforcement
```

### Voice Governance Layer

```text
VoiceGovernancePolicy
- cloud voice allowed?
- sensitive content allowed?
- max characters?
- max minutes?
- local-only mode?
- role-specific limits?
- requires confirmation?
```

### Ledger Events

Add or reuse ledger events for:

```text
VOICE_INPUT_RECEIVED
VOICE_TRANSCRIPT_CREATED
VOICE_OUTPUT_REQUESTED
VOICE_OUTPUT_COMPLETED
VOICE_PROVIDER_USED
VOICE_PROVIDER_BLOCKED
VOICE_BUDGET_EXCEEDED
VOICE_CLOUD_DISCLOSURE_SHOWN
VOICE_ACTION_CANCELLED
VOICE_SAFETY_COMMAND_RECEIVED
```

---

## Required User Settings

Add user-facing settings:

```text
Voice mode:
- Off
- Push-to-talk
- Wake word later
- Conversation mode later

Voice provider:
- Local/private
- Premium natural voice
- Text only

Cloud voice permission:
- Never send text to cloud voice
- Ask each time
- Allow for non-sensitive responses
- Allow within monthly budget

Voice readout length:
- Short only
- Ask before long readouts
- Allow long readouts within budget

Role voice:
- same voice for all roles
- role-specific voices later
```

Plain-language display:

```text
Local voice = more private
Premium voice = more natural
```

---

## Sensitive Content Rules

Cloud voice should be blocked or require confirmation for sensitive content.

Examples:

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
Use local voice or text-only for sensitive content unless user explicitly allows cloud voice.
```

---

## Role-Based Voice Uses

### Home Assistant

```text
read today’s reminders
explain a bill
make a grocery list
set reminders
summarize household documents
```

### Work Helper

```text
summarize work emails
read top tasks
turn instructions into a checklist
draft a reply
summarize policies
```

### Business Assistant

```text
read follow-ups
create quote draft
read customer reply draft
summarize leads
say what is waiting for approval
```

### Business Manager

```text
prioritize customer admin
summarize open quotes
identify overdue follow-ups
read approval queue
summarize what changed today
```

### Research Assistant

```text
read news brief
summarize article
compare sources
highlight what matters
```

### File Organizer

```text
read folder summary
suggest organization plan
confirm before moving files
```

### Owner Mode

```text
read runtime status
read capability status
read failures/warnings
summarize pending locks
```

---

## ElevenAgents Future Path

ElevenAgents should be researched as a separate future track.

Possible safe uses:

```text
website voice intake widget
phone call intake assistant
customer FAQ assistant
appointment inquiry assistant
lead capture assistant
```

Required Nova constraints:

```text
no direct database writes
no direct email sending
no direct calendar booking unless routed through Nova approval
no direct payment/charging
no direct CRM modification without governed approval
no external tool call bypass
```

Allowed architecture:

```text
ElevenAgents handles voice conversation shell
Nova handles policy, action decisions, logging, and execution authority
```

This preserves Nova’s core principle:

> Intelligence and speech can be external, but execution authority stays governed by Nova.

---

## What Should Be Added To Nova

### Must Add For Voice-First MVP

```text
Voice provider abstraction
Push-to-talk control
Transcript display
Spoken response output
Role selection by voice
Safety commands
Approval queue visibility
Action history placeholder
Local/private default voice path
Cloud voice disclosure
Voice budget limits
Voice provider ledger events
```

### Should Add For Premium Voice

```text
ElevenLabs TTS provider
Voice ID configuration
Model selection
Streaming playback support
Character usage tracking
Per-role voice presets
Long readout confirmation
Sensitive-content cloud warning
```

### Could Add Later

```text
ElevenLabs STT provider
Realtime transcription mode
Voice isolator for noisy input
Conversation mode
Wake word
Telephony intake prototype
Website voice widget prototype
Forced alignment for read-along UI
```

### Should Defer / Block Initially

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
unapproved webhook actions
```

---

## Implementation Phases

### Phase 0 — Keep Existing Local Voice Stable

```text
verify current local TTS/STT behavior
keep local/private mode as baseline
make voice errors visible
ensure text fallback always works
```

### Phase 1 — Voice Provider Interface

```text
create VoiceOutputProvider interface
wrap existing local TTS provider
add TextOnly fallback provider
add provider settings
add voice ledger events
```

### Phase 2 — Push-To-Talk Voice MVP

```text
push-to-talk UI
transcript after input
role-aware response
spoken output
stop/cancel command
approval queue access
```

### Phase 3 — ElevenLabs TTS Provider

```text
environment variable for ELEVENLABS_API_KEY
voice ID setting
model setting
NetworkMediator route
budget checks
sensitive-content checks
usage ledger events
cloud disclosure notice
streaming playback if feasible
```

### Phase 4 — Business Assistant Voice Demo

```text
“who do I need to follow up with?”
“draft a reply”
“create a quote”
“what is waiting for approval?”
“what did Nova do?”
```

### Phase 5 — Optional STT Upgrade

```text
ElevenLabs STT provider as optional premium/fallback
realtime STT experiment only after push-to-talk is stable
local STT remains default where possible
```

### Phase 6 — ElevenAgents Research Prototype

```text
no production use yet
no direct tools into business systems
only route into Nova governed endpoints
evaluate website/phone intake use cases
```

---

## Do Not Do First

Do not start with:

```text
always-listening voice
wake word before push-to-talk is stable
conversation mode before cancel/stop works
cloud-only voice
voice cloning
unrestricted ElevenAgents agents
Twilio outbound calls
batch outbound calls
direct webhooks to email/calendar/CRM/payment
full SaaS billing before core workflow works
```

---

## Final Recommendation

ElevenLabs should be added to Nova, but in a narrow and governed way.

Best first use:

> **Optional premium TTS provider for natural spoken Nova responses.**

Second use:

> **Optional premium STT provider for better transcription or multilingual support.**

Later research:

> **ElevenAgents for website/phone intake only if all tool calls route through Nova’s governed execution boundary.**

Do not let ElevenLabs become Nova’s authority layer.

Final product rule:

> **Nova may use ElevenLabs for voice quality, but Nova remains responsible for authority, policy, approvals, logs, and execution boundaries.**

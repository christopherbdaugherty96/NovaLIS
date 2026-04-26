# Nova Full Stack Direction — Final Lock

Date: 2026-04-26

Status: Final lock / future truth-and-goals summary

Related docs:

- [`NOVA_VOICE_STACK_OPERATING_MODEL_2026-04-26.md`](NOVA_VOICE_STACK_OPERATING_MODEL_2026-04-26.md)
- [`NOVA_ELEVENLABS_VOICE_INTEGRATION_PLAN.md`](NOVA_ELEVENLABS_VOICE_INTEGRATION_PLAN.md)
- [`NOVA_VOICE_FIRST_ELEVENLABS_FINAL_REVIEW_2026-04-26.md`](NOVA_VOICE_FIRST_ELEVENLABS_FINAL_REVIEW_2026-04-26.md)
- [`NOVA_ROLE_BASED_ASSISTANT_CORE_VISION.md`](NOVA_ROLE_BASED_ASSISTANT_CORE_VISION.md)

---

## Final Locked Direction

Nova’s future stack direction is:

> **Nova is the governor. Gemma is the local-first reasoning brain. OpenClaw is the hands. ElevenLabs is the standard online voice experience. Local voice/text remains the offline and privacy fallback. Every real-world action stays visible, bounded, approved, logged, and reviewable.**

Short form:

> **ElevenLabs speaks. Gemma reasons. OpenClaw acts. Nova governs.**

This is the preferred future route once the current runtime is stabilized, tested, and trust/action-history foundations are reliable.

---

## Role Of Each Layer

### Nova

Nova is the authority layer.

Nova handles:

```text
policy
roles
intent classification
risk classification
action approval
capability checks
network mediation
ledger entries
trust receipts
pause/stop controls
user-facing explanation
```

Nova does not give authority away to the model, voice provider, worker runtime, plugin, or webhook system.

---

### Gemma

Gemma is the local-first reasoning and language lane.

Gemma handles:

```text
reasoning
summaries
drafts
checklists
plain-language explanations
form help
home/work/business task reasoning
```

Gemma can think and draft.

Gemma does not approve its own actions.

---

### OpenClaw

OpenClaw is the hands / worker runtime.

OpenClaw handles:

```text
bounded task execution
background work
browser/file/repo automation
scheduled tasks
reports
research runs
test runs
worker agents
```

OpenClaw receives Nova task envelopes.

OpenClaw does not act freely outside Nova approval.

---

### ElevenLabs

ElevenLabs is the standard high-quality online voice experience.

ElevenLabs handles:

```text
natural spoken responses
voice output
clean readouts
spoken approval prompts
role-appropriate voice tone
future online STT where appropriate
future website/phone voice intake research
```

ElevenLabs speaks for Nova.

ElevenLabs does not govern Nova.

---

### Local Voice / Text

Local voice and text remain the fallback and privacy path.

Used for:

```text
offline mode
sensitive content
local-only mode
network failure
quota exhaustion
user preference
review/editing/approval
```

---

## Current Build Priority

Do not jump straight into this full future stack before the current runtime is clean.

Current priority remains:

```text
stabilize runtime truth
recover/verify trust receipt work
complete Cap 64 live signoff and lock
harden action receipts
validate Windows installer path
keep local voice stable
```

Then transition into the stack using abstractions.

---

## Transition Order

1. Stabilize current runtime and trust/action-history foundations.
2. Build provider abstractions.
3. Keep local voice/text fallback working.
4. Add ElevenLabs TTS as the standard online voice path.
5. Align Gemma as the local-first reasoning lane.
6. Move OpenClaw behind Nova task envelopes.
7. Build push-to-talk voice MVP.
8. Add role selection by voice.
9. Add approval queue and action-history visibility.
10. Prove one workflow: Business Follow-Up Brief.
11. Expand to home/work/business roles and lightweight CRM later.

---

## First Proof Workflow

The first proof should be:

```text
Business Follow-Up Brief
```

Flow:

```text
User speaks:
"Nova, act as my business assistant. Who do I need to follow up with?"

Nova:
classifies role and risk

Gemma:
helps reason/summarize/draft

OpenClaw:
performs bounded read-only/draft-only work if needed

ElevenLabs:
speaks the result when online

Nova:
shows transcript, drafts, approval queue, and receipt
```

Success criteria:

```text
useful follow-up result
nothing sent automatically
nothing changed without approval
OpenClaw stayed inside envelope
Gemma did not approve actions
ElevenLabs only spoke/provided voice
Nova logged and governed the whole flow
```

---

## Non-Negotiable Guardrails

Do not make:

```text
ElevenLabs the brain
ElevenLabs the authority layer
OpenClaw the governor
OpenClaw free to act without Nova envelopes
Gemma responsible for approval or authority
cloud voice required for sensitive/private/offline mode
voice cloning part of default onboarding
always-listening mode before push-to-talk is stable
SaaS billing before the core role workflow works
```

---

## Product Principle

The product should remain:

> **Voice-first. Text-supported. Dashboard-reviewed. Governed underneath.**

And:

> **Simple outside, governed inside.**

This document is the short final lock for the future stack direction.

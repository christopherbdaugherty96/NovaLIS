# Nova Session Reference Summary

Date: 2026-04-26

Status: Reference summary for future work

Purpose: preserve the main conclusions, current-truth boundaries, future-stack direction, and next-step recommendations from the 2026-04-26 planning/docs session.

This document is a reference summary. Generated runtime truth still lives under `docs/current_runtime/` and should remain the authority for exact live capability counts, hashes, and enabled runtime state.

---

## Core Identity Of Nova

Nova is best understood as:

> **A governance-first local AI system that separates intelligence from execution.**

Nova's core principle remains:

> **Intelligence is not authority.**

That means models can reason, tools can act, voice providers can speak, and connectors can access data, but Nova must decide what is allowed, what needs approval, what gets logged, and what remains blocked.

Nova should not be framed as an unrestricted agent. It should be framed as a governed assistant / governed local AI system / Personal AI Sovereignty Platform where authority remains bounded, visible, and reviewable.

---

## Final Locked Future Stack

The clearest future stack direction is:

> **ElevenLabs speaks. Gemma reasons. OpenClaw acts. Nova governs.**

Expanded:

```text
Nova = governor / orchestrator / authority
Gemma = local-first reasoning / language brain
OpenClaw = hands / worker / action runner
ElevenLabs = standard high-quality online voice experience
Local voice/text = offline and privacy fallback
Google connectors = user-authorized data access
Dashboard/Text = review, editing, approvals, records, fallback
```

The final operating rule:

> **Nova is the governor. Gemma is the local-first reasoning brain. OpenClaw is the hands. ElevenLabs is the standard online voice experience. Local voice/text remains the offline and privacy fallback. Every real-world action stays visible, bounded, approved, logged, and reviewable.**

---

## Current Runtime Truth Boundary

Current docs and memory indicate that Nova has a strong governed runtime foundation, but the future stack is not fully implemented yet.

Current generated runtime truth should remain the source of exact facts:

```text
docs/current_runtime/CURRENT_RUNTIME_STATE.md
docs/current_runtime/RUNTIME_FINGERPRINT.md
docs/current_runtime/GOVERNANCE_MATRIX.md
```

Important current boundaries:

```text
Trust Panel system is not fully implemented yet.
Full Phase-8 governed envelope execution remains deferred/not fully complete.
OpenClaw is active but not yet full hands.
ElevenLabs is future voice-stack work, not current runtime truth.
Google account/connector onboarding is future work, not current runtime truth.
Gemma as the standard local-first reasoning lane is a future architecture target, not something to overstate unless verified in current code.
```

Do not manually edit generated runtime truth docs. Regenerate them through the runtime doc generator when implementation changes.

---

## Voice Direction

Nova's product direction is now:

> **Voice-first. Text-supported. Dashboard-reviewed. Governed underneath.**

This does not mean voice-only.

Voice should become the primary natural interface, while text/dashboard remains essential for:

```text
reviewing exact wording
approving actions
editing drafts
showing receipts
action history
settings
long-form review
fallback input/output
```

---

## ElevenLabs Direction

Earlier wording treated ElevenLabs as optional premium. That was corrected.

The current accepted direction is:

> **ElevenLabs should be Nova's standard high-quality online voice experience.**

But ElevenLabs must not become:

```text
Nova's brain
Nova's authority layer
Nova's action controller
Nova's approval system
the required offline/private path
the required path for sensitive content
an unrestricted external agent layer
```

Correct model:

```text
ElevenLabs = standard online voice quality
Local TTS/STT/text = offline/private fallback
Nova = authority and governance
Gemma/local model = reasoning where capable
```

ElevenLabs can eventually support:

```text
natural spoken responses
spoken summaries
spoken approval prompts
role-appropriate voice tone
future online STT/transcription
future website/phone voice intake experiments
```

Defer or restrict at first:

```text
voice cloning
voice changer
voice remixing
music generation
dubbing
unrestricted ElevenAgents tools
outbound batch calls
automatic phone calls
direct webhooks to email/calendar/CRM/payment
```

---

## Gemma Direction

Gemma should be treated as the local-first reasoning lane, not as a voice fallback.

Correct distinction:

```text
Gemma reasons.
ElevenLabs speaks.
```

Gemma should eventually handle:

```text
local reasoning
summaries
drafts
checklists
plain-language explanations
form help
home/work/business task reasoning
sensitive/private reasoning where possible
```

Gemma must not approve its own actions or become an authority layer.

---

## OpenClaw Current Truth

Current OpenClaw truth:

> **OpenClaw is active today as governed home-agent templates and narrow worker foundations.**

It is not yet accurate to say:

```text
OpenClaw is fully autonomous hands.
OpenClaw can safely run any task.
OpenClaw can send/post/delete/submit/change records freely.
Full worker execution is complete.
```

Current OpenClaw foundations include meaningful pieces such as:

```text
Cap 63 openclaw_execute
TaskEnvelope
EnvelopeFactory foundation
EnvelopeStore
OpenClawAgentRunner
OpenClawAgentScheduler
OpenClaw API router
ThinkingLoop
ToolRegistry
RobustExecutor
ExecutorSkillAdapter
OpenClawProposedAction model
runtime store / active run tracking
cancel request support
ledger events
```

But the current implementation is still mostly:

> **governed home-agent templates + transitional worker/tool paths**

rather than full:

> **Nova-issued task envelopes + real approval gates + mediator-controlled worker execution.**

---

## OpenClaw Future Direction

The future direction is:

> **OpenClaw becomes Nova's bounded hands only after mediator, envelope, approval, receipt, and trust/action-history hardening.**

Required future changes:

```text
OpenClawMediator
mandatory EnvelopeFactory path
real approval queue for proposed actions
envelope-aware thinking loop/tool execution
governed executor-backed tools
role-aware worker envelopes
OpenClaw authority lanes/sub-capabilities
run receipts and non-action statements
Business Follow-Up Brief proof
```

The critical proof:

> **Can Nova safely direct OpenClaw to do useful work without giving OpenClaw uncontrolled authority?**

Do not move to broad OpenClaw autonomy before this is proven.

---

## OpenClaw First Proof Workflow

The recommended first proof is:

```text
Business Follow-Up Brief
```

Example flow:

```text
User:
Nova, act as my business assistant. Who do I need to follow up with?

Nova:
classifies Business Assistant role and read-only/draft-only scope

Gemma:
helps reason, summarize, and draft

OpenClaw:
reads sample/local customer data inside a Nova envelope
identifies follow-ups
drafts suggested replies

ElevenLabs:
speaks the result when online

Nova:
shows transcript, drafts, approval queue, and receipt
confirms nothing was sent or changed
```

Success criteria:

```text
useful result exists
nothing sent automatically
nothing changed without approval
OpenClaw stayed inside envelope
Gemma did not approve actions
ElevenLabs only spoke/provided voice
Nova logged and governed the run
```

---

## Google Connector Direction

The accepted Google connector rule is:

> **Google connects data. Nova governs action.**

Expanded:

> **Google Sign-In identifies the user. Google connectors grant scoped access. Nova governance decides what can happen with that access.**

First login should be identity-only:

```text
openid
email
profile
```

First login should not automatically grant:

```text
Gmail access
Calendar access
Drive access
Contacts access
background access
send/post/delete/modify authority
```

Google connector work is future planning, not current runtime truth.

---

## Google Connector Build Order

Recommended future order:

```text
1. Google Sign-In identity only
2. Local Nova user profile
3. Connected Apps / connector registry
4. Calendar read-only connector
5. Gmail read-only connector
6. Gmail draft-only / Cap 64 alignment
7. Drive read-only/search/summarize
8. Contacts read-only
9. Calendar event proposals
10. Drive/file/contact mutation proposals
11. Advanced automations only after approval queue and receipts are reliable
```

Calendar read-only should come before Gmail/Drive writes because it provides useful value with lower risk.

Connector access is not action authority.

A token means Nova can access an API. It does not mean Nova may perform any action without governance.

---

## Google Connector Guardrails

Do not start with:

```text
one-click all Google permissions
full Gmail access
full Drive access
send-email automation
calendar auto-booking
file moving/deleting
contact editing
bulk inbox changes
background connector sync without explicit permission
plain token storage
automatic connector actions without receipts
```

Every connector should define:

```text
scopes granted
allowed actions
blocked actions
approval-required actions
sensitive-data policy
revoke/disconnect path
ledger events
receipt output
```

---

## Cap 64 Importance

Cap 64 `send_email_draft` remains strategically important because it proves the safe assistant pattern:

```text
Nova may draft.
User sends.
```

This directly supports future business assistant workflows, Gmail connector work, and the Business Follow-Up Brief.

Do not skip Cap 64 signoff.

---

## Trust Receipts / Action History Importance

The future stack depends on Nova being able to explain:

```text
what happened
what did not happen
what was only drafted
what is waiting for approval
what was blocked
what was approved
what was denied
```

This is why trust receipts, action history, and approval queue work must remain ahead of broad OpenClaw/Google/voice automation.

The guiding rule:

> **Do not build Nova's future until Nova can prove what it did, what it did not do, and what still needs approval.**

---

## Current Recommended Execution Path

Do not keep expanding broad docs unless a real contradiction appears.

Recommended next path:

```text
1. Pull latest main locally.
2. Complete Cap 64 P5 live signoff and lock.
3. Complete Cap 65 live Shopify checklist and lock if still pending.
4. Validate Windows installer / bootstrap log.
5. Build or verify trust/action-history dashboard proof.
6. Then begin OpenClawMediator / Business Follow-Up Brief proof.
7. After that, add voice-provider abstraction and ElevenLabs standard online voice path.
8. After identity/connector safety design is ready, begin Google Sign-In identity-only flow.
```

Active execution path should remain stabilization first, future stack second.

---

## Branch / Repo Status From This Session

Recent docs were committed directly to `main` through GitHub connector writes.

Latest verified main commit during the session:

```text
e566dd93545cc38f05846535a5c52b1ace4a1c10
docs: link Google connector final lock
```

One Claude branch was found:

```text
claude/unruffled-swartz-477d53
```

It was diverged from main, 8 commits ahead and 60 commits behind at time of check. Because Claude was still actively working and out of tokens, the recommendation was not to merge, delete, or force-align that branch until Claude resumes and confirms what is still needed.

Instruction for Claude on resume:

```text
Before continuing, sync with origin/main. Current main HEAD is e566dd93545cc38f05846535a5c52b1ace4a1c10. Do not overwrite the new docs. Your branch appears diverged/behind main. Rebase or create a fresh branch from current main, then re-apply only any still-needed work. Treat the recent voice/OpenClaw/Google docs on main as canonical future direction.
```

---

## Key Reference Docs Added Or Updated This Session

Voice / stack:

```text
docs/future/NOVA_VOICE_FIRST_ASSISTANT_DIRECTION.md
docs/future/NOVA_ELEVENLABS_VOICE_INTEGRATION_PLAN.md
docs/future/NOVA_VOICE_FIRST_ELEVENLABS_FINAL_REVIEW_2026-04-26.md
docs/future/NOVA_VOICE_STACK_OPERATING_MODEL_2026-04-26.md
docs/future/NOVA_FULL_STACK_DIRECTION_FINAL_LOCK_2026-04-26.md
```

OpenClaw:

```text
docs/reference/HUMAN_GUIDES/28_OPENCLAW_SETUP_AND_RUNTIME_GUIDE_2026-03-27.md
docs/audits/2026-04-26/NOVA_OPENCLAW_DOCS_TO_CODE_ALIGNMENT_AUDIT_2026-04-26.md
docs/future/NOVA_OPENCLAW_HANDS_LAYER_IMPLEMENTATION_PLAN.md
```

Google connectors:

```text
docs/future/NOVA_GOOGLE_ACCOUNT_AND_CONNECTOR_ONBOARDING_PLAN.md
docs/future/NOVA_GOOGLE_CONNECTOR_DIRECTION_FINAL_LOCK_2026-04-26.md
```

Planning/index:

```text
4-15-26 NEW ROADMAP/BackLog.md
docs/INDEX.md
```

This summary:

```text
docs/future/NOVA_SESSION_REFERENCE_SUMMARY_2026-04-26.md
```

---

## Final One-Page Mental Model

```text
Nova governs.
Gemma reasons.
OpenClaw acts.
ElevenLabs speaks.
Google connects data.
Local voice/text protects offline and private workflows.
Dashboard shows approvals, receipts, and action history.
```

Do not confuse access with authority.

Do not confuse intelligence with permission.

Do not confuse voice quality with control.

Do not confuse OpenClaw's ability to act with permission to act.

Nova's value is the governed layer tying all of this together.

# NovaLIS Consolidated Roadmap

Date: 2026-04-28

Status: Human-readable roadmap / not generated runtime truth

Purpose: provide one clean roadmap that summarizes the current active path, paused work, and future architecture tracks without replacing the detailed source documents.

---

## Source Of Truth Rule

This roadmap is a readable map. It does not replace live code or generated runtime truth.

When docs disagree, use this order:

```text
1. Live code and generated runtime truth docs
2. Current priority override
3. Current handoff docs
4. BackLog.md
5. Future planning docs
6. Older roadmap/audit notes
```

Primary current priority source:

```text
4-15-26 NEW ROADMAP/CURRENT_PRIORITY_OVERRIDE_2026-04-27.md
```

Primary follow-up/backlog source:

```text
4-15-26 NEW ROADMAP/BackLog.md
```

Primary docs index:

```text
docs/INDEX.md
```

---

## Roadmap Summary

```text
Conversation visibility first.
Local capability confidence second.
Connector governance third.
OpenClaw hands fourth.
Voice polish fifth.
Broader integrations later.
```

Guiding rule:

> **Intelligence is not authority.**

Product rule:

> **Nova should prepare, explain, ask, act only inside permission, and record what happened.**

---

# Phase 0 — Current Active Priority

## 1. RequestUnderstanding Trust / Action-History Review Card

Status:

```text
ACTIVE NEXT IMPLEMENTATION TASK
```

Goal:

```text
Make Nova visibly show what it understood, what it can/cannot do, what the safe next step is, and what it must not do.
```

Required visible fields:

```text
understood_goal
request_type
capability_status
confidence
safe_next_step
must_not_do
authority_effect
result / not executed
```

Current foundation exists:

```text
nova_backend/src/conversation/request_understanding.py
nova_backend/src/conversation/request_understanding_formatter.py
nova_backend/tests/conversation/test_request_understanding.py
nova_backend/tests/conversation/test_request_understanding_formatter.py
```

Current gap:

```text
Trust/action-history visibility is not implemented yet.
```

Success criteria:

```text
RequestUnderstanding does not execute capabilities.
RequestUnderstanding does not approve actions.
RequestUnderstanding does not change capability locks.
RequestUnderstanding does not call OpenClaw or connectors.
The review card is visible but non-authorizing.
```

References:

```text
4-15-26 NEW ROADMAP/CURRENT_PRIORITY_OVERRIDE_2026-04-27.md
4-15-26 NEW ROADMAP/HANDOFF_2026-04-27_REQUEST_UNDERSTANDING_LIVE_VERIFICATION.md
docs/future/NOVA_REQUEST_UNDERSTANDING_CONTRACT.md
docs/future/NOVA_COHERENCE_MEMORY_BACKGROUND_ARCHITECTURE_ALIGNMENT.md
```

---

# Phase 1 — Conversation And Trust Stabilization

## 2. Re-Run Live Conversation Checks

Only after the RequestUnderstanding review card exists.

Verify Nova handles:

```text
simple questions
project status questions
paused-work questions
email/draft questions
capability questions
what should I do next?
second pass / polish pass / review gaps
```

Known limitation to re-check:

```text
Live free-form LLM behavior was only partially verified because of local model speed and routing bypasses.
```

## 3. Fix Narrow Routing Bypasses

Only after the review card exists.

Known issue type:

```text
Some prompts can bypass general chat / RequestUnderstanding before the understanding layer sees them.
```

Example class:

```text
continue Shopify
continue email
continue Auralis
```

Goal:

```text
Paused work should stay paused even through continuation-style prompts.
```

---

# Phase 2 — Local Capability Confidence

## 4. Local Capability Signoff Matrix

Status:

```text
NOT ACTIVE UNTIL CONVERSATION VISIBILITY IS STABLE
```

Goal:

```text
Verify every local capability before OpenClaw or broader hands-layer work can rely on it.
```

Each capability should be checked for:

```text
routes correctly
requires confirmation when needed
executes safely
fails safely on bad input
logs attempt/result
has clear platform limits
has live signoff status
```

Candidate local capabilities:

```text
speak_text
volume_up_down
media_play_pause
brightness_control
open_file_folder
screen_capture
screen_analysis
os_diagnostics
memory_governance
send_email_draft later only after Google/email decision
openclaw_execute later only after mediation boundaries
```

Reference:

```text
4-15-26 NEW ROADMAP/BackLog.md
```

---

# Phase 3 — Future Foundation Layer

These are documented future foundations. They are not active implementation unless explicitly reprioritized.

## 5. Task / Run-State Store

Purpose:

```text
Solve token exhaustion, handoff drift, and long-session continuity.
```

Tracks:

```text
active task
paused task
blocked task
files read
files changed
tests run
commits created
blockers
next recommended step
do-not-touch list
handoff summary
```

Core rule:

> **Run state is evidence and continuity, not permission.**

Reference:

```text
docs/future/NOVA_TASK_RUN_STATE_PLAN_2026-04-27.md
```

## 6. Connector Registry

Purpose:

```text
Central registry for Google, GitHub, MCP, ElevenLabs, OpenClaw, Home Assistant, browser/computer-use, workflow runners, and local data connectors.
```

Core rule:

> **Connectors expand access. They do not expand authority without Nova governance.**

Reference:

```text
docs/future/NOVA_CONNECTOR_REGISTRY_PLAN_2026-04-27.md
```

## 7. Approval Queue

Purpose:

```text
Let Nova prepare proposed actions while the user keeps authority.
```

Core rule:

> **Approval is narrow, visible, revocable, and logged.**

Reference:

```text
docs/future/NOVA_APPROVAL_QUEUE_PRODUCT_PLAN_2026-04-27.md
```

## 8. Trust Spans / Trace Cards

Purpose:

```text
Show what Nova understood, routed, considered, blocked, approved, executed, and did not do.
```

Core rule:

> **Show decisions and evidence, not private chain-of-thought.**

Reference:

```text
docs/future/NOVA_TRUST_SPANS_TRACE_CARDS_PLAN_2026-04-27.md
```

## 9. Sensitive Data Routing

Purpose:

```text
Decide when content stays local, can use cloud, must be redacted, needs approval, or must be blocked.
```

Core rule:

> **Sensitive data should move only when the user can understand why, where, and under what limits.**

Reference:

```text
docs/future/NOVA_SENSITIVE_DATA_ROUTING_PLAN_2026-04-27.md
```

---

# Phase 4 — Google / Email Direction

## 10. Google Identity And Read-Only Connectors

Status:

```text
FUTURE / NOT ACTIVE YET
```

Recommended order:

```text
Google Sign-In identity only
→ connector registry / connected apps page
→ Calendar read-only
→ Gmail read-only
→ Drive read-only
→ Contacts read-only
→ Gmail draft-only
→ Calendar event proposal/draft
→ approval-required writes later
```

Core rule:

> **Google connects data. Nova governs action.**

References:

```text
docs/future/NOVA_GOOGLE_CONNECTOR_DIRECTION_FINAL_LOCK_2026-04-26.md
docs/future/NOVA_GOOGLE_ACCOUNT_AND_CONNECTOR_ONBOARDING_PLAN.md
```

## 11. Cap 64 / Email Direction Decision

Current status:

```text
Cap 64 P5/P6 is paused.
```

Preserve:

```text
Cap 64 implementation
Cap 64 confirmation-gate fix
Cap 64 tests
Cap 64 checklist updates
Cap 64 P1-P4 evidence
```

Do not actively run:

```text
Cap 64 P5 live checklist
Cap 64 live signoff
Cap 64 P6 lock
mail-client live testing
standalone email expansion outside Google connector alignment
```

Possible future directions:

```text
Cap 64 remains standalone mailto draft path
OR Cap 64 becomes Gmail-aligned draft creation
OR Cap 64 is replaced by connector-backed draft flow
```

Do not treat the current Cap 64 confirmation-gate behavior as P5 certification.

---

# Phase 5 — OpenClaw Foundation

## 12. OpenClawMediator Skeleton

Status:

```text
FUTURE / AFTER CONVERSATION VISIBILITY AND LOCAL CAPABILITY LIMITS ARE CLEARER
```

Allowed first OpenClaw work:

```text
OpenClawMediator skeleton only
no new execution
no new tools
no approval bypass
no broad hands-layer behavior
```

Target route:

```text
GovernorMediator
→ OpenClawMediator
→ EnvelopeFactory
→ EnvelopeStore
→ OpenClaw runner/thinking loop
→ approval queue if needed
→ ledger/receipt
```

References:

```text
docs/future/NOVA_OPENCLAW_HANDS_LAYER_IMPLEMENTATION_PLAN.md
docs/future/NOVA_OPENCLAW_AUTOMATED_WORKFLOW_OPPORTUNITY_MAP_2026-04-27.md
```

## 13. First Read-Only OpenClaw Workflow Proof

Best first workflow:

```text
Nova Project Foreman Brief
```

It should read repo/docs/status and produce:

```text
what changed
what is blocked
what is stale
what tests ran
what Claude/Codex should do next
what not to touch
```

Required non-action statement:

```text
No files changed.
No commits made.
No capabilities executed.
```

Then consider:

```text
Token Recovery / Session Continuity Brief
Local Capability Signoff Assistant
Business Follow-Up Brief
```

Reference:

```text
docs/future/NOVA_OPENCLAW_AUTOMATED_WORKFLOW_OPPORTUNITY_MAP_2026-04-27.md
```

---

# Phase 6 — MCP Governed Connector Layer

## 14. MCP Read-Only Connector Proof

Status:

```text
FUTURE / AFTER CONNECTOR REGISTRY AND GOVERNANCE FOUNDATION
```

Correct pattern:

```text
MCP server exposes tool/data
→ Nova connector registry records it
→ Nova classifies risk
→ GovernorMediator / ExecuteBoundary checks authority
→ NetworkMediator controls outbound access
→ approval queue handles real actions
→ ledger/trust receipt records use
```

Best first MCP proof:

```text
Read-only repo/docs MCP proof
```

Blocked early:

```text
full filesystem write access
full GitHub mutation
email send/delete/archive
calendar create/update/delete
browser submit/save/buy/book
financial tools
unknown remote MCP servers
```

Core rule:

> **MCP may widen Nova's connector surface. It must not widen execution authority without Nova governance.**

Reference:

```text
docs/future/NOVA_MCP_GOVERNED_CONNECTOR_PLAN_2026-04-27.md
```

---

# Phase 7 — Voice / ElevenLabs

## 15. Voice Provider Abstraction

Status:

```text
FUTURE / AFTER TRUST-ACTION LOOP IS READY
```

Needed before ElevenLabs becomes standard:

```text
local/private fallback
VoiceOutputProvider interface
cloud voice disclosure
budget checks
sensitive-content routing
voice usage logging
stop/cancel behavior
```

## 16. ElevenLabs TTS Provider

Best first ElevenLabs workflow:

```text
natural spoken Nova responses
```

Do not start with:

```text
ElevenAgents
telephony
voice cloning
always-listening mode
direct booking/email/calendar/CRM/payment webhooks
```

Core rule:

> **ElevenLabs gives Nova a voice. Nova keeps the authority.**

References:

```text
docs/future/NOVA_ELEVENLABS_VOICE_INTEGRATION_PLAN.md
docs/future/NOVA_ELEVENLABS_VOICE_OPPORTUNITY_MAP_2026-04-27.md
docs/future/NOVA_VOICE_STACK_OPERATING_MODEL_2026-04-26.md
```

---

# Phase 8 — Governed Memory / Retrieval

## 17. Local Governed Memory / Retrieval

Status:

```text
FUTURE / NOT ACTIVE YET
```

Use for:

```text
project docs
runtime handoffs
audit reports
capability docs
approved user memories
project glossary
conversation summaries
```

Must include:

```text
visible saves
review/delete/supersede
authority_effect = none
no hidden learning
no silent policy changes
```

Core rule:

> **Memory improves understanding. It does not grant authority.**

References:

```text
docs/future/NOVA_GOVERNED_LEARNING_PLAN.md
docs/future/NOVA_COHERENCE_MEMORY_BACKGROUND_ARCHITECTURE_ALIGNMENT.md
```

---

# Phase 9 — Later External Integrations

## 18. GitHub / Git Read-Only Assistant

Use for:

```text
repo status
commit summaries
PR review
doc drift checks
test failure summaries
next Claude/Codex prompt
release note drafts
```

Blocked early:

```text
push
merge
branch deletion
release creation
unapproved file edits
```

## 19. Home Assistant / Smart Home

Start with:

```text
read sensor state
summarize home status
simple reversible lights/media
suggest automations
```

Block early:

```text
unlock doors
open garage
disable alarms
security cameras
safety-critical devices
```

## 20. Browser / Computer-Use Sandbox

Start as:

```text
screen-to-action review
page summary
form-fill draft
GitHub page review
website QA
```

Do not start with:

```text
auto-submit
auto-buy
auto-book
auto-send
change settings
delete files
unbounded shell
```

Reference:

```text
docs/future/NOVA_INTEGRATION_OPPORTUNITY_ROADMAP_2026-04-27.md
```

---

# Explicitly Paused Work

These stay paused unless the owner explicitly unpauses them:

```text
Cap 64 P5/P6 email live signoff
Shopify / Cap 65 live work
Auralis / website merger
Google connector implementation
ElevenLabs implementation
broad OpenClaw execution
background reasoning jobs
governed learning persistence
CRM/SaaS packaging
```

---

# Clean Current Build Order

```text
1. RequestUnderstanding trust/action-history review card
2. Re-run live conversation checks
3. Fix narrow RequestUnderstanding routing bypasses
4. Local capability signoff matrix
5. Task/run-state store
6. Connector registry
7. Approval queue
8. Trust spans / trace cards
9. Sensitive data routing
10. Google identity + Calendar/Gmail read-only
11. Gmail draft-only / Cap 64 direction decision
12. OpenClawMediator skeleton
13. Project Foreman Brief
14. Token Recovery / Session Continuity Brief
15. MCP read-only repo/docs proof
16. ElevenLabs TTS provider
17. Voice setup diagnostic
18. Governed memory/retrieval
19. GitHub/Git read-only assistant
20. Home Assistant later
21. Browser/computer-use sandbox later
```

This order is strategic. It is not permission to start every item now.

---

# Current Final Rule

> **Conversation first, visibility next, hands later.**

The current implementation path should stay narrow until Nova can visibly explain what it understood, what it can do, what it cannot do, and what it did not do.

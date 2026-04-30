# Nova Brain Runtime Architecture

This document defines how Nova can become a practical “full brain” without requiring a giant local model.

Nova should not try to become one massive local model.

Nova should become a governed brain system:

```text
small / medium local model
+ model router
+ context assembler
+ task clarifier
+ intention parser
+ deterministic modules
+ capability contracts
+ sandbox boundary enforcer
+ Governor
+ receipts
+ optional deep reasoning fallback
```

The goal is not uncontrolled autonomy.

The goal is useful local intelligence wrapped in visible authority boundaries.

Core rule:

```text
Intelligence is not authority.
```

---

## Runtime Brain Stack

```text
User Input
   ↓
Task Clarifier
   ↓
Context Assembler
   ↓
Model Router / Tier Manager
   ↓
Local or Approved Reasoning Model
   ↓
Intention Parser / Structured Output Constraint
   ↓
Tool / Function Calling Bridge
   ↓
Sandbox Boundary Enforcer
   ↓
Capability Contract Check
   ↓
Governor
   ↓
Execution Boundary
   ↓
Receipts / Proof
   ↓
Persona / Identity Filter
   ↓
User Response
```

This stack lets Nova use small models effectively because the model does not need to hold the whole system in its weights.

The system around the model supplies memory, context, authority rules, capability definitions, proof, and safe routing.

---

## 1. Model Router / Tier Manager

The Model Router decides which reasoning lane should be used.

It should choose between:

```text
local small model
local medium model
cloud/deep reasoning model
no model needed / deterministic answer
```

The router should consider:

- task complexity
- privacy sensitivity
- current model availability
- local hardware cost
- latency
- user preference
- whether current evidence is needed
- whether deep reasoning is worth the cost

## Privacy Tiers

Model selection should be governed by user privacy settings.

Example tiers:

```text
never_cloud
ask_before_cloud
cloud_allowed_for_marked_tasks
cloud_allowed_for_low_sensitive_tasks
```

Nova should never silently send sensitive local context to a cloud model.

If cloud reasoning is needed, Nova should explain:

```text
This task may require deeper reasoning than the local model can provide.
Do you want to use the approved deep-reasoning lane?
```

## Rule

Model routing is not just optimization.

Model routing is a governed privacy and authority decision.

---

## 2. Context Assembler

The Context Assembler retrieves the right context before the model responds.

It should gather only the context needed for the current task.

Possible context sources:

```text
current conversation
project memory
user preferences
recent decisions
recent receipts
active routines
open loops
runtime truth docs
capability contracts
proof packages
current files in use
```

The Context Assembler should produce a compact context packet.

Example:

```json
{
  "task": "Prepare a morning brief",
  "relevant_preferences": ["prefers concise status first", "tracks AI news"],
  "active_projects": ["NovaLIS", "Auralis"],
  "open_loops": ["Cap 16 search reliability", "Cap 64 P5 paused"],
  "recent_receipts": [],
  "capability_limits": ["memory is not authority", "email is draft-only"]
}
```

## Rule

Context should help Nova understand.

Context should not authorize action.

Memory and context can influence answers, but they cannot grant permission.

---

## 3. Task Clarifier

The Task Clarifier runs before planning or execution.

It catches ambiguous or high-boundary prompts.

Examples:

```text
Find contractors and draft an email.
```

Nova should ask:

```text
What city or service area should I search in?
```

```text
Log into my account and change my settings.
```

Nova should say:

```text
That requires a personal account/browser/account-write environment and cannot proceed without explicit governed capability, confirmation, and proof.
```

The Task Clarifier is deterministic and narrow.

It does not execute tools.

It does not call the Governor.

It does not replace full Brain routing.

---

## 4. Intention Parser / Structured Output Constraint

The model should not freely invent tool calls.

When Nova needs to route work, the model should produce structured intent.

Example schema:

```json
{
  "intent": "web_search",
  "task_type": "current_information",
  "params": {
    "query": "latest AI model releases"
  },
  "clarification_needed": false,
  "environment": "web_search",
  "authority_tier": "network_read",
  "confidence": 0.92
}
```

If the output is malformed, Nova should not guess.

Fallback:

```text
clarification_needed: true
reason: malformed_intent
```

## Rule

Structured output is a safety and reliability boundary.

The model may suggest intent.

Deterministic code validates intent.

---

## 5. Tool / Function Calling Bridge

The Tool Bridge converts validated intent into deterministic module routing.

It should route to:

```text
Task Clarifier
governed search
calendar read
memory retrieval
capability contracts
dry-run planner
receipt reader
Obsidian presence writer
OpenClaw planning
email draft flow
Shopify read-only report
```

The Tool Bridge should not directly execute external actions.

It should prepare a request for the governed path.

Example:

```text
intent: email_draft
→ capability contract check
→ Governor
→ confirmation if needed
→ execution boundary
→ receipt
```

## Rule

The Tool Bridge is not authority.

It is routing.

---

## 6. Search Synthesis Module

The Evidence Lane should not dump raw search results directly into the model.

A Search Synthesis module should convert raw results into structured evidence.

Example:

```json
{
  "query": "latest AI model releases",
  "claims": [
    {
      "claim": "Model X was announced this week.",
      "source": "source_url",
      "confidence": "medium",
      "uncertainty": "source is vendor announcement"
    }
  ],
  "known": [],
  "unclear": [],
  "source_urls": []
}
```

This reduces hallucination and supports better proof.

## Rule

For current facts, Nova should prefer source-backed evidence.

If evidence is weak, Nova should say so.

If search fails, Nova should not answer current facts from stale memory as if certain.

---

## 7. Capability Contracts

Capability Contracts define what each capability can and cannot do.

Priority contracts:

```text
Cap 16 — governed_web_search
Cap 64 — send_email_draft
Cap 65 — shopify_intelligence_report
Cap 63 — openclaw_execute
```

A contract should define:

```text
capability_id
name
environment
authority_tier
can
cannot
required_setup
confirmation_required
expected_receipts
fallbacks
known_failure_modes
```

Example:

```yaml
capability_id: 64
name: send_email_draft
environment: email_draft
authority_tier: external_effect_draft
can:
  - open a local mail client draft through mailto
  - prefill recipient, subject, and body
cannot:
  - send email
  - access inbox
  - use SMTP
confirmation_required: true
expected_receipts:
  - EMAIL_DRAFT_CREATED
  - EMAIL_DRAFT_FAILED
fallbacks:
  - show drafted text in chat
  - user copy/paste manually
```

## Rule

Capability Contracts make Nova smarter without widening authority.

The Governor still decides.

---

## 8. Sandbox Boundary Enforcer

The Sandbox Boundary Enforcer is a hard-coded gate between internal cognition and real-world action.

Inside the sandbox, Nova may:

```text
reason
summarize
draft
plan
compare
retrieve memory
assemble context
prepare dry runs
suggest next steps
```

Outside the sandbox are actions such as:

```text
send
buy
publish
submit
delete
edit account
write Shopify
run OpenClaw
change calendar
modify files
trigger external service
```

Before any outside-sandbox action, Nova must check:

```text
Is this external?
Which capability applies?
Is setup present?
Is confirmation required?
What proof will exist?
Has Governor allowed it?
```

## Rule

The sandbox boundary should be enforced in code, not only described in docs.

---

## 9. Governor

The Governor remains the authority boundary.

The Brain can propose.

The Governor decides.

The Governor should receive structured requests, not vague natural language.

Example request shape:

```json
{
  "task_id": "task_123",
  "capability": "cap64_send_email_draft",
  "environment": "email_draft",
  "authority_tier": "external_effect_draft",
  "confirmation_required": true,
  "proof_required": ["EMAIL_DRAFT_CREATED"],
  "user_visible_summary": "Open a local email draft. Nova will not send it."
}
```

## Rule

No Brain layer may bypass the Governor.

---

## 10. Persona / Identity Filter

The Persona layer should shape the final user-facing response.

It should ensure:

```text
clear tone
honest current capability status
boundary honesty
no overclaiming
consistent Nova identity
helpful next step
```

The Persona layer can be:

```text
prompt wrapper
output validator
deterministic phrase library
small local model style pass
```

It does not need to be a separate huge model.

## Rule

Persona improves communication.

Persona does not authorize action.

---

## 11. Receipts / Proof Layer

Every governed action should leave proof where applicable.

Proof may include:

```text
ledger event
trust receipt
action receipt
source URLs
screenshots
state changes
test output
commit hash
proof report
```

Obsidian may mirror proof later, but the ledger remains proof authority.

Correct:

```text
Ledger receipt → Obsidian summary
```

Incorrect:

```text
Obsidian note → treated as proof authority
```

---

## 12. Optional Deep Reasoning Fallback

Nova may use cloud/deep reasoning for hard tasks.

Examples:

```text
deep repo audit
complex architecture review
large multi-file planning
long-context synthesis
hard debugging
```

But deep reasoning should be governed by privacy settings.

Default behavior should be explicit:

```text
This task may benefit from deeper reasoning.
Use approved deep-reasoning lane?
```

## Rule

Cloud fallback is optional.

Cloud fallback should be visible.

Cloud fallback should never silently receive private context.

---

## 13. Minimal Local Brain Target

A realistic local Nova Brain can run with:

```text
small local model
Task Clarifier
Context Assembler
Model Router
Intention Parser
Capability Contracts
Search Synthesis
Governor
Receipts
Persona Filter
```

This gives Nova brain-like behavior without requiring a giant local model.

The intelligence comes from the system architecture, not just model size.

---

## 14. Runtime Flow Examples

### Local explanation

```text
User asks: What can Nova do?
→ Task Clarifier: no clarification needed
→ Context Assembler: runtime truth summary
→ Model Router: no cloud needed
→ Persona Filter: concise current-truth answer
→ Response
```

### Current search

```text
User asks: What are the latest AI model releases?
→ Task Clarifier: no clarification needed
→ Environment: web_search
→ Capability Contract: Cap 16
→ Search Synthesis: source-backed evidence
→ Response with citations/uncertainty
→ Receipt/proof if applicable
```

### Email draft

```text
User asks: Draft an email to test@example.com.
→ Task Clarifier: recipient/topic present
→ Environment: email_draft
→ Capability Contract: Cap 64
→ Governor: confirmation required
→ User confirms
→ local mailto draft opens
→ receipt written
```

### Personal account write

```text
User asks: Log into my account and change settings.
→ Task Clarifier: high-boundary prompt
→ Sandbox Boundary: account-write environment
→ No execution
→ Response offers manual guide or future dry-run plan
```

---

## 15. Implementation Order

Recommended order:

```text
1. Fix Cap 16 search reliability.
2. Add static Capability Contracts.
3. Add Context Assembler.
4. Add Intention Parser / structured output validation.
5. Add Search Synthesis module.
6. Add Sandbox Boundary Enforcer.
7. Add read-only Dry Run / Plan Preview.
8. Add Persona / Identity Filter.
9. Add Brain Trace metadata.
10. Add Obsidian Presence mirror.
11. Add optional Model Router / Tier Manager.
```

Model Router can be designed early, but it does not need to block Cap 16 or Capability Contracts.

---

## Current Truth

Implemented today:

```text
Task Clarifier
EnvironmentRequest schema scaffold
Brain docs
Brain live proof
```

Still future:

```text
full Task Environment Router
live Capability Contracts
Dry Run API
Brain Trace UI
Context Assembler
Model Router
Search Synthesis
Sandbox Boundary Enforcer
Persona Filter
Obsidian Presence Writer
```

Active P1:

```text
Cap 16 search reliability
```

---

## Final Framing

Nova does not need to become one massive model.

Nova needs to become a governed brain system.

The closest realistic full Brain is:

```text
small local reasoning
+ strong context assembly
+ deterministic routing
+ capability contracts
+ governed tools
+ receipts
+ optional deep reasoning
```

That lets Nova feel intelligent without requiring extreme hardware.

```text
Let intelligence reason.
Let the Governor authorize.
Let receipts prove.
```

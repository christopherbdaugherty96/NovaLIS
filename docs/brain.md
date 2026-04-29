# Brain

This document captures the Nova Brain concept as a canonical architecture note.

Nova is not trying to become another generic autonomous agent.

Nova is trying to become a governed intelligent brain.

The key principle remains:

Intelligence can reason freely.  
Execution still passes through the Governor.  
Receipts prove what happened.

Nova’s brain should be able to ask:

1. What is the user trying to accomplish?
2. What do I know?
3. What do I not know?
4. What memory/context do I need?
5. What environment do I need to enter?
6. Am I allowed to enter that environment?
7. Which capability grants access?
8. Is confirmation required?
9. What proof should exist afterward?
10. What is the next safe step?

The missing layer is the Task Environment Router.

The Task Environment Router answers:

> For this task, what environment does Nova need to enter, what authority is required, which capability would grant it, and what proof should exist afterward?

---

## Core Idea

Nova is not trying to make automation disappear.

Nova is trying to build a brain that understands what kind of world a task requires.

For every task, Nova should be able to reason:

- Can I solve this locally?
- Do I need current evidence?
- Do I need memory?
- Do I need a browser?
- Do I need a signed-in account?
- Do I need to write, change, or send something?
- Is the capability available?
- Is the environment configured?
- Is confirmation needed?
- What happens if blocked?
- What proof will satisfy the user?

This is not safety theater.

This is intelligence.

A smart person does this too:

- Can I answer from memory, or do I need to look it up?
- Can I do this from here, or do I need to log into the account?
- Can I draft it, or am I allowed to send it?
- Do I need the customer’s file?
- What proof do I need to show I did it?

That is the kind of brain Nova needs.

---

## Nova Brain Model

```text
Nova Brain
├── 1. Task Intake
│   └── What is the user trying to accomplish?
│
├── 2. Task Understanding
│   ├── task type
│   ├── risk level
│   ├── ambiguity
│   ├── current-evidence need
│   └── multi-step need
│
├── 3. Task Clarifier
│   ├── is the goal underspecified?
│   ├── what is the minimum question needed?
│   ├── what should Nova not assume?
│   └── can Nova proceed with a bounded partial answer?
│
├── 4. Working Memory
│   ├── current goal
│   ├── known facts
│   ├── unknowns
│   ├── active project
│   ├── current environment
│   └── next decision
│
├── 5. Environment Reasoner
│   ├── local conversation?
│   ├── local memory?
│   ├── runtime docs?
│   ├── web search?
│   ├── isolated browser?
│   ├── personal browser?
│   ├── local OS?
│   ├── email draft?
│   ├── Shopify?
│   └── OpenClaw?
│
├── 6. Authority Question
│   ├── What boundary is being crossed?
│   ├── Which capability grants access?
│   ├── Is confirmation needed?
│   ├── Is setup missing?
│   └── What proof is required?
│
├── 7. Plan Builder
│   ├── step list
│   ├── environment per step
│   ├── capability per step
│   ├── confirmation points
│   ├── fallback path
│   └── expected receipts
│
├── 8. Dry Run / Preview
│   ├── proposed steps
│   ├── environments that would be entered
│   ├── capability contracts involved
│   ├── confirmation points
│   ├── fallback ladder
│   └── proof expected
│
├── 9. Governor Gate
│   └── existing Nova governance spine
│
├── 10. Execution
│   ├── local answer
│   ├── search
│   ├── memory operation
│   ├── browser/OpenClaw
│   ├── email draft
│   └── connector read/write if future-enabled
│
├── 11. Proof
│   ├── receipts
│   ├── sources
│   ├── screenshots
│   ├── state change
│   └── run timeline
│
└── 12. Reflection
    ├── Did this satisfy the task?
    ├── What is still blocked?
    ├── What should be remembered?
    ├── What should be asked next?
    └── What proof package should be updated?
```

This is the true brain.

Not one model.

A governed cognitive operating loop.

---

## Task Clarifier

A stronger brain should not assume the user’s goal is clear.

Before Nova chooses an environment, it should detect whether the task is ambiguous, underspecified, or missing a required constraint.

The Task Clarifier should ask the smallest useful question instead of guessing.

Examples:

```text
User: Find contractors and draft an email.
Clarifier: What city or service area should I search in?
```

```text
User: Update the Shopify product.
Clarifier: Which product, and what field should change? Also, current Shopify support is read-only unless a future governed write capability is implemented.
```

```text
User: Use the browser to handle this.
Clarifier: Do you mean the isolated OpenClaw browser, or a personal signed-in browser session?
```

The Task Clarifier should produce:

```text
clarification_needed: true/false
missing_fields
minimum_question
safe_partial_path
assumptions_to_avoid
```

Rules:

- Ask one concise question when a required field is missing.
- Do not invent missing location, account, recipient, product, file, or permission context.
- Prefer a bounded partial answer when useful.
- Do not use clarification as a hidden execution path.

---

## Task Environment Router

The Task Environment Router is the missing middle layer between conversation and execution.

It should answer:

```text
For this task, what environment does Nova need to enter?
What authority is required?
Which capability grants access?
What confirmation is needed?
What proof should exist afterward?
```

Its output should include:

```text
task_type
required_environments
environment_options
authority_required
capability_needed
confirmation_required
setup_required
proof_required
allowed_status
confidence
risk_level
blocker
fallback_ladder
next_safe_step
```

Example:

```json
{
  "task": "Find a contractor near me and draft an email",
  "task_type": "multi_step",
  "required_environments": [
    "web_search",
    "email_draft"
  ],
  "environment_options": [
    {
      "environment": "web_search",
      "confidence": 0.94,
      "risk_level": "network_read",
      "capability_needed": "cap16_governed_web_search"
    },
    {
      "environment": "email_draft",
      "confidence": 0.88,
      "risk_level": "external_effect_draft",
      "capability_needed": "cap64_send_email_draft"
    }
  ],
  "authority_required": [
    "network_read",
    "external_effect_draft"
  ],
  "capabilities_needed": [
    "cap16_governed_web_search",
    "cap64_send_email_draft"
  ],
  "confirmation_points": [
    "before_opening_email_draft"
  ],
  "proof_expected": [
    "source_urls",
    "EMAIL_DRAFT_CREATED"
  ],
  "blocked_reasons": []
}
```

---

## Confidence-Bracketed Environment Selection

Nova should not always treat environment selection as a single hard answer.

The Environment Reasoner can produce ranked environment options with confidence and risk.

Example:

```json
{
  "task": "Summarize the latest AI model releases",
  "environment_options": [
    {
      "environment": "web_search",
      "confidence": 0.96,
      "risk_level": "network_read",
      "reason": "The user asked for latest/current information."
    },
    {
      "environment": "local_conversation",
      "confidence": 0.28,
      "risk_level": "none",
      "reason": "Local explanation may help frame the answer, but current facts require search."
    }
  ],
  "selected_environment": "web_search"
}
```

This does not grant access by itself.

It helps Nova explain:

```text
I need web search because the question asks for current information.
```

Or:

```text
I can answer locally first, then use web search if you want current evidence.
```

The Governor remains the authority boundary.

---

## EnvironmentRequest

The central object can be conceptualized as an EnvironmentRequest.

```python
@dataclass
class EnvironmentRequest:
    task_id: str
    requested_environment: str
    reason: str
    authority_required: str
    capability_needed: str | None
    confirmation_required: bool
    setup_required: list[str]
    proof_required: list[str]
    confidence: float
    risk_level: str
    fallback_ladder: list[str]
    allowed_status: Literal[
        "allowed_now",
        "allowed_after_confirmation",
        "blocked_missing_setup",
        "blocked_no_capability",
        "blocked_policy",
        "manual_only",
    ]
```

### Supporting data containers

Future light-code scaffolding can also include pure data containers:

```python
@dataclass
class EnvironmentOption:
    environment: str
    confidence: float
    risk_level: str
    capability_needed: str | None
    requires_confirmation: bool
    reason: str


@dataclass
class ClarificationQuestion:
    question: str
    missing_fields: list[str]
    assumptions_to_avoid: list[str]
    safe_partial_path: str | None


@dataclass
class PlanStep:
    step_id: str
    description: str
    environment: str
    capability_needed: str | None
    authority_required: str
    confirmation_required: bool
    proof_required: list[str]
    fallback_step: str | None
```

These are schemas only.

They should not change runtime routing until a later implementation pass.

### Normal chat

```json
{
  "requested_environment": "local_conversation",
  "reason": "User asked for explanation",
  "authority_required": "none",
  "allowed_status": "allowed_now"
}
```

### Current information

```json
{
  "requested_environment": "web_search",
  "reason": "User asked for current external facts",
  "authority_required": "network_read",
  "capability_needed": "cap16_governed_web_search",
  "confirmation_required": false,
  "proof_required": ["source_urls", "search_receipt"],
  "allowed_status": "allowed_now"
}
```

### Browser task

```json
{
  "requested_environment": "openclaw_isolated_browser",
  "reason": "Task requires interacting with a webpage",
  "authority_required": "browser_interaction",
  "capability_needed": "cap63_openclaw_execute",
  "confirmation_required": true,
  "proof_required": ["screenshot_before", "screenshot_after", "browser_action_receipt"],
  "allowed_status": "allowed_after_confirmation"
}
```

### Personal browser

```json
{
  "requested_environment": "personal_browser_session",
  "reason": "Task requires logged-in personal account",
  "authority_required": "account_session_access",
  "confirmation_required": true,
  "proof_required": ["explicit_user_approval", "screenshot_before", "screenshot_after"],
  "allowed_status": "manual_only"
}
```

---

## What Leaving The Environment Means

Nova should clearly define environments.

### Local internal environments

```text
local_conversation
local_runtime_truth
local_memory
local_project_docs
local_ledger
local_dashboard
```

### Local machine environments

```text
local_filesystem
local_screen
local_os_controls
local_mail_client
local_audio_voice
```

### Network read environments

```text
web_search
website_open
news_api
weather_api
calendar_read
shopify_read_only
```

### Browser environments

```text
openclaw_isolated_browser
browser_use_test_browser
personal_browser_session
remote_browser
```

### External effect environments

```text
email_draft
email_send_future
shopify_write_future
calendar_write_future
form_submit
purchase_payment
account_change
```

Nova’s brain should classify each task into these.

---

## Authority Tiers

The brain should not over-ask permission.

If the Governor already allows Cap 16 search, Nova should not annoy the user every time.

Use authority tiers.

### Tier 0 — no permission needed

```text
local explanation
summarization
planning
local docs read
memory explanation
runtime status read
```

### Tier 1 — allowed read lanes

```text
web search
open public website
read-only connector if configured
weather/news snapshot
```

Usually no confirmation, but receipt/source proof.

### Tier 2 — local reversible actions

```text
volume
brightness
open safe folder
screen capture
```

May need user settings/confirmation depending on action.

### Tier 3 — external-effect draft

```text
email draft
calendar draft
browser form preview
```

Confirmation required.

### Tier 4 — external account write

```text
send email
submit form
shopify write
calendar create
purchase
delete/update account data
```

Strong confirmation / future envelope / receipts.

This gives freedom without chaos.

---

## Capability Contracts

Each capability should eventually have a Capability Contract.

A Capability Contract states:

```text
what the capability can do
what the capability cannot do
required setup
authority tier
confirmation rules
expected receipts
fallback behavior
known failure modes
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
  - attach private files without explicit support and confirmation
requires_setup:
  - default mail client or browser mailto handler
confirmation_required: true
expected_receipts:
  - EMAIL_DRAFT_CREATED
  - EMAIL_DRAFT_FAILED
fallbacks:
  - show drafted text in chat
  - explain how to configure a mailto handler
  - ask user to copy/paste manually
```

Capability Contracts make the brain more intelligent without widening authority.

The brain can consult the contract to know what is possible, blocked, or setup-dependent.

The Governor still decides whether execution is allowed.

---

## Fallback Ladder

When an environment is unavailable, Nova should not stop at a dead end.

It should produce a fallback ladder.

Example:

```text
Requested environment: openclaw_isolated_browser
Status: blocked_missing_setup
Fallback ladder:
1. Explain the manual browser steps.
2. Offer a setup checklist for OpenClaw.
3. Prepare a non-executing plan preview.
4. Ask the user to run the browser step manually and report back.
```

Example for Cap 16 search:

```text
Requested environment: web_search
Status: CPU-budget or timeout friction
Fallback ladder:
1. Return partial source-backed results if available.
2. State what is unclear.
3. Offer to retry with a narrower query.
4. Fall back to local explanation with a current-information warning.
```

Example for Cap 64 email draft:

```text
Requested environment: email_draft
Status: local mail client unavailable
Fallback ladder:
1. Show the email draft in chat.
2. Explain that Nova did not send anything.
3. Give mail client setup instructions.
4. Let the user copy/paste manually.
```

Fallbacks should be helpful, but they should not auto-configure tools, bypass setup, or cross environments silently.

---

## Dry Run / Plan Preview

Before a multi-step or higher-authority task executes, Nova should be able to produce a dry run.

A dry run is a non-executing plan preview.

It should show:

```text
planned steps
environments to enter
capabilities involved
confirmation points
expected receipts
fallback ladder
what Nova will not do
```

Example:

```text
Plan preview:
1. Use Cap 16 governed web search to find current local contractor options.
   Proof: source URLs.
2. Summarize candidates and explain uncertainty.
   Proof: cited summary.
3. Draft an email using Cap 64.
   Confirmation required before opening local mail client.
   Proof: EMAIL_DRAFT_CREATED if opened.

Nova will not send the email.
Nova will not use SMTP.
Nova will not access your inbox.
```

A dry run can make Nova faster without making it more autonomous.

The user sees the intended environment crossings and can approve the plan before execution.

---

## Governor-Safe Suggestion Buffer

Nova can become more helpful by noticing repeated user-approved patterns.

This should be a Suggestion Buffer, not autonomous memory execution.

Example:

```text
Pattern noticed:
User often asks for Shopify summary, then asks for an email draft.

Suggestion:
Would you like me to prepare the Shopify summary first and hold an email draft plan for review?
```

Rules:

- Suggestions do not execute.
- Suggestions do not authorize actions.
- Suggestions must be dismissible.
- Suggestions should be based on visible user patterns or explicit preferences.
- Suggestions should be reviewable and deletable.

This makes Nova feel adaptive while preserving the Governor boundary.

---

## Memory Layers For The Brain

Nova should formalize memory into layers:

```text
Session context
Core user memory
Project memory
Topic/story memory
Archival memory
Conversation search
Suggestion buffer
Receipts / ledger
Runtime truth
Future docs
```

The important rule:

```text
Memory can influence answers.
Memory cannot authorize actions.
```

Working Memory should know what environment the task currently needs.

Memory is not just storage.

Memory is part of the brain when it helps Nova understand:

- current goal
- active project
- known facts
- unknowns
- current environment
- blocker
- next decision
- useful suggestion to present for approval

---

## Project Brain Contexts

Nova should eventually support project brain contexts:

```text
NovaLIS
Pour Social
Website Business
Shopify / E-commerce
Personal Admin
Career / Learning
```

Each project should have:

```text
goals
memory
docs
active tasks
allowed environments
blocked environments
proof logs
capability profile
suggestion patterns
```

That lets Nova decide:

```text
In the Shopify project, I may read Shopify if configured, but I may not write products.
In Pour Social, I may draft contracts and menus, but not send client emails.
In NovaLIS, I may inspect repo docs/code and suggest patches.
```

This is how the brain gets context.

---

## Brain Trace

Nova should eventually produce a Brain Trace.

Not hidden chain-of-thought.

A public operational trace:

```text
task received
clarification checked
environment need detected
environment confidence ranked
memory scopes queried
evidence required
capability contract consulted
capability proposed
dry run preview generated
governor decision
execution result
receipt created
fallback used if needed
```

This makes the brain visible.

A user should be able to see:

```text
What did Nova think the task was?
Was clarification needed?
What environment did Nova need?
How confident was the environment choice?
What authority was required?
Which capability was selected?
What capability contract applied?
Was confirmation required?
What happened?
What proof exists?
What fallback was used?
```

---

## OpenClaw Environment Model

OpenClaw should be treated as an environment, not as the brain.

Nova should treat OpenClaw as:

```text
Environment: isolated browser
```

Entering it requires:

```text
environment_request: browser_isolated
authority_required: network_read + browser_interaction
profile: openclaw
proof_required: screenshot_before + screenshot_after + receipt
```

If the user asks for something requiring logged-in personal data:

```text
environment_request: personal_browser
authority_required: account_session_access
status: requires explicit user approval
```

That is the right brain behavior.

Nova should prefer an isolated OpenClaw-managed browser profile by default, not the user’s personal browser.

OpenClaw should be a bounded execution environment, not an uncontrolled co-pilot.

---

## Inspiration Sources

The best outside ideas to absorb are:

1. Letta / MemGPT — layered memory.
2. CrewAI — scoped memory, read-only memory slices, importance/recency scoring.
3. LangGraph / LangChain — namespaced long-term memory stores.
4. Agent Zero — memory dashboard and project isolation.
5. OpenHands — repo-native agent instruction files / microagents.
6. AutoGen — formal memory protocol and multi-agent coordination patterns.
7. OpenAI Agents SDK — tracing, guardrails, handoffs.
8. OpenClaw / browser-use style systems — isolated browser automation with snapshots, screenshots, deterministic actions.
9. AutoGPT Platform — modular workflow blocks.
10. TaskWeaver — structured plan preview before executable work.
11. Open Interpreter — execution approval prompts as a user experience pattern.
12. BabyAGI — task prioritization, inverted into a Governor-pending queue rather than autonomous execution.
13. NeMo Guardrails — explicit guardrails for model behavior, adapted here as environment access guardrails.

Nova should become the governed host that can use all of these patterns without losing its rule:

```text
Intelligence is not authority.
```

---

## Additional Brain Documents To Split Out Later

This file is the canonical single-document Brain note.

Later, when the design matures, split it into:

```text
docs/brain/README.md
docs/brain/NOVA_BRAIN_MODEL.md
docs/brain/TASK_ENVIRONMENT_ROUTER.md
docs/brain/TASK_CLARIFIER_SPEC.md
docs/brain/ENVIRONMENT_CATALOG.md
docs/brain/AUTHORITY_PLANE.md
docs/brain/CAPABILITY_CONTRACTS.md
docs/brain/FALLBACK_LADDER.md
docs/brain/DRY_RUN_AND_PREVIEW.md
docs/brain/BRAIN_TRACE_UI_SPEC.md
docs/brain/MEMORY_LAYERS.md
docs/brain/PROJECT_CONTEXTS.md
docs/brain/OPENCLAW_ENVIRONMENT_MODEL.md
docs/brain/IMPLEMENTATION_ROADMAP.md
```

Do not split until the single document becomes hard to maintain.

---

## Best Implementation Order

Do not build everything at once.

### Phase 1 — Brain design/scaffold

Add:

```text
docs/architecture/TASK_ENVIRONMENT_ROUTER.md
docs/architecture/AUTHORITY_PLANE.md
AGENTS.md
.agent_context/environments.md
.agent_context/brain_loop.md
.agent_context/governance.md
```

No runtime behavior change yet.

### Phase 2 — Read-only EnvironmentRequest object

Add a non-executing classifier result:

```text
nova_backend/src/brain/environment_request.py
```

Used only for logging/debug/tests at first.

### Phase 3 — Task Clarifier and confidence output

Add design/test scaffolding for:

```text
clarification_needed
minimum_question
environment_options
confidence
risk_level
```

No execution behavior change yet.

### Phase 4 — Capability Contracts

Create static capability contract docs or data for the highest-priority capabilities:

```text
Cap 16 governed_web_search
Cap 64 send_email_draft
Cap 65 shopify_intelligence_report
Cap 63 openclaw_execute
```

### Phase 5 — Cap 16 reliability

Tie Cap 16 into EnvironmentRequest:

```text
current info → web_search environment → Cap 16
```

### Phase 6 — Dry Run / Plan Preview

Add a non-executing preview for multi-step tasks.

The preview should show:

```text
steps
environments
capabilities
confirmation points
proof expected
fallback ladder
```

### Phase 7 — OpenClaw environment planning

Before OpenClaw executes, Nova should create:

```text
EnvironmentRequest(openclaw_isolated_browser)
```

Then Governor decides.

### Phase 8 — UI

Add Brain/Trace panel:

```text
Task
Clarification needed
Environment needed
Authority required
Capability route
Proof expected
Fallback ladder
Current status
```

This is the true brain UI.

---

## Compatible Current Nova Truth

This document is conceptual unless and until runtime implementation proves otherwise.

Current truth to preserve:

- Cap 16 search reliability is current active priority.
- Cap 64 remains paused until conversation/search proof is stable.
- Cap 64 is local mailto draft only, no send.
- Cap 65 is read-only.
- Trust Receipts API exists.
- Fuller Trust Panel remains future work.
- Memory is not authority.
- Runtime truth docs are generated authority for current system state.
- The Governor remains the execution authority boundary.

---

## Final Framing

Nova’s next leap is not more automation.

It is a Task Environment Router plus an Authority Plane.

That turns Nova into a brain that can ask:

```text
What world do I need to enter to complete this task?
Am I allowed to enter it?
What capability grants access?
What confirmation is needed?
What proof should exist afterward?
```

DeepSeek’s refinement adds the next layer of intelligence:

```text
What is unclear?
What should I ask before planning?
How confident am I about the environment choice?
What does the capability contract allow?
What fallback ladder exists if the environment is blocked?
Can I show the user a dry run before execution?
```

That is the missing middle layer between conversation and execution.

And it is fully compatible with the vision:

```text
Let the intelligence reason.
Let the Governor authorize.
Let the receipts prove.
```

That is how Nova becomes a real intelligent brain instead of just another agent wrapper.

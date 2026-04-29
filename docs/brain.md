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
├── 3. Working Memory
│   ├── current goal
│   ├── known facts
│   ├── unknowns
│   ├── active project
│   ├── current environment
│   └── next decision
│
├── 4. Environment Reasoner
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
├── 5. Authority Question
│   ├── What boundary is being crossed?
│   ├── Which capability grants access?
│   ├── Is confirmation needed?
│   ├── Is setup missing?
│   └── What proof is required?
│
├── 6. Plan Builder
│   ├── step list
│   ├── environment per step
│   ├── capability per step
│   ├── confirmation points
│   ├── fallback path
│   └── expected receipts
│
├── 7. Governor Gate
│   └── existing Nova governance spine
│
├── 8. Execution
│   ├── local answer
│   ├── search
│   ├── memory operation
│   ├── browser/OpenClaw
│   ├── email draft
│   └── connector read/write if future-enabled
│
├── 9. Proof
│   ├── receipts
│   ├── sources
│   ├── screenshots
│   ├── state change
│   └── run timeline
│
└── 10. Reflection
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
authority_required
capability_needed
confirmation_required
setup_required
proof_required
allowed_status
blocker
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
    allowed_status: Literal[
        "allowed_now",
        "allowed_after_confirmation",
        "blocked_missing_setup",
        "blocked_no_capability",
        "blocked_policy",
        "manual_only",
    ]
```

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

## Memory Layers For The Brain

Nova should formalize memory into layers:

```text
Session context
Core user memory
Project memory
Topic/story memory
Archival memory
Conversation search
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
environment need detected
memory scopes queried
evidence required
capability proposed
governor decision
execution result
receipt created
```

This makes the brain visible.

A user should be able to see:

```text
What did Nova think the task was?
What environment did Nova need?
What authority was required?
Which capability was selected?
Was confirmation required?
What happened?
What proof exists?
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

Nova should become the governed host that can use all of these patterns without losing its rule:

```text
Intelligence is not authority.
```

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

### Phase 3 — Conversation proof

For each prompt, output internal debug summary in dev mode:

```text
task_type
environment_needed
authority_required
route
capability_considered
proof_expected
```

Do not show hidden reasoning. Show structured operational metadata.

### Phase 4 — Cap 16 reliability

Tie Cap 16 into EnvironmentRequest:

```text
current info → web_search environment → Cap 16
```

### Phase 5 — OpenClaw environment planning

Before OpenClaw executes, Nova should create:

```text
EnvironmentRequest(openclaw_isolated_browser)
```

Then Governor decides.

### Phase 6 — UI

Add Brain/Trace panel:

```text
Task
Environment needed
Authority required
Capability route
Proof expected
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

That is the missing middle layer between conversation and execution.

And it is fully compatible with the vision:

```text
Let the intelligence reason.
Let the Governor authorize.
Let the receipts prove.
```

That is how Nova becomes a real intelligent brain instead of just another agent wrapper.

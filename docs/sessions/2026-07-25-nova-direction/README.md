# Nova Direction Session Summary — 2026-07-25

## Status

This folder is a durable record of the 2026-07-25 Nova strategy session.

It captures:

- what Nova is;
- whether Nova is merely an API/OpenClaw wrapper;
- the current engineering and product assessment;
- the highest-leverage improvements;
- the proposed multi-account email awareness system;
- where these decisions belong in the existing roadmap and active TODO system;
- the boundaries that must remain intact while Nova becomes more capable.

This document records direction. It does not authorize implementation, capability expansion, external writes, Gmail sending, autonomous execution, or changes to capability locks.

---

## 1. Converged Definition of Nova

Nova is a local-first, governance-first awareness and orchestration platform.

Its purpose is not merely to answer questions or invoke APIs. Its purpose is to reduce uncertainty, identify what matters, recommend the next useful move, prepare bounded actions, and keep the user as the final authority over consequential execution.

Canonical framing:

```text
Nova is an awareness engine that helps the user know what matters,
converse naturally, and use tools only when awareness changes what
should happen next — asking before it acts.
```

Long-term product direction:

```text
A Jarvis-style personal butler at the interface layer,
with a governed runtime at the execution layer.

Intelligence proposes.
Nova governs.
The user decides.
```

Nova is intended to serve two connected domains:

1. Personal, home, schedule, communication, and daily awareness.
2. Creator-business operations, initially using Auralis Digital and Lucid Creations as the real operating case.

---

## 2. Is Nova Just APIs and an OpenClaw Wrapper?

### Verdict

No.

Nova uses APIs, local models, cloud models, RSS feeds, connectors, and OpenClaw components, but those integrations do not define the whole system.

The more accurate technical description is:

```text
Nova is a custom governance and orchestration platform that uses
external and local intelligence sources through bounded capabilities,
policy checks, execution limits, receipts, and user-visible approval.
```

### What Nova owns

Nova contains its own:

- Governor and execution choke point;
- capability registry and capability locks;
- confirmation and approval boundaries;
- network mediation and budget enforcement;
- execution timeout and resource controls;
- action queueing and normalization;
- ledger and trust receipts;
- deterministic conversation routing;
- daily awareness brief;
- Auralis Today business decision surface;
- grounded follow-up state;
- governed memory boundaries;
- capability verification and certification structure;
- OpenClaw task envelopes, budgets, tool registry, state machine, and runner integration.

A thin wrapper would generally perform:

```text
Prompt -> model -> API call -> response
```

Nova is intended to perform:

```text
Prompt
-> deterministic intent and context resolution
-> capability selection
-> authority and permission checks
-> confirmation checks
-> budget and resource checks
-> bounded execution
-> result normalization
-> trust receipt
-> user-facing result
```

### Correct relationship between Nova and OpenClaw

OpenClaw is an internal execution and planning subsystem inside Nova.

OpenClaw should not become Nova's product identity or final authority.

Correct relationship:

```text
OpenClaw may plan or execute a bounded approved envelope.
Nova defines the capability, policy, budget, approval, result shape,
and receipt requirements.
```

### Current limitation

Nova's backend architecture is currently deeper than the visible daily product.

The system can therefore look like an integration wrapper to an outside observer because the most useful personal functions are still incomplete, even though the underlying governance and orchestration architecture is substantial.

---

## 3. Current Product and Engineering Assessment

Nova is a legitimate alpha-stage software platform, not a finished consumer product.

Current strengths:

- substantial custom Python backend;
- tested governance boundaries;
- local-first posture;
- weather, news, calendar, awareness brief, business awareness, arithmetic, and bounded search paths;
- explicit truth and degradation behavior;
- strong documentation and verification culture;
- user authority preserved over external effects.

Current weaknesses:

- daily usefulness remains thinner than the architecture;
- Gmail, Google Tasks/Reminders, and traffic are not implemented;
- local conversational latency remains weak on current hardware;
- installation and first-run experience are still developer-oriented;
- major runtime files remain monolithic;
- recovery, backup/restore, schema migration, authentication, and idempotency need further hardening;
- broad automation is intentionally limited and should remain limited until reliability and approval integrity are proven.

The key strategic problem is not lack of architecture.

The key problem is converting the architecture into a dependable daily operating experience.

---

## 4. Improvement Principle

Do not make Nova more powerful by adding dozens of disconnected APIs or more agents.

Make Nova more powerful by making the existing system:

1. harder to break;
2. faster to use;
3. more aware of the user's actual life and businesses;
4. better at ranking what matters;
5. able to prepare useful action without silently executing it;
6. easy to install and recover;
7. measurable through repeatable workflow benchmarks.

The correct product loop is:

```text
Awareness
-> recommendation
-> prepared action
-> preview
-> approval
-> bounded execution
-> receipt
-> verification
```

---

## 5. Highest-Leverage Improvement Order

> **2026-07-25 session proposal — NOT current execution ordering (post-#314).** The priorities
> below (including "Priority 1 — Reliability and recovery" and the Priority 4 personal-capability
> sequence) are this session's recommendations, not the active plan. Current canonical execution
> order lives in `docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md` "Ordering Summary": NOW = one
> post-#312 real-use morning (B1 was cleared 2026-07-27 by the merged-main `3799 passed` run, so
> it is no longer a NOW item); then the owner selects the next product-usability lane;
> authorization integrity is the first activatable hardening lane (parallel priority); broad
> reliability/recovery is the LATER B3-B11 band. Read this section as session input, not the
> active sequence.

### Priority 1 — Reliability and recovery

Nova should remain usable when:

- the internet is unavailable;
- Ollama or another provider is down;
- a connector fails;
- one request times out;
- a cache is stale;
- a state file is corrupted;
- a process is restarted;
- an external service returns malformed data.

Required hardening direction:

- complete the stalled test-suite investigation — [RESOLVED 2026-07-27] full suite passed on merged main; B1 cleared;
- rotate and compact the ledger;
- add tamper-evident ledger verification;
- add state backup plus automated restore drills;
- remove blocking provider probes from the main event loop;
- define and test degraded-mode startup contracts;
- split large runtime monoliths into bounded services;
- add state schema versions and migrations;
- add break-glass read-only mode;
- add receipt privacy classes;
- add idempotency keys before any serious write capability;
- add trusted-device/local-auth protections;
- standardize traces, metrics, latency, and errors.

### Priority 2 — Latency and responsiveness

Target product behavior:

```text
The interface opens immediately.
Cached awareness appears first.
Fresh data fills in asynchronously.
A failed provider never freezes the whole product.
The next request remains usable after a timeout.
```

Recommended response hierarchy:

```text
1. Cached local state
2. Deterministic computation
3. Local model
4. Governed cloud model
5. External connectors
```

### Priority 3 — One operating surface

The main Nova surface should answer five questions:

1. What matters now?
2. Why does it matter?
3. What should I do next?
4. What is waiting for approval?
5. What changed since the last session?

The product should avoid presenting disconnected technical widgets as the primary experience.

### Priority 4 — Daily personal gaps

The current intended gap-fill sequence remains:

```text
Google Tasks / Reminders
-> Multi-Account Email Awareness
-> Traffic and leave-time awareness
```

### Priority 5 — Structured world model

Nova should maintain structured, source-labeled awareness of:

- people;
- accounts and identities;
- projects;
- businesses;
- products;
- orders;
- tasks;
- commitments;
- deadlines;
- risks;
- preferences;
- routines;
- decisions;
- open loops.

Every important fact should retain:

- source;
- timestamp;
- confidence;
- expiration/freshness;
- user-stated, externally verified, or inferred status;
- privacy class;
- whether it may inform recommendations;
- explicit confirmation that it does not itself authorize execution.

### Priority 6 — Prepared action and approval inbox

Nova should prepare useful work such as:

- email drafts;
- scheduling suggestions;
- customer responses;
- business checklists;
- social captions;
- product or project follow-ups;
- approval-ready action envelopes.

Prepared work must remain unexecuted until the applicable policy and approval requirements are satisfied.

### Priority 7 — Shadow mode and earned autonomy

Autonomy should progress through stages:

```text
Observe
-> Shadow / would-have-done receipts
-> Prepare and wait for approval
-> Narrow delegated routine
-> Earned low-risk execution
```

Nova should never jump directly from read-only awareness to broad autonomous action.

### Priority 8 — Product packaging

Target installation flow:

```text
Download
-> install
-> choose local/cloud posture
-> connect optional services
-> run system check
-> receive first brief
```

A normal user should not require Git, Python, terminals, environment-variable knowledge, or FastAPI knowledge.

### Priority 9 — Workflow benchmark

Create a repeatable benchmark covering real workflows such as:

- show the daily brief;
- explain a selected news story;
- identify the day's priority;
- detect messages needing replies;
- prepare but do not send an email;
- identify a calendar conflict;
- recover after Ollama failure;
- recover after network loss;
- restart without losing state;
- reject unauthorized actions;
- prevent duplicate effects;
- show evidence and receipts.

Measure:

- success rate;
- first-response latency;
- total completion latency;
- hallucination rate;
- incorrect routing;
- unnecessary model calls;
- timeout recovery;
- duplicate-action prevention;
- user corrections required;
- approval correctness.

---

## 6. Multi-Account Email Awareness — New Direction

### Product objective

Nova should provide one awareness layer across multiple personal, employment, and business email accounts while maintaining strict identity, permission, privacy, and provenance boundaries.

This should not be designed as one merged uncontrolled inbox.

It should be designed as:

```text
Unified awareness across separate identities.
```

### Account types

Nova should support separately configured accounts such as:

- personal Gmail;
- employment/work email;
- Auralis Digital email;
- Lucid Creations/customer-support email;
- future project, financial, administrative, or business accounts.

### Account registry

Every connected mailbox should have a first-class account record containing:

```text
account_id
display_name
email_address
provider
account_role
purpose
credential_reference
active_scopes
permissions
enabled_status
last_successful_sync
privacy_mode
```

Every message, thread, summary, extracted action, recommendation, and draft must permanently retain the source `account_id`.

### Account roles

Initial account roles:

- Personal
- Employment
- Business
- Customer support
- Financial
- Administrative
- Project-specific

The user defines or approves account roles. Nova may suggest a role but must not silently assign a sensitive operational identity.

### Unified awareness output

Nova should answer:

```text
What across all of my inboxes requires attention?
```

Recommended sections:

- Needs reply
- Deadline
- Decision required
- Waiting on someone
- Account/security warning
- Payment/financial event
- Order/customer issue
- Schedule change
- Personal/admin
- Work/employment
- Business
- No action

### Cross-account awareness examples

Nova should be able to detect:

- a work schedule change that conflicts with a personal appointment;
- the same vendor or invoice appearing in personal and business mail;
- a Shopify order, Printify failure, and customer support message referring to the same order;
- a business contact using the wrong email identity;
- a deadline mentioned in one account that affects a project tracked elsewhere.

Cross-account correlation must be evidence-based using entities such as:

- sender identity;
- organization;
- order number;
- invoice number;
- project name;
- explicit dates;
- product names;
- thread links;
- verified relationship metadata.

### Identity boundary

Nova must distinguish between the user acting as:

- a private individual;
- an employee;
- Auralis Digital;
- Lucid Creations;
- another defined business or project identity.

A draft or send action must never silently cross identities.

Required wrong-account protection:

```text
This conversation belongs to the Lucid Creations account,
but the selected sending identity is the personal account.
Action blocked pending correction.
```

### Per-account permissions

Permissions must be independent for each account.

Example:

```text
Personal account:
- read/search/summarize: allowed
- prepare drafts: allowed
- send: confirmation required
- delete: disabled

Employment account:
- read/search/summarize: allowed
- prepare drafts: disabled or policy-controlled
- send: disabled
- delete: disabled

Business support account:
- read/search/summarize: allowed
- prepare drafts: allowed
- send: confirmation required
- archive: confirmation required
```

Permission granted to one account must never transfer automatically to another account.

### Normalized message model

Provider-specific adapters should normalize Gmail, Microsoft 365/Outlook, and later IMAP into a common structure:

```text
NormalizedMessage
- account_id
- provider
- provider_message_id
- provider_thread_id
- sender
- recipients
- subject
- body_or_bounded_excerpt
- received_at
- labels
- attachment_metadata
- account_role
- sensitivity_class
- source_link
```

### Initial capability split

Avoid one oversized email capability.

Recommended narrow capabilities:

```text
EMAIL_ACCOUNT_CONNECT
EMAIL_ACCOUNT_LIST
EMAIL_MESSAGE_SEARCH
EMAIL_THREAD_READ
EMAIL_AWARENESS_SUMMARY
EMAIL_CROSS_ACCOUNT_CORRELATE
EMAIL_DRAFT_PREPARE
EMAIL_DRAFT_REVIEW
EMAIL_SEND_CONFIRMED
EMAIL_ARCHIVE_CONFIRMED
```

The first implementation should include read-only capabilities only. Preparation capabilities begin in Phase 6.

### Privacy rules

- OAuth tokens stored outside the repository and encrypted at rest.
- Credentials referenced by ID and never written into prompts, memory, receipts, or logs.
- Least-privilege scopes first.
- Sensitive work and personal email should default to local-only or ask-first model routing.
- Cross-account awareness remains temporary reasoning context unless the user explicitly promotes information into governed memory.
- Work-email content must not silently become permanent personal memory.
- Every email-derived claim should expose source account, thread, date, extraction time, confidence, privacy route, and inference status.

### Implementation sequence

```text
Phase 1: One Gmail account, read-only
Phase 2: Multiple Gmail identities
Phase 3: Personal/work/business separation and wrong-account blocking
Phase 4: Microsoft 365/Outlook adapter
Phase 5: Generic IMAP adapter if justified
Phase 6: Prepared drafts with source-linked review
Phase 7: Confirmed sending only after idempotency, recipient, identity,
         attachment, failure-recovery, and receipt tests pass
```

### Explicit first-lane exclusions

```text
No automatic sending
No deletion
No archiving
No label modification
No silent inbox monitoring by default
No automatic memory promotion
No cloud processing of sensitive content without visible policy
No inherited permission between accounts
No broad OpenClaw authority expansion
```

---

## 7. Roadmap and TODO Placement

### Canonical ordering source

Use:

`docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md`

The master roadmap determines ordering. This session should not create a competing roadmap.

### Active work source

Use:

`docs/todo/ACTIVE_TODO.md`

The active TODO should show only work that is currently authorized or the next evidence-ranked candidate.

### Recommended roadmap candidate

Add or preserve the following concept under observation-driven candidates when the roadmap is next updated:

```text
Multi-Account Email Awareness

Unified read-only awareness across separate personal, employment,
and business email identities, with per-account scopes, permanent
provenance, wrong-account blocking, sensitive-data routing, and
prepared-but-unexecuted drafts.
```

### Recommended TODO wording

Replace generic future wording such as:

```text
Google Tasks -> Gmail -> Traffic
```

with the clearer sequence:

```text
Google Tasks / Reminders
-> Multi-Account Email Awareness
   (Gmail read-only first; personal/work/business identity separation)
-> Traffic / leave-time awareness
```

This wording change does not authorize implementation by itself.

### Existing design documents to extend rather than replace

- `docs/future/EMAIL_COORDINATION_BOARD.md`
- `docs/future/NOVA_GOOGLE_CONNECTOR_MODEL.md`
- `docs/future/GOOGLE_WORKSPACE_CONNECTOR_PLAN.md`
- `docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md`
- `docs/todo/ACTIVE_TODO.md`
- sensitive-data routing and privacy-class plans already referenced by the master roadmap

Distinction to preserve:

```text
gmail_multi_email_summary
= multiple messages or threads

multi_account_email_awareness
= multiple independently governed mailbox identities
```

---

## 8. Decisions To Preserve as Project Memory

1. Nova is not to be described as merely an API wrapper or external OpenClaw wrapper.
2. Nova's differentiator is governed awareness and execution, not the number of integrations.
3. OpenClaw remains an internal bounded subsystem; Nova remains the product and authority layer.
4. Reliability, recovery, latency, and daily usefulness outrank adding more agents or APIs.
5. The desired product is one calm operating surface showing what matters, why, the next move, approvals, and changes.
6. The next major personal capabilities are Tasks/Reminders, Multi-Account Email Awareness, and Traffic.
7. Email must support multiple separately governed personal, work, and business identities.
8. Unified awareness must not become identity merging or permission merging.
9. Email read/context comes before drafts; drafts come before sending; sending is a later independently governed capability.
10. Sensitive email should default to local-only or ask-first processing.
11. Cross-account relationships may inform awareness but do not authorize action or automatically enter long-term memory.
12. Prepared Reality, shadow mode, and earned autonomy remain the correct progression toward a Jarvis-style experience.
13. The existing master roadmap remains canonical; this session should be incorporated into it rather than creating a competing roadmap.
14. This dated folder serves as the durable handoff and recovery record for the session.

---

## 9. Recommended Next Documentation Change

When implementation planning resumes, create a dedicated design document rather than coding directly:

```text
docs/future/NOVA_MULTI_ACCOUNT_EMAIL_AWARENESS_PLAN.md
```

That design document should define:

- account registry schema;
- provider adapter interface;
- normalized message/thread schemas;
- account-role model;
- account-level scopes and permissions;
- sensitive-data routing;
- cross-account correlation evidence rules;
- wrong-account negative tests;
- receipt events;
- failure and degradation behavior;
- capability contracts;
- phased acceptance gates.

Do not implement Gmail sending, mailbox modification, or background monitoring in the first lane.

---

## Final Direction

The strongest next form of Nova is not a larger collection of APIs.

It is:

```text
A fast, resilient personal operating layer that understands the user's
personal life, employment, businesses, communications, commitments,
and changing environment; identifies what matters; prepares the next
useful action; and keeps execution bounded, visible, and approved.
```

The highest-value user experience remains:

```text
Here is what changed.
Here is what matters.
Here is why.
Here is the next move.
I prepared it.
Approve when ready.
```

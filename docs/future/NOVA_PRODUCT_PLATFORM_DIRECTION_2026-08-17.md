# Nova Product / Platform Direction — 2026-08-17

Status: strategic synthesis; non-authorizing.

This document consolidates the current product-level direction for Nova after the August 2026
architecture, product, competitive, and runtime reviews. It is a durable strategic reference only.
It does not change current roadmap ordering, activate a lane, modify runtime behavior, authorize
Google domain access, expand capabilities, change authority, or authorize OpenClaw/browser work.

Current runtime truth remains defined by code and generated runtime documentation. Current work
ordering remains defined by the canonical roadmap/current-state surfaces and separately reviewed
lane scope. Owner approval remains the source of activation.

Grounded baseline when this document was created:

```text
main: e69ca987cd458de8723f1ce9f3885de2de4ec6e8
latest merged PR: #352 — keep private Drive searches off public web
```

---

## 1. Product identity

Nova should not be treated as another general-purpose chatbot or autonomous agent.

The clearest product identity is:

> **Nova is a local-first personal operations system and governed AI control plane that maintains
> operational state, identifies what matters, prepares the next useful step, coordinates optional
> reasoning providers and tools, and preserves what actually happened afterward.**

Its permanent architecture remains:

```text
Awareness -> Decision -> Authority -> Execution -> Outcome
```

Continuity surrounds that loop as persistent, reconciled operational state.

The product-level objective is not maximum task throughput. The objective is to reduce uncertainty
and help the user make the next better decision while preserving truthful state across time.

---

## 2. Nova is a platform whose core contains a governed AI harness/control plane

If forced to choose between "harness" and "platform," Nova is best classified as a **platform**.

The distinction is:

```text
PRODUCT
Nova — Personal Operations System

        built on

PLATFORM
State + Continuity + Evidence + Decision + Authority + Outcome

        containing

HARNESS / CONTROL PLANE
Models + capabilities + tools + execution boundaries
```

The harness is the technical layer that wraps and controls models/tools. The platform is broader:
it provides durable state, evidence, policy, authority, provider routing, capability management,
execution, reconciliation, and eventually multiple operating surfaces.

Nova should not be marketed primarily as an "AI harness." That is an engineering description.
The user-facing product is the personal operations system.

---

## 3. Local-first means local control, not local-only intelligence

Nova should remain **local-first**, but local-first should be interpreted as:

> **Local control plane, hybrid intelligence.**

The preferred topology is:

```text
LOCAL / USER-CONTROLLED
- durable Continuity state
- credentials / secrets
- authority / approvals
- capability policy
- receipts / ledger
- local files
- sensitive memory
- user preferences
- local model default

OPTIONAL EXTERNAL REASONING
- OpenAI
- Anthropic
- Gemini
- other future providers

OPTIONAL EXTERNAL ACTUATORS / SERVICES
- Google APIs
- Shopify
- web search
- OpenClaw
- browser/computer-use later if separately warranted
```

Nova does not need the smartest model to be durable. Models should remain replaceable reasoning
providers beneath Nova's state, evidence, authority, and outcome system.

---

## 4. Multi-provider model direction

Nova should eventually support OpenAI, Anthropic, Gemini, and other providers as optional reasoning
engines while keeping local inference as the default.

Target routing hierarchy:

```text
Tier 1 — Local
Use the smallest capable local model for routine/private work.

Tier 2 — External advisory reasoning
Escalate to OpenAI / Anthropic / Gemini / others for harder reasoning, large context,
second opinions, research synthesis, coding review, or specialized capabilities.

Tier 3 — Specialized execution / technical workers
Codex, OpenClaw, browser/computer-use, or other specialist agents receive bounded work only.
```

Future provider policy should be able to express:

```text
local_only
local_preferred
ask_before_cloud
cloud_allowed_for_selected_data
preferred_provider
preferred_coding_provider
cost ceiling / budget
privacy class
allowed data classes
fallback order
```

A future provider registry/router may track:

- provider;
- model;
- task strengths;
- context limits;
- latency;
- cost class;
- privacy class;
- permitted data classes;
- network requirement;
- fallback order.

Hard rule:

> **Models advise. Nova governs.**

A model recommendation, plan, memory, confidence score, or prior success never becomes action
authority.

---

## 5. Capability and authority remain permanently separate

Capability answers:

> What can the runtime technically do?

Authority answers:

> May this exact action occur now, in this scope, for this actor/session, with these parameters?

Therefore:

```text
capability != authority
provider access != Nova authority
memory != permission
recommendation != mandate
connection != action permission
```

The existing governed execution spine remains the correct foundation:

```text
User
-> GovernorMediator
-> Governor
-> CapabilityRegistry
-> SingleActionQueue
-> LedgerWriter
-> ExecuteBoundary
-> Executor
```

Effectful growth should preserve exact-action binding, approval authenticity, bounded execution,
receipts, and truthful outcome handling.

---

## 6. ApprovalGrant and outcome truth are core trust assets

Approval should not be represented as a reusable caller-controlled Boolean.

ApprovalGrant exists to bind approval to the exact action/session/capability and prevent classes of
failure such as:

- parameter mutation after approval;
- replay;
- cross-session reuse;
- cross-capability reuse;
- stale approval reuse;
- caller-fabricated `confirmed=true` authority.

Nova should continue treating outcome truth independently from execution truth.

`accepted_unverified` exists because:

```text
request accepted != external effect verified
```

Nova should preserve distinctions such as:

```text
rejected
failed
accepted_unverified
verified
unknown
```

Execution answers what Nova attempted. Outcome answers what Nova can actually prove happened.

---

## 7. Current engineering pressure point: request understanding / routing

The current Governor/execution architecture is stronger than the natural-language interpretation
layer.

Recent defects have clustered around:

- explicit parameters being dropped;
- temporal scope loss (`tomorrow` -> `today`);
- source confusion (private Drive -> public web);
- route precedence;
- equivalent word-order variants;
- follow-up scope binding;
- broad intent being narrowed incorrectly.

This indicates semantic interpretation/source resolution is now the primary architectural pressure
point.

Do not perform a big-bang routing rewrite during the current stabilization sequence.

Post-stabilization direction should be incremental semantic normalization, for example:

```text
raw language
-> request understanding
-> typed semantic request
-> source resolution
-> capability resolution
-> Governor
```

Illustrative future request shape:

```text
intent: retrieve
domain: calendar
source_scope: private
resource: events
temporal_scope: tomorrow
requested_effect: read
confidence: high
provenance: deterministic_rule | bounded_classifier
```

The safer long-term approach is hybrid:

- deterministic guards for effectful/private/source-sensitive requests;
- typed normalization for domain/source/time/effect;
- bounded model classification only for unresolved advisory/read-only ambiguity;
- GeneralChat fallback only after governed/private/source-sensitive routes are excluded.

An LLM may suggest a route. It may not manufacture authority.

---

## 8. Continuity is the primary product moat

Governance is the technical trust foundation. **Continuity is the user-facing moat.**

Continuity is not generic memory. It is persistent operational state answering:

```text
What am I trying to accomplish?
What did I decide?
What did I commit to?
What is due?
What am I waiting on?
What is blocked?
What actually happened?
What was verified?
What remains unresolved?
What deserves attention next?
```

Continuity should preserve and reconcile:

- commitments;
- decisions;
- dependencies;
- open loops;
- waiting items;
- blockers;
- evidence;
- status;
- review/reopen conditions;
- next-action projections;
- attention ranking.

Hard boundaries remain:

- Continuity never authorizes;
- Continuity never executes;
- Continuity never silently invents commitments;
- Continuity never converts learning/history into permission.

The first runtime slice should remain deliberately small. A good initial product proof would support:

```text
Objects:
- commitment
- open loop
- waiting item

Sources:
- owner confirmed
- provider observed
- Nova receipt observed

States:
- active
- waiting
- completed_unverified
- verified
- abandoned
```

No graph database, broad learning system, predictive automation, or autonomous extraction is required
to prove the core value.

---

## 9. Google is evidence infrastructure, not the product

Google Workspace should enter Nova as a governed external evidence ecosystem.

The current Foundation direction remains correct:

```text
OAuth identity / connection
-> exact granted scopes
-> encrypted credential lifecycle
-> no automatic domain access
-> no automatic Nova capability
-> no automatic Nova authority
```

Permanent rule:

```text
Google capability != Google authorization != Nova authority
connected != evidence collected != action permitted
```

First Google evidence vertical should remain **Google Tasks READ**.

Target chain:

```text
Google account identity
-> exact Tasks read scope
-> scoped API read
-> normalized evidence
-> provenance/freshness
-> observed commitment state
-> Nova Awareness
```

Google Tasks is not being added so Nova can become another task-list app. It is being added because
Tasks provides external evidence of real commitments.

After Tasks evidence is proven, minimal Continuity should follow quickly so Nova can reconcile
provider-backed obligations across days.

Gmail READ is a high-value next evidence source because many commitments and waiting items live in
messages rather than task systems. Gmail should therefore be treated as an evidence stream into
Continuity, not as "Gmail inside Nova."

---

## 10. Product experience should center on operational state

The long-term product should feel less like "open chatbot, ask question" and more like a persistent
operations layer.

A strong daily loop is:

```text
Observe real sources
-> reconcile state
-> identify what matters
-> present a small attention set
-> support natural questions
-> prepare the next step
-> require authority for real effects
-> execute through governed capability
-> verify outcome
-> reconcile back into Continuity
```

The Today surface should eventually prioritize:

- commitments;
- deadlines;
- waiting items;
- blockers;
- decisions needing review;
- verified/unverified completions;
- changes since last review;
- 3–5 highest-value attention items.

Weather/news/traffic remain supporting context rather than defining the product.

Conversation remains an interface into state, not the primary persistence model.

Long-term primary objects are closer to:

```text
Commitment
Decision
Project
Open Loop
Evidence
Action
Outcome
```

---

## 11. Prepared Reality should bridge decision and action

Nova should avoid a false binary where it either talks or acts.

Prepared Reality allows Nova to:

```text
understand
-> gather evidence
-> prepare draft/checklist/plan/preview
-> show exact proposed effect
-> await user authority
```

Examples include:

- follow-up email draft;
- proposed calendar change;
- client proposal;
- task plan;
- workflow preview;
- prepared form;
- bounded action packet.

Prepared Reality remains non-authorizing and non-executing.

---

## 12. OpenClaw and other agents remain actuators/workers

OpenClaw should not own:

- strategy;
- durable state;
- authority;
- budgets;
- approval interpretation;
- long-term memory;
- outcome reconciliation.

The same principle should apply to future external workers such as Codex or other agents.

Nova owns the control relationship:

```text
Nova state / decision / authority
        ↓
typed bounded task
        ↓
worker / actuator
        ↓
structured evidence
        ↓
Nova outcome / reconciliation
```

More OpenClaw/browser autonomy is not the current product priority.

---

## 13. Deployment direction

Nova does **not** inherently require a remote server.

Near-term deployment should remain local-first.

If Nova only needs to operate while the user machine is running, the local application is enough.

An always-on component becomes useful later for:

- reliable scheduling;
- background polling;
- connector refresh;
- monitoring;
- notifications;
- morning preparation while the primary machine is asleep/off.

A future topology may be:

```text
LOCAL CONTROL PLANE
- Governor / authority
- Continuity
- credentials
- receipts
- user policy
- sensitive memory

OPTIONAL ALWAYS-ON NODE
- schedule runner
- polling/monitoring
- connector refresh
- low-risk read workflows
- notification triggers

REMOTE PROVIDERS / SERVICES
- Google APIs
- Shopify
- OpenAI / Anthropic / Gemini
- web search
```

The always-on node must not become authority merely because it is available continuously.

If Nova becomes a multi-user product, hosted services will likely be needed for account/sync/update
infrastructure, but local authority/control can remain a product principle.

---

## 14. Competitive position

The market is rapidly commoditizing:

- chat;
- memory;
- connected apps;
- daily briefs;
- scheduled tasks;
- background monitoring;
- browser/computer use;
- long-running agents;
- app actions;
- generic personalization.

Nova should not compete feature-for-feature with ChatGPT, Gemini, Copilot, Siri, Claude, Grok, or
other major assistants.

The more defensible direction is:

> **Vendor-neutral operational continuity + explicit authority + evidence-backed outcome truth.**

Nova's strategic advantage is the combination of:

```text
cross-platform operational state
+ commitments / decisions / open loops
+ evidence provenance
+ explicit authority boundaries
+ exact action approvals
+ verified outcomes
+ model/agent replaceability
+ local control
```

Other systems may supply intelligence, apps, models, search, and execution. Nova should own the
coherent operational state and control relationship among them.

---

## 15. Engineering / collaboration posture

Nova is now complex enough that an independent senior engineering review is warranted before the
Google + Continuity phase compounds integration complexity.

The first useful outside review should focus on:

- request-understanding/routing architecture;
- session/orchestration maintainability;
- Semantic Substrate boundaries;
- Governor/ApprovalGrant architecture;
- Google OAuth/security foundation;
- persistence/state/Continuity design;
- what should **not** be refactored.

The recommended collaboration model is not a full team yet:

```text
1. independent senior architecture/security review
2. one bounded paid contribution
3. recurring collaborator only after demonstrated judgment
4. team growth after real user/revenue/production obligations
```

AI-assisted development is not treated as invalid engineering. The important standard is whether
architecture, constraints, tests, failures, tradeoffs, and behavior are understood and can be
explained/reviewed rather than blindly accepted from generated code.

---

## 16. Immediate product-validation sequence

This strategic document does not change current roadmap authority. The recommended product-level
sequence is nevertheless:

```text
1. Finish current semantic/routing stabilization.
2. Reconcile stale human-maintained operational truth surfaces to current main.
3. Complete remaining evidence-backed P2 defects only.
4. Run one clean fresh-main regression checkpoint.
5. Reconcile/harden Google Workspace Foundation onto that checkpoint.
6. Independently review the Google Foundation + request-understanding architecture.
7. Prove identity-only Google connection live.
8. Build/prove Google Tasks READ.
9. Build minimal Continuity.
10. Run a 7–14 day real-life Continuity test.
11. Add Gmail READ as commitment/waiting evidence.
12. Make Today/Attention Continuity-driven.
13. Test with external users.
14. Expand OpenClaw/browser/execution only after product pull is demonstrated.
```

Do not prioritize now:

- broad feature expansion;
- multi-agent architecture;
- broad browser/computer-use;
- more OpenClaw autonomy;
- predictive learning;
- large graph/memory infrastructure;
- SaaS productization before core product proof;
- another architecture redesign unrelated to observed failures.

---

## 17. Core validation test

The next major product threshold is not capability count.

Nova should prove that it can maintain one person's real operational state for at least 7–14 days
and answer accurately, from evidence:

```text
What am I trying to accomplish?
What did I commit to?
What is due?
What changed?
What am I waiting on?
What is blocked?
What did I decide?
What actually executed?
What was verified?
What remains unresolved?
What deserves attention next?
```

If Nova can do this reliably across provider evidence, conversation, project state, and Nova's own
receipts, then it has crossed from a governed AI system into a differentiated personal operations
product.

If it cannot, the response should not be additional capability breadth. The state/continuity and
request-understanding foundations should be corrected until the loop works.

---

## 18. Final direction

Nova should be developed as:

> **A local-first, vendor-neutral personal operations platform whose core governed AI harness
> coordinates replaceable reasoning providers, data sources, capabilities, and actuators while
> Nova itself owns Continuity, evidence, authority, execution truth, and outcome reconciliation.**

The durable hierarchy is:

```text
PRODUCT
Personal Operations System

PLATFORM
Operational State + Continuity + Evidence + Decision + Authority + Outcome

CONTROL PLANE / HARNESS
Local model + OpenAI + Anthropic + Gemini + future providers
Capabilities + APIs + OpenClaw + other actuators
```

The Governor makes Nova safe.
Capabilities make Nova able.
Models make Nova intelligent.
Connectors make Nova informed.
Continuity makes Nova useful across time.
Outcome reconciliation makes Nova trustworthy after action.

The product should now prove that combination rather than continue expanding horizontally.

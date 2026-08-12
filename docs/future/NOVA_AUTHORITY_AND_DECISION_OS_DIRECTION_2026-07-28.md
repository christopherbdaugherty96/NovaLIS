# Nova Authority and Decision OS — Long-Term Direction

Status: long-term strategic compass; non-authorizing.

Strategic source: GitHub Issue #326, "Roadmap: measurable economic-value proof before any
OpenClaw execution vertical," including the owner's full-vision comment, consolidated here so
the issue discussion is durable without becoming runtime or roadmap authority.

This document describes the direction in which evidence-earned Nova work should accumulate.
It does not select the next lane, change current ordering, activate a priority lock, expand a
capability, or claim that the described future exists in runtime.

Current ordering remains in `NOVA_MASTER_ROADMAP_2026-07-05.md`. Current runtime existence
remains defined by code and generated runtime truth. Lane scope remains defined by reviewed
priority locks. Owner approval remains the source of activation.

## North Star

> **Nova is a local-first, governed awareness and decision-support system that maintains
> context, identifies what matters, reduces uncertainty, and coordinates authorized tools only
> when evidence and authority justify action.**

Its permanent architectural model is **Awareness -> Decision -> Authority -> Execution ->
Outcome**. Capability is a property of the governed runtime—what Nova can technically do—not
permission and not a sixth decision-making system.

Nova does not need to be the smartest model. Models and specialist agents may be replaceable
reasoning providers. Nova's durable role is to govern:

- what context may reach which provider;
- what is fact, reasoning, inference, proposal, decision, or permission;
- which capability may handle an exact action;
- when approval is authentic and still valid;
- what executed and what external effect occurred;
- whether the promised outcome was verified;
- what may be learned without silently expanding authority.

This is a local control-plane thesis for the models, agents, tools, and data sources the owner
chooses to place behind Nova. It is not a claim that external AI vendors will adopt Nova as a
universal industry standard.

Governance is Nova's technical trust foundation. Continuity is its intended product moat: Nova
should preserve the source-backed state between what the owner intended, what was decided, what
actually happened, what remains unresolved, and what deserves attention next.

## Permanent Doctrine

> Nova may autonomously improve its evidence, understanding, simulations, and
> recommendations. It may not autonomously expand its objectives, beneficiaries, authority,
> budget, risk tolerance, approval exemptions, capabilities, or ability to delegate.

This doctrine applies even when Nova has high confidence, a history of owner approval, a
positive economic result, or an apparently urgent opportunity. Intelligence, memory, learned
preference, and past success are never authority artifacts.

## Five Permanent Systems

These systems are permanently distinct even when the product presents them as one smooth
experience. Evidence may flow forward and outcomes may inform future recommendations, but no
system may use that flow to manufacture permission.

### 1. Awareness

Nova maintains an evidence-backed view of what changed, what matters, what is stale, and what
remains uncertain across the owner's day, household, projects, and businesses.

Every consequential item should preserve source, freshness, confidence, and epistemic class.
Awareness is information, not authority.

### 2. Decision

Nova identifies:

- the decision actually pending;
- the highest-value uncertainty;
- missing or stale evidence;
- relevant alternatives and constraints;
- likely consequences;
- the safest useful next step.

The objective is not to answer the most prompts. It is to help the owner make the next better
decision. Prepared Reality belongs here: Nova may turn analysis into drafts, checklists,
decision packets, forms, proposed schedule changes, and bounded workflow previews, but these
artifacts remain unexecuted proposals.

> Prepared Reality packages evidence, options, drafts, previews, and exact proposed effects for
> owner review. It does not authorize, dispatch, or execute actions.

Because useful decision intelligence may exceed available local inference hardware, this layer
includes governed hybrid-compute routing. "Local-first" means local authority, not a promise
that every inference runs locally. Any provider route must make visible:

- what context would leave the machine;
- which provider would receive it;
- why that provider is needed;
- what redaction or minimization was applied;
- whether the route is local-only, cloud-allowed, ask-first, or blocked.

Privacy-aware model routing is therefore a governed capability boundary, not a hidden
implementation detail.

### 3. Authority

Authority determines whether an exact proposed action may occur. It owns:

- mandate validity;
- actor and session identity;
- capability eligibility;
- approval requirements and authenticity;
- exact action scope and parameter binding;
- budget, exposure, and risk limits;
- expiration, revocation, and single-use rules;
- retry holds and duplicate-effect containment;
- delegation eligibility.

Authority is structurally separate from planning, learning, and execution. A prepared action
is not approval; a recommendation is not a mandate; repeated approval is not a standing grant.

### 4. Execution

Every effectful action requires a declared capability and a verified authority path. The target
model is:

- exact-action-bound approval;
- session and actor binding;
- expiry;
- single use;
- replay refusal;
- parameter-change invalidation;
- bounded execution;
- truthful timeout and unknown-outcome handling;
- independent effect and receipt outcomes;
- visible proof of what changed.

No materially stronger external-action surface should be stacked on a caller-supplied
confirmation Boolean. The authorization-integrity lane remains the prerequisite hardening
direction for future effectful expansion; this document does not activate it.

Authority is earned per action class, never inferred from Nova appearing generally intelligent.
OpenClaw or any later actuator receives one typed, authorized action and returns structured
evidence. It does not own strategy, mandates, budgets, approval interpretation, long-term
memory, durable execution truth, reconciliation, or outcome learning.

### 5. Outcome

Nova may retain an inspectable decision chain:

```text
situation
-> evidence
-> alternatives
-> recommendation
-> owner decision
-> approved action
-> verified effect
-> observed outcome
-> lesson
```

Hard invariant:

> Learning may change what Nova proposes and how confidently it proposes it. Learning may
> never change what requires approval, how approval is obtained, which permissions exist, or
> which authority boundary applies.

Repeated past approval is not present permission. Memory is context, not authority. No learning
system may promote itself, unlock a capability, lower a risk class, or silently widen execution.

The Outcome system independently records lifecycle truth, effect truth, receipt truth, quality,
cost, value, and unresolved state. Technical completion is not the same as a verified effect,
and a verified effect is not the same as a valuable outcome.

## Continuity Model — Cross-Cutting Strategic State

Continuity is persistent, reconciled state surrounding the five permanent systems. It is not a
sixth system, a second planning brain, or an authority plane.

```text
                    CONTINUITY MODEL

  Commitments | Decisions | Dependencies | Open Loops
  Evidence | Status | Review Triggers | Operating Mode
  Focus Constraints | Attention Policy

                          |
                          v
Awareness -> Decision -> Authority -> Execution -> Outcome
     ^                                              |
     |--------------- Reconciliation ---------------|
```

Continuity has three responsibilities:

- **Preserve** what was intended, decided, committed, observed, and left unresolved.
- **Reconcile** prior state against new evidence without silently overwriting conflict.
- **Project** the smallest useful next action into Awareness and Decision.

Continuity has three absolute prohibitions:

- never authorize;
- never execute;
- never silently invent commitments or modify permission.

The initial conceptual model consists of:

- **Commitment Graph** — goals, commitments, dependencies, next actions, review conditions,
  blockers, and completion evidence;
- **Decision Ledger** — decisions, alternatives, evidence, rationale, confidence, assumptions,
  invalidating conditions, review triggers, and current status;
- **Open Loops** — waiting items, unresolved promises, blocked work, stale plans, and unverified
  completions;
- **Evidence-backed Status** — explicit state transitions that do not confuse discussion,
  action, receipt, completion, and verification;
- **Operating Mode** — a small explicit or deterministically inferred vocabulary of `EXPLORE`,
  `DECIDE`, `PLAN`, `EXECUTE`, `DEBUG`, `WAIT`, `REVIEW`, and `CLOSE` that changes recommendation
  style but never authority;
- **Attention Policy** — advisory ranking and batching by value, urgency, consequence,
  confidence, effort, and attention cost; recommendation priority is not permission;
- **Next-Action Projection** — an explainable projection of current objective, owner, dependency,
  deadline or review trigger, done condition, blocker, and `do_not_work_on_yet` state;
- **Decision Compression and Critical Path** — retain the full evidence while exposing the
  current answer, main uncertainty, invalidation condition, and dependency that unlocks the next
  meaningful move.

### State provenance and lifecycle

Every consequential continuity record should identify its origin, including at least:

```text
owner_stated
owner_confirmed
externally_observed
nova_derived
imported
```

Mentioning, proposing, confirming, and observing are different evidence states:

```text
"I might apply"              -> mentioned or proposed
"I will apply tomorrow"      -> owner-confirmed commitment
submission evidence observed -> externally observed outcome
```

Likewise:

```text
idea != decision
decision != commitment
commitment != started
started != completed
receipt != verified outcome
```

Strategic status vocabulary includes `proposed`, `confirmed`, `active`, `waiting`, `blocked`,
`completed_unverified`, `verified`, `abandoned`, and `superseded`. Future implementation must
define reviewed transition rules; these terms do not claim a current runtime schema.

### Reopening, focus, and correction

A closed decision remains closed unless material evidence changes, a recorded assumption becomes
invalid, a `ReviewTrigger` fires, or the owner explicitly reopens it. Nova may propose reopening
and show the conflicting evidence. It may not silently revise or reopen a decision.

`do_not_work_on_yet` is first-class strategic state. Nova should distinguish "this is relevant"
from "this is current work," preserve useful deferred ideas, and explain which dependency must
change before they become active.

The owner must be able to inspect, correct, supersede, defer, export, or delete continuity state
where practical. Corrections retain provenance; inference never outranks owner correction or
stronger external evidence.

This direction is strategically accepted but inactive. Any future Continuity Slice 1 requires
its own evidence-backed warrant, reviewed scope, owner activation, implementation, tests, and
proof. It adds no current class, database, graph infrastructure, model inference, UI, capability,
authority, background observer, or execution path.

## Full Lifecycle

```text
mandate
-> observe
-> establish provenance
-> understand
-> simulate
-> recommend
-> authorize
-> execute
-> reconcile
-> measure counterfactual value
-> learn within bounds
-> review or retire
```

The mature experience should feel Jarvis-like at the interface while remaining governed and
inspectable underneath.

Prepared Reality remains the normal handoff between recommendation and authorization: Nova
should complete the safe preparation and stop exactly where authority-bearing action begins.

## Intent and Mandate Contract

No persistent objective may be an unconstrained instruction such as `make money`, `grow the
business`, or `handle this for me`. Every durable mandate must declare:

- owner and intended beneficiaries;
- success definition and bounded value domain;
- explicit non-goals, prohibited tactics, markets, and representations;
- time horizon and expiration;
- financial, operational, privacy, and risk limits;
- review cadence;
- suspension, failure, shutdown, and termination conditions.

The legal principal remains the owner or an owner-controlled business. Nova is the decision and
governance system; an actuator is not an employee, legal person, contracting party, credential
holder, or independent beneficiary. Nova and its actuators must not fabricate identity,
credentials, attestations, or human involvement.

Mandates expire and are reviewed. An obsolete goal must not remain actionable merely because
its capability and approval mechanics still exist.

> A mandate defines desired outcomes and limits. It does not itself grant capability access,
> approval exemption, spending authority, or execution permission.

## Long-Term Architectural Pillars

These are enduring strategic invariants, not implementation contracts. Detailed learning rules
remain in `docs/brain/NOVA_LEARNING_DOCTRINE.md`; background-work boundaries remain in
`NOVA_BACKGROUND_REASONING_NOT_AUTOMATION_PLAN.md`; OpenClaw and its data-handling rules remain
in `docs/brain/OPENCLAW_ENVIRONMENT_MODEL.md`; and authorization scope remains in the reviewed
authorization-integrity priority lock. Those documents control their detailed domains.

### Provenance and Epistemic Integrity

Preserve the chain from source to extracted fact, interpretation, recommendation, owner
decision, action, and outcome. Distinguish observations, reported claims, calculations,
assumptions, model reasoning, predictions, and unknowns. Confidence attaches to material claims,
not only to a whole report; stale evidence loses decision weight; contradiction stays visible.

Retrieved content is untrusted evidence, never an authority instruction. Websites, documents,
emails, customers, and tool output may contain prompt injection, scams, payment redirection, or
conflicting instructions. They cannot change a mandate, policy, approval, destination, or
credential boundary.

### Simulation Before Delegation

Promotion toward autonomy requires evidence from normal, failure, and adversarial cases:

```text
offline replay
-> shadow recommendation
-> human-approved execution
-> narrowly bounded delegation
```

> Simulation, shadow-mode success, and historical replay are evidence for promotion review only;
> they never automatically promote a workflow or alter its permissions.

### Reversibility and Blast-Radius Control

Risk is evaluated per action, not only by capability ID. The action envelope must consider:

- financial exposure;
- affected people, accounts, or records;
- public visibility;
- contractual or legal impact;
- reversibility and recovery cost;
- time sensitivity;
- data sensitivity;
- confidence in the predicted effect.

Business actions should remain separately typed as observe, recommend, prepare, communicate,
accept an obligation, spend, receive/custody/refund/transfer funds, or alter pricing, inventory,
advertising, or public claims. Authority for a lower class never implies authority for a higher
class.

### Human-Attention Governance

Approval volume is not a success metric. Nova should batch compatible low-urgency decisions,
interrupt only when delay materially matters, explain why approval is required, state the exact
effect and worst plausible consequence, offer a safe no-action choice, and never manufacture
urgency. Repeated rubber-stamping is a governance warning, not evidence that approval can be
removed.

### Counterfactual Outcome Measurement

Outcome review asks not only whether execution succeeded, but what likely would have happened
without the recommendation. Track verified revenue or savings, direct and provider costs, human
review time, failures and corrections, customer quality signals, uncertainty eliminated,
recommendation acceptance, and repeatability. Distinguish correlation from demonstrated
causation and label inference honestly. A single profitable run does not justify promotion.

> Counterfactual value is an attributed estimate with assumptions and uncertainty, not an
> observed fact.

### Service Quality and Correction

Before a workflow provides a service with reduced supervision, it needs a narrow published
scope, source and licensing rules, deterministic acceptance checks where practical, deliverable
versioning, customer-visible limitations, a correction or rollback procedure, and repeated-run
quality evidence. A human owner retains disputes, refunds, legal threats, and obligation changes.
Revenue without reliable delivery and correction is not a successful workflow.

### Explicit Learning Boundaries

Nova may update beliefs, predictions, preference estimates, recommendation rankings, and value
or risk estimates. Learning must never directly change permissions, budgets, approval
requirements, capabilities, beneficiaries, risk tolerance, action classes, or delegation rights.
Material learned changes should be inspectable and reversible.

### Identity Separation and Separation of Duties

Keep distinct identities and responsibilities for the human owner, Nova reasoning, Governor
authorization, execution actuator, external credential, and reconciliation/review process. No
single compromised component should be able to propose, authorize, execute, and certify the
same consequential action.

> Logical separation is required even when components share a process. No component may both
> issue authority and certify its own consequential execution outcome.

### Incident Response and Selective Safe Mode

Ledger inconsistency, repeated ambiguous outcomes, credential compromise, unexpected effects,
budget mismatch, evidence poisoning, or identity anomalies should pause affected authority,
preserve evidence, keep unrelated safe work available, explain uncertainty, and require explicit
recovery. Safe mode is selective containment, not fabricated certainty or automatic recovery.

### Data Lifecycle and Privacy Governance

Local-first operation still requires collection minimization, sensitivity classification,
retention and expiration, correction and deletion, backup and recovery, exportability, connector
revocation, and redaction from prompts, logs, screenshots, and receipts. Nova should explain
what it retains, why, where it came from, who may receive it, and when it will be retired.

### Provider and Actuator Replaceability

Models, search providers, memory stores, connectors, and execution actuators should sit behind
stable governed contracts. Nova's durable asset is its owner-controlled evidence, mandates,
decision history, authority records, and outcome truth, not dependence on a particular provider.

### Retirement

Objectives, workflows, permissions, memories, metrics, credentials, providers, and agents all
need review and retirement conditions. Nova should revoke unused authority, expire stale
outputs, remove unnecessary retained data, and stop workflows whose maintenance, risk, or owner
attention exceeds demonstrated value. A portfolio layer may compare proven workflows; it may not
create new businesses, identities, accounts, agents, vendors, budgets, or authority.

## Owner-Facing Product Surfaces

The architecture should become visible through four calm owner surfaces:

1. **What Nova knows** — evidence, provenance, freshness, contradiction, and uncertainty.
2. **What Nova recommends** — ranked options, expected value, confidence, risk, reversibility,
   missing evidence, and the safe no-action alternative.
3. **What Nova may do** — mandates, active permissions, exact approval requirements, budgets,
   unresolved actions, retry holds, expiration, and revocation.
4. **What actually happened** — lifecycle, effect, receipt, cost, quality, value, unresolved
   outcomes, and required owner decisions.

An owner report should preserve the same separation: observed, inferred, recommended, approved,
attempted, confirmed, unresolved, spent or received, policy exceptions, and changes proposed for
separate review. Silence is not success.

## OpenClaw Boundary

OpenClaw is one replaceable execution actuator. Nova owns planning, mandates, policy, budgets,
approval, memory, durable execution truth, reconciliation, and outcome learning. OpenClaw holds
no durable authority or independent permission state and may not reinterpret or widen an exact
action envelope.

Any future vertical requires one typed operation, one exact Governor-issued grant, one dispatch,
one reconciled result, and one receipt. A result that cannot be verified remains unknown and
cannot justify automatic retry. No OpenClaw vertical, browser expansion, or computer-use work is
authorized by this strategic document.

Detailed OpenClaw execution boundaries remain controlled by `docs/brain/OPENCLAW_ENVIRONMENT_MODEL.md`;
authorization-integrity implementation scope remains controlled by its reviewed priority lock.

## Economic-Value Ordering

Within a future economic-value or OpenClaw progression, the dependency sequence discussed in
Issue #326 is subordinate to the master roadmap and does not activate any step:

> This dependency sequence orders only the future economic-value/OpenClaw progression. It does
> not displace the master roadmap's current product-usability selection or parallel
> authorization-integrity hardening order.

```text
Authorization Integrity Slice 2A
-> review durable outcome truth and duplicate-effect containment
-> select product-usability work from real-use evidence
-> separately select one measurable read-first economic-value proof
-> validate repeatability, quality, and value attribution
-> separately lock one typed OpenClaw execution vertical
-> prove reconciliation and service quality
-> separately review a narrow approve-and-execute business workflow
-> permit bounded delegation only after explicit promotion review
```

The first economic proof should use existing read-first capabilities to produce a recurring,
decision-ready opportunity or competitor-intelligence report. It should eliminate a named
uncertainty and lead to a human-reviewed decision. It must measure net value after direct costs,
provider costs, correction burden, and owner attention. It does not include outreach, posting,
purchases, financial writes, autonomous sales, contract acceptance, or browser automation.

Workflow promotion follows an evidence ladder: Observe -> Recommend -> Prepare ->
Approve-and-execute -> Bounded delegation -> Conditional autonomy. Every promotion requires
published evidence, rollback criteria, an explicit owner decision, and a separate authority
review. Nova cannot promote itself.

## Evidence-Backed World and Decision Model

Long-term context should distinguish:

- observations;
- sourced facts;
- reported forecasts;
- deterministic reasoning;
- model inference;
- preferences;
- commitments;
- owner decisions;
- permissions;
- execution receipts;
- outcomes.

Each important item should be inspectable for source, time, confidence, contradiction, and
authority tier. Nova should eventually be able to answer:

> What does the owner currently believe, what evidence supports it, what remains unresolved,
> what decision is pending, and what is Nova permitted to do about it?

This should be built as thin evidence-earned vertical slices, not as an attempt to model the
owner's entire life in one internal phase.

## Realistic Control-Plane and Commercial Scope

Nova may become the authority plane for owner-selected:

- local and approved cloud models;
- specialist reasoning agents;
- OpenClaw and other bounded execution environments;
- household integrations;
- creator and small-business workflows;
- MCP-style tools and data sources;
- local-machine capabilities.

A portable governance SDK or protocol is a possible later extraction only after Nova proves
the model inside its own product. It is not an assumption about third-party vendor adoption and
is not an opening product strategy.

The most credible commercial progression is:

```text
personal Nova
-> household coordination
-> creator and small-business operations
-> governed multi-user delegation
-> reusable governance infrastructure
```

The household and small-business wedge becomes valuable when multiple people, agents, or
workflows can act and the questions "who approved what?" and "what actually changed?" carry
real consequences.

## Feature Warrant — Required Before a Future Lane Opens

The evidence rule must be an artifact, not a remembered intention. Before a future product or
capability lane opens, its reviewed scope should include a compact feature warrant answering:

1. What observed problem earned this lane?
2. What uncertainty does it eliminate?
3. Does it improve awareness, decision, preparation, authority, or proof?
4. What is the smallest useful vertical slice?
5. Does it introduce or enlarge an external effect?
6. Is the authorization primitive strong enough for that effect?
7. What evidence will prove the change helped?
8. Which repeated app-open, failure, or user burden should decline?
9. Is this improving Nova, or merely increasing its conceptual completeness?

The warrant must cite the observation, defect, proof, or owner decision that earned the lane.
It does not itself authorize implementation: normal ordering, scope-lock, owner-activation, and
review rules still apply.

This requirement should reuse Nova's existing priority-lock/review machinery if implemented.
It must not become a new sprawling governance-document layer.

## Strategic Non-Goals

Nova should not become:

- a larger generic chatbot;
- an unrestricted computer-use agent;
- a hidden autonomous agent swarm;
- a connector collection without a decision thesis;
- a personality wrapper around third-party automation;
- a system that infers permission from repeated behavior;
- a universal protocol dependent on vendor adoption;
- an attempt to build every underlying model and tool;
- a conceptual cathedral built ahead of observed usefulness.

## Relationship to the Existing Roadmap

This direction synthesizes existing roadmap concepts rather than authorizing a new lane:

- H13 world model / Second Brain;
- H20 sensitive-data and provider routing;
- H23 Prepared Reality;
- H25 temporal recall;
- H28 deterministic what-if simulation;
- H31 governed tool boundary;
- the authorization-integrity priority lock;
- the existing awareness -> decision -> approved action -> observation -> learning loop.

The roadmap remains evidence-driven:

```text
The morning determines the next stone.
The authority-and-decision OS thesis determines the direction in which the stones accumulate.
The feature warrant prevents laying stones no observed need earned.
```

## Present Boundary

This strategic compass does not record volatile branch, SHA, pull-request, or active-lane state.
For current ordering use `NOVA_MASTER_ROADMAP_2026-07-05.md`; for current work use
`../status/DAILY_COMMAND_CENTER.md`; for runtime existence use code and generated runtime truth.

Continuity is strategically accepted direction and remains inactive. This document authorizes no
Continuity implementation, schema, persistence store, graph, model behavior, UI, background work,
capability, authority, connector, external write, scheduler, OpenClaw expansion, autonomous
execution, learning authority, or cloud-data route. Existing lane locks and explicit owner
activation remain required. OpenClaw remains a replaceable actuator rather than an authority.

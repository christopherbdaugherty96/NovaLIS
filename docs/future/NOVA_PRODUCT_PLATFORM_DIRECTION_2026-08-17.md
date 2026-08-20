# Nova Product / Platform Direction — 2026-08-17

Status: consolidated strategic synthesis; non-authorizing.

Wave A2 reconciliation: 2026-08-20, after Wave A1 merged through PR #353 at `f25c798c7cb488495a343068463e9214cab0a763`.

This is the single durable Product / Platform strategy for Nova from the August 2026 review cycle. It consolidates the original direction and the second-pass conclusions. It does not change runtime truth, roadmap ordering, lane scope, capability state, Google scopes, authority, or approval requirements.

Current runtime truth remains defined by code and the evidence/current-truth hierarchy in `docs/CANONICAL/00_INDEX.md`. Current implementation ordering remains defined by the canonical roadmap/current-state surfaces and reviewed lane locks. Owner approval remains the source of activation.

Historical baseline when this direction was first established:

```text
main: e69ca987cd458de8723f1ce9f3885de2de4ec6e8
latest merged PR at original strategy baseline: #352 — keep private Drive searches off public web
```

A2 reconciliation baseline:

```text
main: f25c798c7cb488495a343068463e9214cab0a763
latest merged PR at reconciliation baseline: #353 — Wave A1 operational truth synchronization
```

The original baseline remains provenance for the strategy's creation; the A2 baseline is the current repository state against which this durable strategy was reconciled.

## 1. Product identity

Nova should not be treated as another general-purpose chatbot or autonomous agent.

> **Nova is a local-first, vendor-neutral personal operations platform and governed AI control plane. It consumes evidence from external systems, maintains operational Continuity, uses replaceable local/cloud reasoning providers, separates intelligence from authority, prepares bounded next steps, executes only through governed capabilities, and reconciles verified outcomes back into state.**

Permanent architecture:

```text
Awareness -> Decision -> Authority -> Execution -> Outcome
```

Continuity surrounds the loop as persistent, reconciled operational state.

The product objective is not maximum task throughput. It is to reduce uncertainty, preserve truthful state across time, focus attention, prepare the next useful step, and help close real loops without silently taking authority.

## 2. Product, platform, and harness

Nova is product-wise a **Personal Operations System**, architecturally a **platform**, and internally contains a governed AI **harness/control plane**.

```text
PRODUCT
Personal Operations System

PLATFORM
Operational State + Continuity + Evidence + Decision + Authority + Outcome

HARNESS / CONTROL PLANE
Models + provider routing + capabilities + tools + execution boundaries
```

`AI harness` is an engineering description, not the preferred user-facing identity.

## 3. Local-first means local control, not local-only intelligence

Nova should remain local-first permanently:

> **Local control plane, hybrid intelligence.**

Local/user-controlled state should preferentially own:

- authority and approval policy;
- Continuity and durable operational state;
- credentials/secrets;
- capability policy;
- receipts/ledger;
- local files and sensitive memory;
- provider/data-sharing preferences.

Optional external reasoning may include OpenAI, Anthropic, Gemini, and future providers. Optional actuators/services may include Google APIs, Shopify, web search, OpenClaw, and later browser/computer-use when separately warranted.

Nova does not need to own the smartest model. Models should remain replaceable beneath Nova's state, evidence, authority, and outcome system.

Hard rule:

> **Models advise. Nova governs.**

## 4. Frontier-model escalation and provider neutrality

Large frontier models should be first-class **optional escalation targets**, while local inference remains the default when sufficient.

```text
request
-> deterministic/local handling where sufficient
-> local model when reasoning is needed and sufficient
-> if local is insufficient, evaluate escalation
-> apply privacy / data-sharing / cost / provider policy
-> send bounded/minimized context to an allowed frontier provider
-> return reasoning to Nova
-> Nova retains decision, authority, execution, and outcome truth
```

Provider classes may include:

```text
Local models     -> default routine/private reasoning
OpenAI           -> optional frontier reasoning/coding/analysis
Anthropic        -> optional frontier reasoning/long-context analysis
Gemini           -> optional frontier reasoning/multimodal/Google-adjacent work
Future providers -> replaceable additions behind the same provider contract
```

Provider names are examples, not permanent dependencies. Quality, pricing, privacy characteristics, and capabilities will change.

Future policy should be able to express requirements such as:

```text
local_only
local_preferred
ask_before_cloud
cloud_allowed_for_selected_tasks/data
preferred_frontier_provider
preferred_coding_provider
allowed_data_classes
max_cost_per_request
monthly_provider_budget
fallback order
```

A future `ModelProviderRegistry` / `ModelRouter` may track provider/model capability profile, context limits, privacy/data eligibility, network requirement, latency, cost, preferred task types, availability, and fallback order.

Do **not** implement that broad contract until the provider-routing lane is actually activated. Strategy preserves the requirements; active-lane design should define the real interfaces against then-current provider APIs and Nova state models.

Permanent boundaries:

```text
frontier intelligence != Nova authority
provider tool access != Nova capability grant
provider recommendation != permission to execute
cloud escalation != permission expansion
```

## 5. Local-first economics and cost-aware execution

Nova's architecture should minimize unnecessary recurring frontier-model inference.

> **Use the cheapest sufficient computation for each workflow step while keeping correctness, privacy, truth, and authority ahead of cost optimization.**

Routine work should use deterministic/local execution or local inference when sufficient. Hard, high-context, ambiguous, or quality-sensitive steps may escalate to paid frontier intelligence when the expected value justifies it.

A workflow should not automatically run end-to-end through the most expensive model because one step requires frontier intelligence.

```text
1. classify local files        -> local model
2. move approved files         -> local executor
3. analyze difficult document  -> frontier model
4. prepare proposal            -> local/frontier based on quality need
5. stage email                 -> Nova/local capability
6. send external effect        -> separately governed action path
```

`Local` does not mean literally free. Hardware, electricity, maintenance, storage, APIs, and external services can still cost money. Avoid market claims such as `Nova does what Codex does for free`; provider pricing and capabilities are temporary market conditions.

Durable positioning:

> **Local-first execution for routine work; premium frontier intelligence only when it is actually useful.**

Future metrics may include local completion rate, frontier escalation rate, cost per completed workflow, average frontier cost per user/day, escalation quality improvement, latency, and user overrides. No arbitrary local-completion percentage is assumed in advance.

## 6. Capability and authority remain permanently separate

Capability answers `What can the runtime technically do?`

Authority answers `May this exact action occur now, in this scope, for this actor/session, with these parameters?`

```text
capability != authority
provider access != Nova authority
memory != permission
recommendation != mandate
connection != action permission
```

The governed execution spine remains foundational:

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

Effectful growth should preserve exact-action binding, approval authenticity, bounded execution, receipts, and truthful outcome handling.

## 7. ApprovalGrant and outcome truth

Approval must not degrade into a reusable caller-controlled Boolean.

ApprovalGrant binds approval to the exact action/session/capability and prevents parameter mutation after approval, replay, cross-session reuse, cross-capability reuse, stale approval reuse, and caller-fabricated `confirmed=true` authority.

Nova should also keep execution truth separate from outcome truth.

```text
request accepted != external effect verified
```

`accepted_unverified` exists because Nova may have evidence that an execution request was accepted without sufficient evidence that the intended external effect actually occurred.

Outcome vocabulary should preserve distinctions such as:

```text
rejected
failed
accepted_unverified
verified
unknown
```

Execution answers what Nova attempted. Outcome answers what Nova can prove happened.

## 8. Request understanding is the current architectural pressure point

The Governor/execution architecture is stronger than the natural-language interpretation/source-resolution layer.

Recent defects have clustered around parameter loss, temporal-scope loss, private/public source confusion, route precedence, equivalent word-order variants, follow-up binding, and broad intent being narrowed incorrectly.

Do not replace this with an unconstrained LLM router or perform a big-bang rewrite during stabilization.

Preferred post-stabilization direction:

```text
raw language
-> request understanding
-> typed semantic request
-> source resolution
-> capability resolution
-> Governor
```

Principle:

> **Interpret once, preserve semantics, route deterministically.**

Use deterministic guards for effectful/private/source-sensitive requests, typed normalization for domain/source/time/effect, bounded model classification only for unresolved advisory/read-only ambiguity, and GeneralChat fallback only after governed/private/source-sensitive routes are excluded.

An LLM may suggest a route. It may not manufacture authority.

## 9. Continuity is the primary product moat

Governance is the technical trust foundation. **Continuity is the user-facing moat.**

Memory answers `What does the system know about the user?`

Continuity answers `What is actually going on?`

Continuity should preserve and reconcile goals, commitments, decisions, dependencies, open loops, waiting items, blockers, evidence, status, review/reopen conditions, verified/unverified outcomes, next-action projections, and attention ranking.

It should answer accurately from evidence:

```text
What am I trying to accomplish?
What did I decide?
What did I commit to?
What is due?
What changed?
What am I waiting on?
What is blocked?
What actually executed?
What was verified?
What remains unresolved?
What deserves attention next?
```

Hard boundaries:

- Continuity never authorizes;
- Continuity never executes;
- Continuity never silently invents commitments;
- Continuity never converts learning/history into permission.

The first runtime slice should remain deliberately small: commitments, open loops, waiting items, provenance, and a minimal state vocabulary. No graph database, predictive-learning system, or autonomous extraction is required to prove the value.

## 10. Evidence sources are not product clones

Google Tasks, Gmail, Calendar, GitHub, Shopify, local state, and Nova receipts should primarily feed evidence into Nova's operational state rather than become cloned applications inside Nova.

```text
Google Tasks -> observed commitments
Gmail        -> commitments/deadlines/waiting/counterparty evidence
Calendar     -> temporal commitments/scheduled obligations
GitHub       -> project/action/outcome evidence
Shopify      -> business-state evidence
Nova receipts-> execution/effect evidence
```

Nova owns reconciliation across these sources.

### Google sequencing

Google Workspace should enter Nova as a governed external evidence ecosystem:

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

The preferred first evidence vertical remains Google Tasks READ, followed quickly by minimal Continuity. Gmail READ is a high-value next evidence stream because many commitments and waiting items live in messages rather than task systems.

## 11. Product experience and attention

The product should feel less like `open chatbot, ask question` and more like a persistent operations layer.

Chat remains an interface into state, not the primary persistence model.

The `Today` surface should eventually become the operating front door once real Continuity exists. It should prioritize:

```text
Needs attention
Commitments / deadlines
Waiting items
Blockers
Decisions needing review
Changed since last review
Completed but unverified
3–5 highest-value next attention items
```

Weather/news/traffic remain supporting context.

The scarce resource is attention, not information. Attention ranking may later consider value, urgency, consequence, confidence, effort, dependencies, and interruption cost while remaining separate from authority.

## 12. Prepared Reality bridges decision and action

Nova should not be forced into a binary of `talk` versus `act`.

Prepared Reality lets Nova research, gather evidence, draft, assemble, preview, or stage the next useful action while leaving it unexecuted until the correct authority path is satisfied.

Examples include a follow-up email draft, proposed calendar change, client proposal, task plan, workflow preview, prepared form, or bounded action packet.

Prepared Reality remains non-authorizing and non-executing.

## 13. OpenClaw, Codex, and other agents remain workers/actuators

External workers should not own strategy, durable state, authority, budgets, approval interpretation, long-term memory, or outcome reconciliation.

```text
Nova state / decision / authority
-> typed bounded task
-> worker / actuator
-> structured evidence
-> Nova outcome / reconciliation
```

More OpenClaw/browser autonomy is not the current product priority.

## 14. Deployment direction

Nova does **not** inherently require a remote server.

Near-term deployment should remain local-first. If Nova only needs to operate while the user machine is running, the local application is enough.

An always-on node becomes useful later for reliable scheduling, background polling, connector refresh, monitoring, notifications, and morning preparation while the primary machine is unavailable.

The always-on node must not become authority merely because it is continuously available.

If Nova becomes multi-user, hosted account/sync/update infrastructure will likely be needed, but local authority/control can remain a core product principle.

## 15. Competitive position

Major AI platforms are converging on chat, memory, connected apps, daily briefs, scheduled/background work, browser/computer use, long-running agents, app actions, and generic personalization. Treat these as necessary/commodity capabilities rather than Nova's moat.

Nova should not race ChatGPT, Gemini, Copilot, Siri, Claude, Grok, or future assistants feature-for-feature.

The differentiated thesis is one abstraction higher:

> **Nova maintains the governed operational truth connecting intent -> commitment -> decision -> authority -> action -> verified outcome across whichever models, agents, apps, and providers the user chooses.**

Strategic combination:

```text
Operational Continuity
+ evidence/provenance
+ explicit authority
+ exact-action approval
+ verified outcomes
+ vendor-neutral intelligence
+ local-first execution
+ frontier escalation
+ cost-aware routing
+ local control
```

As external agents become more capable, Nova can become more valuable as the state/authority/control layer coordinating them rather than another competing agent.

The separate Governed Protection Wall concept remains `REFERENCE / LONG-TERM SECURITY / DIGITAL-SOVEREIGNTY EXTENSION` material. It may inform later privacy/data-minimization/security work, but it does not replace this Product/Platform identity, change present roadmap authority, or activate a runtime lane.

## 16. Pursuit decision and investment gates

Nova is worth pursuing, but product-market fit is not established.

Current strategic judgment:

```text
Technical feasibility: high
Core architecture: strong
Governance / trust model: very strong
Market need: real
Competition: extremely high
Generic-assistant differentiation: low
Nova-specific differentiation: plausible
Current product proof: incomplete
Worth continuing: yes
Worth betting everything on today: no
```

The next stage must earn stronger investment through evidence rather than capability count.

Escalate investment when evidence changes:

```text
Gate A — stabilized semantic/runtime behavior
Gate B — real external evidence (Google Tasks, then Gmail/Calendar)
Gate C — minimal Continuity works across days
Gate D — owner 7–14 day Continuity proof
Gate E — 3–10 external users show repeat/voluntary usage
Gate F — users/revenue/production obligations justify recurring team capacity
```

The strongest signal is not that users say the idea is impressive. It is that they return because Nova preserved something important, reduced reconstruction, surfaced the right unresolved item, or helped close a real loop.

If Continuity does not create meaningful daily value, do not compensate by adding more capabilities.

## 17. Engineering collaboration and builder posture

Nova is complex enough that an independent senior engineering/security review is high-value before Google + Continuity compound integration complexity, but a full team is not yet justified.

The first outside review should focus on request understanding/routing, orchestration maintainability, Governor/ApprovalGrant, Google OAuth/security, persistence/Continuity, and what should **not** be refactored.

Recommended collaboration model:

```text
1. independent senior architecture/security review
2. one bounded paid contribution
3. recurring collaborator only after demonstrated judgment
4. team growth after real user/revenue/production obligations
```

AI-assisted development is legitimate when represented transparently and paired with demonstrated understanding. The owner should be able to explain and defend the capability/authority split, execution path, ApprovalGrant, `accepted_unverified`, routing fragility, Google OAuth boundaries, Continuity, and major architectural tradeoffs without pretending to have hand-written every line.

## 18. Product-validation sequence

This strategy does not override current roadmap authority. The canonical operational sequence is maintained by `docs/CANONICAL/07_ROADMAP_TRUTH.md`, the master roadmap, current status surfaces, and Issue #343.

At the Wave A2 reconciliation checkpoint, the sequence is:

```text
1. Wave A1 operational truth synchronization — MERGED through PR #353.
2. Wave A2 strategy reconciliation — this package; strategy only, non-authorizing.
3. Wave B1 runtime-truth instrumentation.
4. Wave B2 capability narration.
5. Wave B3 memory governance.
6. Wave B4 reproducibility hygiene.
7. Wave C: freeze an exact candidate, run semantic/proof stabilization, and record an immutable validated baseline only after required proof passes.
8. Reconstruct/reconcile Google Workspace Foundation PR #335 onto that exact validated baseline; harden/review it and make merge a separate decision.
9. If #335 merges, prove identity-only Google connection live.
10. Build/prove Google Tasks READ as the first provider-backed Google evidence vertical.
11. Only then warrant and build a minimal Continuity runtime slice.
12. Run the 7–14 day owner Continuity proof defined by the validation protocol.
13. Add Gmail READ as commitment/waiting evidence when separately warranted and authorized.
14. Make Today/Attention Continuity-driven after the state model earns that role.
15. Run the 3–10 external-user pilot.
16. Expand providers/agents/OpenClaw/browser execution only after product pull and separate governance gates justify it.
```

This checkpoint list is provenance, not a permanent operational authority. If later current-state/roadmap surfaces change, those current sources win.

Do not prioritize now:

```text
large graph/memory infrastructure
predictive learning
multi-agent orchestration
broad browser/computer-use
expanded OpenClaw autonomy
autonomous business operation
broad SaaS productization
provider marketplace / broad ModelRouter implementation
Protection Wall runtime expansion
```

The detailed future product-proof criteria live in `NOVA_PRODUCT_VALIDATION_PROTOCOL_2026-08-17.md`.

## 19. Documentation and implementation discipline

Generated runtime truth is a strength. Stale human-maintained planning/status surfaces are a project-management defect because AI coding agents can consume them as instructions.

Do not duplicate a competing repository-wide truth hierarchy inside strategy. For implementation/evidence/current-ordering authority, follow `docs/CANONICAL/00_INDEX.md`.

Strategy-specific interpretation rule:

```text
current code establishes implemented behavior
scoped tests/proofs establish only the evidence they actually exercised
generated runtime artifacts establish only mechanically measured claims
current canonical/status/roadmap surfaces establish active ordering
lane locks establish exact authorized implementation scope
strategic/future docs preserve direction but never create authority
```

Older Second Brain, learning, Brain/Daily Brief, agent-workspace, multi-model, economic/OpenClaw, and Protection Wall concepts should remain historical/reference material and be explicitly classified so they do not compete with current direction. See `NOVA_STRATEGIC_DOCUMENT_STATUS_INDEX_2026-08-17.md`.

Implementation contracts should be created **when their lane activates**, not speculatively. Strategy should preserve requirements; active implementation should define schemas/interfaces against current runtime and current provider APIs.

## 20. Final direction

The durable hierarchy is:

```text
PRODUCT
Personal Operations System

PLATFORM
Operational State + Continuity + Evidence + Decision + Authority + Outcome

CONTROL PLANE / HARNESS
Local models + optional OpenAI / Anthropic / Gemini / future providers
Capabilities + APIs + OpenClaw + other bounded actuators
```

The Governor makes Nova safe.
Capabilities make Nova able.
Models make Nova intelligent.
Connectors make Nova informed.
Continuity makes Nova useful across time.
Outcome reconciliation makes Nova trustworthy after action.
Cost-aware local-first routing makes routine operation economically efficient without tying the product to one provider's pricing.

The core product threshold is:

> **Can Nova know what is actually going on, preserve that truth across days, focus attention correctly, and help close real loops without silently taking authority?**

If yes for the owner and then repeatedly for external users, Nova justifies deeper investment. If not, repair the state/request-understanding/product loop rather than expanding horizontally.
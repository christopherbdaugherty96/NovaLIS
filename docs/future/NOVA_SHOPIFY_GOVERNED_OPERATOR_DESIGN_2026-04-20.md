# Nova Shopify Governed Operator Design
Date: 2026-04-20
Status: Future design — not yet implemented
Source: Voice brainstorm session, three-pass review + second-pass improvement

## Purpose

This document defines the full governed integration design for Nova operating as a Shopify storefront operator. It covers read-only intelligence, human-gated action execution, proactive anomaly detection, scenario simulation, social media marketing support, long-term goal refinement, and multi-platform expansion.

Every layer follows the same governing principle Nova applies everywhere:

**Bounded. Explicit. Logged. User-approved before execution.**

---

## Core Governing Principle

Nova should never become an autonomous Shopify operator.

The right model is:

- Nova **reads, analyzes, and proposes**
- You **approve, adjust, or reject**
- Nova **executes only what you explicitly authorize**
- Every step is **logged to the ledger**

This applies at every tier below — reporting, recommending, simulating, executing, and marketing.

---

## Capability Tiers

Nova's Shopify capabilities are explicitly separated into modular tiers. Each tier has its own authority level and its own approval requirement.

| Tier | Name | Nova Authority | User Approval Required |
| --- | --- | --- | --- |
| 1 | Reporting | Read and summarize | No — output only |
| 2 | Recommending | Propose actions | Yes — before any action |
| 3 | Simulating | Model scenarios | No — output only |
| 4 | Executing | Apply approved actions | Yes — explicit per action |
| 5 | Marketing | Draft and schedule content | Yes — before any publish |
| 6 | Goal Refinement | Surface strategic pivots | Yes — governed check-in |

Two cross-cutting capabilities sit across all tiers:

- **Anomaly Detection** — passive monitoring that can trigger alerts at any tier level
- **Feedback Loop** — outcome tracking that follows every Tier 2 recommendation through Tier 4 execution

These tiers must remain modular. Expanding one tier must not silently expand another.

---

## Shopify API Surface Map

This design requires three distinct Shopify API surfaces. They must never be conflated.

### Admin API
Used for: store data reads, inventory, orders, products, pricing, promotions, shipping rules, customer data (aggregate), analytics.
Authority: the primary surface for Tier 1 reporting, Tier 2 recommendations, and Tier 4 execution.
Access model: OAuth with explicit Admin API scopes. Scopes are locked to the minimum required for each tier — read-only scopes are granted first, write scopes only when Tier 4 is activated.

### Storefront API
Used for: product catalog browsing, collection structure, pricing display, cart behavior analysis.
Authority: read-only. Used by Nova when analyzing storefront-facing data, not store operations.
Access model: public Storefront API token. No write access.

### Customer Account API
Used for: customer-account-specific flows — login state, order history per customer, account management.
Authority: kept strictly separate from Admin and Storefront flows. Nova does not mix customer-account concerns into storefront or operations logic.
Access model: separate OAuth flow with Customer Account API scopes only.

These three surfaces are separate connections, separately logged, and separately permissioned. Nova must never route an Admin API concern through the Storefront API or vice versa.

See also: `docs/future/HYDROGEN_OXYGEN_STOREFRONT_BUILD_RULESET_2026-04-12.md` for the same API separation principle applied to Hydrogen storefront build work.

---

## Authentication and Connection Model

Nova's Shopify connection uses OAuth 2.0 through the Shopify Admin API authorization flow.

### Setup flow
1. User initiates connection through Nova's Settings or Agent page
2. Nova presents the OAuth authorization URL with the minimum required scopes for the active tiers
3. User authenticates and approves in Shopify
4. Shopify returns the access token
5. Nova stores the token through the governed identity layer (`src/identity/`)
6. Connection state is surfaced in Nova's Trust and Settings pages alongside other connection states

### Scope management
- Tier 1 (reporting) requires read-only Admin API scopes only
- Tier 4 (execution) requires write scopes — these are only requested when Tier 4 is explicitly activated by the user, not at initial connection
- Scope expansion must be re-authorized through Shopify OAuth — Nova cannot silently expand its own permissions

### Token handling
- Tokens are stored through the governed identity layer, never in plain config
- Token validity is checked before every API call
- Expired or revoked tokens surface as a visible connection error in Trust/Settings — Nova does not silently fail

---

## Data Freshness and Polling Model

Nova's no-hidden-background-execution rule applies here. Data is not fetched silently on a background loop.

### On-demand fetch
The default model. Nova fetches Shopify data when you ask for a report, trigger an anomaly check, or initiate a recommendation cycle. Fresh data, explicit trigger, logged fetch.

### Scheduled fetch (optional)
If you enable a schedule, Nova's existing scheduler carve-out handles it — the same quiet-hours, rate-limit, and policy controls that govern other scheduled operations apply. No special background pathway is created.

### Data retention
Fetched Shopify data is held in session-scoped working context for the current interaction. Summary-level snapshots may be persisted to governed memory if you explicitly save them. Raw Shopify API responses are not stored persistently — they are fetched fresh on each cycle.

### Staleness labeling
Every report surface shows when the data was last fetched. Nova does not present data as current if it is more than one fetch cycle old. If data is stale, Nova says so.

---

## Rate Limiting

Shopify Admin API enforces rate limits (REST: leaky bucket; GraphQL: cost-based). Nova must respect these.

### How Nova handles rate limits
- API calls are paced through the governed network path — not fired in parallel without cost accounting
- If a rate limit is hit, Nova surfaces it as a visible operational notice, not a silent failure
- Nova does not retry rate-limited calls automatically — it reports the limit and waits for your signal
- Bulk data operations (large report pulls) are broken into governed batches with explicit progress reporting

---

## Tier 1: Read-Only Shopify Intelligence

### What Nova does
Nova connects to the Shopify Admin API in read-only mode and generates structured intelligence reports on demand or on schedule.

### Capabilities
- Sales reports: revenue, units sold, order volume, average order value over configurable time windows
- Top products: best-sellers by revenue, by units, by margin where available
- Traffic analytics: sessions, conversion rate, bounce signals, drop-off points in the funnel
- Inventory signals: low-stock alerts, out-of-stock detection, velocity-based restock suggestions
- Customer behavior: repeat purchase rates, new vs returning split, cohort snapshots
- Order health: fulfillment rate, return rate, dispute signals

### Output format
- Structured report with a visible bottom line first
- Supporting data and breakdown visible on request
- Source label showing which Shopify API surface and endpoint produced each data point
- Fetch timestamp on every report — you always know how fresh the data is

### Authority boundary
- Read only — no write, no mutation, no cart or order modification
- All API calls pass through NetworkMediator and are logged
- Storefront API and Admin API are called separately and never mixed

---

## Tier 2: Governed Recommendations

### What Nova does
Nova proposes specific actions based on its intelligence read. It does not execute them. Every recommendation is a proposal waiting for your explicit approval.

### Examples of proposals Nova might surface
- "Top product X has been out of stock for 3 days — recommend restocking"
- "Conversion rate dropped 18% this week — recommend reviewing the checkout flow"
- "Product Y is trending in traffic but has a low add-to-cart rate — recommend reviewing the product page"
- "Shipping threshold is currently $75 — data suggests $50 increases conversion for your average order range"
- "A 15% discount on Category Z for the next 48 hours matches your best-performing past promotion pattern"

### Approval flow
1. Nova surfaces the proposal in the Agent page review surface
2. You see: what Nova is recommending, why, and which data it is based on
3. You approve, adjust, or reject
4. If approved, the recommendation enters a pending execution state in Tier 4
5. If rejected, the rejection is logged with your reason if you provide one

### Approval expiry
An approved recommendation does not remain valid forever. If the underlying conditions change materially before execution (e.g., the product was already restocked by another team member, or the promotion window passed), Nova must re-check conditions before executing and surface any mismatch for your review. Nova does not execute a stale approval against changed conditions.

### Authority boundary
- No action is taken without your explicit approval
- Nova does not execute recommendations autonomously under any condition
- Recommendations that have not been acted on within a configurable window are surfaced again for review or expiry, not silently discarded

---

## Tier 3: Scenario Simulation

### What Nova does
Nova models hypothetical scenarios before any action is taken. This gives you a governed forecast to evaluate before committing.

### Examples
- "What would happen to revenue if you ran a 20% sitewide sale this weekend?"
- "What is the projected impact on margin if you change the free shipping threshold from $75 to $50?"
- "If you added Product Z to the homepage feature slot, what is the estimated traffic uplift based on past feature slot performance?"
- "What does a 10% increase in ad spend on your top channel look like against current conversion rates?"

### How simulations work
- Nova uses your historical Shopify Admin API data as the basis
- It applies the hypothetical change and models the likely outcome range
- It presents the forecast with explicit confidence signals — not false precision
- It shows what assumptions it made so you can inspect and adjust them
- Simulations that produce a high-uncertainty result label that uncertainty clearly — Nova does not present a narrow range when the data does not support one

### Authority boundary
- Simulations are output only — no changes are made
- Nova must label all simulations clearly as projections, not guarantees
- Simulation outputs are logged
- If you approve a simulated action, it moves to Tier 2 as a recommendation first, then to Tier 4 as execution — the simulation does not directly trigger execution

---

## Tier 4: Governed Execution

### What Nova does
Nova applies actions you have explicitly approved from Tier 2.

### Examples of executable actions
- Update a product price
- Apply a discount code or promotion
- Adjust inventory quantities
- Change a product's status (active/draft)
- Update shipping rules within policy bounds
- Modify a collection or product page within approved parameters

### Execution rules
- Every action requires a discrete approval — bulk blanket approvals are not permitted
- Nova presents the exact change it will make before executing, including the specific API call and payload
- You confirm
- Nova executes through the governed Shopify Admin API write path via NetworkMediator
- The action is logged to the ledger: what changed, when, the API surface used, why it was requested, who approved

### Pre-execution condition check
Before executing, Nova re-checks that the conditions at approval time still hold. If something has changed — the product is already updated, the inventory is already restocked, the promotion window has passed — Nova surfaces that mismatch and asks for a fresh approval rather than executing against stale context.

### Failure handling
- If a Shopify API write call fails, Nova reports the failure with the error detail
- Nova does not retry automatically — it surfaces the failure and waits for your instruction
- Partial failures (e.g., a batch update where some items succeed and some fail) are reported item by item — Nova does not present a partial success as full success

### Authority boundary
- Nova cannot execute anything not explicitly approved in the current session
- Nova cannot chain executions without returning to you between each one
- Write API scopes must be explicitly activated by the user before any Tier 4 execution is possible — they are not on by default

---

## Tier 5: Social Media Marketing

### What Nova does
Nova supports your social and marketing operation as a governed content and campaign assistant. It drafts, schedules, and analyzes — but posting remains user-approved.

### Supported platforms (priority order)
1. Instagram — product showcasing, story campaigns, Reels where relevant
2. TikTok — short-form product and brand content
3. X (Twitter) — announcements, promotions, customer-facing communications
4. Pinterest — product discovery and collection boards
5. LinkedIn — brand and operator presence if applicable
6. Facebook — page posts and campaign support

Additional platforms follow the same governed connector model as they are added.

### Brand voice configuration
Before Nova can draft any content, brand voice must be configured. This is not assumed.

Brand voice configuration includes:
- Tone descriptors: how your brand speaks (e.g., direct, warm, playful, premium)
- Topics to avoid
- Terminology preferences and restrictions
- Example posts you consider high quality
- Platform-specific tone adjustments if your voice differs by platform

Brand voice is stored in governed memory, is visible and editable at any time, and is shown alongside every draft Nova produces so you can see what parameters shaped the output.

### Content drafting
- Nova generates social post drafts grounded in your brand voice configuration and your Shopify data (product launches, inventory, promotions, seasonal signals)
- Drafts are tied to a specific product, promotion, or campaign context — not generic content
- Nova produces variants: short form, long form, story format, caption-only, platform-native formats
- All drafts are presented for your review before any scheduling or publishing
- Drafts include Nova's reasoning: why this product, why this angle, why now

### Content calendar
- Nova maintains a governed content calendar
- It suggests timing based on engagement pattern analysis from your past content and platform-level signals
- You approve the calendar before it becomes active
- Nova does not post on its own schedule — only on the schedule you have explicitly approved
- Calendar changes (adding, removing, rescheduling posts) require your approval

### Campaign planning
- Nova proposes campaign ideas tied to your Shopify data: upcoming inventory, seasonal patterns, sales history, anomaly signals
- Each campaign proposal includes: objective, target audience, platform, content format, proposed timeline, and expected outcome range
- You approve, adjust, or reject each proposal before Nova acts on it
- Campaign execution follows the same per-action approval model as Tier 4

### Engagement analytics
- Nova reads engagement metrics from connected social platform APIs
- It reports: what is working, what is not, what changed week over week, which content types drove the most Shopify traffic
- It ties social performance back to Shopify conversion data where the signal exists
- It does not invent correlations — if the signal is not clear, Nova says so

### Posting execution
- Nova can post to approved platforms when you explicitly authorize a specific post
- You see the exact content, the exact platform, the exact account, and the exact time before Nova publishes
- Nova does not publish autonomously
- Every publish action is logged: content, platform, time, approval reference

### Authority boundary
- Nova does not post, comment, reply, or boost without explicit per-action approval
- Draft generation is output only and requires no approval
- Publishing requires explicit per-post approval — no scheduled batch publish without per-post review
- Nova does not engage with comments or direct messages without explicit instruction

---

## Tier 6: Long-Term Goal Refinement

### What Nova does
Nova periodically surfaces structured strategic check-in sessions to help you evaluate whether Nova's current operating parameters still match your business goals.

### What a goal refinement session covers
- Are the current reporting priorities still the right ones?
- Have your business goals shifted — new regions, new product categories, new channels?
- Are the current recommendation thresholds still calibrated to your strategy?
- Do the current execution permissions still match your risk tolerance?
- Should any capability be expanded, constrained, or paused?
- Is Nova's brand voice configuration still accurate?
- Are the anomaly detection thresholds still calibrated correctly?

### How it works
- Nova surfaces a goal refinement prompt on a schedule you set, or on demand
- The session is a structured conversation: Nova presents what it currently understands your goals and parameters to be, and asks you to confirm, adjust, or redirect
- Changes to Nova's operating parameters from this session are logged as policy updates with a timestamp and reason

### Authority boundary
- Nova does not change its own operating parameters
- Parameter changes require your explicit confirmation during the refinement session
- All changes are logged and visible in the Trust page

---

## Cross-Cutting: Proactive Anomaly Detection

Anomaly detection is not a separate tier — it is a monitoring layer that runs across Tier 1 data and can surface alerts that feed into Tier 2 recommendations or direct your attention without triggering any action.

### What Nova monitors
- Traffic drops more than a configurable threshold day over day or week over week
- A product suddenly spikes in traffic but conversion is declining
- Revenue is tracking significantly below the rolling average for this time period
- A top product goes out of stock
- Cart abandonment rate moves outside normal range
- Order volume anomaly — could indicate a fraud pattern, a viral event, or a fulfillment problem
- A social post drives unusual inbound traffic — positive or negative signal

### Alert format
- Nova surfaces the alert with: what happened, when, what the normal baseline was, and how significant the deviation is
- Nova asks: do you want to review this, or dismiss it?
- If you want to review, Nova produces a full drill-down Tier 1 report
- If you dismiss, the dismissal is logged with the timestamp

### Threshold configuration
- Alert thresholds are configurable: you set what counts as a meaningful deviation for your store
- Default thresholds are conservative — Nova alerts less rather than more until you calibrate them
- Threshold changes are logged

### Authority boundary
- Alerts are output only
- Nova does not take any action in response to an anomaly without your explicit approval
- Anomaly detection does not create background polling — data is checked at scheduled fetch intervals or on demand

---

## Cross-Cutting: Feedback Loop

The feedback loop tracks whether Nova's recommendations are actually working. It is not a tier but a quality layer that follows every Tier 2 → Tier 4 execution.

### How it works
1. After a recommendation is approved and executed, Nova logs the approval and execution
2. At the next relevant data fetch (or on demand), Nova compares the actual outcome to the projected outcome from the Tier 3 simulation or recommendation rationale
3. It surfaces a plain outcome report: "You approved this change — here is what happened"
4. You can optionally rate the recommendation: useful, not useful, or wrong

### What Nova does with feedback
- Over time, Nova surfaces patterns in its own recommendation track record: which recommendation types have been reliable, which have been off
- This is presented as a visible audit, not silent model adjustment
- You can review the full recommendation history and outcome record at any time
- Nova does not use feedback to autonomously adjust its own behavior — feedback informs your view and informs Nova's reasoning in future recommendations with your awareness

---

## Transparency Requirements

Every Nova action in this integration must meet Nova's standard transparency requirements:

- **Source visible**: Nova shows which Shopify API surface and endpoint produced each insight
- **Reasoning visible**: Nova explains why it is recommending something — the data chain, not just the conclusion
- **Confidence visible**: Nova labels projections as projections, uncertain signals as uncertain, and does not present narrow ranges when the data does not support them
- **Boundary visible**: Nova states what it cannot or will not do without approval
- **Log visible**: every fetch, recommendation, approval, rejection, execution, and publish is in the ledger and reviewable from the Trust page

---

## Capability Registry Integration

This integration will require new governed capability entries in Nova's capability registry.

Planned new capabilities (to be formally registered and locked through the existing P1-P6 verification process):

| Capability Name | Tier | Write | Notes |
| --- | --- | --- | --- |
| shopify_intelligence_report | 1 | No | Read-only Admin API report generation |
| shopify_anomaly_alert | Cross | No | Anomaly monitoring and alert surface |
| shopify_recommendation | 2 | No | Proposal generation, no execution |
| shopify_simulate | 3 | No | Scenario modeling, output only |
| shopify_execute | 4 | Yes | Governed write actions, per-action approval |
| shopify_social_draft | 5 | No | Content draft generation |
| shopify_social_publish | 5 | Yes | Governed posting, per-post approval |
| shopify_goal_refinement | 6 | No | Strategic check-in surface |

Each capability follows the standard P1-P6 verification path before being marked live:
- P1 Unit, P2 Routing, P3 Integration, P4 API, P5 Live sign-off, P6 Lock

Write capabilities (shopify_execute, shopify_social_publish) require explicit user activation before their scopes are requested from Shopify OAuth.

---

## Hydrogen and Oxygen Storefront Connection

This operator design and the Hydrogen/Oxygen storefront build ruleset are related but separate.

- The **storefront build ruleset** (`HYDROGEN_OXYGEN_STOREFRONT_BUILD_RULESET_2026-04-12.md`) governs how Nova reviews and proposes changes to the storefront codebase — it is a code review and operator standard.
- The **operator design** (this document) governs how Nova interacts with your live Shopify store data and operations at runtime.

When Nova is operating at full depth, both apply:
- Nova reviews storefront code against the Hydrogen ruleset before proposing deployment
- Nova monitors live store performance through this operator design after deployment
- The two surfaces close a loop: build quality governs what ships, runtime intelligence governs what happens after it ships

---

## Data Privacy and Storage

### What Nova stores
- Session-scoped: raw Shopify API responses are held in working context for the current session only
- Governed memory: summary-level snapshots (e.g., a weekly sales summary) may be persisted to governed memory if you explicitly save them through the standard `save this` flow
- Ledger: every API call, recommendation, approval, and execution is logged — this is audit data, not operational data

### What Nova does not store
- Raw customer PII from Shopify (names, addresses, payment data) is not persisted to Nova's memory under any condition
- Full order-level detail is not stored — aggregate signals only unless you explicitly instruct otherwise

### Retention
- Session data expires at session end
- Governed memory follows Nova's standard memory governance (editable, exportable, deletable by you)
- Ledger entries are append-only and not deleted

---

## Multi-Platform Expansion

This design is intentionally scoped to Shopify first. As Nova's connector layer expands, the same governed model applies to:

- Other e-commerce platforms (if you expand beyond Shopify)
- Social commerce channels (Instagram Shopping, TikTok Shop, Pinterest Shopping)
- Email marketing platforms (governed campaign drafting and send approval)
- Paid advertising platforms (governed budget proposals and creative drafts)
- Inventory and fulfillment systems beyond Shopify's native tools
- Analytics platforms (unified cross-channel performance view)

Each new platform connection must go through the same governed connector process: explicit OAuth or API key setup, minimum-required scopes, explicit permissions surfaced in Trust and Settings, and full logging.

---

## Human Skill Development

Nova's involvement in your Shopify operation should strengthen your strategic judgment, not replace it.

### How Nova supports this
- Nova explains its reasoning on every recommendation — the data chain, the assumption, the confidence level
- Nova surfaces the underlying data so you can build your own read of the business, not just consume Nova's summary
- Nova flags when a decision is genuinely ambiguous — it does not manufacture false confidence to appear more useful
- Nova's goal refinement sessions are structured to prompt your strategic thinking, not just confirm Nova's current parameters
- Nova surfaces its own track record through the feedback loop so you can judge whether to weight its recommendations more or less heavily over time

### The right outcome
You should become a better Shopify operator because Nova is surfacing better data and explaining its reasoning — not a passive approver of Nova's decisions.

---

## Implementation Sequence

When this is built, the right order is:

1. **Shopify OAuth connection** — Admin API read-only scopes, token storage through `src/identity/`, connection state in Trust/Settings
2. **Connector package registration** — extend `src/connectors/package_registry.py` and `src/config/connector_packages.json` with the Shopify connector manifest
3. **Reporting surface** — on-demand sales, product, traffic, and inventory reports via Admin API; Tier 1 capability registered and P1-P4 verified
4. **Anomaly detection** — configurable threshold monitoring, alert surface in Agent page
5. **Recommendation engine** — governed proposals with explicit approval flow, Tier 2 capability registered
6. **Scenario simulation** — forecast modeling tied to historical Admin API data, Tier 3 capability registered
7. **Execution lane** — Shopify Admin API write path, write OAuth scopes added as optional activation, per-action approval UI, Tier 4 capability registered and P5 sign-off required before live
8. **Social marketing layer** — brand voice config, draft generation, content calendar, per-post publish approval, Tier 5 capabilities registered
9. **Feedback loop** — outcome tracking and recommendation quality rating surface
10. **Goal refinement sessions** — governed strategic check-ins on a user-set schedule, Tier 6 capability registered
11. **Multi-platform expansion** — additional connectors through the same governed model, each following the full P1-P6 process

No step in this sequence should be skipped to move faster. Each step builds the trust foundation for the next. Write-capable tiers (4 and 5) must not be activated until the read-only tiers they depend on have passed P5 live sign-off.

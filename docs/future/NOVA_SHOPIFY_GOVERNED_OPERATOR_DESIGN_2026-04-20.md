# Nova Shopify Governed Operator Design
Date: 2026-04-20
Status: Implementation started — connector interface stub complete; registry and executor work in progress
Source: Voice brainstorm session — seven improvement passes

## Architecture in Three Layers

Before the details: the full design resolves into three layers. Every section below belongs to one of them.

| Layer | What it does | Capabilities |
| --- | --- | --- |
| **Intelligence** | Read, research, monitor, report | 65, 66, 72, 75 (KPI brief is a composed view of 65+66+72) |
| **Decisions** | Recommend, simulate, refine goals | 67, 68, 73 |
| **Operations** | Execute, publish, play back | 69, 70, 71, 74, 76 |

Intelligence flows into Decisions. Decisions flow into Operations. Operations feed back into Intelligence through the Feedback Loop. Nova can be used at any layer independently — you do not have to activate Operations to benefit from Intelligence.

---

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

Four cross-cutting capabilities sit across all tiers:

- **Anomaly Detection** — passive monitoring that can trigger alerts at any tier level
- **Feedback Loop** — outcome tracking that follows every Tier 2 recommendation through Tier 4 execution
- **Competitive Intelligence** — read-only market awareness using Nova's existing governed research lane, separate from Shopify Admin API
- **SOP / Playbook Engine** — persisted, named, user-approved sequences of Tier 2 recommendations that can be re-triggered as governed workflows

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

### GraphQL vs REST
Shopify is actively deprecating its REST Admin API in favor of GraphQL. Nova's Shopify integration uses the **GraphQL Admin API as primary**. REST endpoints are only used where a GraphQL equivalent does not yet exist for the required operation. All GraphQL queries follow the conventions in the Hydrogen build ruleset: `#graphql` tagged literals, `as const`, `@inContext(...)` for market-aware queries, fragment reuse over copy-pasted field selections.

See also: `docs/future/HYDROGEN_OXYGEN_STOREFRONT_BUILD_RULESET_2026-04-12.md` for the same API separation principle applied to Hydrogen storefront build work.

---

## Authentication and Connection Model

Nova's Shopify connection uses OAuth 2.0 through the Shopify Admin API authorization flow.

### Development store first
Before Nova's Tier 4 execution is ever tested against a live store, it must first be validated against a Shopify development store. Shopify provides free development stores through the Partner program that are functionally identical to live stores but carry no real inventory or customer data risk.

The implementation sequence enforces this: Tier 4 execution does not pass P5 live sign-off until it has been exercised end-to-end against a development store with all write flows confirmed working correctly.

### Setup flow
1. User initiates connection through Nova's Settings or Agent page
2. Nova presents the OAuth authorization URL with the minimum required scopes for the active tiers
3. User authenticates and approves in Shopify
4. Shopify returns the access token
5. Nova stores the token through the governed identity layer (`src/identity/`)
6. Connection state is surfaced in Nova's Trust and Settings pages alongside other connection states

### Scope management
Tier 1 (reporting) requires the following read-only Admin API scopes:
- `read_orders` — order history, revenue, fulfillment, returns
- `read_products` — product catalog, variants, inventory levels
- `read_inventory` — inventory quantities across locations
- `read_analytics` — Shopify analytics data (sessions, conversion, funnel)
- `read_price_rules` — existing discount and promotion rules
- `read_shipping` — shipping profile and rate configuration

Tier 4 (execution) adds write scopes — only requested when Tier 4 is explicitly activated by the user:
- `write_products` — product and variant updates
- `write_inventory` — inventory quantity adjustments
- `write_price_rules`, `write_discounts` — promotion and discount creation/modification
- `write_shipping` — shipping rule changes

Scope expansion must be re-authorized through Shopify OAuth — Nova cannot silently expand its own permissions. The user sees the scope list at each authorization step.

### API version
Nova pins to a specific Shopify Admin API version (e.g. `2025-04`) rather than using `latest` or `unstable`. The pinned version is updated intentionally, not automatically — an API version bump is a deliberate change that must be tested. The active version is surfaced in the connector's health check output so it is visible in Trust and Settings. When Shopify deprecates a version, Nova surfaces a visible upgrade prompt before the cutoff date — it does not silently fail when a deprecated version is removed.

### Token handling
- Tokens are stored through the governed identity layer, never in plain config
- Token validity is checked before every API call
- Expired or revoked tokens surface as a visible connection error in Trust/Settings — Nova does not silently fail
- If a token is revoked mid-session during an active operation, Nova surfaces the revocation immediately, halts any pending executions, and does not attempt to complete them with stale credentials

### Future: Shopify Partner app model
This design assumes single-merchant access (your store). If Nova is later offered as a tool for multiple merchants, it would need to be a Shopify Partner app using the Partner OAuth flow with per-merchant token management. That is a different auth architecture and a separate design decision — noted here so the single-merchant model does not accidentally foreclose it.

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

Shopify Admin API enforces rate limits (GraphQL: cost-based query budget; REST: leaky bucket — legacy only). Nova must respect these.

### How Nova handles rate limits
- GraphQL calls track their cost against the query budget before sending — expensive queries are split rather than sent and rejected
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
- Traffic analytics: sessions, conversion rate, bounce signals, drop-off points in the funnel — sourced from Shopify's native analytics; note that Shopify's traffic analytics do not capture UTM-level attribution with the same fidelity as GA4 or Meta Pixel — if you use those tools, they are the more accurate source for paid-channel attribution
- Inventory signals: low-stock alerts, out-of-stock detection, velocity-based restock suggestions
- Customer behavior: repeat purchase rates, new vs returning split, cohort snapshots
- Order health: fulfillment rate, return rate, dispute signals
- Market-aware reporting: if Shopify Markets is active on your store, reports can be scoped to a specific market or region — Nova uses `@inContext(country:, language:)` on market-sensitive queries and labels all outputs with the market context used

### Reporting periods
All Tier 1 report requests accept a `period` parameter scoped to one of four windows:
- `today` — current calendar day
- `last_7_days` — rolling 7-day window
- `last_30_days` — rolling 30-day window
- `last_90_days` — rolling 90-day window

Default is `last_7_days`. Period is shown on every report output so you know the window the data covers.

### Connector data contract
The Tier 1 connector interface produces a `ShopifyStoreSnapshot` — the primary data structure for capability 65 and the KPI Command Center brief. It contains:
- `shop_domain` and `shop_name` — store identity
- `orders` — `ShopifyOrderSummary`: order count, total revenue, currency, average order value, period label, fetch timestamp
- `products` — `ShopifyProductSummary`: total, active, draft, out-of-stock count, low-stock count, fetch timestamp
- `market_context` — populated when `@inContext` was applied to the query (e.g. `"US/en"`)
- `fetched_at` — ISO 8601 UTC timestamp for the full snapshot
- `error` — non-empty if the fetch partially failed; Nova surfaces this rather than presenting incomplete data as complete

The interface lives in `src/connectors/shopify_connector.py`. This stub is the implementation contract — executors and the API layer build against it.

### Output format
- Structured report with a visible bottom line first
- Supporting data and breakdown visible on request
- Source label showing which Shopify API surface and endpoint produced each data point
- Fetch timestamp on every report — you always know how fresh the data is

### KPI Command Center (daily executive brief)
The KPI Command Center is a composed Tier 1 output — not a new capability, but a structured view that aggregates signals from across all active capability 65 reports into a single daily cockpit surface.

What it shows:
- **Revenue today** vs yesterday and the rolling 7-day average
- **Conversion rate** current vs baseline
- **Top SKU** by revenue and by units today
- **Low inventory** — products below configured restock threshold
- **Traffic anomalies** — any signals from the anomaly detection layer since last review
- **Pending approvals** — count and summary of Tier 2 recommendations awaiting your decision
- **Last social performance** — engagement summary for the most recent published content

Each signal area carries a visible status state:

| State | Meaning |
| --- | --- |
| **Healthy** | Within normal range, no action indicated |
| **Watch** | Moving outside normal range but not yet at threshold |
| **Action Needed** | Threshold crossed — Nova has surfaced a Tier 2 recommendation |
| **Pending Approval** | A recommendation has been approved and is awaiting execution |

The status model makes the brief decision-oriented rather than just data-oriented. Opening the Command Center answers one question first: is anything actually requiring my attention right now?

The Command Center is the recommended daily entry point for Nova's Shopify operator mode. You open it, scan the status column, drill into anything marked Watch or above, and either approve the surfaced recommendation or dismiss it with a reason. It does not take any action — it is a governed status surface, nothing more.

The brief lives in the Agent page as a dedicated Shopify operator card — the same surface used for OpenClaw home-agent briefings. This keeps all governed operator outputs in one place. The brief can be delivered on a schedule (same scheduler infrastructure as existing reminder and briefing lanes) or on demand. All fetches are logged.

The connection health state shown in the brief (connected / disconnected / token expired / scope mismatch) comes from the connector's `health_check()` method, which returns `ok`, `label`, and `shop` at minimum. A stale or revoked token surfaces as a visible error on the brief card, not a silent empty report.

### Third-party app data boundary
Shopify's Admin API surfaces only data that lives inside Shopify's platform. Data held in third-party apps — email lists in Klaviyo, subscription data in Recharge, loyalty points in LoyaltyLion, review data in Yotpo — is not accessible through the Shopify Admin API. Nova's Tier 1 reporting covers Shopify-native data only. If you want Nova to surface third-party app data, those platforms need their own governed connector entries and their own OAuth authorizations. Nova must never present a reporting gap as if the data does not exist — if a signal is outside the Shopify Admin API surface, Nova labels that boundary explicitly.

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

### What "adjust" means
Adjusting a recommendation means changing one or more of its parameters before approving it — for example, changing a proposed 20% discount to 15%, or narrowing the scope from sitewide to a single collection. Nova surfaces the adjustable parameters for the specific recommendation type and accepts your change. An adjusted recommendation is treated as a new proposal: Nova re-presents the full adjusted version and requires a fresh explicit approval before it enters a pending execution state. Adjusted recommendations are logged with both the original Nova proposal and your modified version so the record is clear.

Nova defines the adjustable parameters for each recommendation type at implementation time — they are not open-ended. Parameters that Nova cannot safely validate the impact of are not exposed as adjustable inputs without a Tier 3 simulation.

### Approval expiry
An approved recommendation does not remain valid forever. If the underlying conditions change materially before execution (e.g., the product was already restocked by another team member, or the promotion window passed), Nova must re-check conditions before executing and surface any mismatch for your review. Nova does not execute a stale approval against changed conditions.

### Pending approval persistence
Approved recommendations that have not yet been executed are persisted across session boundaries — they survive Nova restarting or the session ending. Pending approvals are stored in Nova's governed memory layer (a dedicated `shopify_pending_approvals` memory domain, not general memory) so they are visible, inspectable, and manageable from the Memory page. On next session start, Nova surfaces any pending approvals for your review before proceeding. You can confirm, adjust, or rescind them. Nova does not silently execute a pending approval that was made in a prior session without surfacing it first in the new session.

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

### Rollback and undo
After a Tier 4 execution completes, Nova retains a governed record of the exact change made (the before state and the after state where the API surfaces this). If you want to reverse an executed action, Nova can propose a reversal as a new Tier 2 recommendation — the same approval flow applies in reverse. Nova does not undo autonomously.

For actions where Shopify does not expose a direct API reversal (e.g., a sent notification), Nova surfaces that constraint explicitly and does not suggest a rollback path it cannot deliver.

### Shopify Flow boundary
Shopify has a native automation platform called Shopify Flow. Nova does not interact with, trigger, or modify Shopify Flow workflows. If a Tier 4 execution action would overlap with an active Shopify Flow trigger for the same resource (e.g., both Nova and a Flow rule would respond to an inventory threshold event), Nova must surface that potential conflict at recommendation time and require explicit confirmation before proceeding. Nova does not suppress or disable Shopify Flow behaviors — it operates alongside them and makes any overlap visible to you.

### Authority boundary
- Nova cannot execute anything not explicitly approved in the current session or a persisted pending approval confirmed in the current session
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

### Social platform authentication model
Each social platform is a separate OAuth connection with its own governed connector entry. None of them share the Shopify OAuth token. Platform-specific requirements:

- **Instagram / Facebook**: Requires a Meta Business account and a Facebook Page linked to an Instagram Professional account. OAuth is through Meta's Graph API. Write access (publishing) requires the `pages_manage_posts` and `instagram_content_publish` permissions — these are not granted at initial connection and must be explicitly activated when Tier 5 publishing is enabled. Meta's API review process may require Nova's publishing surface to be submitted for app review before it can post on behalf of your account.
- **TikTok**: Requires a TikTok for Business account. OAuth is through the TikTok Marketing API. The publishing API is available for verified business accounts but has tighter rate limits than Meta. TikTok's API terms restrict certain content categories — these constraints must be surfaced to you in the draft review, not filtered silently.
- **X (Twitter)**: The write-capable X API (posting) is currently behind X's paid Basic tier or higher. This is a cost that the implementation must surface clearly — Nova's X publishing capability cannot be enabled without a paid X API subscription. Read-only access (engagement metrics) is available on the free tier.
- **Pinterest**: Requires a Pinterest Business account. OAuth is through the Pinterest API v5. Organic pin publishing is available on the business tier.
- **LinkedIn**: Requires a LinkedIn Company Page. OAuth is through LinkedIn's Marketing API. Organic posting requires the `w_organization_social` scope.

Every social connection state (connected, disconnected, scope mismatch, API tier insufficient) is surfaced in Nova's Trust and Settings pages alongside the Shopify connection state. None of these platforms can be used for publishing without explicit per-platform activation by you.

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

### Image and media handling
Social posts require imagery. Nova's approach:
- Nova pulls existing product images from the Shopify Admin API (product media, variant images, collection images) and attaches them as candidates to the draft for your selection
- Nova does not generate images autonomously — image selection or creation is your decision
- If no suitable Shopify product image exists, Nova flags the gap in the draft and prompts you to supply an image before the post can be published
- Video and Reel content: Nova can draft the script and caption, but video production remains outside Nova's scope — it surfaces the draft alongside a note that video asset creation is required
- All media attached to a post is logged with the post record

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

### Email marketing extension
Email marketing (Klaviyo, Mailchimp, Shopify Email) is a planned Tier 5 extension (capability 74 — shopify_email_campaign), not part of the initial social media scope. When added, it follows the same model: Nova drafts campaigns tied to Shopify data signals, you approve content and send timing, Nova executes the send only on explicit per-send approval. Email sends are irreversible once dispatched — the approval gate for email is therefore treated as high-consequence and will require an explicit confirmation step beyond the standard approval flow. Klaviyo and Mailchimp data (subscriber lists, campaign history, open rates) are not accessible through the Shopify Admin API — they require their own governed connector entries and separate API authorizations.

### Authority boundary
- Nova does not post, comment, reply, or boost without explicit per-action approval
- Draft generation is output only and requires no approval
- Publishing requires explicit per-post approval — no scheduled batch publish without per-post review
- Nova does not engage with comments or direct messages without explicit instruction
- Nova does not select or attach media without presenting the selection to you first

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

### Shopify webhooks (enhancement path)
Polling alone is slow for anomaly detection — a traffic spike or sudden out-of-stock event can happen between fetch cycles. The enhancement path is Shopify webhook subscriptions: Shopify pushes event notifications to Nova's governed bridge endpoint when defined events occur (orders created, inventory updated, product status changed, etc.).

Webhooks are not part of the initial implementation — they require an inbound endpoint that is reachable from Shopify's servers, which adds infrastructure requirements. They are listed here as the planned improvement to anomaly detection latency once the base polling model is proven.

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

## Cross-Cutting: Competitive Intelligence

Competitive intelligence is not a Shopify-connected capability — it uses Nova's existing governed web research lane (capabilities 16 and 48) to monitor publicly visible competitor signals. It does not touch Shopify Admin API and does not require additional OAuth.

### Signal categories
Competitive signals are split into five independently configurable categories. You enable only the ones that matter for your operation.

**Pricing changes** — competitor product pricing on public storefront pages. Nova detects price cuts, price increases, and bundle/threshold changes. Surfaced as: changed from X to Y on [date], source.

**New products** — catalog additions or launches detected through public storefront crawls and press/review signals. Surfaced as: new product detected in [category] on [date].

**Review sentiment** — what customers say about competitors at scale. Recurring complaints, top praise themes, rating trends. Surfaced as: sentiment shift detected — [theme] appearing more frequently since [date].

**Ad and creative changes** — changes in ad creative or copy visible through public ad libraries (Meta Ad Library, TikTok Creative Center). Surfaced as: new ad creative detected in [category], [date].

**Promotions** — public discount events, seasonal sales, referral programs, and threshold-based offers. Surfaced as: promotion detected — [description], active since [date].

Each category has its own monitoring frequency setting and can be enabled or disabled independently. Nova does not conflate signal types — a pricing change report does not include review sentiment unless you request the combined view.

### What Nova does not do
- Nova does not access non-public competitor data — no login-required areas, no API scraping, no private channels
- Nova does not fabricate competitive insight — if public signal is thin, Nova says so rather than inventing a narrative
- Nova does not make competitor claims without sourcing — every competitive observation includes the source and the date of the observation

### Output format
- Regular competitive brief (on schedule or on demand): what changed, what is trending, where you appear to be priced above or below the market
- Source-labeled: every data point shows where it came from
- Bottom line first: the one most actionable signal for your category this week

### Connection to Tier 2
When a competitive signal suggests a response — a competitor dropped price, a category trend is emerging — Nova can link the competitive brief directly to a Tier 2 recommendation. Example: "Competitor X reduced price on [product category] by 12% this week. Based on your current pricing and margin data, here is a governed recommendation if you want to respond." The recommendation requires the same explicit approval as any other Tier 2 proposal.

### Authority boundary
- All competitive intelligence is read-only web research
- Nova does not interact with competitor platforms in any way that could be construed as automated access
- Competitive briefs are logged as governed research outputs

### Planned capability
Capability 75 — shopify_competitive_intel — registered as a governed research output using the existing research infrastructure. No write authority. Depends on Nova's existing web research capabilities (16, 48) passing live sign-off first.

---

## Cross-Cutting: SOP / Playbook Engine

A playbook is a named, persisted, user-approved sequence of Tier 2 recommendations that can be re-triggered as a governed workflow. It is not automation — every individual action in a playbook still requires your per-action approval at execution time. The playbook is a way to avoid rediscovering the same sequence of decisions every time a known situation recurs.

### What a playbook is
A playbook captures a decision pattern you have already approved and executed successfully. Instead of Nova re-deriving the full recommendation set each time, you can invoke the playbook by name and Nova pre-loads the sequence of proposals for your review and approval.

Each playbook surfaces the following metadata before you trigger it:

| Field | What it shows |
| --- | --- |
| **Steps** | The ordered list of capabilities this playbook invokes, viewable before running |
| **Estimated approvals** | How many per-step approval prompts to expect |
| **Estimated time** | Approximate time to complete if all steps are approved (based on prior runs) |
| **Last run** | Date, how many steps were approved vs skipped vs adjusted |
| **Last outcome** | The bottom-line result of the most recent run |

Playbook templates are fully editable. Editing a template triggers the same define-review-approve cycle as creating one — a change to a template is not silent.

Example playbooks:
- **New product launch** — check inventory readiness, draft 3 social posts in launch format, flag low-stock threshold, propose homepage feature slot
- **Weekly marketing review** — pull last 7 days of social performance, pull Shopify traffic and conversion data, surface top 3 recommendations for the coming week
- **Monthly catalog cleanup** — flag products with zero sales in 90 days, surface restock recommendations for top performers, propose draft/archive decisions for slow-movers
- **Promotion recovery** — if a promotion is underperforming vs projection, surface the deviation and propose three adjustment paths

### How playbooks connect to Phase 6 policy infrastructure
Playbooks are not a separate architecture — they are Shopify-domain policy templates built on top of Nova's existing Phase 6 delegated policy layer. A playbook is defined as a named policy with a set of governed steps. Each step maps to an existing Shopify capability (reporting, recommendation, or execution). The policy layer handles the sequencing; the existing per-action approval model handles execution authority.

This means playbooks inherit all Phase 6 governance properties: they are visible in the Policy Review Center, auditable, reviewable before they run, and never self-modifying.

### Playbook lifecycle
1. **Define** — you describe a recurring situation and the response you want Nova to prepare
2. **Nova drafts** — Nova proposes the playbook as an ordered sequence of capability invocations with the parameters for each step
3. **You review and approve the template** — you approve, adjust, or reject the playbook definition before it is saved
4. **Playbook is persisted** — saved to governed memory (playbook domain) and visible in the Policy Review Center
5. **Trigger** — you invoke the playbook by name; Nova runs the sequence in order, surfacing each step's recommendation for your per-step approval before moving to the next
6. **Outcome is logged** — the full run is logged: which steps were approved, which were adjusted, which were skipped

### What playbooks are not
- Playbooks are not cron jobs that run without you — you must explicitly invoke them
- Playbooks are not autonomous execution sequences — each step still requires per-action approval
- Playbooks do not self-update based on outcomes — if a playbook needs to change, you update it through the same define-review-approve cycle
- Playbooks do not run in parallel or queue themselves

### Authority boundary
- Playbook definition and editing requires explicit approval for every change to the template
- Playbook invocation is always user-initiated
- Each step in a running playbook presents its recommendation for approval before proceeding
- Playbooks are visible, editable, and deletable from the Policy Review Center at any time

### Planned capability
Capability 76 — shopify_playbook — registered as a policy-layer capability. No write authority of its own — write actions flow through the existing capability 69 (shopify_execute) and 71 (shopify_social_publish) approval paths. Must not be registered until Phase 6 policy infrastructure and Tier 2 recommendation capability (67) have both passed P5 live sign-off.

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

Planned new capabilities — IDs 65–76 are assigned sequentially from the current highest registered capability (64). IDs are now fixed; the connector stub for capability 65 is the first concrete artifact. Each capability must pass the full P1-P6 verification process before being marked live.

| Planned ID | Capability Name | Tier | Write | Notes |
| --- | --- | --- | --- | --- |
| 65 | shopify_intelligence_report | 1 | No | Read-only Admin API report generation |
| 66 | shopify_anomaly_alert | Cross | No | Anomaly monitoring and alert surface |
| 67 | shopify_recommendation | 2 | No | Proposal generation, no execution |
| 68 | shopify_simulate | 3 | No | Scenario modeling, output only |
| 69 | shopify_execute | 4 | Yes | Governed write actions, per-action approval |
| 70 | shopify_social_draft | 5 | No | Content draft generation |
| 71 | shopify_social_publish | 5 | Yes | Governed posting, per-post approval |
| 72 | shopify_feedback_loop | Cross | No | Outcome tracking and recommendation quality rating |
| 73 | shopify_goal_refinement | 6 | No | Strategic check-in surface |
| 74 | shopify_email_campaign | 5 ext | Yes | Governed email draft and send (Klaviyo/Shopify Email) — high-consequence gate |
| 75 | shopify_competitive_intel | Cross | No | Governed web research for competitor pricing, product, and ad signals |
| 76 | shopify_playbook | Cross | No | Named policy-layer workflows; execution flows through caps 69 and 71 |

Each capability follows the standard P1-P6 verification path before being marked live:
- P1 Unit, P2 Routing, P3 Integration, P4 API, P5 Live sign-off, P6 Lock

Write capabilities (shopify_execute, shopify_social_publish, shopify_email_campaign) require explicit user activation before their scopes are requested from Shopify or platform OAuth. These capabilities must not be registered until the read-only capabilities they depend on (65, 66, 67) have passed P5 live sign-off.

### Single-store scope
This design assumes Nova is connected to a single Shopify store. Multi-store operation — where a user operates multiple independent Shopify stores — is not addressed in this design and would require a materially different connector architecture: separate OAuth tokens and separate connector instances per store, with explicit per-store context in every API call and every report. If multi-store support is required in the future, it must be designed as a separate extension rather than retrofitted into the single-store model described here.

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

### The broader pattern

Shopify is the first domain this design addresses. But the pattern — authority tiers, read-before-write, per-action approval, feedback loop, playbook engine, competitive awareness, goal refinement — is not Shopify-specific. It is a **governed business operator layer**.

The same pattern applies to:
- **Amazon seller operations** — inventory, pricing, ad spend, A+ content proposals
- **Local business ops** — appointment scheduling, review monitoring, local ad management
- **Service businesses** — proposal drafting, project status reporting, client communication approvals
- **Multi-channel commerce** — unified cross-platform performance view with per-platform execution authority

What makes this pattern work is that it does not try to automate business judgment. It structures business judgment: surface the data, propose the action, require the approval, log the outcome. Nova becomes more useful over time not by accumulating more autonomy but by accumulating more context — a better read of your store, your patterns, and your decisions.

That is the architecture to protect.

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

1. **Connector interface stub** ✓ — `src/connectors/shopify_connector.py` defines the `ShopifyConnector` abstract base, data contracts (`ShopifyStoreSnapshot`, `ShopifyOrderSummary`, `ShopifyProductSummary`), error type, and singleton registry. This is the implementation contract that executors and the API layer build against.
2. **Capability 65 registration** — add `shopify_intelligence_report` to `src/config/registry.json` (status: design) and `src/config/capability_locks.json` (all phases pending). Also add the connector entry to `src/config/connector_packages.json` pointing to the stub.
3. **Shopify OAuth connection** — Admin API read-only scopes only (see Scope management for the specific scope list), token storage through `src/identity/`, connection state surfaced in Trust and Settings pages alongside existing connectors.
4. **Development store validation** — connect to a Shopify development store and confirm the read-only API surface works end-to-end before any further development.
5. **Reporting surface** — on-demand sales, product, traffic, inventory, and market-aware reports via GraphQL Admin API; capability 65 registered and P1-P4 verified.
6. **Anomaly detection** — configurable threshold monitoring, alert surface in Agent page; capability 66 registered. Polling model first, webhooks as a later enhancement.
7. **Recommendation engine** — governed proposals with explicit approval flow, pending approval persistence across sessions; capability 67 registered.
8. **Scenario simulation** — forecast modeling tied to historical GraphQL Admin API data; capability 68 registered.
9. **Execution lane** — GraphQL Admin API write path via NetworkMediator, write OAuth scopes added as optional activation, pre-execution condition check, rollback record, per-action approval UI; capability 69 registered. P5 sign-off against development store required before any live store activation.
10. **Social marketing layer** — brand voice configuration, product image pull from Shopify media, draft generation, content calendar, image gap flagging, per-post publish approval; capabilities 70 and 71 registered.
11. **Feedback loop** — outcome tracking, recommendation quality rating surface, track record audit view; capability 72 registered.
12. **Goal refinement sessions** — governed strategic check-ins on a user-set schedule; capability 73 registered.
13. **Webhook enhancement** — inbound webhook endpoint on the governed bridge, Shopify webhook subscription management, faster anomaly detection latency.
14. **Email marketing extension** — Tier 5 email capability (Klaviyo, Mailchimp, or Shopify Email), governed draft and send approval with high-consequence confirmation gate.
15. **Multi-platform expansion** — additional social and commerce connectors through the same governed model, each following the full P1-P6 process.
16. **Competitive intelligence** — governed web research lane for competitor monitoring (capability 75). Depends on existing research capabilities (16, 48) being live and stable. Can begin in parallel with Tier 4/5 execution work since it uses no Shopify Admin API write paths.
17. **SOP / Playbook Engine** — Shopify-domain policy templates on the Phase 6 policy layer (capability 76). Must not begin until Phase 6 policy infrastructure, capability 67 (recommendation), and at least one write-capable capability (69 or 71) have passed P5 live sign-off. A playbook that cannot reach execution has no meaningful test surface.
18. **KPI Command Center** — composed daily brief surface aggregating signals from capabilities 65, 66, and 72. No new capability required. Implement as a report template within capability 65 once reporting, anomaly, and feedback loop capabilities are all live.

No step in this sequence should be skipped to move faster. Each step builds the trust foundation for the next. Write-capable capabilities (69, 71) must not be registered until the read-only capabilities they depend on have passed P5 live sign-off against a development store.

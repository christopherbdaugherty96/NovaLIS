# Nova Shopify Governed Operator Design
Date: 2026-04-20
Status: Future design — not yet implemented
Source: Voice brainstorm session, three-pass review

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

Nova's Shopify capabilities should be explicitly separated into modular tiers. Each tier has its own authority level and its own approval requirement.

| Tier | Name | Nova Authority | User Approval Required |
| --- | --- | --- | --- |
| 1 | Reporting | Read and summarize | No — output only |
| 2 | Recommending | Propose actions | Yes — before any action |
| 3 | Simulating | Model scenarios | No — output only |
| 4 | Executing | Apply approved actions | Yes — explicit per action |
| 5 | Marketing | Draft and schedule content | Yes — before any publish |
| 6 | Goal Refinement | Surface strategic pivots | Yes — governed check-in |

These tiers must remain modular. Expanding one tier must not silently expand another.

---

## Tier 1: Read-Only Shopify Intelligence

### What Nova does
Nova connects to the Shopify API in read-only mode and generates structured intelligence reports on demand or on schedule.

### Capabilities
- Sales reports: revenue, units sold, order volume, average order value over configurable time windows
- Top products: best-sellers by revenue, by units, by margin where available
- Traffic analytics: sessions, conversion rate, bounce signals, drop-off points in the funnel
- Inventory signals: low-stock alerts, out-of-stock detection, velocity-based restock suggestions
- Customer behavior: repeat purchase rates, new vs returning split, cohort snapshots

### Output format
- Structured report with a visible bottom line first
- Supporting data and breakdown visible on request
- Source label showing which Shopify API surface produced each data point

### Authority boundary
- Read only
- No write, no mutation, no cart or order modification
- All API calls pass through NetworkMediator and are logged

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
- Nova surfaces the proposal in a visible review surface
- You see: what Nova is recommending, why, and what data it's based on
- You approve, adjust, or reject
- If approved, the action moves to Tier 4 (execution)
- If rejected, the rejection is logged with your reason if provided

### Authority boundary
- No action is taken without your explicit approval
- Nova does not execute recommendations autonomously under any condition

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
- Nova uses your historical Shopify data as the basis
- It applies the hypothetical change and models the likely outcome range
- It presents the forecast with explicit confidence signals — not false precision
- It shows what assumptions it made so you can adjust them

### Authority boundary
- Simulations are output only — no changes are made
- Nova must label all simulations clearly as projections, not guarantees
- Simulation outputs are logged

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
- Nova presents the exact change it will make before executing
- You confirm
- Nova executes through the governed Shopify API write path
- The action is logged to the ledger with: what changed, when, why, who approved

### Authority boundary
- Nova cannot execute anything not explicitly approved in the current session
- Nova cannot chain executions without returning to you between each one
- If an execution fails, Nova reports the failure and does not retry without another explicit approval

---

## Tier 5: Social Media Marketing

### What Nova does
Nova supports your social and marketing operation as a governed content and campaign assistant. It drafts, schedules, and analyzes — but posting remains user-approved.

### Content drafting
- Nova generates social post drafts based on your brand tone and past high-performing content
- Drafts are tied to a specific product, promotion, or campaign context
- Nova can produce variants: short form, long form, story format, caption-only
- All drafts are presented for your review before any scheduling or publishing

### Content calendar
- Nova maintains a governed content calendar
- It suggests when to post based on engagement pattern analysis from your past content and general platform signals
- You approve the calendar before it becomes active
- Nova does not post on its own schedule — only on the schedule you have approved

### Campaign planning
- Nova proposes campaign ideas tied to your Shopify data: upcoming inventory, seasonal patterns, sales history
- Each campaign proposal includes: objective, target audience, platform, content format, proposed timeline, and expected outcome range
- You approve, adjust, or reject each proposal before Nova acts on it

### Engagement analytics
- Nova reads engagement metrics from connected social platforms
- It reports: what is working, what is not, what changed week over week
- It ties social performance back to Shopify conversion data where the signal is available

### Posting execution
- Nova can post to approved platforms when you explicitly authorize a specific post
- You see the exact content, the exact platform, and the exact time before Nova publishes
- Nova does not publish autonomously
- Every publish action is logged

### Authority boundary
- Nova does not post, comment, reply, or boost without explicit per-action approval
- Draft generation is output only and requires no approval
- Publishing requires explicit per-post approval

---

## Tier 6: Long-Term Goal Refinement

### What Nova does
Nova periodically surfaces strategic check-in sessions to help you evaluate whether Nova's current operating parameters still match your business goals.

### What a goal refinement session covers
- Are the current reporting priorities still the right ones?
- Have your business goals shifted — new regions, new product categories, new channels?
- Are the current recommendation thresholds still calibrated to your strategy?
- Do the current execution permissions still match your risk tolerance?
- Should any capability be expanded, constrained, or paused?

### How it works
- Nova surfaces a goal refinement prompt on a schedule you set, or on demand
- The session is a structured conversation: Nova presents what it currently understands your goals to be, and asks you to confirm, adjust, or redirect
- Changes to Nova's operating parameters from this session are logged as policy updates

### Authority boundary
- Nova does not change its own operating parameters
- Parameter changes require your explicit confirmation during the refinement session
- All changes are logged

---

## Proactive Anomaly Detection

### What Nova does
Rather than waiting for you to ask for a report, Nova monitors signals and alerts you when something unusual happens.

### Examples of anomaly triggers
- Traffic drops more than X% day over day or week over week
- A product suddenly spikes in traffic but has low or declining conversion
- Revenue is tracking significantly below the rolling average for this time period
- A top product goes out of stock
- A cart abandonment rate moves outside normal range
- An order volume anomaly that could indicate a fraud pattern or a viral event

### Alert format
- Nova surfaces the alert with: what happened, when, what the normal baseline was, how significant the deviation is
- Nova asks: do you want to review this, or dismiss it?
- If you want to review, Nova produces a full drill-down report
- If you dismiss, the dismissal is logged

### Authority boundary
- Alerts are output only
- Nova does not take action in response to an anomaly without your approval
- Alert thresholds are configurable by you

---

## Feedback Loop

### What Nova does
Nova tracks the quality of its own recommendations over time so it can improve.

### How it works
- After a recommendation is approved and executed, Nova follows up to measure the outcome
- It compares the projected outcome (from Tier 3 simulation or from the recommendation rationale) against the actual result
- It surfaces this as a simple outcome report: "You approved this change — here is what happened"
- You can optionally rate the recommendation quality: useful, not useful, or wrong

### Why this matters
- Over time, Nova's recommendation quality improves based on your ratings and actual outcome data
- Nova learns which recommendation types have been reliable and which have been off
- This feedback is logged and visible so you can audit it

---

## Transparency Requirements

Every Nova action in this integration must meet Nova's standard transparency requirements:

- **Source visible**: Nova shows which data source produced each insight
- **Reasoning visible**: Nova explains why it is recommending something, not just what
- **Confidence visible**: Nova labels projections as projections, not facts
- **Boundary visible**: Nova states what it cannot or will not do without approval
- **Log visible**: every action, recommendation, approval, and rejection is in the ledger and reviewable

---

## Multi-Platform Expansion

This design is intentionally scoped to Shopify first. As Nova's connector layer expands, the same governed model should apply to:

- Other e-commerce platforms (if you expand beyond Shopify)
- Social commerce channels (Instagram Shopping, TikTok Shop, Pinterest)
- Email marketing platforms (governed campaign drafting and send approval)
- Paid advertising platforms (governed budget proposals and creative drafts)
- Inventory and fulfillment systems beyond Shopify's native tools

Each new platform connection must go through the same connector governance process: explicit setup, explicit permissions, explicit logging, no autonomous action.

---

## Human Skill Development

Nova's involvement in your Shopify operation should strengthen your strategic judgment, not replace it.

### How Nova supports this
- Nova explains its reasoning on every recommendation, not just the conclusion
- Nova surfaces the data it used so you can build your own read of the business
- Nova flags when a decision is genuinely ambiguous — it does not give false confidence
- Nova's goal refinement sessions are structured to prompt your strategic thinking, not just confirm Nova's current parameters

### The right outcome
You should become a better Shopify operator because Nova is surfacing better data and explaining its reasoning — not a passive approver of Nova's decisions.

---

## Implementation Sequence

When this is built, the right order is:

1. **Read-only Shopify API connection** — governed connector, logged, NetworkMediator enforced
2. **Reporting surface** — on-demand sales, product, and traffic reports
3. **Anomaly detection** — proactive alerts with configurable thresholds
4. **Recommendation engine** — governed proposals with explicit approval flow
5. **Scenario simulation** — forecast modeling tied to your historical data
6. **Execution lane** — governed write access for approved actions, per-action approval
7. **Social marketing layer** — draft, calendar, campaign, governed publish
8. **Feedback loop** — outcome tracking and recommendation quality ratings
9. **Goal refinement sessions** — governed strategic check-ins on schedule
10. **Multi-platform expansion** — additional connectors through the same governed model

No step in this sequence should be skipped to move faster. Each step builds the trust foundation for the next.

# Nova E-Commerce Operator End-State Plan

Date: 2026-04-30

Status: Future product / architecture plan. Not current runtime truth.

Second-pass status: tightened 2026-04-30 to add explicit execution gates, social-publishing boundaries, order-processing boundaries, playbook limits, and demo criteria.

Purpose: document the intended end-state for Nova as a governed e-commerce operator and the phased path to get there.

---

## Source Of Truth Rule

This document describes where Nova can go. It does not replace generated runtime truth, live code, certification status, or current priority overrides.

Use this order when status conflicts:

```text
1. Live code and generated runtime truth
2. Current priority override
3. Capability verification / signoff docs
4. Current handoff docs
5. Future planning docs, including this document
```

Current runtime truth at the time this document was drafted:

```text
Cap 65 shopify_intelligence_report exists as Tier 1 read-only Shopify intelligence.
Cap 65 does not write Shopify.
Cap 64 send_email_draft opens a local mail draft only after confirmation; Nova does not send email.
Cap 63 openclaw_execute is a governed OpenClaw surface, not broad autonomous hands.
Full governed envelope execution, approval queue, connector registry, and social publishing are future work unless later runtime truth proves otherwise.
```

---

## End-State Vision

Nova should become a governed e-commerce operator for small businesses and online stores.

The end-state is not an autonomous store bot.

The end-state is:

```text
Nova monitors the business,
understands store and channel signals,
drafts front-end and back-end actions,
proposes operating decisions,
waits for approval where authority is required,
executes only approved actions,
and records receipts for what happened and what did not happen.
```

Short version:

```text
Nova prepares and operates the workflow.
The user keeps authority.
Receipts prove the boundary.
```

---

## Core Rule

```text
Intelligence is not authority.
```

Applied to e-commerce:

```text
A store signal does not grant permission to change the store.
A campaign idea does not grant permission to publish.
A customer issue does not grant permission to message the customer.
A low-stock alert does not grant permission to change inventory.
A saved operation plan does not grant permission to execute external actions automatically.
```

Nova may read, analyze, draft, simulate, and propose inside defined permissions.

Nova may execute only when the action is inside an approved capability, scoped to an explicit request or approved playbook step, and logged with a receipt.

---

## Product Thesis

Most e-commerce automation tools either stop at dashboards or jump too quickly into unsafe action.

Nova should sit in the middle:

```text
It should understand what is happening.
It should prepare the next move.
It should make the risk visible.
It should ask before changing anything.
It should prove what happened.
```

This creates a defensible product category:

```text
A governed e-commerce operating layer.
```

Not:

```text
A chatbot for Shopify.
A social posting bot.
An unsupervised store manager.
```

---

## What The User Ultimately Wants Nova To Handle

The desired end-state includes both the front-end and back-end of e-commerce operations.

### Front-End / Growth Surface

Nova should eventually support:

```text
TikTok product post drafting
Instagram product post drafting
Facebook / Meta content drafting
Pinterest content planning
X / Twitter announcements where useful
content calendar planning
campaign angle generation
caption and script writing
product media selection suggestions
promotion launch drafts
approved social publishing
approved scheduled publishing
performance review of prior content
```

### Back-End / Store Operations Surface

Nova should eventually support:

```text
Shopify store intelligence
sales and KPI reporting
inventory monitoring
low-stock and out-of-stock alerts
product status review
promotion and discount recommendations
product page improvement recommendations
pricing / margin scenario simulation
order health review
fulfillment status review
customer support draft preparation
supplier/vendor follow-up drafts
approved product updates
approved discount creation
approved inventory updates
approved order/fulfillment workflows where safe
```

### Operating Plan / SOP Surface

Nova should eventually let the user create governed operation plans, such as:

```text
When a product is low stock, prepare a supplier email and pause promotion recommendation.
When inventory is high and sales are slow, draft a social campaign and discount proposal.
When revenue is below baseline for three days, prepare a diagnostic report and campaign options.
When a new product is added, prepare launch content and checklist tasks.
When a campaign ends, compare expected vs actual results and suggest the next move.
```

These plans should be explicit, inspectable, editable, pausable, and revocable.

---

## What Nova Should Not Become

Nova should not become:

```text
an autonomous Shopify admin
an autonomous social media poster
an autonomous customer messaging agent
an autonomous refund/fulfillment agent
an autonomous advertising spender
an agent with broad browser/account access
an always-on bot that changes business state without review
```

Blocked early behavior:

```text
auto-post to TikTok or Instagram
auto-create discounts
auto-change prices
auto-update inventory
auto-fulfill or refund orders
auto-send customer emails
auto-send supplier emails
auto-buy ads or boost posts
auto-submit forms
auto-modify store settings
auto-delete products or content
```

These can only become possible later as narrow, approved, capability-bound actions with explicit receipts.

---

## Authority Lanes

Every e-commerce workflow should be classified into one of these lanes.

| Lane | Meaning | Approval Requirement |
| --- | --- | --- |
| Read-only | Nova reads and summarizes data | Usually no approval after connector is enabled |
| Draft-only | Nova prepares content, messages, plans, or payloads | Approval may be needed to create an external draft; never sends/publishes |
| Recommendation | Nova proposes a business action | User approval required before execution |
| Simulation | Nova models a possible action | No execution; must label assumptions and uncertainty |
| Local reversible | Nova performs a reversible local action | Only after local capability signoff/settings allow |
| Durable mutation | Nova changes persistent local/business state | Approval required |
| External write | Nova changes Shopify/social/email/customer systems | Hard approval required |
| Financial/security-sensitive | Ads spend, billing, payments, refunds, security settings | Blocked by default or high-friction approval after maturity |

---

## Non-Negotiable Execution Gates

No e-commerce write-capable action should be implemented until these gates exist or a later runtime truth document explicitly supersedes this plan.

### Gate 1 — Request Understanding Visibility

Nova must show what it understood before acting.

Required fields:

```text
understood goal
request type
target system
authority lane
safe next step
must not do
confidence / uncertainty
result or not-executed state
```

### Gate 2 — Connector Registry

Every external business system must have a registered connector entry showing:

```text
provider
connection status
scopes
read permissions
write permissions
draft permissions
blocked actions
approval requirements
last use
last error
revoke/disconnect path
```

### Gate 3 — Approval Queue

Any durable or external action must go through a queue item with:

```text
exact target system
exact proposed change
preview / payload
risk level
what will happen
what will not happen
expiration
approve / deny / edit
receipt link
```

### Gate 4 — Capability Contract

Every e-commerce capability must define:

```text
can
cannot
required setup
authority tier
confirmation requirement
expected receipts
known failure modes
fallbacks
```

### Gate 5 — Dev/Test Environment Proof

Write-capable Shopify operations must pass first in a development store or test store.

Write-capable social publishing must pass first against a sandbox/test account or non-public test surface where the platform allows it.

Order/customer/refund/fulfillment workflows must begin as read/review/draft only before any write action is considered.

### Gate 6 — Receipt Proof

Every approved execution must produce a receipt that states:

```text
what changed
what did not change
who/what approved it
which connector/capability was used
whether the action succeeded or failed
where to inspect the evidence
```

---

## Target End-State Workflow

The full e-commerce workflow should look like this:

```text
1. User defines business goal or operation plan.
2. Nova validates the goal and labels authority boundaries.
3. Nova reads approved data sources.
4. Nova generates a store/channel status brief.
5. Nova detects signals or opportunities.
6. Nova drafts recommendations or campaign assets.
7. Nova optionally simulates outcomes.
8. Nova creates approval cards for actions that would change anything.
9. User approves, edits, denies, or expires each action.
10. Nova re-checks current conditions before execution.
11. Nova executes only the approved action inside its scoped capability.
12. Nova logs receipts.
13. Nova tracks outcomes and reports whether the action worked.
```

Required final statement for every run:

```text
What Nova did.
What Nova did not do.
What is waiting for approval.
What changed, if anything.
Where the receipt is.
```

---

## Example End-State Playbook

### Playbook: Slow Sales + High Inventory Promotion

User-approved rule:

```text
If Product A has more than 50 units in stock and sales are below the 7-day average for 3 days, prepare a campaign and discount proposal.
```

Nova allowed actions:

```text
read Shopify product/order/inventory data
generate a sales diagnosis
draft TikTok and Instagram content
draft a discount proposal
create an approval card
```

Nova blocked actions until approval:

```text
publish social content
create discount code
change product page
send customer email
boost/ad spend
```

Approval card:

```text
Proposed action: Launch 10% Product A promo for 48 hours.
Will happen if approved: create discount code and publish selected social post.
Will not happen: no email sent, no ads purchased, no other products changed.
Requires approval because: external Shopify/social write.
```

Receipt after approval/execution:

```text
Discount code created after approval.
TikTok post published after approval.
No customer messages sent.
No inventory changed.
Receipt IDs: ...
```

---

## Example Early Safe Workflow

Before social publishing or Shopify writes exist, the same business value can be delivered safely.

```text
User: Run my e-commerce morning check.

Nova:
1. Fetches read-only Shopify report.
2. Summarizes revenue, orders, AOV, active products, low stock, and out-of-stock counts.
3. Identifies one issue or opportunity.
4. Drafts a TikTok/Instagram campaign concept.
5. Drafts a discount recommendation.
6. Creates a not-yet-executable approval preview.
7. States: no store data changed, no content posted, no customer messages sent.
```

This is the first target workflow because it proves e-commerce value without requiring dangerous authority.

---

## Capability Roadmap

### Phase 1 — Store Intelligence Foundation

Status target: current/near-term.

Build and verify:

```text
Cap 65 Shopify read-only intelligence
Shopify connector status visibility
live P5 signoff against a Shopify development store
Shopify KPI Command Center
period-aware reports: today, 7 days, 30 days, 90 days
low-stock and out-of-stock summaries
trust receipt for report generation
```

Success criteria:

```text
Nova can answer how the store is doing.
Nova can show store KPIs with fetch timestamps.
Nova refuses cleanly when Shopify credentials are missing.
Nova performs no writes.
Nova logs the read/report action.
```

---

### Phase 2 — E-Commerce Command Center

Build:

```text
daily store status card
revenue / order / AOV summary
inventory watch list
products needing attention
pending recommendation section
connector health state
last fetch timestamp
read-only scheduled brief
```

Success criteria:

```text
Opening Nova gives the operator one useful store view.
Scheduled briefs remain read-only.
Quiet hours and rate limits apply.
Every brief states that no store changes were made.
```

---

### Phase 3 — Recommendations

Build:

```text
Shopify recommendation schema
recommendation rationale
supporting data references
confidence / uncertainty labels
adjustable parameters
recommendation expiry
pending recommendation persistence
```

Example recommendations:

```text
restock Product X
review Product Y page
draft supplier email
prepare promotion for Category Z
review checkout/conversion drop
pause promotion for low-stock product
```

Success criteria:

```text
Nova can propose actions without executing them.
Every recommendation says why it exists and what data supports it.
Recommendations can be approved, adjusted, rejected, or expired.
```

---

### Phase 4 — Approval Queue

Build:

```text
pending action store
approval card UI
approve / deny / edit / expire states
receipt linkage
non-action statements
single-action scoped approvals
approval expiry
condition re-check before execution
```

Success criteria:

```text
No durable or external action can happen without a visible approval record.
Edited actions require revalidation.
Expired approvals cannot execute.
Approvals do not become broad future permission.
```

---

### Phase 5 — Content And Campaign Drafting

Build:

```text
brand voice configuration
product post drafts
caption/script generation
platform-specific variants
content calendar proposal
campaign plan drafts
product media candidate selection
content approval cards
```

Supported early platforms:

```text
TikTok draft-only
Instagram draft-only
Facebook / Meta draft-only
Pinterest draft-only
X / Twitter draft-only if useful
```

Success criteria:

```text
Nova can draft social content tied to Shopify signals.
Nova does not publish.
Nova shows why the product/angle/timing was chosen.
User can edit or reject drafts.
```

---

### Phase 6 — Scenario Simulation

Build:

```text
discount impact simulation
free-shipping threshold simulation
inventory velocity projection
campaign impact estimate
margin risk estimate
assumption display
confidence range display
```

Success criteria:

```text
Nova labels simulations as projections.
Nova does not overstate precision.
Simulation outputs do not trigger execution directly.
Simulation can become a recommendation only after user review.
```

---

### Phase 7 — Dev-Store Write Proofs

Build only after approval queue and connector governance exist.

Start with a Shopify development store only.

Candidate first write capability:

```text
create a test discount code in dev store after approval
```

Then:

```text
update test product status
update test product title/description
update inventory in dev store
```

Success criteria:

```text
No live store writes during early proof.
Exact payload preview before execution.
User explicitly approves each action.
Nova re-checks state before execution.
Failures are reported item by item.
Receipt includes before/after where available.
```

---

### Phase 8 — Approved Shopify Operations

Build after dev-store proof and live signoff.

Possible approved operations:

```text
create discount code
update product fields
change product status
adjust inventory quantity
update collection/product placement
prepare fulfillment review
create supplier/customer draft
```

Blocked or high-friction operations:

```text
refunds
payments
billing
bulk customer messaging
mass product edits
shipping rule changes
ad spend
security settings
```

Success criteria:

```text
Every Shopify write is capability-bound.
Every Shopify write has approval and receipt.
Nova never chains writes without returning to the user.
Rollback is proposed as a new action, not automatic.
```

---

### Phase 9 — Approved Social Publishing

Build after social connector registry and content approval flow exist.

For each platform:

```text
separate OAuth / connection state
separate scopes
read vs publish lanes
platform-specific health check
approval before publishing
receipt after publishing
```

Publishing rule:

```text
Nova can publish only the exact approved content, to the exact approved platform/account, at the exact approved time.
```

Minimum social publish approval card:

```text
platform
account/page/profile
content text
media asset
scheduled time or immediate publish
what will not happen
whether comments/DMs/replies are blocked
receipt requirement
```

Success criteria:

```text
No autonomous posting.
No batch publishing without per-post review.
No comments/replies/DMs without explicit instruction.
Every post has a receipt.
```

---

### Phase 10 — Order And Customer Workflow Support

Start with read/review/draft only.

Build:

```text
order health brief
fulfillment exception summary
customer support draft preparation
supplier/vendor follow-up draft
return/refund review recommendations
fraud/dispute signal summary where available
```

Only later consider approved actions:

```text
mark internal status
prepare fulfillment update
send approved customer response through connector
create approved refund only with hard approval if ever allowed
```

Order/customer hard boundary:

```text
Nova must not refund, fulfill, cancel, edit shipping, or message customers automatically.
Customer-impacting actions require explicit approval and a clear preview.
Refunds, payment actions, and legal/compliance-sensitive actions should remain blocked by default until a separate high-risk policy exists.
```

Success criteria:

```text
Nova never refunds, fulfills, cancels, or messages customers automatically.
High-consequence customer/order actions require hard approval.
```

---

### Phase 11 — Feedback Loop

Build:

```text
recommendation outcome tracking
campaign result comparison
approved action history
actual vs expected result
user rating: useful / not useful / wrong
pattern review
```

Success criteria:

```text
Nova reports whether recommendations worked.
Nova does not silently self-modify policy.
User can inspect recommendation history.
```

---

### Phase 12 — Governed SOP / Playbook Engine

Build:

```text
named operation plans
condition triggers
allowed reads
allowed drafts
blocked actions
approval requirements
schedule settings
pause/resume
version history
receipts
```

Playbook example fields:

```text
playbook_id
name
goal
trigger_conditions
required_connectors
allowed_reads
allowed_drafts
proposed_actions
blocked_actions
approval_required_for
schedule
quiet_hours_policy
rate_limit_policy
owner_notes
version
status
```

Playbook execution rule:

```text
A playbook can trigger read, analysis, draft, recommendation, and approval-card creation.
A playbook cannot silently perform external writes unless a later explicitly approved narrow action lane exists.
Changing a playbook requires user confirmation.
Paused playbooks cannot run.
Stale playbook approvals must be rechecked.
```

Success criteria:

```text
A playbook can prepare and propose.
A playbook cannot silently expand its own authority.
Changing a playbook requires user confirmation.
External writes still require approval unless a future explicitly approved narrow lane exists.
```

---

## Needed Connectors

### Required First

```text
Shopify Admin API read-only
Shopify connector health/status
local email draft / future Gmail draft-only alignment
```

### Required For Social

```text
TikTok business / publishing API connector
Meta / Instagram / Facebook connector
Pinterest connector
X connector if cost/API access is justified
LinkedIn connector if business use case exists
```

### Required For Better Attribution

```text
GA4
Meta Pixel / Ads reporting
TikTok Ads reporting
Google Merchant Center
Klaviyo / Mailchimp / Shopify Email
```

### Required For Full Back-End Ops

```text
shipping / fulfillment provider connectors
CRM / customer support connector
supplier/vendor contact source
payment/refund surfaces only after high-risk governance exists
```

---

## Connector Scope Rules

Each connector should start in the lowest useful lane.

```text
Shopify: read-only first, write scopes later only after dev-store proof.
Social platforms: draft/planning first, publish scopes later only after approval queue.
Email platforms: draft-only first, send later only after high-consequence approval design.
Order/fulfillment providers: read/review first, mutation later only after separate high-risk design.
Ad platforms: read-only reporting first, spend/budget mutation blocked by default.
```

Scope expansion must be explicit. Nova must not silently request or use broader scopes because a new workflow wants them.

---

## Data Boundaries

Shopify Admin API does not automatically expose all e-commerce data.

Nova must label gaps clearly:

```text
Klaviyo data requires Klaviyo connector.
Recharge subscription data requires Recharge connector.
Yotpo review data requires Yotpo connector.
Meta/TikTok ad performance requires platform connectors.
GA4 attribution requires GA4 connector.
```

Nova must not say a signal does not exist just because the Shopify connector cannot see it.

---

## Trust / Receipt Requirements

Every e-commerce run should produce one of these statements:

```text
No store data was changed.
No content was published.
No customer messages were sent.
No orders were fulfilled, refunded, or cancelled.
One draft was prepared and is waiting for approval.
One proposed action is pending approval.
One approved action was executed and logged.
```

Receipts should capture:

```text
request
understood goal
data sources used
capability invoked
authority lane
action proposed
approval decision
execution result
non-action statement
receipt id
```

---

## Minimum Viable E-Commerce Demo

The best early demo should not require write authority.

Demo flow:

```text
1. User asks: How is my store doing?
2. Nova fetches Shopify read-only report.
3. Nova shows revenue/orders/product/inventory snapshot.
4. Nova identifies one business opportunity.
5. Nova drafts a TikTok or Instagram campaign concept.
6. Nova drafts a Shopify discount recommendation.
7. Nova says: nothing was posted, no discount was created, no store data changed.
8. Nova shows the proposed approval card as future/preview or queue item.
```

Why this demo works:

```text
It proves e-commerce value.
It proves governance.
It avoids unsafe writes.
It shows the front-end and back-end connection.
It demonstrates Nova's product identity.
```

MVP demo success line:

```text
Nova found one business opportunity and prepared the work, but did not publish, discount, message, fulfill, refund, or modify anything.
```

---

## Do Not Overstate

Do not claim Nova can currently:

```text
post to TikTok
publish to Instagram
run paid social campaigns
process Shopify orders
fulfill orders
refund customers
change product prices
update inventory
create discounts on a live store
send customer emails
operate a store autonomously
```

Correct wording:

```text
Nova currently has a read-only Shopify intelligence foundation.
Nova is being designed toward governed e-commerce operation.
Front-end publishing and back-end store actions require future connectors, approval queue, capability signoff, and live testing.
```

---

## Build Priority Note

This e-commerce plan should not displace the current core Nova priority unless the owner explicitly reprioritizes it.

Correct near-term order:

```text
1. RequestUnderstanding / trust-action visibility.
2. Local capability confidence and signoff.
3. Connector governance surfaces.
4. Cap 65 live dev-store signoff.
5. E-commerce command center and draft-only workflows.
6. Approval queue.
7. Dev-store writes.
8. Approved live writes / social publishing later.
```

---

## Final Product Framing

Nova should be framed as:

```text
A governed e-commerce operator that connects store intelligence, campaign preparation, operational recommendations, approval-based execution, and receipts.
```

Not:

```text
An autonomous Shopify/social media bot.
```

Final rule:

```text
Nova may prepare the work.
Nova may explain the work.
Nova may ask to do the work.
Nova may do only the approved work.
Nova must prove what happened.
```

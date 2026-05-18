# Nova / Auralis Big Picture Operating Model - 2026-05-18

Status: future planning / not runtime truth.

This packet preserves the useful planning material from the local `BigPicture/`
notes without promoting raw audit drift as current repo truth.

It does not authorize runtime behavior changes, generated runtime doc edits,
capability expansion, authority expansion, OpenClaw expansion, browser/computer-use,
external writes, Shopify writes, email sending, finance automation, social posting
automation, or approval-gate certification.

Current generated runtime docs, runtime code, status docs, and reviewed PR truth
remain authoritative.

---

## Source Handling

Local source notes reviewed:

```text
BigPicture/5-16-26Audit.txt
BigPicture/New Text Document.txt
```

These raw files are not committed in this packet. They contain useful strategic
direction, but also include older Auralis/Formspree status details that have
since moved. This cleaned packet keeps the durable operating model and drops
stale checklist claims.

Current operating boundary:

```text
Nova drafts and recommends.
Christopher approves.
Execution stays manual for business actions.
Governed execution comes later only inside approved bounded paths.
```

---

## Current Conservative Truth

Nova:

```text
Focused approval-gate regression coverage is merged.
Behavioral live-session approval-gate coverage is merged.
Basic workflow verification and regression fixes are merged.
Full approval-gate certification remains pending.
Website-preview live-backend validation remains follow-up debt.
```

Auralis:

```text
Lead capture/contact path is the current business foundation.
Temporary Gmail contact path remains the current contact path until domain email is verified.
Domain email remains pending.
LLC/business setup remains a blocker for broader outreach and client execution.
Custom design remains the lightest first proof lane once outreach is appropriate.
Shopify product routing is live, but full commerce readiness still needs checkout,
policy, payment, tax, shipping, fulfillment, support, margin, and test-order proof.
```

Shopify/business execution:

```text
Shopify remains checkout/order/payment source of truth.
Nova must not write Shopify data under the current boundary.
Nova may become a read-only analyst and drafting assistant before any governed
execution expansion is considered.
```

---

## Durable Operating Model

The best near-term shape is:

```text
Nova = read-only commerce analyst + drafting assistant + approval-gated workflow system later
Auralis = public product / custom-design / website-services surface
Shopify = checkout, order, product, and payment source of truth
Christopher = final operator and approver
```

The model is not:

```text
Nova posts automatically
Nova changes Shopify products automatically
Nova runs ads
Nova changes prices
Nova messages customers
Nova sends emails directly
Nova manages finance
Nova executes business workflows autonomously
```

The safe current sequence is:

```text
Nova reads or receives data
Nova analyzes
Nova drafts or recommends
Christopher approves
Christopher manually executes business actions
Nova tracks the result
```

Future governed execution can only happen after separate reviewed locks, tests,
receipts, and bounded capability paths.

---

## Auralis Public Surface Model

Auralis has three public surfaces:

```text
1. Auralis Design products
2. Custom / personalized design requests
3. Website design services
```

Recommended sequencing:

```text
contact trust
measurement spine
custom design proof
product/Shopify proof
website-services proof
```

Reasoning:

```text
Custom design needs less infrastructure than full product commerce or website
client delivery. It can create a proof artifact faster, but outreach can wait
until LLC/business setup is ready.
```

---

## Measurement Spine

The strongest useful infrastructure is a measurement spine, not autonomous
execution.

Recommended stack:

```text
Shopify - checkout, orders, products, payments
Auralis site - product display, trust, lead capture
GA4 - traffic and event tracking
Google Tag Manager - tag/event control
Search Console - search visibility
Microsoft Clarity - session behavior
Formspree - lead capture
CSV/Sheet trackers - manual social/product/margin tracking
Nova - analysis, recommendations, drafting, reporting
```

Events worth standardizing later:

```text
page_view
view_item_list
view_item
select_item
shopify_click
generate_lead
custom_design_click
web_design_click
purchase
```

These are measurement concepts only. They do not authorize implementation in
Nova, Auralis, or Shopify without a scoped PR in the relevant repo.

---

## Nova Report Concepts

The most useful first report concept is:

```text
Auralis Weekly Growth Report
```

It should eventually summarize:

```text
traffic
product clicks
Shopify outbound clicks
Shopify orders
lead inquiries
best-performing products
weak products
conversion gaps
recommended actions
manual next steps
```

Follow-on report concepts:

```text
Social Content Draft Pack
Product Improvement Queue
Margin Watch
Custom Design Lead Summary
Nova Action Tracker
```

These are planning concepts. They do not add runtime capabilities.

---

## Read-Only Analysis Boundary

Nova may eventually help analyze:

```text
Shopify product/order exports or read-only reports
website traffic data
product click data
social post performance
Formspree leads
margin/cost assumptions
manual tracker files
```

Nova may draft:

```text
social captions
short video hooks
product descriptions
custom design replies
outreach messages
product improvement notes
weekly action plans
```

Nova must not directly execute:

```text
posting
customer messaging
email sending
Shopify writes
price changes
refunds
ad spend
financial decisions
tax handling
browser/computer-use workflows
external writes
```

---

## Business Readiness Gaps

These are business/manual gaps, not Nova runtime gaps:

```text
LLC / EIN / business bank account
domain email
public support/contact policy
Google Business Profile
analytics setup
Search Console
Clarity
Shopify checkout test
Shopify policies
fulfillment/test order proof
product margin assumptions
first real client proof
testimonial/portfolio permission
```

Do not turn these into autonomous Nova execution. Treat them as planning and
manual operating checklist items unless a separate reviewed repo task scopes a
specific doc or implementation update.

---

## Future Tracker Concepts

Useful tracker files may eventually include:

```text
auralis_weekly_growth_report.md
social_content_tracker.csv
product_performance_tracker.csv
margin_tracker.csv
nova_action_tracker.csv
custom_design_lead_tracker.csv
```

Required fields for a Nova action tracker:

```text
date
recommendation
source data
risk level
Christopher decision
manual action taken
result
next test
receipt/proof link
```

This keeps Nova in the analysis/recommendation lane while preserving human
approval and manual execution.

---

## Stale Source Notes Not Carried Forward

The raw `BigPicture/` notes contain older claims about:

```text
Formspree test state
Auralis docs needing specific old patches
outreach timing
approval-gate implementation wording
Cap 65 live proof timing
```

Those claims should not be copied as current truth. Use current repo docs,
merged PR state, generated runtime docs, and live verified status instead.

---

## Future Work That Needs Separate Scope

Potential future docs/tasks:

```text
docs: define Auralis Measurement Spine v1
docs: define Auralis Weekly Growth Report template
docs: define Nova manual action tracker
docs: define Margin Watch inputs and warnings
docs: define custom design proof workflow
```

Each should stay docs-only unless explicitly scoped otherwise.

---

## Final Verdict

```text
The durable BigPicture direction is worth preserving.
The raw BigPicture folder should not be merged as-is.
This cleaned packet preserves the operating model while keeping runtime truth,
approval-gate certification, authority boundaries, and business execution
separate.
```

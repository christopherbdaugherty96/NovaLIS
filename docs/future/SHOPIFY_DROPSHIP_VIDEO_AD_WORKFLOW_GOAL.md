# Shopify Dropship Video Ad Workflow Goal

Status: future workflow goal
Scope: Shopify business model planning
Runtime impact: none
Current capability impact: none — Cap 65 remains read-only Shopify intelligence reporting
Research note: live web research was not available during this pass; this document is hardened using stable commerce, fulfillment, advertising, and Nova governance principles. Before implementation, re-check current Shopify, Meta, TikTok, YouTube, payment processor, and supplier platform policies.

---

## Reviewer summary

This document defines the true long-term Shopify direction for Nova: a governed dropshipping / third-party fulfillment / AI video-ad product-validation workflow.

It does not authorize autonomous commerce. It does not modify Cap 65. It does not authorize store writes, paid ads, supplier purchases, customer support actions, or publishing.

The first implementation should be manual-first:

```text
research cards
→ supplier validation cards
→ margin models
→ claim reviews
→ ad script drafts
→ Shopify read-only performance summaries
→ user-approved next-test recommendations
```

The central rule is simple:

```text
Nova may help think, draft, calculate, review, and recommend.
Nova must not spend money, publish, fulfill, order, message customers, or mutate the store without a separate governed capability and explicit approval.
```

---

## Core goal

The real Shopify goal is not only to read store metrics.

The intended business workflow is:

1. Identify a product with demand potential.
2. Source it from a wholesaler, Chinese retailer, dropshipping supplier, print-on-demand provider, or other third-party fulfillment path.
3. List the product on a Shopify store without carrying inventory directly.
4. Generate short-form product ads using AI video tools, virtual avatars, product mockups, captions, and scripted hooks.
5. Drive traffic through organic short-form content first, then paid ads only after proof.
6. When a customer orders, fulfill through the selected supplier.
7. Sell at a higher retail price while preserving honest shipping, refund, supplier, and product-quality expectations.
8. Use Nova to read performance data, recommend next tests, and keep the workflow governed.

This is a real commerce operation, not a get-rich-quick automation loop. The store owner remains responsible for product quality, delivery, customer support, refunds, chargebacks, taxes, platform rules, ad claims, and supplier failures.

---

## First implementation rule

The first version of this workflow must be manual-first and review-first.

Allowed in the first implementation:

- Draft product research cards.
- Draft supplier validation cards.
- Draft margin models.
- Draft product page copy.
- Draft ad scripts.
- Draft claim reviews.
- Summarize Shopify performance from Cap 65.
- Recommend next tests.

Forbidden in the first implementation:

- Publishing Shopify listings.
- Changing prices.
- Launching ads.
- Increasing ad budgets.
- Posting social content.
- Placing supplier orders.
- Sending customer messages.
- Issuing refunds.
- Editing live policies.
- Auto-selecting products for launch.

---

## Business model boundary

Legitimate version:

- The supplier is known before the product is advertised.
- Shipping windows are known before the product is advertised.
- Product quality is checked before scaling.
- The product page accurately describes the product.
- The customer receives tracking and support.
- Refund and return expectations are visible before checkout.
- The seller can still make the customer whole if the supplier fails.

Unacceptable version:

- Sell first, then search for any random cheap supplier after the order.
- Hide long delivery windows.
- Pretend products are locally stocked if they are not.
- Use fake reviews, fake scarcity, or fake testimonials.
- Use AI avatars to impersonate real customers, experts, doctors, celebrities, or influencers.
- Advertise unsupported medical, financial, safety, or performance claims.
- Rely on suppliers that cannot reliably fulfill orders.

---

## Non-negotiable trust boundary

This workflow must not become deceptive.

Nova must help enforce these boundaries:

- Do not advertise shipping speeds that are not true.
- Do not claim inventory is held locally if it is not.
- Do not claim a product is made in the USA unless verified.
- Do not advertise fake scarcity or fake guarantees.
- Do not sell products from unverified suppliers without checking delivery time, quality, returns, and refund risk.
- Do not hide long shipping windows.
- Do not use stolen product videos, stolen reviews, or misleading before/after claims.
- Do not generate fake customer testimonials.
- Do not use avatars to impersonate real people, doctors, celebrities, influencers, or customers.
- Do not use scraped competitor assets unless rights are clear.
- Do not make product claims that would require proof, certification, clinical evidence, or regulatory review unless that evidence exists.

Acceptable framing:

- AI-generated product demonstrations or explainer videos.
- Clearly branded virtual presenters.
- Honest product benefits that can be supported.
- Clear shipping estimates.
- Real return/refund policy.
- Real supplier and fulfillment process.
- Product mockups that do not misrepresent the physical item delivered.

---

## Product risk boundaries

Avoid by default until there is a specific compliance process:

- Medical devices, supplements, health claims, weight-loss products, and pain-relief claims.
- Baby/child safety products.
- Electrical products without clear safety certifications.
- Cosmetics or skin products without ingredient/compliance review.
- Weapons, self-defense items, surveillance tools, or restricted goods.
- Counterfeit, trademark-infringing, replica, or brand-confusing products.
- Products using copyrighted characters, logos, or protected designs.

Nova should flag these as high-risk instead of optimizing ads for them.

---

## Operating gates

### Unit economics gate

No product should move to paid ads until the margin model is explicit.

Required fields:

- Product landed cost.
- Supplier shipping cost.
- Shopify/payment processing fees.
- Expected refund allowance.
- Expected chargeback allowance.
- App/tool cost allocation.
- Estimated tax/accounting reserve.
- Maximum allowable cost per purchase.
- Break-even ROAS.
- Minimum target profit per order.

Acceptance gate:

- [ ] Break-even point is known before paid spend.
- [ ] Kill criteria are defined before paid spend.
- [ ] Product can remain profitable after refunds, failed deliveries, payment fees, and ad spend.

### Supplier SLA gate

A product is not valid until the supplier can be treated like a fulfillment partner, not just a cheap listing.

Required checks:

- Processing time.
- Delivery time to target country.
- Tracking availability.
- Return/refund process.
- Damaged-item policy.
- Inventory reliability.
- Order volume capacity.
- Product media rights.
- Packaging/branding expectations.
- Backup supplier availability.

Acceptance gate:

- [ ] Supplier SLA is written down.
- [ ] Customer-facing shipping promise is equal to or slower than supplier reality.
- [ ] Supplier failure path exists before scaling.

### Platform-account health gate

Nova must treat these as operational risks:

- Payment processor holds from high chargebacks or long shipping delays.
- Shopify store suspension for deceptive claims or prohibited goods.
- Ad account rejection for unsupported claims, misleading creative, or restricted products.
- Social account trust damage from spam posting or low-quality creative.
- Customer support overload from unclear delivery expectations.

Acceptance gate:

- [ ] Refund policy, shipping policy, privacy policy, and terms are present before launch.
- [ ] Support inbox/process exists before orders are accepted.
- [ ] Ad creative has claim review before publishing.
- [ ] Platform policy review is re-run before paid scaling.

### Customer service and post-purchase gate

Required before taking real orders:

- Order confirmation email.
- Tracking email or tracking page.
- Support email/contact form.
- Refund/return policy.
- Late-shipment response template.
- Damaged-item response template.
- Supplier failure/refund path.
- Manual review flow for suspicious orders.

Nova may draft templates, but support promises must be reviewed and approved by the user.

---

## Pause and kill-switch criteria

The workflow should pause automatically at the planning/recommendation level if any of these are observed:

- Supplier cannot provide tracking.
- Delivery estimate becomes materially longer than customer-facing promise.
- Chargeback/refund rate crosses a user-defined threshold.
- Product quality complaints repeat.
- Ad platform rejects creative for deceptive or restricted claims.
- Payment processor flags or holds funds.
- Product category is later found to be restricted, counterfeit, unsafe, or compliance-sensitive.
- Customer support backlog exceeds the defined response window.
- Margin model becomes negative after real costs are observed.

Pause means: Nova stops recommending scale-up, stops drafting expansion actions, and surfaces a review card. It does not attempt to fix the issue autonomously.

---

## Data model for future Nova workflow

Future implementation should not be a loose chat-only process. It should use explicit records.

Suggested records:

- `ProductCandidate`: product idea, niche, supplier links, risk category, status.
- `SupplierRecord`: supplier name, platform, cost, shipping estimate, SLA, backup status.
- `MarginModel`: price, landed cost, fees, ad budget, break-even CPA, target profit.
- `ClaimReview`: product claims, evidence, prohibited/risky claim flags.
- `CreativeVariant`: hook, script, asset source, avatar disclosure, claim checklist.
- `OrganicTestResult`: views, clicks, saves, comments, CTR, conversion signal.
- `PaidTestPlan`: budget, kill criteria, platform, approved creative IDs.
- `FulfillmentRun`: order ID, supplier used, tracking, delay/refund state.

These records should be inspectable and ledger-linked. Nova should not rely on hidden memory for commerce operations.

---

## State model

Every product candidate should move through explicit states.

Suggested states:

```text
idea
→ supplier_review
→ rejected | listing_draft
→ creative_draft
→ organic_test
→ paid_test_proposed
→ paid_test_approved
→ active_limited
→ paused | killed | scaled_review
```

No state transition that creates external effects should happen without an explicit user approval event.

A killed product should not be silently revived by Nova. It requires a new user-created review entry.

---

## Review card requirements

Before a product moves past draft/planning, Nova should show a review card with:

- Product name and category.
- Supplier and backup supplier.
- Shipping estimate.
- Product cost and proposed sale price.
- Break-even ad cost.
- Refund/chargeback assumptions.
- Risk category.
- Product claim checklist.
- Creative asset provenance.
- Customer-facing shipping promise.
- Required user decision: approve, revise, reject, or defer.

This card should be stored or ledger-linked so later decisions can be audited.

---

## Initial stack concept

Potential tools and services:

- Shopify — storefront and checkout.
- DSers, CJdropshipping, Zendrop, AutoDS, Spocket, Alibaba, AliExpress — sourcing/fulfillment candidates.
- CapCut, Canva, Creatify, HeyGen, Synthesia, Arcads, Runway, Pika, Kling — ad/video/avatar creation candidates.
- TikTok, Instagram Reels, YouTube Shorts — organic test channels.
- Meta Ads / TikTok Ads — paid testing only after organic proof.
- Judge.me — reviews, only real reviews.
- Track123 / AfterShip — tracking visibility.
- Shopify Email or Klaviyo — later email follow-up, governed separately.

Free-first rule applies: prefer free or low-cost tools first; flag paid/API costs before adoption.

Tool selection must be rechecked before implementation because platform pricing, API access, and terms change.

---

## Workflow phases

### Phase 1 — Product and supplier validation

- [ ] Pick a narrow product niche.
- [ ] Find 10-20 candidate products.
- [ ] Verify supplier cost.
- [ ] Verify delivery time to the United States.
- [ ] Verify return/refund policy.
- [ ] Verify product quality by ordering samples when possible.
- [ ] Identify backup suppliers.
- [ ] Reject products with unclear safety, legal, counterfeit, medical, certification, or exaggerated-claim risk.
- [ ] Confirm the supplier can provide tracking.
- [ ] Confirm the supplier can handle expected order volume.
- [ ] Confirm whether the supplier packaging creates brand/confusion issues.

Acceptance gate:

- [ ] Product has at least one verified supplier.
- [ ] Backup supplier exists or risk is explicitly accepted.
- [ ] Shipping estimate is known and can be shown to customers.
- [ ] Margin can survive product cost, shipping, payment fees, refunds, chargebacks, platform fees, taxes, and ad spend.
- [ ] Product category is not high-risk or has been separately reviewed.

### Phase 2 — Shopify listing setup

- [ ] Create Shopify product page draft.
- [ ] Use accurate product description.
- [ ] Use supplier-approved, licensed, or original product media.
- [ ] State realistic shipping time.
- [ ] State refund/return policy.
- [ ] Add tracking/support contact path.
- [ ] Avoid fake scarcity, fake reviews, and unsupported claims.
- [ ] Avoid claiming local inventory unless inventory is actually held locally.
- [ ] Add any required product warnings, sizing details, compatibility limits, or material details.

Acceptance gate:

- [ ] Product page is honest and ready for manual review.
- [ ] Fulfillment path is known before any paid ads run.
- [ ] Customer support path exists before orders are accepted.

### Phase 3 — AI video ad generation

- [ ] Generate 5-10 hooks per product.
- [ ] Generate short scripts for avatar/product demo videos.
- [ ] Generate captions and on-screen text.
- [ ] Create multiple ad variants.
- [ ] Keep avatars clearly fictional or brand-presenter style.
- [ ] Avoid impersonation and fake testimonial framing.
- [ ] Avoid fake expert endorsements.
- [ ] Avoid before/after claims unless evidence is valid and reviewable.
- [ ] Track each video variant by ID.
- [ ] Keep a claim checklist for every ad variant.

Acceptance gate:

- [ ] Each ad is tied to a product page.
- [ ] Each ad has a clear claim review.
- [ ] No ad makes unsupported claims.
- [ ] No ad uses stolen creative or impersonation.

### Phase 4 — Organic validation

- [ ] Post videos manually on TikTok/Reels/Shorts.
- [ ] Track views, saves, comments, clicks, add-to-carts, and orders.
- [ ] Do not scale paid ads until organic signal exists.
- [ ] Kill weak products quickly.
- [ ] Iterate hooks and offers.
- [ ] Watch comments for confusion, shipping concerns, trust objections, and claim-risk flags.

Acceptance gate:

- [ ] At least one product/ad angle shows measurable interest.
- [ ] Store metrics are readable through Shopify.
- [ ] Customer objections are understood before paid scaling.

### Phase 5 — Paid ad test, only after proof

- [ ] Set small daily budget.
- [ ] Test winning organic videos first.
- [ ] Cap losses with a daily spend limit.
- [ ] Monitor cost per click, add-to-cart, checkout, conversion rate, refund risk, chargeback risk, and profit margin.
- [ ] Stop campaigns that do not meet threshold.
- [ ] Do not let Nova or any automation increase budget without explicit approval.

Acceptance gate:

- [ ] Paid test has defined budget, kill criteria, and margin model.
- [ ] No uncontrolled ad spend.
- [ ] Product can be fulfilled reliably if sales spike.

### Phase 6 — Nova workflow expansion

Future Nova support should be split by authority level:

- Read-only intelligence: store/ad/product performance summaries.
- Recommendation: suggest which product/ad/price/hook to test next.
- Simulation: estimate margin and break-even ad cost.
- Drafting: create ad scripts, product descriptions, captions, and offer variants.
- Execution: only after explicit approval; posting/publishing/spending money must be governed separately.

---

## Candidate Nova capability split

Do not cram this workflow into Cap 65.

Potential future capabilities should be separate and authority-scoped:

- `shopify_product_candidate_review` — read/analysis only.
- `shopify_supplier_validation` — read/analysis only; may use governed web/API lookups later.
- `shopify_margin_simulation` — simulation only; no execution.
- `shopify_ad_script_draft` — drafting only.
- `shopify_creative_claim_review` — safety/trust review only.
- `shopify_organic_test_report` — read-only performance report.
- `shopify_paid_test_plan` — proposal only.
- `shopify_product_listing_draft` — draft only.
- `shopify_product_listing_publish` — write-capable, explicit approval required, dev-store first.
- `shopify_supplier_order_prepare` — draft/prep only.
- `shopify_supplier_order_execute` — purchase/spend action, explicit approval required, highest friction.
- `shopify_ad_publish` — external publish/spend-related action, explicit approval required.

Each write/spend/publish capability needs its own tests, NetworkMediator proof, ledger proof, and approval gate.

---

## Required Nova safeguards

Before Nova gains any execution power in this workflow:

- [ ] Supplier validation card exists.
- [ ] Product claim review exists.
- [ ] Shipping honesty check exists.
- [ ] Margin calculator exists.
- [ ] Refund/chargeback risk checklist exists.
- [ ] High-risk product category screen exists.
- [ ] Creative rights / asset provenance checklist exists.
- [ ] Avatar disclosure / impersonation check exists.
- [ ] Ad approval gate exists.
- [ ] Paid spend approval gate exists.
- [ ] Posting/publishing approval gate exists.
- [ ] Supplier-order approval gate exists.
- [ ] Ledger receipts record every external action.

---

## Explicit non-goals

This document does not authorize:

- Autonomous dropshipping.
- Autonomous paid ads.
- Autonomous supplier purchasing.
- Autonomous customer support.
- Autonomous refund handling.
- Autonomous store edits.
- Autonomous price changes.
- Autonomous product launch decisions.
- Automated deception, fake scarcity, fake reviews, or fake testimonials.

Any future automation must be separately designed as a governed capability and reviewed against Nova's execution boundaries.

---

## Relationship to Cap 65

Cap 65 remains the first foundation.

Cap 65 should only read Shopify metrics and report store performance.

This dropshipping/video-ad workflow should build on top of Cap 65 later, after Cap 65 is live-signed and locked.

Do not overload Cap 65 with sourcing, ad generation, publishing, product creation, price updates, supplier ordering, paid ad spend, or fulfillment actions.

---

## Current next action

1. Finish Shopify developer store setup.
2. Complete Cap 65 live signoff.
3. Lock Cap 65.
4. Re-check current platform/API/tool policies with live web research before implementation.
5. Create the first manual-only workflow design: product candidate card, supplier validation card, margin model, claim review, and ad script draft.
6. Only after that, consider separate governed capabilities for publishing, paid ads, supplier orders, or fulfillment.

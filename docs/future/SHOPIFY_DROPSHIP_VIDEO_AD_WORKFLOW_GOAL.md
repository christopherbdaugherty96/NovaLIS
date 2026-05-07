# Shopify Dropship Video Ad Workflow Goal

Status: future workflow goal
Scope: Shopify business model planning
Runtime impact: none
Current capability impact: none — Cap 65 remains read-only Shopify intelligence reporting

---

## Core goal

The real Shopify goal is not only to read store metrics.

The intended business workflow is:

1. Identify a product with demand potential.
2. Source it from a wholesaler, Chinese retailer, dropshipping supplier, print-on-demand provider, or other third-party fulfillment path.
3. List the product on a Shopify store without carrying inventory directly.
4. Generate short-form product ads using AI video tools, fake/virtual avatars, product mockups, captions, and scripted hooks.
5. Drive traffic through organic short-form content first, then paid ads only after proof.
6. When a customer orders, fulfill through the selected supplier.
7. Sell at a higher American retail price while preserving honest shipping, refund, and product-quality expectations.
8. Use Nova to read performance data, recommend next tests, and keep the workflow governed.

This is a dropshipping / third-party fulfillment / product-validation model, not a traditional inventory-held storefront.

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

Acceptable framing:

- AI-generated product demonstrations or explainer videos.
- Clearly branded virtual presenters.
- Honest product benefits that can be supported.
- Clear shipping estimates.
- Real return/refund policy.
- Real supplier and fulfillment process.

---

## Why this matters for Nova

Nova should eventually support the full loop:

```text
Product sourcing
→ supplier validation
→ Shopify listing
→ AI video concept generation
→ ad/script variant creation
→ organic content testing
→ Shopify performance reading
→ recommendation generation
→ user approval
→ next test cycle
```

Nova should not autonomously choose products, publish ads, spend money, change prices, or order inventory without explicit approval.

---

## Initial stack concept

Potential tools and services:

- Shopify — storefront and checkout
- DSers, CJdropshipping, Zendrop, AutoDS, Spocket, Alibaba, AliExpress — sourcing/fulfillment candidates
- CapCut, Canva, Creatify, HeyGen, Synthesia, Arcads, Runway, Pika, Kling — ad/video/avatar creation candidates
- TikTok, Instagram Reels, YouTube Shorts — organic test channels
- Meta Ads / TikTok Ads — paid testing only after organic proof
- Judge.me — reviews, only real reviews
- Track123 / AfterShip — tracking visibility
- Shopify Email or Klaviyo — later email follow-up, governed separately

Free-first rule applies: prefer free or low-cost tools first; flag paid/API costs before adoption.

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
- [ ] Reject products with unclear safety, legal, counterfeit, medical, or exaggerated-claim risk.

Acceptance gate:

- [ ] Product has at least one verified supplier.
- [ ] Shipping estimate is known.
- [ ] Margin can survive product cost, shipping, payment fees, refunds, and ad spend.

---

### Phase 2 — Shopify listing setup

- [ ] Create Shopify product page.
- [ ] Use accurate product description.
- [ ] Use supplier-approved or original product media.
- [ ] State realistic shipping time.
- [ ] State refund/return policy.
- [ ] Add tracking/support contact path.
- [ ] Avoid fake scarcity, fake reviews, and unsupported claims.

Acceptance gate:

- [ ] Product page is honest and ready to receive traffic.
- [ ] Fulfillment path is known before any paid ads run.

---

### Phase 3 — AI video ad generation

- [ ] Generate 5-10 hooks per product.
- [ ] Generate short scripts for avatar/product demo videos.
- [ ] Generate captions and on-screen text.
- [ ] Create multiple ad variants.
- [ ] Keep avatars clearly fictional or brand-presenter style.
- [ ] Avoid impersonation and fake testimonial framing.
- [ ] Track each video variant by ID.

Acceptance gate:

- [ ] Each ad is tied to a product page.
- [ ] Each ad has a clear claim review.
- [ ] No ad makes unsupported claims.

---

### Phase 4 — Organic validation

- [ ] Post videos organically on TikTok/Reels/Shorts.
- [ ] Track views, saves, comments, clicks, add-to-carts, and orders.
- [ ] Do not scale paid ads until organic signal exists.
- [ ] Kill weak products quickly.
- [ ] Iterate hooks and offers.

Acceptance gate:

- [ ] At least one product/ad angle shows measurable interest.
- [ ] Store metrics are readable through Shopify.

---

### Phase 5 — Paid ad test, only after proof

- [ ] Set small daily budget.
- [ ] Test winning organic videos first.
- [ ] Cap losses with a daily spend limit.
- [ ] Monitor cost per click, add-to-cart, checkout, conversion rate, refund risk, and profit margin.
- [ ] Stop campaigns that do not meet threshold.

Acceptance gate:

- [ ] Paid test has defined budget, kill criteria, and margin model.
- [ ] No uncontrolled ad spend.

---

### Phase 6 — Nova workflow expansion

Future Nova support should be split by authority level:

- Read-only intelligence: store/ad/product performance summaries.
- Recommendation: suggest which product/ad/price/hook to test next.
- Simulation: estimate margin and break-even ad cost.
- Drafting: create ad scripts, product descriptions, captions, and offer variants.
- Execution: only after explicit approval; posting/publishing/spending money must be governed separately.

---

## Required Nova safeguards

Before Nova gains any execution power in this workflow:

- [ ] Supplier validation card exists.
- [ ] Product claim review exists.
- [ ] Shipping honesty check exists.
- [ ] Margin calculator exists.
- [ ] Refund/chargeback risk checklist exists.
- [ ] Ad approval gate exists.
- [ ] Paid spend approval gate exists.
- [ ] Posting/publishing approval gate exists.
- [ ] Ledger receipts record every external action.

---

## Relationship to Cap 65

Cap 65 remains the first foundation.

Cap 65 should only read Shopify metrics and report store performance.

This dropshipping/video-ad workflow should build on top of Cap 65 later, after Cap 65 is live-signed and locked.

Do not overload Cap 65 with sourcing, ad generation, publishing, product creation, price updates, or fulfillment actions.

---

## Current next action

1. Finish Shopify developer store setup.
2. Complete Cap 65 live signoff.
3. Lock Cap 65.
4. Then create a separate design for the dropshipping/video-ad workflow using the authority-tier model above.

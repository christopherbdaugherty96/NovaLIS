# Hydrogen And Oxygen Storefront Build Rules
Date: 2026-04-12
Status: Inactive reference packet
Scope:
- Shopify Hydrogen storefront work
- Oxygen deployment targets
- Storefront performance, maintainability, and integration hygiene

Authority note:
- this is not an active Nova-wide build rule
- this packet is a preserved storefront standard for later adoption or selective use
- only apply it when building or reviewing a Shopify Hydrogen storefront

## Purpose

This packet defines a practical build and review standard for Shopify Hydrogen storefront work.

It exists to prevent the most common failure pattern in storefront projects:

`the app works locally, but the data flow, cache behavior, cart handling, and deployment shape become inconsistent over time`

These rules are meant to make Hydrogen storefronts:
- faster
- more predictable
- easier to review
- easier to deploy safely
- less likely to drift into old Remix-era patterns or raw hand-rolled HTML patterns

## When To Use This

Use this packet when:
- building a new Hydrogen storefront
- reviewing a Hydrogen storefront implementation
- refactoring existing Hydrogen data-loading code
- debugging cart, cache, session, or Oxygen deployment behavior

Do not treat this as a general frontend rule for:
- non-Shopify web apps
- Nova dashboard work
- generic React applications
- backend-only services

## Core Rule

If the project is a Hydrogen storefront, the team should build and review against:

`loader discipline + cache discipline + Hydrogen-native component usage + correct cart/session behavior + Oxygen-safe deployment behavior`

## Required Build Rules

### 1. Loader Patterns: Critical / Deferred Split

Every route loader should explicitly separate:
- critical data needed for first paint
- deferred data that can load after the core page is usable

What this means in practice:
- above-the-fold data should be loaded as critical
- low-priority recommendation, editorial, or secondary merchandising data should be deferred
- loaders should be shaped for user-perceived speed, not just for developer convenience

Review questions:
- what must be present before the route can render correctly?
- what can appear after the page is already usable?
- is non-critical data blocking initial render unnecessarily?

Red flag:
- a large loader fetches everything synchronously even though only a fraction is needed for first paint

### 2. Caching: Explicit Strategy On Every Storefront Query

Caching is the number-one default gap in baseline Hydrogen implementations.

Every `storefront.query()` call should have an intentional cache strategy.

Expected practice:
- choose the cache behavior explicitly
- do not rely on unstated defaults
- match cache strategy to the data type

Typical cache thinking:
- stable merchandising or CMS-style data can usually tolerate longer caching
- inventory, cart-adjacent, or rapidly changing session-sensitive data usually needs much tighter control
- route behavior should make cache decisions obvious during review

Review questions:
- what is the cache policy for this query?
- is the cache lifetime appropriate for the volatility of the data?
- does this query need to vary by country, language, or context?

Red flag:
- `storefront.query()` appears without a visible cache decision

### 3. GraphQL Conventions

Hydrogen GraphQL usage should follow a consistent convention set.

Expected conventions:
- use `#graphql` tagged template literals
- use `as const` where appropriate to preserve stronger typing and stable query definitions
- use `@inContext(...)` when the route depends on country, language, or market context
- prefer fragment reuse over copy-pasted field selections
- keep query shapes readable and composable rather than hiding them behind ad hoc string assembly

Review questions:
- is this query written in the standard Hydrogen style?
- does it reuse fragments where reuse improves consistency?
- is market or localization context being handled explicitly?

Red flags:
- raw string GraphQL without the usual Hydrogen conventions
- repeated copy-pasted field selections across multiple files
- context-sensitive storefront queries without visible `@inContext`

### 4. Prefer Hydrogen Components Over Raw HTML Reimplementation

Use Hydrogen-native components when they are the intended surface.

Prefer:
- `<Image />`
- `<Money />`
- `<CartForm />`
- `<Pagination />`

over custom raw HTML patterns that manually duplicate Hydrogen behavior without a reason.

Why:
- these components encode platform-specific best practices
- they reduce formatting drift
- they make review easier because intent is clearer

Review questions:
- is there a Hydrogen component that should be used here?
- are we hand-rolling formatting or cart behavior that Hydrogen already solves?

Red flag:
- repeated custom money formatting, image handling, cart forms, or pagination logic with no clear justification

### 5. Cart And Session Behavior Must Stay Server-Correct

Cart behavior should use Hydrogen's intended action flow rather than improvised form patterns.

Expected practice:
- use `<CartForm />` for cart mutations
- keep cart actions aligned with the server-side flow
- commit the session in the server response when required
- treat cart and session as correctness-critical, not cosmetic

In practical terms:
- cart updates should survive the next request
- session writes should not be silently skipped
- the server should remain the source of truth for cart mutations and persistence behavior

Red flags:
- cart mutations triggered through arbitrary client-side fetches without the normal Hydrogen flow
- missing session commit in server code where persistence is expected
- cart behavior that works only until refresh or next navigation

### 6. Customer Account API Is Separate From Storefront API

The Customer Account API and Storefront API should be treated as separate systems with separate purposes.

Do not blur them together conceptually.

Expected practice:
- use the Storefront API for storefront data concerns
- use Customer Account API only for customer-account-specific flows
- keep auth and account behavior clearly separated from product/catalog behavior

Review questions:
- is this really storefront data, or is it customer-account data?
- are we crossing API boundaries in a way that makes auth or maintenance harder?

Red flag:
- customer-account flows being implemented as if they were just another storefront query

### 7. Analytics Must Be Deliberate, Not Bolted On

Analytics should not be an afterthought added inconsistently at the end.

Expected practice:
- use view tracking components or the standard Hydrogen/Shopify analytics surfaces
- make page-view and key commerce events intentional
- keep tracking logic consistent across comparable route types

Review questions:
- does this route emit the tracking it should?
- are product, collection, cart, and purchase-adjacent events being tracked in a coherent way?
- is analytics implemented through the intended integration surface instead of one-off event wiring?

Red flag:
- analytics added only on a few pages or mixed between multiple incompatible approaches

### 8. Oxygen Deployment Rules Must Be First-Class

Oxygen deployment requirements should be treated as part of the build standard, not as an afterthought.

Expected practice:
- target the correct worker/runtime format
- document required environment variables
- keep deploy commands explicit
- review runtime assumptions for Oxygen rather than assuming generic Node hosting behavior

Review questions:
- is the output shape correct for Oxygen?
- are required environment variables documented?
- would another developer know how to deploy this without guessing?

Red flag:
- storefront code is built as if deployment details can be figured out later

## Common Mistakes Table

| Mistake | Why It Hurts | Corrective Direction |
| --- | --- | --- |
| Loading all route data as critical | slows first render and hides what actually matters | split critical and deferred loader data |
| Missing cache strategy on `storefront.query()` | causes inconsistent performance and stale/freshness mistakes | choose cache behavior explicitly on every query |
| Using raw GraphQL strings casually | weakens consistency and readability | use `#graphql` and standard Hydrogen query patterns |
| Repeating long field selections everywhere | creates drift and update pain | extract and reuse fragments where appropriate |
| Ignoring market context | can produce wrong regional data | use `@inContext(...)` where route context matters |
| Hand-rolling money formatting | creates inconsistency and locale issues | use `<Money />` |
| Hand-rolling storefront image behavior | loses Hydrogen-specific image conventions | use `<Image />` where appropriate |
| Building cart actions without `<CartForm />` | makes cart behavior fragile and harder to review | use Hydrogen cart form patterns |
| Forgetting session commit on server responses | cart/session state appears broken after navigation | commit session in the server response path where needed |
| Treating Customer Account API like Storefront API | blends auth/account concerns into storefront logic | keep the two APIs conceptually and structurally separate |

## Red Flags: Self-Check Triggers

Use these as a quick self-review before submitting or shipping storefront work.

Ask:
- am I importing from old Remix-era paths that Hydrogen no longer expects?
- did I add a `storefront.query()` without an explicit cache decision?
- did I fetch too much synchronously in a route loader?
- am I hand-rolling money, image, cart, or pagination behavior that Hydrogen already provides?
- did I mix customer-account concerns into storefront data flow?
- did I forget `@inContext(...)` for country or language-aware storefront data?
- did I make analytics inconsistent across comparable pages?
- did I assume generic hosting behavior instead of Oxygen deployment rules?
- did I skip documenting required environment variables?
- does the implementation work locally only because the happy path hides session or cache mistakes?

If the answer to any of those is "yes" or "maybe," the implementation needs another pass.

## Review Checklist

When reviewing a Hydrogen storefront PR or implementation, check:
- loader critical/deferred split is intentional
- every Storefront query has an explicit cache strategy
- GraphQL follows the standard conventions
- Hydrogen-native components are preferred where appropriate
- cart mutations use the intended Hydrogen flow
- server-side session behavior is correct
- Customer Account API usage is clearly separate
- analytics are consistently applied
- Oxygen deployment assumptions are documented
- known red flags were checked before handoff

## How It Was Tested

Every storefront delivery should include a plain-language testing section.

Minimum expected format:

### How It Was Tested
- verified route renders locally
- verified critical content appears before deferred content
- verified cache-sensitive queries behave as intended
- verified cart add/update/remove behavior
- verified cart/session persistence across navigation or refresh
- verified customer-account-sensitive flows separately from storefront data
- verified analytics hooks or tracking surfaces on the affected route(s)
- verified Oxygen deployment assumptions or documented what still requires deployment validation

If something was not tested, say so directly.

Do not leave testing implied.

## Suggested Adoption Language

If this packet is later promoted into an active project rule, the shortest good rule is:

`For Shopify Hydrogen storefront work, always use intentional critical/deferred loaders, explicit cache strategy on every Storefront query, standard GraphQL conventions, Hydrogen-native commerce components, correct cart/session server handling, separate Customer Account API usage, analytics coverage, Oxygen-aware deployment assumptions, and a written "How It Was Tested" section.`

## Short Version

The point of this packet is simple:

Hydrogen storefront work should not stop at:

`it renders`

It should reach:

`it renders, caches correctly, uses the platform properly, handles cart/session correctly, deploys cleanly, and is reviewable by another developer without guesswork`

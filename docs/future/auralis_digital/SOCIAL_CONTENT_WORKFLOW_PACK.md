# Auralis Social Content Workflow Pack

Status: future planning.

This document defines a future Auralis Digital workflow pack for local-business social media content generation and review.

It is not runtime truth, does not implement publishing, and does not authorize Nova to post, message, buy ads, or act on client accounts.

## Core idea

Auralis should not offer a generic social media generator.

Auralis should offer a local-business content workflow that turns business context, website audit findings, services, seasonal promos, and customer pain points into reviewable social media drafts.

```text
business profile
→ audit / service context
→ content ideas
→ captions
→ reel scripts
→ image prompts
→ calendar
→ human review
→ manual scheduling / posting
```

## Best product framing

### Local Business Visibility Pack

A recurring support package for local businesses that need practical website + content help.

Possible included outputs:

- website visibility audit
- Google/profile improvement notes
- 12 social posts per month
- 4 reel scripts per month
- monthly promo calendar
- review-response drafts
- website update suggestions
- content approval queue

## Fit with existing Auralis offer

Auralis currently sells website refreshes, basic websites, standard growth websites, and monthly website support.

Social content can become an add-on:

- Website Refresh — $250
- Basic Website — $500+
- Standard Website — $1,000+
- Monthly Website Support — $250/month
- Social Content Add-on — $150–$300/month
- Website + Social Support Bundle — $400–$600/month

Pricing is planning-only and should be tested manually before being treated as a real offer.

## Best first niches

### First niche: restaurants / bars / mobile bartending

Reason:

- strong visual content needs
- recurring specials, menus, events, holidays, promotions
- user has restaurant/bar background
- Pour Social creates related authority

### Second niche: lawn care / contractors

Reason:

- before/after content works well
- local lead value is clear
- easy bundle with website refresh and quote-request flow

## Workflow objects

### ClientVoiceProfile

Stores approved tone and style for a client.

Fields:

- client_name
- industry
- city / service area
- tone
- words to use
- words to avoid
- offers
- seasonal themes
- approval notes

### ContentCard

A single content idea/draft.

Fields:

- client
- platform
- content_type
- topic
- goal
- draft_caption
- image_prompt
- reel_script
- call_to_action
- claim_check_required
- approval_status
- scheduled_date
- notes

### ContentCalendar

A monthly plan.

Fields:

- client
- month
- weekly themes
- post slots
- promo dates
- seasonal hooks
- review deadlines

### PlatformVariant

A version of a post for a specific platform.

Platforms:

- Facebook
- Instagram
- TikTok
- Google Business Profile
- LinkedIn if applicable

### ClaimCheck

Prevents unverified or risky claims.

Examples requiring review:

- “best in town”
- price claims
- legal/compliance claims
- health/safety claims
- guaranteed results
- client testimonials
- before/after claims

## Nova role later

Nova may help:

- create content ideas
- draft captions
- draft reel scripts
- generate image prompts
- repurpose long-form content
- create weekly/monthly content calendars
- suggest posting schedules
- identify claim-check risks
- prepare review packets
- track client approval state

Nova may not:

- post automatically
- message customers
- buy ads
- access client accounts without governed connector design
- impersonate a client without an approved voice profile
- use copyrighted content blindly
- make unverified claims
- publish without review

## First manual MVP

Do not build an app first.

Manual validation steps:

1. Pick one niche: restaurants/bars or lawn care/contractors.
2. Create 30 reusable post templates.
3. Create a Google Sheet content calendar.
4. Create 3 mock client packs.
5. Generate example posts manually.
6. Use best examples in Auralis outreach.
7. Offer social content as a monthly add-on only after samples are strong.

## Simple weekly routine

```text
Monday: choose weekly theme and promo
Tuesday: draft posts and reel scripts
Wednesday: human edit / claim check
Thursday: client approval packet
Friday: schedule or manually post approved content
```

## Free-first tools

- Google Sheets or CSV for content calendar
- Canva for manual designs
- CapCut for short videos
- GitHub docs for templates/prompts
- Nova later for drafting and context
- Local Look Pro / Auralis audits for content source material

## Integration with Local Look Pro

Local Look Pro can generate website/visibility audit findings.
Those findings can become social content prompts.

Example:

```text
Audit finding: no clear service explanation.
Content output: “3 things to ask before hiring a lawn care company.”
```

## Integration with Pour Social

Pour Social can provide event/bar content themes:

- wedding bar planning tips
- signature cocktail ideas
- alcohol quantity planning
- event service FAQ
- holiday party beverage ideas

These can become Auralis portfolio samples and/or a future Pour Social content workflow.

## Approval states

- draft
- internal_review
- client_review
- approved
- rejected
- scheduled_manually
- posted_manually
- archived

## Guardrails

- no autonomous posting
- no client account access by default
- no ad spend
- no customer messaging
- no unverified business claims
- no copyrighted asset use without review
- no health/legal/compliance claims without explicit verification

## Proof requirements before runtime integration

Before this becomes a Nova runtime workflow, prove:

- ContentCard schema works manually
- ContentCalendar works manually
- claim checks catch risky claims
- approval status is visible
- drafts are not published automatically
- client voice profile is explicitly approved
- Nova only drafts/recommends

## Recommended first offer copy

```text
Monthly Local Content Support

We help local businesses stay visible with simple monthly social content: post ideas, captions, promo reminders, and review-ready content based on your services, website, and seasonal offers.
```

## Build boundary

Do not implement this before:

1. Nova memory loop exists.
2. Context Pack exists.
3. Routine Layer v0 exists or is planned for manual content workflows.
4. Auralis validates at least one social content sample pack manually.

## Final rule

This workflow should create drafts and review packets, not autonomous posting.

# Nova Governed Social Content Operator Design
Date: 2026-04-21
Status: Future design — not yet implemented
Source: Operator design session, converted and corrected 2026-04-21
Phase alignment: Builds on Shopify operator foundation (caps 65–76). Social capabilities
planned as caps 77–82. Operates independently; cap 65 (shopify_intelligence_report) is
preferred for product data and conversion attribution but is not a hard prerequisite.

Related: `docs/future/NOVA_SHOPIFY_GOVERNED_OPERATOR_DESIGN_2026-04-20.md`

---

## Purpose

This document defines Nova's governed social content operator — a research, draft,
approve, publish, and measure engine for short-form content. Nova researches, drafts,
packages, measures, and proposes. The human approves all public-facing actions.

The goal is not a general-purpose social automation platform. It is a repeatable,
monetizable content engine for a single, well-defined audience — and to prove it
generates cash before writing unnecessary code.

**Bounded. Explicit. Logged. User-approved before any post is published.**

---

## Architecture in Two Layers

| Layer | What Nova does | Capabilities |
| --- | --- | --- |
| **Intelligence** | Research trends, fetch analytics, read engagement signals | 77, 80 |
| **Operations** | Draft content, publish posts, draft replies, publish replies | 78, 79, 81, 82 |

Cross-cutting: **Content Memory** — a governed learning layer that tracks what works
and influences future drafts. Uses Nova's governed memory layer (dedicated
`social_content_memory` domain). No new capability required.

---

## Core Governing Principle

Nova should never become an autonomous content publisher.

The right model is:
- Nova **researches, drafts, and proposes**
- You **approve, adjust, or reject** every piece before it goes public
- Nova **publishes only what you explicitly authorize**, one post at a time
- Every research fetch, draft, publish action, and analytics pull is **logged to the ledger**

---

## Capability Registry

Planned capabilities (77–82), assigned sequentially after the Shopify operator block
(65–76). Each follows the standard P1–P6 verification path before being marked live.

| ID | Name | Authority | Write | Notes |
| --- | --- | --- | --- | --- |
| 77 | social_intelligence_research | read_only_network | No | Trend/competitor research via existing web search lane (caps 16, 48) |
| 78 | social_content_package | read_only_local | No | Draft generation — output only, no external effect |
| 79 | social_publish | external_effect | Yes | Per-post approval required; irreversible once sent |
| 80 | social_analytics_fetch | read_only_network | No | Platform engagement and conversion data |
| 81 | social_reply_assist | read_only_network | No | Fetch comments from platform API, classify, draft replies — output only |
| 82 | social_reply_publish | external_effect | Yes | Per-reply approval required; irreversible once sent |

Write capabilities (79, 82) require explicit per-platform OAuth activation before
their scopes are requested. They must not be registered until cap 78 (drafting) has
passed P5 live sign-off.

---

## 1. Niche Selection Framework

Before writing a single line of Nova content operator code, commit to one niche for
the next 90 days.

### Evaluation Criteria

| Criterion | Why It Matters |
| --- | --- |
| Monetization Clarity | Can you attach a product, affiliate offer, or service immediately? |
| Content Repeatability | Can you generate 30+ unique pieces without running out of ideas? |
| Platform Fit | Does the niche perform well on TikTok/Shorts/Reels? |
| Comment Volume | Will there be engagement to practice reply assist? |
| Competitor Weakness | Is existing content in this niche low-quality or inconsistent? |
| Personal Interest/Expertise | Will you (or the operator) stay motivated for 90 days? |

### Recommended Launch Niches

| Niche | Monetization Path | Content Angle |
| --- | --- | --- |
| AI Tools for Solopreneurs | Affiliate links to software, newsletter, consulting | Daily AI workflow tips, tool comparisons |
| Shopify Store Growth | Leads for Nova Shopify Operator, e-commerce consulting | Fixing common store mistakes, conversion tactics |
| Local Restaurant Marketing | Monthly retainer service ($500–$1,500/mo) | Behind-the-scenes content for a client restaurant |
| Real Estate Agent Lead Gen | Lead magnets → CRM → referral fees | Hyperlocal market updates, listing tours |
| Fitness for Busy Professionals | Digital workout plans, supplement affiliates | 30-second exercise demos, nutrition hacks |

For the remainder of this blueprint, **Shopify Store Growth** is used as the example
niche. This aligns with Nova's existing Shopify connector work and creates internal
synergy — social posts for a Shopify store can draw directly from Shopify product data,
sales signals, and the store's brand voice configuration defined in the Shopify operator.

### Ideal Customer Profile (ICP)

Within the Shopify growth niche, do not target "everyone with a Shopify store." Lock
one ICP before Sprint 1. Options:

- New Shopify consultants (0–2 years) growing their personal brand
- Small Shopify agencies (2–10 person teams) needing content at scale
- Solo store owners under $50k/month with weak social presence
- DTC founders with strong product but thin content output

ICP selection sharpens hooks, outreach messaging, and caption tone immediately. All
`BrandToneProfile` and `ContentPackage` defaults are ICP-specific, not generic.

---

## 2. Data Models

**File:** `nova_backend/src/social/models.py` (new module)

```python
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum


class Platform(str, Enum):
    TIKTOK = "tiktok"
    YOUTUBE_SHORTS = "youtube_shorts"
    INSTAGRAM_REEL = "instagram_reel"
    X = "x"


class BrandToneProfile(BaseModel):
    """Defined once per niche/ICP; used in all generation prompts. Required input
    before any content generation begins — Nova will not draft without it."""
    primary_tone: str           # e.g. "educational", "bold", "calm expert"
    sentence_style: str         # e.g. "short punchy", "conversational", "data-driven"
    hook_pattern: str           # e.g. "question", "controversial statement", "quick win"
    cta_style: str              # e.g. "soft suggestion", "direct link", "comment for more"
    forbidden_phrases: List[str] = []   # e.g. "game-changer", "secret hack"
    target_icp: str             # e.g. "new Shopify consultants 0-2 years"


class ContentResearchSource(BaseModel):
    """A piece of trend or competitor intelligence used to generate content ideas."""
    source_url: Optional[str] = None
    platform: Platform          # Platform where the trend/insight was spotted
    insight: str
    engagement_metric: Optional[int] = None    # likes, views, etc.
    captured_at: datetime


class ResearchBrief(BaseModel):
    """Daily output of the research module — 3–5 content angles with supporting data."""
    date: datetime
    niche: str
    icp: str
    angles: List[ContentResearchSource]  # Each angle is a sourced, timestamped insight


class ContentPackage(BaseModel):
    """A complete, platform-ready post draft awaiting approval."""
    id: str
    niche: str
    platform: Platform
    brand_tone: BrandToneProfile

    # Conversion intent — must be explicit, not assumed
    offer_type: str             # e.g. "lead_magnet", "affiliate", "service", "product"
    target_audience: str        # e.g. "new Shopify founders under $50k/month"
    conversion_goal: str        # e.g. "email_signup", "link_click", "dm_inquiry"

    # Core creative
    hook: str
    script: str                 # Full spoken text / caption body
    caption: str
    hashtags: List[str]

    # Visual direction
    thumbnail_concept: str
    shot_list: List[str]        # For video content
    overlay_text_timeline: List[dict]   # {"timestamp": 2.0, "text": "..."}

    # Scheduling recommendation
    recommended_post_time_utc: datetime

    # UTM tracking (populated at publish time)
    utm_campaign: Optional[str] = None
    utm_content: Optional[str] = None  # Set to id at publish time

    # State
    published: bool = False
    publish_url: Optional[str] = None
```

`offer_type`, `target_audience`, and `conversion_goal` are required fields, not
optional. Content that does not know what it is trying to cause cannot produce clean
revenue attribution. These fields are also what connect social performance back to
Shopify conversion data when the two operators are running together.

---

## 3. Phase 1: Research and Draft Engine (Weeks 1–2)

**Goal:** Produce a daily queue of 5 complete, niche-specific content packages without
any platform integration. Validate quality manually before publishing anything.

### Research Module

Uses existing Nova capabilities (cap 77 — social_intelligence_research, backed by
web search caps 16 and 48) to gather:

- Trending topics in the Shopify/e-commerce niche (Google Trends, X search, TikTok
  Creative Center)
- Top-performing competitor content (manually seeded account list, then public metrics)
- Common questions from Shopify subreddits, Facebook groups, YouTube comments

Output: a daily `ResearchBrief` containing 3–5 distinct content angles with supporting
data. Each angle is sourced and timestamped.

### Drafting Module

Combines `ResearchBrief` + `BrandToneProfile` + `ContentMemoryStore` (Section 5) to
generate `ContentPackages` via cap 78 (social_content_package).

Uses a structured LLM prompt with a strict output schema so the result can be
parsed directly into a `ContentPackage` object without free-form cleanup.

Example prompt pattern:
```
You are Nova, a content strategist for a Shopify growth brand.
Brand Tone: {brand_tone.primary_tone}. Sentences: {brand_tone.sentence_style}.
ICP: {brand_tone.target_icp}.
Niche: Shopify store optimization for beginners.
Offer type: {offer_type}. Conversion goal: {conversion_goal}.

Research Insight: {insight}
Top Performing Hook Pattern from Memory: {best_hook_pattern}
Avoid these patterns (low engagement): {low_performing_patterns}

Generate a TikTok script (15-30 seconds) with:
- Hook (first 2 seconds)
- Body (value delivery)
- Call to Action aligned with conversion_goal
- Caption with 3-5 relevant hashtags
- Shot list for a simple talking-head video
```

### Phase 1 Dashboard (Minimum Viable)

Simple queue view in the Nova Agent page (vanilla JS — `dashboard-control-center.js`
or a new `dashboard-social.js` surface, not a separate React application):

```
Nova Content Queue — 2026-04-21
────────────────────────────────────────────────────────
1. Hook: "Why your Shopify store has traffic but no sales"
   ICP: New Shopify founders | Goal: email_signup | Offer: lead_magnet
   Script: ... [expand]
   [Approve]  [Edit]  [Reject]
────────────────────────────────────────────────────────
2. Hook: "The one app every new store needs"
   ICP: New Shopify founders | Goal: link_click | Offer: affiliate
   Script: ...
   [Approve]  [Edit]  [Reject]
────────────────────────────────────────────────────────
```

No publishing happens in Phase 1. This phase is purely for validating content quality,
hook consistency, and ICP alignment before any platform connection is made.

---

## 4. Phase 2: Lightweight Media Pipeline (Weeks 3–4)

**Goal:** Turn approved `ContentPackage` drafts into publishable video files without
expensive AI generation.

### Template-Based Assembly (Start Here)

Use FFmpeg with pre-built templates as the Nova-native rendering path. FFmpeg is
already bundled in the Nova runtime (`nova_backend/tools/`).

- **Template A** — Talking head: Nova provides the script and teleprompter output.
  Human records. Nova handles subtitle generation (.srt) and any overlay text.
- **Template B** — Stock footage + text overlays: Nova queries Pexels/Pixabay API
  for relevant clips using the `shot_list` from the ContentPackage, generates subtitle
  file, assembles via FFmpeg.
- **Template C** — Screen recording: Nova generates a Loom-style script for walking
  through a Shopify dashboard; human records the screen capture.

**Note on Remotion:** The original design referenced Remotion (programmatic React
video). Remotion requires a React/Node.js rendering environment. Nova's frontend is
vanilla JS and Nova's backend is Python. Remotion would need to be a separate
standalone rendering service, not embedded in Nova's stack. FFmpeg templates are the
correct Nova-native path. Remotion can be revisited if a separate rendering service
is warranted later.

### When to Introduce AI Video Generation

Only after proving:
1. The niche content is resonating (high engagement on manually created videos)
2. Revenue from the content justifies the API cost

Start with a single tool (e.g. HeyGen for avatar-based videos) for specific,
high-volume content types only. Do not build dependency on AI video generation
before the content model is proven.

### Human Voice Recording Workflow

For B2B niches like Shopify growth, real human voiceovers build trust faster than
AI-generated audio. Nova's role:
- Generate the script
- Provide a teleprompter view in the dashboard
- Propose silence gap edits using Descript API or similar — presents proposed
  edits for user review before any audio file is modified

---

## 5. Content Memory Layer

**Goal:** Prevent Nova from repeating failed patterns and accelerate discovery of
winning formulas.

Introduced in Phase 1, enhanced continuously as performance data arrives.

### ContentMemoryEntry Schema

**File:** `nova_backend/src/social/memory.py` (or extend existing memory layer)

```python
class ContentMemoryEntry(BaseModel):
    id: str
    niche: str
    icp: str                    # Matches BrandToneProfile.target_icp
    platform: Platform
    content_type: str           # "hook", "topic", "cta", "format"

    # The pattern being tracked
    pattern: str                # e.g. "question hook", "list format", "urgency CTA"

    # Performance data (populated after analytics fetch)
    impressions: Optional[int] = None
    engagement_rate: Optional[float] = None
    click_through_rate: Optional[float] = None
    conversion_count: Optional[int] = None     # Leads or sales attributed via UTM

    # Nova's learning
    effectiveness_score: float = 0.5  # 0.0 to 1.0; starts neutral, updated via analytics
    last_used_at: datetime
    usage_count: int
    notes: Optional[str] = None        # Human annotation — always surfaces to user
```

### Usage in Generation

- When drafting hooks: Nova queries memory for top-performing hook patterns for this
  niche and ICP
- When selecting topics: Nova avoids topics with historically low engagement
- When writing CTAs: Nova retrieves the CTA with the highest conversion rate for the
  target conversion_goal
- Memory query results are shown to the user alongside the draft — not applied silently

### Storage

Initially: SQLite table under `nova_backend/memory/social_content_memory.db`. Governed
by Nova's standard memory governance (exportable, editable, deletable by the user).
Later: vector store for semantic similarity queries once the dataset is large enough
to warrant it.

Memory updates are a governed write to the `social_content_memory` domain — logged,
not silent. Analytics data is never written to memory without displaying the update
to the user first.

---

## 6. Phase 3: Single-Platform Publishing with Approval Gate (Weeks 5–6)

**Platform choice:** YouTube Shorts first — owned channel, reliable API, less
aggressive anti-automation policy than TikTok for initial validation.

### Connector Registration

Each social platform requires a dedicated connector entry in
`nova_backend/src/config/connector_packages.json` before OAuth can be initiated.
YouTube Shorts is the first platform; subsequent platforms (Instagram, TikTok, X)
each require their own connector package entry following the same pattern. Write
capabilities (cap 79, cap 82) must not be registered until the corresponding
read capabilities (77, 78, 80) have passed P5 live sign-off.

### Social Platform Authentication

YouTube OAuth is a separate connector from Shopify OAuth. Setup:
1. User initiates YouTube connection through Nova's Settings or Agent page
2. Nova presents the OAuth authorization URL with the minimum required scopes
   (`youtube.upload` for publishing, `youtube.readonly` for analytics)
3. User authenticates and approves in Google
4. Token stored through the governed identity layer (`nova_backend/src/identity/`)
5. Connection state surfaced in Trust and Settings alongside other connector states

**X (Twitter) note:** X posting requires a paid Basic tier API subscription or higher.
This cost must be surfaced to the user before X publishing is enabled — Nova cannot
post to X without a paid API subscription. Read-only access (engagement metrics) is
available on the free tier. This is already documented in the Shopify operator social
platform section; it applies equally here.

### Publishing Workflow (cap 79 — social_publish)

1. User approves a `ContentPackage` in the Nova content queue
2. Nova presents the exact content, platform, account, and scheduled time before
   any action is taken
3. User confirms publish
4. Nova calls YouTube Data API `videos.insert` with:
   - Video file (rendered in Phase 2)
   - Title (hook + niche keyword)
   - Description (caption + affiliate links + UTM parameters)
   - Tags (hashtags)
   - `categoryId` and `privacyStatus` (start with `unlisted` for first 3 posts,
     then `public` once quality is confirmed)
5. Nova logs to ledger: capability_id=79, content_id, platform, account, publish_url,
   approval reference, UTM campaign
6. `ContentPackage.published` is set to True; `publish_url` recorded

Nova does not publish autonomously. Every post is a discrete explicit approval.

### Approval Gate

Publish is a high-consequence action — once a post is live it is visible. The approval
gate for cap 79 treats this as an `external_effect` capability requiring confirmation
(same model as cap 64 send_email_draft). The user sees exactly what will be posted
before confirming.

### Bulk Approval and Trusted Templates (Phase 5+, not Phase 1)

To prevent approval fatigue, introduce only after Phase 5 validation:

- **Bulk Approve:** Checkbox selection for multiple safe posts of the same template type
- **Trusted Template:** A `ContentPackage` derived from a proven template can be
  auto-published if:
  - It matches a pre-approved pattern (e.g. daily Shopify tip format)
  - It has a computed `risk_score` below threshold (risk_score is not in the current
    `ContentPackage` model — must be added or computed at evaluation time in Phase 5+)
  - It is within a volume cap (max 1 auto-post per day)

These are governed lanes, not open sluices. Every auto-action still passes through
a pre-approved capability envelope with an expiration. This connects directly to the
Phase 6 policy layer and the SOP/Playbook Engine designed in the Shopify operator doc.

---

## 7. Revenue Dashboard

**Principle: Views are vanity. Revenue is truth.**

### UTM and Tracking Infrastructure

Every link Nova generates (affiliate, product page, lead magnet) includes UTM parameters.
These are populated in `ContentPackage` at publish time:

```
utm_source=nova_content
utm_medium=social
utm_campaign={platform}_{date}
utm_content={content_package_id}
```

Nova stores these parameters with each published post in the ledger and in the
`ContentPackage` record. Conversion attribution requires correlating `utm_content` ID
with revenue events — which comes from either:

- **Google Analytics API** — planned connector (not yet in connector registry; requires
  its own OAuth and governed connector entry before Nova can pull GA4 data)
- **Shopify analytics** — if the Shopify operator (cap 65) is also active, Nova can
  pull Shopify order data and correlate against UTM-tagged traffic directly without
  needing a separate GA4 integration

The Shopify analytics path is the preferred first implementation because it reuses
existing infrastructure. GA4 integration is a planned second step.

### Dashboard Metrics (Priority Order)

| Metric | Why It Matters |
| --- | --- |
| Revenue per Post | The ultimate KPI |
| Click-Through Rate | Hook and caption effectiveness signal |
| Engagement Rate | Platform algorithm signal |
| Conversion Rate | Landing page and offer strength |
| Cost per Post | Profitability if paid tools are in use |

Display as a leaderboard of top-performing content, ranked by Revenue per Post.
Each row links back to the original `ContentPackage` and the `ContentMemoryEntry`
patterns it used — so you can see what to repeat.

---

## 8. Phase 4 and 5: Analytics Loop and Reply Assist (Weeks 7–10)

### Analytics Feedback Loop

Analytics fetch is user-initiated, not scheduled. Nova does not poll platforms
autonomously. The user triggers cap 80 from the Revenue Dashboard ("Refresh Analytics")
or the content queue row for a specific post.

After each post's analytics stabilize (3–7 days post-publish):
1. User triggers analytics refresh — Nova fetches platform engagement data via cap 80 (social_analytics_fetch)
2. Nova compares actual performance against the ContentPackage's `conversion_goal`
3. Nova proposes `ContentMemoryEntry.effectiveness_score` updates for each pattern used,
   displayed to the user before any write occurs
4. User confirms — scores are written to `social_content_memory` domain and logged

This closes the loop: research → draft → publish → measure → memory → better draft.

### Reply Assist (caps 81 and 82)

Comment classification using few-shot prompting (not a fine-tuned classifier —
Nova has no ML training infrastructure and fine-tuning adds a dependency that is
not justified at this stage):

| Comment Type | Nova Action |
| --- | --- |
| SAFE_QUESTION (e.g. "What app is that?") | Draft templated reply with link (cap 81) |
| POSITIVE | Draft friendly acknowledgment reply (cap 81) |
| NEGATIVE | Surfaced in reply inbox with NEGATIVE label — no reply drafted, no action taken |
| SPAM | Suggest deletion — requires explicit approval before any action |

Reply drafts are presented in a review inbox on the Agent page. Cap 82
(social_reply_publish) requires explicit per-reply approval. Nova does not reply
to comments autonomously under any condition.

---

## 9. Service-First Monetization: $0 → $5k/month

Do not wait for a polished SaaS. This is the fastest path to revenue.

### Month 1: Build While Selling

- **Week 1:** Lock niche (Shopify growth) and ICP. Create a landing page offering
  "Done-for-You Short-Form Content for Shopify Experts."
- **Week 2:** Build Phase 1 draft engine (research + drafts). Use it to create 5
  sample content packages as portfolio proof.
- **Week 3:** Cold outreach to 20 Shopify consultants/agencies on LinkedIn and X.
  Offer a free 7-day trial of daily content drafts.
- **Week 4:** Onboard first paying client at $500/month. Use feedback to refine
  templates and tighten ICP.

### Month 2: Scale Delivery

- Use revenue to pay a VA or freelancer for video editing (or use template rendering)
- Aim for 3 clients → $1,500 MRR
- Build Phase 2 media pipeline to reduce per-client labor cost

### Month 3–6: Productize

- Develop Nova dashboard for clients to view and approve their content queue
- Introduce self-serve onboarding at $99/month (low-touch) and $299/month (managed)
- Target 20+ clients → $5k–$10k MRR

The software is the delivery mechanism, not the product. The product is consistent,
niche-specific content that drives business results.

---

## 10. Transparency Requirements

Every Nova action in this integration meets Nova's standard transparency requirements:

- **Source visible:** Nova shows which sources and signals produced each research brief
- **Reasoning visible:** Nova explains why it is recommending a content angle — the
  data chain, not just the output
- **Memory visible:** When memory influences a draft, the specific patterns used are
  shown alongside the draft
- **UTM visible:** Before publishing, Nova shows the exact UTM parameters that will
  be appended to every link in the post — the user sees what will be tracked
- **Boundary visible:** Nova states when it cannot act without approval (publish, reply)
- **Log visible:** Every research fetch, draft, publish action, analytics pull, and
  memory update is in the ledger and reviewable from the Trust page

---

## 11. Connection to Shopify Operator

When both operators are active, they share data surfaces:

- **Product data:** Social content for a Shopify store can pull current product
  images, descriptions, and inventory signals from cap 65 (shopify_intelligence_report)
  rather than requiring separate manual input
- **Brand voice:** The `BrandToneProfile` defined for social content should align with
  the Shopify operator's brand voice configuration — ideally a shared governed memory
  entry rather than two separate definitions
- **Conversion attribution:** Social UTM data correlates against Shopify order data
  via cap 65 — the preferred first attribution path before adding GA4
- **Anomaly signals:** A Shopify anomaly (inventory spike, sudden traffic from a
  viral post) can trigger a social content recommendation — the cross-cutting
  anomaly detection layer in the Shopify operator feeds into the social content queue

The implementation sequence for the social operator can proceed to Phase 3
(publishing) independently of the Shopify operator. However, revenue attribution
before cap 65 (shopify_intelligence_report) is live will depend on GA4 alone.
If the Shopify operator is already at P5, prefer the Shopify analytics path — it
reuses existing infrastructure and avoids the GA4 OAuth dependency. If neither is
available yet, UTM links can be tracked manually until one of the two paths is live.

---

## 12. Implementation Sequence

| Sprint | Deliverable | Success Metric |
| --- | --- | --- |
| 1 | Lock niche, ICP, and `BrandToneProfile`. Build cap 77 research module that populates `ContentResearchSource` and `ResearchBrief`. | One research brief generated daily |
| 2 | Build `ContentPackage` generation prompt with `offer_type`, `target_audience`, `conversion_goal` (cap 78). Create queue UI in Agent page. | 5 quality drafts per day |
| 3 | Implement `ContentMemoryEntry` SQLite store (`social_content_memory.db`). Add memory queries to generation prompts. | Memory patterns visible alongside every draft |
| 4 | Build template-based video rendering (FFmpeg + stock footage via Pexels API). | One video rendered per approved draft |
| 5 | Register YouTube connector in `connector_packages.json`. Integrate YouTube OAuth. Add publish approval gate (cap 79). UTM parameters populated at publish. | One post published to YouTube Shorts with explicit approval |
| 6 | Add Shopify analytics integration for UTM conversion attribution (reuses cap 65). Revenue per post visible in Revenue Dashboard. | Revenue per post visible; attribution does not require GA4 |
| 7 | Build comment fetching and few-shot classification (cap 81 — social_reply_assist). Create reply draft inbox with SAFE_QUESTION / POSITIVE / NEGATIVE / SPAM lanes. | 10 reply drafts reviewed daily |
| 8 | Close analytics loop: user-triggered analytics refresh (cap 80), proposed `effectiveness_score` updates shown before write, confirmed scores logged. | Memory scores update after user confirmation |

No step should be skipped to move faster. Phase 3 (publishing) should not begin
until Phase 1 (draft quality) and Phase 2 (media pipeline) are both validated.
Write capabilities (caps 79, 82) must not be activated until read-only capabilities
(77, 78, 80) have passed P5 live sign-off.

# Nova Governed Content Operator - Implementation Blueprint

Version: 2.2
Date: 2026-04-21
Status: Draft ready for sprint planning
Proposed destination: `docs/future/governed_content_operator.md`
Depends on:

- Trial Loop reliability work for routing and degraded runtime.
- OpenClaw approval/envelope work before any publishing action ships.
- Current dashboard files under `Nova-Frontend-Dashboard/`.

Non-goal: This is not an autonomous social posting system. It is a governed content service workflow with approval gates.

## Executive Summary

Nova can become a governed content operator that researches, drafts, packages, measures, and proposes social content. The human approves all public-facing actions.

The goal is not to build a general-purpose social automation platform first. The goal is to build a repeatable, monetizable content engine for one defined audience, prove it can produce useful output, and connect revenue attribution early.

## Core Principle

Nova may generate and prepare content. Nova should not publish publicly or alter accounts without explicit approval.

Governance lanes:

- Research: read-only.
- Drafting: safe by default.
- Packaging: local artifact creation.
- Publishing: approval required.
- Reply assist: approval required unless a trusted template lane is introduced later.

## Niche First

Pick one niche for the first 90 days. The recommended example remains Shopify Store Growth because it aligns with the existing Shopify connector direction.

Recommended initial ICP:

**Small Shopify agencies and consultants who need consistent short-form content but do not have a dedicated content team.**

Why this ICP:

- They understand the value of content.
- They can pay for service delivery.
- They can give fast feedback.
- Their clients create repeatable content themes.
- The work can later feed the Shopify Operator path.

Other possible ICPs, deferred:

- solo store owners under $50k/month
- DTC founders with weak content
- AI tools for solopreneurs
- local restaurant marketing
- real estate lead generation

## Phase 1: Research And Draft Engine

Goal: produce a daily queue of five complete content packages with no platform integration.

Suggested package placement:

- `nova_backend/src/content_operator/models.py`
- `nova_backend/src/content_operator/content_memory_store.py`
- `nova_backend/src/content_operator/research.py`
- `nova_backend/src/content_operator/drafting.py`

This creates a clear new package rather than implying an existing `social` package. If the team prefers tighter integration, the package can be moved later, but Phase 1 should keep it isolated.

### Data Models

```python
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Platform(str, Enum):
    TIKTOK = "tiktok"
    YOUTUBE_SHORTS = "youtube_shorts"
    INSTAGRAM_REEL = "instagram_reel"
    X = "x"


class BrandToneProfile(BaseModel):
    primary_tone: str
    sentence_style: str
    hook_pattern: str
    cta_style: str
    forbidden_phrases: list[str] = Field(default_factory=list)


class ContentResearchSource(BaseModel):
    source_url: Optional[str] = None
    platform: Platform
    insight: str
    engagement_metric: Optional[int] = None
    captured_at: datetime


class ContentPackage(BaseModel):
    id: str
    niche: str
    platform: Platform
    brand_tone: BrandToneProfile

    offer_type: str
    target_audience: str
    conversion_goal: str

    hook: str
    script: str
    caption: str
    hashtags: list[str]

    thumbnail_concept: str
    shot_list: list[str]
    overlay_text_timeline: list[dict]

    recommended_post_time_utc: datetime
    published: bool = False
    publish_url: Optional[str] = None
```

### Research Inputs

Research should start conservative and source-backed:

- manually seeded competitor accounts
- public Shopify/e-commerce questions
- public YouTube or X posts where allowed
- Google Trends or platform trend pages where accessible
- existing Nova web search capabilities

Avoid brittle scraping as a dependency for Phase 1. If scraping is used, it should be optional and failure-tolerant.

### Drafting Strategy

Inputs:

- ResearchBrief
- BrandToneProfile
- ContentMemoryStore
- ICP
- offer_type
- conversion_goal

Output:

- structured ContentPackage
- reasoning notes
- source references
- risk flags

Drafts should be evaluated manually before any media pipeline exists.

## Phase 1 Dashboard

Use the current dashboard architecture first:

- `Nova-Frontend-Dashboard/dashboard-control-center.js`
- `Nova-Frontend-Dashboard/dashboard-chat-news.js`
- `Nova-Frontend-Dashboard/dashboard-surfaces.css`

Do not reference `frontend/components/*.tsx` unless the team intentionally starts a React migration.

Minimum UI:

- content queue
- package detail view
- approve for production
- edit
- reject
- source notes
- conversion goal

No publishing in Phase 1.

## Phase 2: Lightweight Media Pipeline

Goal: turn approved packages into publishable local media without expensive AI video dependency.

Recommended order:

1. human voice/talking-head workflow
2. stock footage plus overlays
3. screen recording scripts
4. optional AI avatar/video only after engagement and revenue justify cost

Nova's role:

- generate teleprompter script
- generate shot list
- generate overlay timeline
- generate subtitle file
- prepare render instructions

Implementation can start with FFmpeg or a small local renderer. Keep this behind approval.

## Phase 3: Single-Platform Publishing With Approval

Recommended first platform: YouTube Shorts.

Reasons:

- clearer API surface than TikTok
- owned channel model
- suitable for education content
- less dependence on fragile automation

Publishing flow:

1. User approves a ContentPackage.
2. Nova renders or attaches a video file.
3. User reviews title, description, tags, and links.
4. User clicks publish.
5. Nova calls platform API.
6. Nova logs the action and stores publish URL.

Capability and ledger work should be defined before this ships.

## Content Memory Layer

ContentMemoryStore tracks what works and what fails.

Suggested fields:

- id
- niche
- platform
- content_type
- pattern
- offer_type
- target_audience
- conversion_goal
- impressions
- engagement_rate
- click_through_rate
- conversion_count
- effectiveness_score
- last_used_at
- usage_count
- notes

Phase 1 can use SQLite or JSON. Later versions can add semantic search.

## Revenue Attribution

Every outbound link should carry UTM fields:

```text
utm_source=nova_content
utm_medium=social
utm_campaign=shorts_{date}
utm_content={content_id}
```

The dashboard should prioritize:

- revenue per post
- click-through rate
- conversion rate
- engagement rate
- cost per post

Views are useful, but revenue and leads decide whether the operator is working.

## Reply Assist

Reply assist should start as draft-only.

Categories:

- SAFE_QUESTION: draft a helpful answer
- POSITIVE: draft a thank-you reply
- NEGATIVE: flag for human review
- SPAM: suggest deletion, approval required

Auto-reply should wait until trusted templates and volume caps exist.

## Service-First Monetization

Fastest path:

1. Pick Shopify agency/consultant ICP.
2. Draft a cold outreach sequence.
3. Generate five sample content packages.
4. Offer a seven-day content draft trial.
5. Convert first client at a managed monthly price.

Software is the delivery mechanism. The initial product is consistent, niche-specific content that helps a real operator grow.

## Sprint Plan

| Sprint | Goal | Success Metric |
| --- | --- | --- |
| 1 | Define ICP and BrandToneProfile; create outreach sequence | 20 prospects contacted |
| 2 | Build ContentPackage prompt and daily draft queue | 5 usable drafts per day |
| 3 | Add ContentMemoryStore | Memory influences drafts |
| 4 | Add local media preparation | 1 approved package becomes a video asset |
| 5 | Add YouTube approval publish flow | 1 approved post published |
| 6 | Add UTM and basic analytics | Revenue/lead attribution visible |
| 7 | Add reply draft inbox | 10 reply drafts reviewed |
| 8 | Close analytics-to-memory loop | Effectiveness scores update |

## Recommended Next Move

Start with cold outreach, then the ContentPackage prompt. That validates demand before investing in media automation.

## First Commit Slice

The first code slice should not touch publishing APIs.

1. Add `nova_backend/src/content_operator/` with models only.
2. Add a local JSON or SQLite `ContentMemoryStore`.
3. Add a CLI or test helper that produces one ContentPackage from a static ResearchBrief.
4. Add tests for schema validation and forbidden phrase handling.
5. Only after sample quality is acceptable, add dashboard queue UI.

# Personal Personality Layer

Status: future brain/personality architecture plan / not shipped runtime capability

This document defines the Personal Personality Layer for Nova's brain/conversation system.

It is a planning artifact. It does not grant execution authority, does not bypass governance, and does not represent a shipped runtime capability.

---

## Core Idea

Nova should have one coherent personal interface above the manager and agent system.

The Personal Personality Layer receives structured feeds from Nova Core, Global Manager, domain managers, and task assistants, then presents them to the user in a consistent personal voice.

Best framing:

```text
The Personal Personality Layer is the user's relationship and presentation surface for Nova.

It makes many agents feel like one assistant.
```

It is not an execution layer.

---

## Placement

Recommended hierarchy:

```text
Owner / Human Authority
-> Personal Personality Layer
-> Nova Core
-> Global Manager
-> Domain Managers
-> Task Assistants
-> Connector Packages
-> Capability Registry
-> Governor / Execute Boundary / NetworkMediator / Ledger
```

The layer sits above Nova Core from the user's perspective, but it does not own authority. It receives and shapes operational outputs.

---

## Responsibilities

The Personal Personality Layer should:

- provide one coherent conversational interface
- receive feeds from all managers and agents
- translate structured findings into natural voice/text briefings
- preserve the user's tone and style preferences
- decide how much detail to speak versus route to dashboard/text
- maintain continuity across personal, home, and business contexts
- keep the user from feeling like they are managing many separate bots
- preserve trust, approval, and risk information in the final presentation

---

## Non-Responsibilities

The Personal Personality Layer must not:

- execute actions
- call tools directly
- bypass Nova Core
- bypass GovernorMediator
- bypass Capability Registry
- bypass Execute Boundary
- bypass NetworkMediator
- override approval requirements
- silently merge sensitive contexts
- create hidden authority

Hard rule:

```text
The Personal Personality Layer can shape presentation.
It cannot create authority.
```

---

## Agent Feed Contract

Managers and agents should emit structured feeds.

Example:

```json
{
  "feed_id": "auralis_daily_feed_001",
  "source_agent": "auralis_manager",
  "workspace": "business/auralis",
  "summary": "Three leads need review and one project has a launch blocker.",
  "priority": "high",
  "items": [
    {
      "type": "lead",
      "label": "GreenEdge Lawn Care",
      "status": "needs_reply",
      "recommended_action": "draft_intake_reply",
      "risk_tier": 2,
      "requires_approval": true
    }
  ],
  "safe_to_speak": true,
  "requires_dashboard_review": true
}
```

Feed requirements:

- source agent
- workspace
- summary
- priority
- items
- risk tier for proposed actions
- approval requirement
- safe-to-speak flag
- dashboard-review flag
- sensitivity flag when needed

---

## Personality Memory

The layer should have access to a narrow memory scope:

```text
personal/personality
```

This memory may include:

- tone preference
- verbosity preference
- preferred briefing style
- preferred business-summary style
- voice response style
- what the user usually wants surfaced first
- preferred phrasing for approvals

It must not authorize actions.

Personality memory should shape presentation only.

---

## Example Flow

Input feeds:

```text
Email/Calendar Manager:
- 6 emails need action
- 2 scheduling conflicts

Auralis Manager:
- 3 leads
- 1 project launch blocker

Pour Social Manager:
- 1 quote follow-up

Personal Manager:
- appointment tomorrow morning
```

Personal Personality Layer output:

```text
You have a business-heavy day. The main thing is Auralis: three leads came in, and one project is blocked by a missing form destination. Pour Social has one quote follow-up. You also have a calendar conflict tomorrow morning. I can open the review board with drafts and scheduling options.
```

---

## Voice Safety Rules

Voice is useful for briefings and navigation, but risky actions need visible review.

Suggested rules:

- if `safe_to_speak` is false, route to dashboard/text
- if `requires_dashboard_review` is true, summarize only and offer to open review board
- if risk tier is 3 or higher, do not rely on voice-only approval
- if content includes sensitive personal/business details, keep the spoken version compact
- if an action has external effect, preserve the approval requirement clearly

---

## Dashboard Relationship

The Personal Personality Layer should not replace the dashboard.

It should decide when to hand off to dashboard surfaces such as:

- Email Coordination Board
- Daily Command Board
- Business Command Board
- Trust Panel
- Batch Approval Review
- Workspace dashboard

Voice/text should summarize. Dashboard should review, approve, reject, defer, and receipt.

---

## Trust Requirements

When presenting agent outputs, the layer should preserve:

- source agent
- source workspace
- what Nova read
- what Nova inferred
- proposed action
- capability requested
- risk tier
- approval requirement
- expected external effect
- receipt status

It should never make a risky action sound already approved.

---

## Product Value

This layer solves a major multi-agent UX problem.

Without it:

```text
The user feels like they are managing many agents.
```

With it:

```text
The user feels like Nova is one coherent assistant backed by many controlled specialists.
```

---

## Honest Framing

Best framing:

```text
The Personal Personality Layer is the unified voice and continuity layer for Nova's governed agent system.
```

Avoid:

- autonomous personality agent
- unrestricted personal agent
- agent that can act above governance
- hidden decision-maker

The personality layer should make Nova feel personal without weakening Nova's authority boundaries.

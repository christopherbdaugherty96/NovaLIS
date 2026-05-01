# Agent Feed Contract

Status: future brain/system interface contract / not implemented

This document defines the canonical structure for feeds emitted by managers and agents and consumed by the Personal Personality Layer.

---

## Purpose

The feed contract standardizes how Nova components communicate so that:

- multiple agents can be combined safely
- the Personal Personality Layer can summarize consistently
- risk, approval, and source information is never lost
- UI and voice layers can behave predictably

---

## Canonical Feed Shape

```json
{
  "feed_id": "string",
  "source_agent": "string",
  "workspace": "string",
  "summary": "string",
  "priority": "low|medium|high|urgent",
  "items": [
    {
      "type": "string",
      "label": "string",
      "status": "string",
      "recommended_action": "string",
      "capability": "string",
      "risk_tier": 0,
      "requires_approval": false
    }
  ],
  "safe_to_speak": true,
  "requires_dashboard_review": false,
  "sensitivity": "normal|private|business_sensitive"
}
```

---

## Field Requirements

Required:

- feed_id
- source_agent
- workspace
- summary

Strongly recommended:

- priority
- items
- risk_tier within items
- requires_approval within items

Behavioral flags:

- safe_to_speak
- requires_dashboard_review
- sensitivity

---

## Rules

- feeds must include source attribution
- feeds must preserve risk tiers
- feeds must preserve approval requirements
- feeds must not collapse multiple actions into one without metadata
- feeds must not silently merge sensitive domains

---

## Flow

```text
Managers / Agents
-> emit feed objects
-> Personal Personality Layer consumes feeds
-> outputs voice/text summary
-> dashboard renders full detail
```

---

## Enforcement Direction

Future enforcement should ensure:

- Personality Layer cannot generate feeds
- Personality Layer cannot modify risk tiers
- Personality Layer cannot remove approval requirements
- Personality Layer can only transform presentation

---

## Relationship to Other Docs

- Personality behavior: docs/design/brain/PERSONAL_PERSONALITY_LAYER.md
- System architecture: docs/future/NOVA_AGENT_OPERATING_MODEL.md

---

## Goal

```text
Make all agent output structured, traceable, and safe to present.
```

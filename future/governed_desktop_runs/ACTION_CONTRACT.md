# Action Execution Contract

This document defines how individual actions inside a governed run should be structured and validated.

---

## Purpose

An action contract ensures that each allowed action is:

- clearly defined
- validated before execution
- scoped to approved inputs
- auditable

---

## Action Structure

Each action should include:

```json
{
  "action_type": "open_url",
  "parameters": {
    "url": "https://example.com"
  },
  "expected_surface": "browser",
  "expected_result": "page_loaded",
  "risk_level": "low"
}
```

---

## Validation Rules

Before execution:

- action_type must exist in allowed_actions
- parameters must match allowed scope
- surface must match allowed_surfaces
- risk_level must not exceed envelope limits

---

## Execution Rules

During execution:

- action must not modify unapproved state
- action must not trigger blocked_actions
- action must produce observable result

---

## Post-Execution Validation

After execution:

- result must match expected_result
- if mismatch → PAUSE or STOP
- log action and result

---

## Fail Conditions

- unknown action_type → DENY
- invalid parameters → DENY
- unexpected result → PAUSE
- blocked side-effect → STOP

---

## First Implementation

Start with minimal actions:

- open_url
- read_visible_content
- return_summary

Expand only after policy evaluator and tests are stable.

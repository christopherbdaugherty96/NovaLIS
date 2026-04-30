# Governed Run Envelope Schema

This document defines the first implementation-ready shape for a governed desktop/browser/OpenClaw run envelope.

This is a planning document. It is not current runtime behavior until implemented and reflected in generated runtime truth.

---

## Purpose

A governed run envelope is the contract that limits what NovaLIS may do for one approved task.

It answers:

- What is the user asking NovaLIS to do?
- What is allowed?
- What is blocked?
- What approvals are required?
- When must the run stop?
- What must be logged?

---

## Core Rule

> No envelope, no desktop/browser/OpenClaw execution.

---

## Minimum Schema

```json
{
  "run_id": "generated_id",
  "intent": "generate_voiceover",
  "goal": "Generate audio for the approved script",
  "risk_level": "medium",
  "approved_steps": [
    "open approved voice provider",
    "paste approved script",
    "generate audio",
    "download audio",
    "stop"
  ],
  "allowed_surfaces": [
    "browser",
    "elevenlabs.com",
    "approved_output_folder"
  ],
  "allowed_actions": [
    "open_url",
    "paste_approved_text",
    "click_generate",
    "download_file",
    "save_to_approved_folder"
  ],
  "blocked_actions": [
    "purchase",
    "account_change",
    "credential_entry",
    "publish",
    "send_message",
    "unrelated_browsing",
    "continue_after_completion"
  ],
  "required_approvals": [
    "start_run",
    "high_risk_action",
    "scope_expansion"
  ],
  "stop_conditions": [
    "goal_complete",
    "timeout",
    "user_cancel",
    "scope_violation",
    "executor_uncertain",
    "blocked_action_attempted"
  ],
  "timeout_seconds": 600,
  "audit_level": "step_receipt",
  "created_at": "timestamp"
}
```

---

## Required Fields

- `run_id`
- `intent`
- `goal`
- `risk_level`
- `allowed_surfaces`
- `allowed_actions`
- `blocked_actions`
- `required_approvals`
- `stop_conditions`
- `timeout_seconds`
- `audit_level`
- `created_at`

Missing required fields should fail closed.

---

## Allowed Risk Levels

```text
low
medium
high
```

Unknown risk levels should fail closed.

---

## Approval Types

```text
start_run
high_risk_action
scope_expansion
resume_after_pause
retry_after_failure
publish_or_send
purchase
credential_entry
```

Unknown approval types should fail closed unless explicitly registered.

---

## Stop Conditions

```text
goal_complete
timeout
user_cancel
scope_violation
executor_uncertain
blocked_action_attempted
policy_denied
runtime_error
```

Completion ends permission. A completed run cannot continue without a new envelope.

---

## Audit Levels

```text
summary
step_receipt
full_trace
```

Initial implementation should use `step_receipt` for governed desktop/OpenClaw runs.

---

## Validation Rules

1. Empty `allowed_actions` is invalid.
2. Empty `blocked_actions` is invalid.
3. Empty `stop_conditions` is invalid.
4. `timeout_seconds` must be greater than zero and below a configured maximum.
5. High-risk actions require explicit approval.
6. Credential entry is blocked by default.
7. Purchases are blocked by default.
8. Public publishing is blocked by default.
9. Unknown action types fail closed.
10. Unknown surfaces fail closed unless explicitly approved.
11. A run cannot start if required approval is missing.
12. A run cannot continue after a terminal stop condition.

---

## Terminal States

These states end the envelope permission:

```text
COMPLETED
FAILED
CANCELLED
DENIED
TIMEOUT
SCOPE_VIOLATION
POLICY_DENIED
```

To continue after any terminal state, NovaLIS must create a new envelope and request any required approval.

---

## First Safe Envelope

The first implementation should use a harmless read-only task:

```json
{
  "intent": "read_approved_page_title",
  "goal": "Open one approved URL, read visible page title, return result, and stop.",
  "risk_level": "low",
  "allowed_surfaces": ["browser", "approved_url"],
  "allowed_actions": ["open_url", "read_visible_content", "return_summary"],
  "blocked_actions": ["click_unapproved_link", "login", "download_file", "upload_file", "send_message", "purchase", "continue_after_completion"],
  "required_approvals": ["start_run"],
  "stop_conditions": ["goal_complete", "timeout", "user_cancel", "scope_violation", "executor_uncertain"],
  "timeout_seconds": 120,
  "audit_level": "step_receipt"
}
```

---

## Implementation Note

The schema should be implemented before connecting broader OpenClaw desktop/browser execution.

The first code version should favor strictness over convenience.

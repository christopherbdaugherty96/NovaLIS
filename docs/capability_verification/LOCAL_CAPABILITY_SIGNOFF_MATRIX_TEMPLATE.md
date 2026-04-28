# Local Capability Signoff Matrix Template

Date: 2026-04-28

Status: Verification template / not a completed signoff record

Purpose: provide a standard template for verifying local Nova capabilities before they are relied on by OpenClaw, connector workflows, or broader hands-layer behavior.

---

## Use Rule

This template does not certify any capability by itself.

A capability is signed off only when evidence exists for routing, execution, failure behavior, platform limits, and ledger/trust behavior.

---

## Capability Signoff Fields

```text
capability_id:
capability_name:
risk_type:
current_status: not_started / pass / blocked / fail / paused
platform_tested:
date_tested:
tested_by:
```

## Routing Evidence

```text
expected_route:
actual_route:
router_test_passed: yes / no / n/a
governor_mediator_used: yes / no
execute_boundary_used: yes / no / n/a
network_mediator_used: yes / no / n/a
bypass_checked: yes / no
notes:
```

## Confirmation / Approval Behavior

```text
confirmation_required: yes / no
confirmation_prompt_clear: yes / no / n/a
negative_response_blocks: yes / no / n/a
positive_response_executes_only_expected_action: yes / no / n/a
stale_confirmation_rejected: yes / no / n/a
notes:
```

## Manual Test Steps

```text
1.
2.
3.
```

## Automated Tests

```text
test_files:
commands_run:
result:
```

## Success Evidence

```text
expected_success_behavior:
actual_success_behavior:
ledger_attempt_recorded: yes / no / n/a
ledger_result_recorded: yes / no / n/a
trust_receipt_created: yes / no / n/a
user_message_clear: yes / no
```

## Failure Evidence

```text
bad_input_tested: yes / no
missing_dependency_tested: yes / no / n/a
permission_denied_tested: yes / no / n/a
safe_failure_message:
no_crash: yes / no
no_partial_action: yes / no / n/a
ledger_failure_recorded: yes / no / n/a
```

## Known Limits

```text
platform_limits:
dependency_limits:
security_limits:
UX_limits:
```

## Signoff Decision

```text
decision: pass / blocked / fail / paused
reason:
required_follow_up:
can_OpenClaw_rely_on_this: yes / no
```

---

## Required Default Rule

> **If a capability has not passed this matrix, OpenClaw and external workflows should not rely on it.**

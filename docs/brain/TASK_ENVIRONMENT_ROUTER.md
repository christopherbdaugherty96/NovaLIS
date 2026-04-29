# Task Environment Router

The Task Environment Router is the missing middle layer between conversation and execution.

It answers:

```text
For this task, what environment does Nova need to enter?
What authority is required?
Which capability would grant access?
What confirmation is needed?
What proof should exist afterward?
```

## Required Questions

- Can Nova solve this locally?
- Does it need current evidence?
- Does it need memory or project context?
- Does it need a browser?
- Does it need a signed-in account?
- Does it need to write, change, submit, send, or purchase?
- Is the capability available?
- Is the environment configured?
- Is confirmation needed?
- What happens if blocked?
- What proof will satisfy the user?

## Output Shape

```text
task_type
required_environments
environment_options
authority_required
capability_needed
confirmation_required
setup_required
proof_required
allowed_status
confidence
risk_level
blocker
recovery_path
fallback_ladder
next_safe_step
```

## Capability Contract Check

Before selecting a capability, the router should consult the capability contract.

The contract should say:

- what the capability can do
- what it cannot do
- required setup
- authority tier
- confirmation rules
- expected receipts
- fallback behaviors
- known failure modes

If a user requests an action outside the contract, the router should mark the request as blocked or future-only and offer a recovery path.

## Example

```json
{
  "task": "Find a contractor near me and draft an email",
  "task_type": "multi_step",
  "required_environments": ["web_search", "email_draft"],
  "environment_options": [
    {
      "environment": "web_search",
      "confidence": 0.94,
      "risk_level": "network_read",
      "capability_needed": "cap16_governed_web_search"
    },
    {
      "environment": "email_draft",
      "confidence": 0.88,
      "risk_level": "external_effect_draft",
      "capability_needed": "cap64_send_email_draft"
    }
  ],
  "confirmation_points": ["before_opening_email_draft"],
  "proof_expected": ["source_urls", "EMAIL_DRAFT_CREATED"],
  "recovery_path": []
}
```

## Recovery Path

If blocked, the router should not simply stop.

It should produce a recovery path such as:

- ask a clarifying question
- run a lower-authority read-only step
- produce a manual guide
- offer setup instructions
- show a dry-run plan only
- ask the user to perform a manual step and report back

Recovery paths are suggestions, not execution authority.
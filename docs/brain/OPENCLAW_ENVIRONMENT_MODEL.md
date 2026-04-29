# OpenClaw Environment Model

OpenClaw is an environment, not the brain.

Nova's brain may decide that a task requires an OpenClaw environment, but execution still requires the governed OpenClaw capability path.

## Preferred Default

Prefer an isolated OpenClaw-managed browser profile over the user's personal signed-in browser.

## Environment Types

- `openclaw_isolated_browser`
- `personal_browser_session`
- `browser_use_test_browser`
- `remote_browser`

## Provision Request Concept

OpenClaw sessions should be treated like temporary sandboxes.

Conceptual schema:

```json
{
  "task_id": "task_123",
  "environment": "openclaw_isolated_browser",
  "required_screenshots": ["before", "after"],
  "max_runtime_seconds": 300,
  "allowed_domains": [],
  "blocked_actions": ["purchase", "send", "delete", "submit_without_confirmation"]
}
```

## Proof Requirements

- session started receipt
- screenshot before meaningful action
- proposed action preview
- confirmation where required
- screenshot after action
- session closed receipt

## Personal Browser Rule

A personal browser session may contain logged-in accounts, cookies, private data, and account authority.

It should require explicit user approval and strong proof.

## No Persistent Drift

After a governed browser task, the environment should close or be explicitly preserved by user choice.

The default should avoid silent persistent state drift.
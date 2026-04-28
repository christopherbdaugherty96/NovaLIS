# Nova Connector Registry Plan

Date: 2026-04-27

Status: Future architecture plan / not current runtime truth

Purpose: define the future central registry for all Nova connectors and provider integrations. This is planning only and does not claim implementation exists today.

---

## Active Priority Note

Current active task remains RequestUnderstanding trust/action-history visibility. Do not implement the connector registry until the active priority override allows it.

---

## Executive Summary

Nova needs a connector registry before broad Google, MCP, GitHub, ElevenLabs, Home Assistant, browser, or external workflow-runner integrations.

Core rule:

> **A provider being connected is not the same as Nova being allowed to act.**

The connector registry should answer:

```text
What is connected?
What scopes does it have?
What can it read?
What can it draft?
What can it write?
What requires approval?
What is blocked?
When was it last used?
How can it be disconnected?
What receipts are required?
```

---

## Connectors To Cover Eventually

```text
Google identity
Google Calendar
Gmail
Google Drive
Google Contacts
GitHub / Git
MCP servers
ElevenLabs
OpenClaw
Home Assistant
browser/computer-use provider
n8n/external workflow runner
local filesystem/repo/document sources
future CRM/customer systems
```

---

## Suggested Registry Fields

```text
connector_id
provider_name
connector_type
status: disconnected / connected / paused / blocked / error / revoked
owner_enabled
scopes
read_capabilities
write_capabilities
draft_capabilities
allowed_actions
blocked_actions
requires_approval_for
sensitive_data_policy
network_policy
credential_storage_ref
last_used_at
last_error
receipt_policy
disconnect_supported
revoke_url_or_instructions
health_check_status
notes
```

---

## Permission Model

Connector permissions should be separated into lanes:

```text
identity_only
read_only
draft_only
local_reversible
durable_mutation
external_write
financial_or_security_sensitive
```

Default policy:

```text
identity_only and read_only can be first proofs.
draft_only may prepare but not send/submit.
local_reversible requires local capability signoff.
durable_mutation requires approval and receipts.
external_write requires approval and receipts.
financial/security-sensitive actions are blocked by default or require hard approval after mature governance.
```

---

## Required UX

The user should be able to see:

```text
Connected provider
current status
scopes granted
what Nova can read
what Nova can draft
what Nova cannot do
what requires approval
last use
last error
turn off / disconnect / revoke instructions
```

---

## Receipts

Connector use should create receipts or trace events for:

```text
connector connected
connector disconnected/revoked
connector read used
connector draft prepared
connector write proposed
connector write approved
connector write denied
connector error
connector blocked by policy
```

Example non-action statement:

```text
Nova read today's calendar. No events were created, changed, or deleted.
```

---

## Guardrails

```text
Tokens are never placed in prompts.
Scopes are minimized.
Connected status does not grant action authority.
Writes require approval unless explicitly classified safe and reversible.
Paused connectors cannot be used.
User can disconnect/revoke.
Connector results are untrusted input.
Sensitive data routing applies before cloud/model use.
```

---

## Build Order

```text
1. Define connector registry schema.
2. Add read-only registry view/API.
3. Add connector status card in settings/trust surface.
4. Register local/static planned connectors without live auth.
5. Add Google identity/read-only connector entries later.
6. Add MCP server registration later.
7. Add approval/receipt integration before writes.
```

---

## Final Rule

> **Connectors expand access. They do not expand authority without Nova governance.**

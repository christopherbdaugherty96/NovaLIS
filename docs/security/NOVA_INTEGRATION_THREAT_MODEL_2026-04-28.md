# Nova Integration Threat Model

Date: 2026-04-28

Status: Future security reference / not runtime truth until implemented

Purpose: define the main threat categories Nova must account for before broad connectors, MCP, Google, OpenClaw, ElevenLabs, browser/computer-use, Home Assistant, and external workflow runners expand.

---

## Core Rule

> **Every integration is a new authority risk unless Nova keeps data access, action approval, and receipts separate.**

---

## Threat Categories

```text
prompt injection from web pages, emails, docs, repos, or MCP outputs
tool poisoning through malicious tool descriptions or schemas
credential/token exposure
connector spoofing or unexpected remote host
excessive scopes
unreviewed external writes
browser automation submitting forms or purchases
OpenClaw worker bypassing envelopes
Home Assistant safety/security device misuse
ElevenLabs voice/data leakage or cloning misuse
hidden memory writes
ledger/receipt tampering
sensitive data sent to cloud unintentionally
supply-chain risk from third-party MCP/tools/plugins
```

---

## Integration-Specific Risks

### MCP

```text
malicious server/tool descriptions
prompt injection in tool results
filesystem + git chained risk
argument injection
path traversal
unknown remote servers
```

Required controls:

```text
tool allowlist
risk classification
read-only first
argument validation
path/domain allowlists
receipts and non-action statements
```

### Google / Gmail / Calendar / Drive

```text
token exposure
excessive scopes
email send/delete/archive mistakes
calendar auto-booking
Drive file mutation or data leak
```

Required controls:

```text
identity-first onboarding
read-only first
draft-only before send
approval queue for writes
scope visibility
revoke/disconnect
```

### OpenClaw

```text
worker bypassing Nova governance
unbounded tool calls
approval passthrough
hidden external writes
run-state confusion after failure
```

Required controls:

```text
OpenClawMediator
envelope-required execution
approval queue
run checkpoints
receipts
non-action statements
```

### ElevenLabs / Voice

```text
sensitive content sent to cloud voice
voice cloning consent risk
voice output making unsafe actions feel trusted
cost spikes from long readouts
```

Required controls:

```text
local/private fallback
cloud voice disclosure
budget controls
sensitive-data routing
no voice cloning without consent record
```

### Browser / Computer-Use

```text
form submit
purchase/book/send actions
credential exposure
web prompt injection
account settings changes
```

Required controls:

```text
screen-to-action review first
submit/save/send/buy/book require approval
sandbox boundaries
credential minimization
receipts
```

### Home Assistant

```text
unlock doors
open garage
disable alarms
security camera misuse
safety-critical device control
```

Required controls:

```text
read-only first
low-risk reversible actions only after signoff
security/safety device block or hard approval
local network mediator
receipts
```

---

## Cross-Cutting Required Controls

```text
connector registry
risk classification table
approval queue
sensitive data routing
provider budget controls
trust spans / trace cards
receipt/non-action statements
safe failure messages
revocation/disconnect
read-only/draft-only first proofs
```

---

## Non-Action Receipts

For risky integrations, always state what did not happen:

```text
No email was sent.
No calendar event was created.
No file was changed.
No purchase was made.
No external system was updated.
No connector was called.
```

---

## Final Rule

> **If Nova cannot prove an integration stayed inside its boundary, the integration should fail closed.**

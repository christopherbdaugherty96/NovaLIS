# Nova Connector Risk Classification Table

Date: 2026-04-28

Status: Future governance reference / not runtime truth until implemented

Purpose: provide one shared risk classification table for Google, MCP, GitHub, OpenClaw, ElevenLabs, Home Assistant, browser/computer-use, workflow runners, and future connectors.

---

## Core Rule

> **Connector access is not connector authority.**

Every connector/tool must be classified by what it can do, not only by what provider it belongs to.

---

## Risk Classes

| Class | Name | Meaning | Default Policy |
|---|---|---|---|
| 0 | Public read-only | Public or low-sensitivity read | May be allowed first with receipts when useful |
| 1 | Private read-only | Reads private/local/user data | Allowed only with explicit connector scope and visible status |
| 2 | Draft/proposal only | Prepares output but does not send/submit/mutate | Allowed after draft-only boundary is visible |
| 3 | Local reversible action | Changes local state that is easy to reverse | Requires local capability signoff and settings |
| 4 | Durable local mutation | Writes/moves/deletes files, repo edits, DB updates | Requires approval and receipts |
| 5 | External write | Sends/posts/books/creates/updates external systems | Requires explicit approval and receipts |
| 6 | Financial/security/safety critical | Money, locks, alarms, accounts, credentials, safety systems | Blocked by default or hard approval after mature governance |

---

## Examples

```text
Google Calendar read → Class 1
Google Calendar create event → Class 5
Gmail thread summary → Class 1
Gmail draft creation → Class 2 or Class 5 depending whether external draft is created
Gmail send → Class 5
Google Drive doc read → Class 1
Google Drive file write/delete → Class 4 or 5 depending scope
GitHub repo read → Class 1
GitHub issue/PR draft text → Class 2
GitHub issue/PR creation → Class 5
Git commit/write to repo → Class 4
MCP filesystem read → Class 1
MCP filesystem write/delete → Class 4
MCP browser page summary → Class 1
MCP/browser form submit → Class 5
Home Assistant sensor read → Class 1
Home Assistant light toggle → Class 3
Home Assistant door lock/garage/alarm → Class 6
ElevenLabs TTS output → Class 1 or provider-use event; authority effect none
ElevenLabs voice clone → Class 6 consent-sensitive
OpenClaw read-only brief → Class 1
OpenClaw draft proposal → Class 2
OpenClaw external write → Class 5
purchase/payment workflow → Class 6
```

---

## Approval Defaults

```text
Class 0: no approval required; log if useful
Class 1: connector permission required; receipt if meaningful
Class 2: draft-only label required; no send/submit/mutate
Class 3: local signoff required; may need confirmation
Class 4: approval required
Class 5: approval required
Class 6: blocked by default or hard approval after mature governance
```

---

## Required Metadata For Any Connector Tool

```text
connector_id
tool_or_action_name
risk_class
read_write_scope
requires_approval
receipt_required
sensitive_data_policy
network_policy
failure_mode
non_action_statement
```

---

## Final Rule

> **When uncertain, classify the connector action higher-risk until proven otherwise.**

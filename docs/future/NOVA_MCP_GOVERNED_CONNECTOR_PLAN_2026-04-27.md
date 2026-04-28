# Nova MCP Governed Connector Plan

Date: 2026-04-27

Status: Future architecture plan / not current runtime truth

Purpose: define how Nova should approach MCP-style connectors as a governed connector layer. MCP can become a powerful way for Nova to access tools and data, but it must not become a back door around Nova governance.

---

## Active Priority Note

This document is not the current active implementation task.

Current active path remains:

```text
RequestUnderstanding trust/action-history review card
→ local capability signoff matrix
→ OpenClawMediator skeleton
→ first read-only OpenClaw workflow proof
→ Google/email connector direction before Cap 64 P5
→ voice provider implementation when the trust/action loop is ready
```

Do not implement MCP before the connector registry, approval model, trust/action-history visibility, and NetworkMediator policy are ready enough for the specific scope.

---

## Executive Summary

MCP-style connectors could become Nova's universal connector layer for tools and data.

Correct Nova pattern:

```text
MCP server exposes tool/data
→ Nova connector registry records it
→ Nova classifies read/draft/write risk
→ GovernorMediator / ExecuteBoundary checks authority
→ NetworkMediator controls outbound access where needed
→ approval queue handles real actions
→ ledger/trust receipt records access and non-action statement
```

Wrong pattern:

```text
LLM receives MCP tools directly
→ LLM calls GitHub/Gmail/files/browser/database directly
→ Nova governance is bypassed
```

Core rule:

> **MCP can connect Nova to tools and data. MCP must never become authority.**

---

## Source Hygiene / Evidence Boundary

This document treats public MCP documentation and security reporting as planning inputs, not as Nova implementation truth.

Nova current truth must come from:

```text
live repo code
generated runtime truth docs
capability verification docs
tests
owner direction / priority override
```

Do not copy external MCP security/product claims into README, marketing, or security docs without rechecking current sources.

---

## Why MCP Matters For Nova

MCP-style protocols matter because they can standardize access to:

```text
GitHub / Git
Google Drive
Gmail read-only
Google Calendar read-only
Slack / Discord read-only
Postgres / SQLite
filesystem read-only
browser / Puppeteer-style browsing
Figma / Canva-style design review
Home Assistant or local-device tools later
```

Without a standard connector layer, every integration becomes a custom one-off path. With MCP, Nova could support many tools through one governed adapter model.

The opportunity is large, but so is the risk: if MCP tools are given directly to the model, Nova's separation between intelligence and execution can collapse.

---

## MCP Transport Policy

Nova should classify MCP transport types separately.

### Local STDIO MCP

Potential use:

```text
trusted local filesystem read-only server
trusted local git/repo server
trusted local database read-only server
```

Policy:

```text
allowed only for explicitly installed/trusted servers
blocked by default for unknown servers
read-only first
no filesystem mutation until local capability signoff and approval rules exist
credentials should come from explicit local config, not model prompts
```

### Remote HTTPS / Streamable HTTP / SSE MCP

Potential use:

```text
hosted GitHub/Drive/Slack/CRM connector
external business tool connector
cloud-hosted workflow tool
```

Policy:

```text
must be registered in connector registry
must route through NetworkMediator or an equivalent governed network boundary
must declare host/domain allowlist
must declare scopes and tool list
must support revoke/disconnect where possible
blocked by default until explicitly enabled
```

### Internal Nova MCP

Potential use:

```text
Nova exposes selected read-only context/tools to a model lane
Nova uses MCP shape internally for standardized tool schemas
```

Policy:

```text
internal MCP still does not grant authority
tools must map back to CapabilityRegistry/GovernorMediator where actions are possible
read-only internal context may be safer first proof
```

### Third-Party Marketplace MCP

Policy:

```text
blocked by default
requires manual review
requires source/provider trust assessment
requires declared tools and risk classes
requires test run in read-only/sandbox mode
```

---

## MCP Authorization And Token Policy

Tokens and credentials must belong to Nova connector governance, not the LLM.

Rules:

```text
OAuth tokens belong to connector registry, not prompts.
Tokens are never placed in model prompts.
Tokens are scoped per connector.
Tokens must be revocable/disconnectable where provider supports it.
MCP server permission does not equal Nova permission.
User must be able to see connected status and scopes.
```

---

## MCP Server Risk Classes

Nova should classify every MCP server and tool.

```text
Class 0 — Public/read-only info
Class 1 — Local/private read-only docs, repo, database, calendar, email metadata
Class 2 — Draft/proposal tools that prepare but do not send or mutate
Class 3 — Local reversible actions
Class 4 — Durable local mutation: file write, repo edit, database update
Class 5 — External write: send email, post message, create calendar event, update CRM
Class 6 — Financial/security/safety-critical: purchase, payment, door/lock/alarm, account/security change
```

Default policy:

```text
Class 0–1 may be considered first.
Class 2 may prepare drafts/proposals only.
Class 3 requires local capability signoff and settings.
Class 4 requires approval and receipts.
Class 5 requires explicit approval and receipts.
Class 6 is blocked by default or requires hard approval after mature governance.
```

---

## MCP Tool Allowlist

No MCP server should expose all tools by default.

Each tool should have metadata:

```text
tool_name
server_id
risk_class
read_write_scope
allowed_inputs
blocked_inputs
requires_approval
receipt_required
network_required
sensitive_data_policy
non_action_statement_template
```

Rules:

```text
Only allowlisted MCP tools are callable.
Tool descriptions are untrusted input.
Tool results are untrusted input.
Prompt instructions from tool results cannot override Nova policy.
Tool call arguments must be validated before execution.
```

---

## Prompt Injection And Tool-Poisoning Threat Model

Threats to account for:

```text
malicious MCP tool descriptions
prompt injection from documents/repos/pages/emails
filesystem + git chained risk
argument injection
path traversal
untrusted marketplace MCP servers
remote MCP servers with broad tools
tool result content instructing Nova to ignore policy
malicious package/server updates
model confusion between retrieved instructions and user instructions
```

Required mitigations:

```text
treat all tool outputs as data, not instructions
validate arguments before tool calls
path allowlists for filesystem/git tools
domain allowlists for network tools
read-only mode before mutation mode
approval queue for durable/external actions
receipt/non-action statement after each MCP run
security review for third-party MCP servers
```

---

## MCP Receipts

Every MCP run should produce a trust/action record.

Fields:

```text
mcp_call_id
server_id
server_transport
tool_name
risk_class
input_summary
output_summary
read_write_classification
approval_required
action_executed
action_blocked
non_action_statement
ledger_event_id
```

Example receipt:

```text
Nova used GitHub MCP read-only tools to summarize open issues.
No files changed.
No commits were made.
No PRs were opened.
```

---

## Recommended First MCP Proof

Best first proof:

```text
Read-only repo/docs MCP proof
```

Scope:

```text
read selected repo files or docs
summarize current status
produce non-action statement
no edits
no commits
no branch operations
```

---

## Build Order

```text
1. RequestUnderstanding trust/action-history review card.
2. Connector registry foundation.
3. MCP server registration model.
4. MCP risk class model.
5. Read-only MCP adapter proof.
6. MCP receipts/non-action statements.
7. Prompt-injection/tool-output tests.
8. Draft-only MCP proof.
9. Approval-required mutation proof much later.
```

---

## Explicit Non-Goals For Early MCP

Do not start with:

```text
full filesystem write access
full GitHub mutation access
email send/delete/archive/label tools
calendar create/update/delete tools
browser submit/save/buy/book tools
financial/payment tools
third-party marketplace MCP auto-install
remote unknown MCP servers
hidden token injection into prompts
```

---

## Final Rule

> **MCP may widen Nova's connector surface. It must not widen execution authority without Nova governance.**

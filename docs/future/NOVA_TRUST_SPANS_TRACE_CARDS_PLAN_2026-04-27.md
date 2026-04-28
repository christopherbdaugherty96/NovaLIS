# Nova Trust Spans / Trace Cards Plan

Date: 2026-04-27

Status: Future product/architecture plan / not current runtime truth

Purpose: define a safe trace-card model for showing what Nova understood, routed, considered, blocked, approved, executed, and did not do without exposing private chain-of-thought.

---

## Active Priority Note

This is future planning. The active implementation remains RequestUnderstanding trust/action-history visibility.

---

## Executive Summary

Nova already values ledger/trust. Trust spans would make that easier to understand as a sequence of safe, user-facing cards.

Core rule:

> **Show decisions and evidence, not private chain-of-thought.**

---

## Suggested Span Types

```text
conversation_received
request_understanding_created
route_decision_made
model_provider_selected
capability_considered
capability_blocked
approval_required
approval_decision_recorded
tool_called
tool_blocked
connector_used
voice_provider_used
receipt_created
non_action_statement_created
response_delivered
```

---

## User-Facing Trace Card Fields

```text
span_id
run_id/session_id
span_type
summary
status: info / allowed / blocked / pending / complete / failed
source
risk_level optional
capability_or_connector optional
what_happened
what_did_not_happen
receipt_id optional
timestamp
```

---

## Example Cards

```text
Nova understood: User wants help drafting an email.
Boundary: Draft-only. Nova will not send email automatically.
Authority effect: none.
```

```text
Capability considered: send_email_draft.
Result: confirmation required.
Nothing was sent.
```

```text
Connector used: Google Calendar read-only.
Result: summarized today's events.
No calendar events were created, changed, or deleted.
```

---

## What Not To Expose

```text
private chain-of-thought
raw prompts with secrets
raw tokens/API keys
full sensitive document contents
unredacted email bodies by default
internal exploit/security details that increase risk
```

Use summaries, hashes, and references when content is sensitive.

---

## Integration Points

```text
RequestUnderstanding trust/action card
approval queue
connector registry
OpenClaw run records
ElevenLabs/voice usage events
MCP tool calls
browser/screen analysis
local capability signoff
```

---

## Guardrails

```text
Trace cards do not approve actions.
Trace cards do not replace ledger.
Trace cards summarize evidence from governed paths.
Trace cards must not create hidden memory.
Trace cards should be readable by nontechnical users.
```

---

## Build Order

```text
1. RequestUnderstanding card first.
2. Define generic span/card schema.
3. Add receipt-backed cards for existing trust events.
4. Add capability-considered/blocked cards.
5. Add connector and OpenClaw cards later.
6. Add voice-provider and budget cards later.
```

---

## Final Rule

> **A user should be able to ask “what did Nova do?” and receive a clear, bounded answer.**

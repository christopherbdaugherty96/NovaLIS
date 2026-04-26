# Nova Google Connector Direction — Final Lock

Date: 2026-04-26

Status: Final lock / future connector direction summary

Related docs:

- [`NOVA_GOOGLE_ACCOUNT_AND_CONNECTOR_ONBOARDING_PLAN.md`](NOVA_GOOGLE_ACCOUNT_AND_CONNECTOR_ONBOARDING_PLAN.md)
- [`NOVA_FULL_STACK_DIRECTION_FINAL_LOCK_2026-04-26.md`](NOVA_FULL_STACK_DIRECTION_FINAL_LOCK_2026-04-26.md)
- [`NOVA_OPENCLAW_HANDS_LAYER_IMPLEMENTATION_PLAN.md`](NOVA_OPENCLAW_HANDS_LAYER_IMPLEMENTATION_PLAN.md)
- [`NOVA_VOICE_STACK_OPERATING_MODEL_2026-04-26.md`](NOVA_VOICE_STACK_OPERATING_MODEL_2026-04-26.md)

---

## Final Locked Direction

Nova should support Google sign-in and Google app connectors, but identity, access, and authority must remain separate.

Final rule:

> **Google connects data. Nova governs action.**

Expanded rule:

> **Google Sign-In identifies the user. Google connectors grant scoped access. Nova governance decides what can happen with that access.**

This is future work and should not be treated as current runtime truth until implemented and verified.

---

## What First Login Means

First login should be identity-only.

Initial Google Sign-In should request only:

```text
openid
email
profile
```

First login should create:

```text
local Nova user profile
email/display name identity
connector status records
Connected Apps screen
```

First login should not automatically grant:

```text
Gmail access
Calendar access
Drive access
Contacts access
background access
send/post/delete/modify authority
```

---

## What Connectors Mean

Connectors are separate user choices after profile creation.

Connector access means:

```text
Nova may access the approved Google app within granted scopes.
```

Connector access does not mean:

```text
Nova may send, delete, modify, share, invite, book, archive, label, or change records without governance.
```

A token is access.

It is not authority.

---

## Correct User Flow

```text
Welcome to Nova
→ Continue with Google or Use local-only mode
→ create local Nova profile with identity scopes only
→ show Connected Apps screen
→ user chooses Calendar, Gmail, Drive, or Contacts one at a time
→ Nova requests narrow scopes for the selected connector
→ token is stored safely
→ connector actions remain governed, logged, and reviewable
```

---

## Recommended Build Order

Build in this order:

```text
1. Google Sign-In identity only
2. Local Nova user profile
3. Connected Apps / connector registry
4. Calendar read-only connector
5. Gmail read-only connector
6. Gmail draft-only / Cap 64 alignment
7. Drive read-only/search/summarize
8. Contacts read-only
9. Calendar event proposals
10. Drive/file/contact mutation proposals
11. Advanced automations only after approval queue and receipts are reliable
```

Calendar read-only should come before Gmail/Drive writes because it provides clear user value with lower risk.

---

## Required Governance

Every connector must define:

```text
scopes granted
allowed actions
blocked actions
approval-required actions
sensitive-data policy
revoke/disconnect path
ledger events
receipt output
```

Every connector action should be classified:

```text
READ
DRAFT
REMOTE_MUTATION
EXTERNAL_WRITE
DESTRUCTIVE
FINANCIAL
```

Default policy:

```text
READ → allowed when connector/scope permits
DRAFT → approval-gated depending on connector
REMOTE_MUTATION → approval required
EXTERNAL_WRITE → approval required
DESTRUCTIVE → hard approval or blocked first
FINANCIAL → blocked unless separately designed/certified later
```

---

## Required Receipts

Google connector receipts should say what happened and what did not happen.

Examples:

```text
Nova read today's calendar.
Nova summarized 3 email threads.
Nova created 1 draft after approval.
Nova did not send any emails.
Nova did not delete or modify files.
Nova did not create or cancel calendar events.
```

---

## Token Safety

Tokens are secrets.

Required rules:

```text
never log tokens
encrypt refresh tokens or use OS credential storage
support disconnect/revoke
refresh only when needed
track token status
fail safely if expired/revoked
make background/offline access explicit
```

Preferred storage targets:

```text
Windows: Credential Manager
macOS: Keychain
Linux: Secret Service / keyring
```

---

## What Not To Do First

Do not start with:

```text
one-click all Google permissions
full Gmail access
full Drive access
send-email automation
calendar auto-booking
file moving/deleting
contact editing
bulk inbox changes
background connector sync without explicit permission
plain token storage
automatic connector actions without receipts
```

---

## Fit With Full Stack Direction

Future stack:

```text
Gemma reasons
OpenClaw acts
ElevenLabs speaks
Google connects data
Nova governs action
```

Example:

```text
User asks by voice:
Nova, what do I need to handle today?

Google Calendar connector reads today's events.
Gmail connector summarizes selected inbox items if connected.
Gemma turns results into a plain-language plan.
OpenClaw performs bounded worker tasks only if needed.
ElevenLabs speaks the answer online.
Nova shows transcript, actions, approvals, and receipts.
```

Trust line:

```text
Nova read your calendar and summarized selected inbox items. Nothing was sent, deleted, moved, or changed.
```

---

## Final Product Rule

> **Google connects data. Nova governs action.**

This is the short reference for future Google account and connector onboarding work.

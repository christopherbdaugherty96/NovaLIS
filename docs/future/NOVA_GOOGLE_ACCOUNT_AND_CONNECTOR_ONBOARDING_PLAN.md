# Nova Google Account And Connector Onboarding Plan

Date: 2026-04-26

Status: Future implementation plan / connector onboarding architecture

Purpose: define how Nova should support first-time Google sign-in and later Google app connections without giving Google access hidden authority inside Nova.

Related docs:

- [`NOVA_FULL_STACK_DIRECTION_FINAL_LOCK_2026-04-26.md`](NOVA_FULL_STACK_DIRECTION_FINAL_LOCK_2026-04-26.md)
- [`NOVA_VOICE_STACK_OPERATING_MODEL_2026-04-26.md`](NOVA_VOICE_STACK_OPERATING_MODEL_2026-04-26.md)
- [`NOVA_OPENCLAW_HANDS_LAYER_IMPLEMENTATION_PLAN.md`](NOVA_OPENCLAW_HANDS_LAYER_IMPLEMENTATION_PLAN.md)
- [`NOVA_ROLE_BASED_ASSISTANT_CORE_VISION.md`](NOVA_ROLE_BASED_ASSISTANT_CORE_VISION.md)

Research references:

- Google OpenID Connect / Sign in with Google: https://developers.google.com/identity/openid-connect/openid-connect
- Google OAuth 2.0 web server flow and incremental authorization: https://developers.google.com/identity/protocols/oauth2/web-server
- Gmail API scopes: https://developers.google.com/workspace/gmail/api/auth/scopes
- Calendar API scopes: https://developers.google.com/workspace/calendar/api/auth
- Drive API scopes: https://developers.google.com/drive/api/guides/api-specific-auth
- People API / contacts scopes: https://developers.google.com/people/contacts-api-migration

---

## Executive Summary

Nova should support Google sign-in and Google app connections, but these must be separated.

Core rule:

> **Google Sign-In identifies the user. Google connectors grant scoped access. Nova governance decides what can happen with that access.**

The user should not enter an email and silently grant Nova access to Gmail, Calendar, Drive, and Contacts all at once.

Correct flow:

```text
User signs in with Google
→ Nova creates a local user profile
→ Nova shows connector setup
→ user chooses which apps to connect
→ Nova requests narrow scopes for that connector
→ tokens are stored securely
→ all actions still route through Nova governance
```

This preserves Nova’s product rule:

> **Simple outside, governed inside.**

---

## Core Mental Model

```text
Google Sign-In = who the user is
Google OAuth connectors = what Nova can access
Nova governance = what Nova is allowed to do with that access
```

Full stack mapping:

```text
Nova = governor / orchestrator / authority
Gemma = local-first reasoning / language brain
OpenClaw = hands / worker / action runner
ElevenLabs = standard online voice experience
Google connectors = user-authorized app access
Dashboard/Text = review, editing, approvals, records
```

Short rule:

> **Google connects data. Nova governs action.**

---

## First Login Should Be Identity-Only

The first login should identify the user, not request broad app access.

First login scopes should be limited to identity:

```text
openid
email
profile
```

This creates a Nova profile with:

```text
Google subject/account ID
email
display name
profile image if needed
local Nova user ID
connector statuses
```

Example profile:

```json
{
  "user_id": "local-user-001",
  "auth_provider": "google",
  "google_subject": "google-sub-id",
  "email": "user@gmail.com",
  "display_name": "User Name",
  "connectors": {
    "gmail": "not_connected",
    "calendar": "not_connected",
    "drive": "not_connected",
    "contacts": "not_connected"
  }
}
```

Do not request Gmail, Calendar, Drive, or Contacts scopes during the first sign-in unless the user explicitly chooses that connector during onboarding.

---

## First-Time User Flow

### Step 1 — Welcome

```text
Welcome to Nova

Sign in to create your Nova profile.

[Continue with Google]
[Use local-only mode]
```

Local-only mode should remain available because Nova is local-first and should not require Google to exist.

---

### Step 2 — Google Identity

Nova performs Google sign-in using identity scopes only.

Result:

```text
Nova knows who the user is.
Nova does not yet have Gmail/Calendar/Drive/Contacts access.
```

---

### Step 3 — Create Local Nova Profile

Nova stores a local profile record.

```text
Profile created
Connector status: none connected yet
Mode: standard / local-first capable
```

---

### Step 4 — Connector Setup Screen

After sign-in, show:

```text
Connect apps to Nova

[Connect Calendar]
Read your schedule and summarize your day.

[Connect Gmail]
Summarize inbox and prepare draft replies.

[Connect Drive]
Find and summarize documents.

[Connect Contacts]
Help address drafts and identify people.

[Skip for now]
```

Each connector should explain:

```text
what Nova can do
what Nova cannot do
what permissions are requested
what requires approval
how to disconnect later
```

---

## Incremental Authorization

Nova should use incremental authorization.

Pattern:

```text
User clicks Connect Calendar
→ request Calendar scopes only

User clicks Connect Gmail later
→ request Gmail scopes only

User clicks Connect Drive later
→ request Drive scopes only
```

Use narrow scopes and request them only when needed.

Do not request every Google Workspace scope up front.

---

## Connector Registry

Nova should have a connector registry separate from capability registry.

Each connector record should include:

```text
connector_id
provider
account_email
status
scopes_granted
token_status
last_connected_at
last_used_at
last_sync_at
allowed_actions
blocked_actions
requires_approval_for
sensitive_data_policy
ledger_event_types
revoke_disconnect_supported
```

Example:

```json
{
  "connector_id": "google_gmail",
  "provider": "google",
  "account_email": "user@gmail.com",
  "status": "connected",
  "scopes_granted": [
    "gmail.readonly",
    "gmail.compose"
  ],
  "allowed_actions": [
    "read_selected_threads",
    "summarize_email",
    "prepare_reply",
    "create_draft_after_approval"
  ],
  "blocked_actions": [
    "send_email_automatically",
    "delete_email_automatically"
  ],
  "requires_approval_for": [
    "create_draft",
    "archive_email",
    "send_email"
  ]
}
```

---

## Recommended Connector Order

Do not build all Google connectors at once.

Recommended order:

```text
1. Google Sign-In identity only
2. Connector registry and Connected Apps screen
3. Calendar read-only
4. Gmail read-only
5. Gmail draft-only / Cap 64 alignment
6. Drive read-only/search/summarize
7. Contacts read-only
8. Calendar event proposals
9. Drive/file mutation proposals
10. Advanced automations only after approval queue and receipts are solid
```

Why Calendar first:

```text
high everyday value
lower risk than Gmail/Drive writes
simple daily assistant use case
useful for voice-first summaries
```

---

## Connector Rules

### Google Calendar

Start with:

```text
read today's schedule
read upcoming events
summarize day
show conflicts
suggest available times
```

Initial scope preference:

```text
calendar.readonly
calendar.freebusy where appropriate
```

Approval required for:

```text
create event
move event
cancel event
invite guests
change reminders
modify calendar settings
```

User-facing rule:

> **Nova may read and summarize your calendar. Calendar changes require approval.**

---

### Gmail

Start with:

```text
read selected inbox/thread data
summarize threads
extract tasks
prepare reply drafts
create Gmail draft only after approval
```

Initial scope preference:

```text
gmail.readonly first
gmail.compose later for draft creation
avoid full mail scope early
```

Approval required for:

```text
create draft
send email
archive email
apply labels
delete email
bulk actions
```

User-facing rule:

> **Nova may summarize and draft. User approves before drafts are created or sent.**

Strong default:

> **Nova drafts. User sends.**

---

### Google Drive / Docs

Start with:

```text
search documents
summarize selected documents
extract tasks
answer questions about user-selected files
suggest folder organization
```

Initial scope preference:

```text
drive.file or narrow per-file access when possible
drive.readonly only when broader read access is truly needed
Docs read scopes only when Docs-specific access is required
```

Approval required for:

```text
rename file
move file
delete file
share file
edit document
create document
publish/export content
```

User-facing rule:

> **Nova may help find and summarize documents. File changes require approval.**

---

### Google Contacts / People API

Start with:

```text
find contacts
identify email recipients
help address drafts
match names to known contacts
```

Initial scope preference:

```text
contacts.readonly where possible
contacts only if contact edits are later needed
```

Approval required for:

```text
create contact
edit contact
delete contact
mass message contacts
sync/export contacts
```

User-facing rule:

> **Nova may look up contacts to help with drafts. Contact changes require approval.**

---

## Consent Screen Language

### Calendar

```text
Connect Calendar

Nova can:
- read your schedule
- summarize your day
- suggest available times

Nova will not:
- create, move, cancel, or invite people without approval

You can disconnect Calendar anytime.
```

### Gmail

```text
Connect Gmail

Nova can:
- read selected email information
- summarize threads
- prepare draft replies

Nova will not:
- send emails automatically
- delete emails automatically
- make bulk inbox changes without approval

You can disconnect Gmail anytime.
```

### Drive

```text
Connect Drive

Nova can:
- help find documents
- summarize selected files
- extract tasks and notes

Nova will not:
- edit, move, delete, or share files without approval

You can disconnect Drive anytime.
```

### Contacts

```text
Connect Contacts

Nova can:
- help find people you know
- use contact info when preparing drafts

Nova will not:
- edit, delete, export, or message contacts without approval

You can disconnect Contacts anytime.
```

---

## OAuth / Backend Architecture

Suggested routes:

```text
/auth/google/start
/auth/google/callback
/auth/logout
/connectors
/connectors/google/calendar/connect
/connectors/google/gmail/connect
/connectors/google/drive/connect
/connectors/google/contacts/connect
/connectors/{connector_id}/status
/connectors/{connector_id}/disconnect
/connectors/{connector_id}/revoke
/connectors/{connector_id}/scopes
```

Suggested storage:

```text
users table/profile store
connector_accounts table/store
oauth_token_store
connector_scope_grants
connector_audit_events
approval_queue
trust_receipts
```

Suggested internal services:

```text
GoogleAuthService
ConnectorRegistry
OAuthTokenStore
ConnectorPermissionPolicy
ConnectorMediator
GoogleCalendarConnector
GoogleGmailConnector
GoogleDriveConnector
GoogleContactsConnector
```

---

## Token Storage Rules

Tokens must be treated as sensitive secrets.

Rules:

```text
do not log access tokens
do not log refresh tokens
do not show tokens in UI
encrypt refresh tokens at rest
track token expiration
refresh only when needed
support disconnect/revoke
record connector use in ledger/trust history
```

Local OS storage targets:

```text
Windows: Credential Manager
macOS: Keychain
Linux: Secret Service / keyring
```

Development fallback may use encrypted local storage, but plain JSON refresh tokens should not be a long-term design.

---

## Offline Access / Background Access

Offline access should be explicit.

User-facing setting:

```text
Allow Nova to access this connector when I am not actively using Nova?

[No, only when I am using Nova]
[Yes, for scheduled summaries]
```

If enabled, Nova may request offline access/refresh tokens.

Do not silently enable scheduled connector access.

---

## Governance Rules

Every connector action should be classified.

```text
READ
DRAFT
LOCAL_RECORD
REMOTE_MUTATION
EXTERNAL_WRITE
DESTRUCTIVE
FINANCIAL
```

Suggested defaults:

```text
READ → allowed if connector is connected and scope permits
DRAFT → allowed or approval-gated depending on connector
REMOTE_MUTATION → approval required
EXTERNAL_WRITE → approval required
DESTRUCTIVE → hard approval or blocked first
FINANCIAL → blocked unless specifically designed/certified later
```

Connector access is not action authority.

> **A token means Nova can access an API. It does not mean Nova may perform any action without governance.**

---

## Ledger / Receipt Events

Add or reuse event types such as:

```text
GOOGLE_SIGNIN_STARTED
GOOGLE_SIGNIN_COMPLETED
GOOGLE_SIGNIN_FAILED
CONNECTOR_CONNECT_STARTED
CONNECTOR_CONNECTED
CONNECTOR_CONNECT_FAILED
CONNECTOR_DISCONNECTED
CONNECTOR_REVOKED
CONNECTOR_TOKEN_REFRESHED
CONNECTOR_SCOPE_GRANTED
CONNECTOR_SCOPE_DENIED
CONNECTOR_READ_PERFORMED
CONNECTOR_DRAFT_CREATED
CONNECTOR_ACTION_PROPOSED
CONNECTOR_ACTION_APPROVED
CONNECTOR_ACTION_DENIED
CONNECTOR_ACTION_COMPLETED
CONNECTOR_ACTION_BLOCKED
```

Receipts should be able to say:

```text
Nova read today's calendar.
Nova summarized 3 email threads.
Nova created 1 draft after approval.
Nova did not send any emails.
Nova did not delete or modify files.
```

---

## How This Fits The Final Stack

Example future flow:

```text
User:
Nova, what do I need to handle today?

Nova:
checks role and permissions

Google Calendar Connector:
reads today's events if connected

Gmail Connector:
summarizes selected inbox items if connected

Gemma:
turns results into a plain-language plan

OpenClaw:
performs bounded worker tasks if needed

ElevenLabs:
speaks the answer when online

Nova:
shows transcript, actions, approvals, and receipt
```

Trust line:

```text
Nova read your calendar and summarized selected inbox items.
Nothing was sent, deleted, moved, or changed.
```

---

## First MVP Recommendation

Build this in small steps.

### MVP 1 — Google Identity Only

```text
Continue with Google
Create local Nova profile
Show connected apps screen
No Gmail/Calendar/Drive/Contacts access yet
Local-only mode still available
```

### MVP 2 — Calendar Read-Only

```text
Connect Calendar
Read today/upcoming events
Summarize schedule
No event creation
No event editing
Receipt says calendar was read
```

### MVP 3 — Gmail Read-Only

```text
Connect Gmail
Summarize selected inbox/thread data
Extract tasks
No sending
No deleting
No labels/archive yet
```

### MVP 4 — Gmail Draft-Only

```text
Prepare reply
Ask approval to create draft
Create draft only after approval
User sends manually
Receipt says draft created / not sent
```

### MVP 5 — Drive / Contacts Read-Only

```text
Find and summarize selected files
Find contacts for draft addressing
No file/contact mutation
```

---

## What Not To Do First

Do not start with:

```text
full Gmail access
full Drive access
send-email automation
calendar auto-booking
file moving/deleting
contact editing
bulk inbox changes
background connector sync without explicit permission
one-click all Google permissions
plain token storage
automatic connector actions without receipts
```

---

## Final Recommendation

Build Google onboarding as identity-first, connector-second, governance-always.

Best summary:

> **Sign in with Google creates the Nova profile. Connecting Google apps grants scoped access. Nova governance decides what can happen with that access.**

Final product rule:

> **Google connects data. Nova governs action.**

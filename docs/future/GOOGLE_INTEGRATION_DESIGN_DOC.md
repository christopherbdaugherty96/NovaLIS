# Google Integration Design Doc

Status: future implementation design / not implemented runtime connector

Date: 2026-04-30

Second-pass hardening: 2026-04-30

Purpose: define Nova's Google integration clearly enough that future implementation stays aligned with Nova's governance model, security model, runtime truth discipline, and product UX.

This document consolidates and hardens the Google connector direction from the Google OAuth, Google account onboarding, Google read-context, Google Workspace, Cap 64, and business workflow planning notes.

---

## 1. Current Truth

Nova does not currently have a live Google OAuth / Gmail / Google Calendar runtime connector.

Current runtime truth:

```text
Cap 64 — send_email_draft
- active
- confirmation-gated
- opens a local mail client draft through mailto
- user manually reviews and sends
- Nova does not transmit email autonomously
- Nova does not read Gmail inboxes through Cap 64
- Nova does not use SMTP
- Nova does not create Gmail API drafts through Cap 64

Cap 57 — calendar_snapshot
- active calendar/agenda snapshot surface
- should not be treated as proof of Google Calendar OAuth integration unless runtime truth separately verifies that source
```

Planned but not implemented:

```text
google_signin_identity
google_connector_registry
google_oauth_connection
gmail_read_only
calendar_read_only
gmail_context_for_email_draft
drive_read_only
docs_read_only
sheets_read_only
contacts_read_only
gmail_api_draft_confirmed
gmail_send_confirmed
calendar_write_confirmed
drive_write_confirmed
```

Do not describe Google account access as shipped until all of the following exist:

```text
runtime registry entries
executor / connector code
governor-mediated routes
NetworkMediator routing where network is used
ledger / receipt event types
tests for allow and deny paths
runtime truth docs regenerated
manual smoke validation with a real or mocked OAuth flow
```

---

## 2. Core Rule

Nova's Google integration must preserve the core product doctrine:

```text
Intelligence is not authority.
```

Google can provide context.
Google context can help Nova summarize, search, prepare, draft, and plan.
Google context must not authorize actions.

A Google token means Nova can technically access an API.
It does not mean Nova may perform any action without governance.

Final rule:

```text
Google connects data.
Nova governs action.
```

Operational translation:

```text
OAuth scope ≠ capability permission
Connected account ≠ action authority
Read access ≠ write access
Draft creation ≠ send permission
Prior approval ≠ future blanket approval
Scheduled read ≠ silent monitoring
```

---

## 3. Separation Of Authority Layers

Google integration must keep four layers separate:

```text
Identity Layer     → who the user is
Connector Layer    → which external account/data source is connected
Capability Layer   → what Nova is allowed to attempt
Governor Layer     → whether this request is permitted now
```

Mental model:

```text
Google Sign-In = who the user is
Google OAuth connectors = what Nova can access
Nova Capability Registry = what Nova knows how to do
Nova Governor = whether this action can run now
Ledger / Receipts = proof of what happened
```

Correct flow:

```text
User signs in with Google
→ Nova creates a local user profile
→ Nova shows connector setup
→ user chooses which Google apps to connect
→ Nova requests narrow scopes for that connector only
→ tokens are stored securely
→ connector use remains governed by Nova
→ each real action is checked against capability, scope, policy, confirmation, and receipt rules
```

Incorrect flow:

```text
User signs in with Google
→ Nova silently gains Gmail, Calendar, Drive, Contacts access
→ Nova treats account access as action authority
→ assistant layer bypasses governance because a token exists
```

---

## 4. Identity-Only First Login

First login should identify the user only.

Initial Google Sign-In scopes:

```text
openid
email
profile
```

This may create a local Nova profile:

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

Do not request Gmail, Calendar, Drive, Docs, Sheets, or Contacts scopes during first sign-in unless the user explicitly chooses that connector.

Local-only mode must remain available.

First-login UX should say:

```text
Continue with Google creates your Nova profile.
It does not connect Gmail, Calendar, Drive, or Contacts yet.
You can choose those later.
```

---

## 5. Connected Apps / Connector Registry

Before implementing Gmail or Calendar actions, Nova needs a connector registry separate from the capability registry.

Capability Registry answers:

```text
What can Nova do?
```

Connector Registry answers:

```text
What external accounts and data sources are connected?
What scopes are granted?
What is allowed, blocked, expired, revoked, or waiting for approval?
```

Each connector record should include:

```text
connector_id
provider
account_email
account_subject_id
status
scopes_granted
token_status
token_storage_backend
last_connected_at
last_used_at
last_sync_at
allowed_actions
blocked_actions
requires_approval_for
sensitive_data_policy
network_policy
ledger_event_types
revoke_disconnect_supported
background_access_policy
```

Example:

```json
{
  "connector_id": "google_gmail",
  "provider": "google",
  "account_email": "user@gmail.com",
  "account_subject_id": "google-sub-id",
  "status": "connected",
  "scopes_granted": [
    "gmail.readonly"
  ],
  "token_status": "valid",
  "token_storage_backend": "os_keychain",
  "allowed_actions": [
    "search_selected_threads",
    "read_selected_threads",
    "summarize_email",
    "prepare_reply"
  ],
  "blocked_actions": [
    "send_email_automatically",
    "delete_email_automatically",
    "bulk_modify_inbox"
  ],
  "requires_approval_for": [
    "create_draft",
    "archive_email",
    "apply_label",
    "send_email"
  ],
  "background_access_policy": "disabled"
}
```

Connector registry invariants:

```text
A disconnected connector cannot be used.
An expired token cannot be silently treated as connected.
A scope mismatch must fail closed.
A connector record cannot grant a capability that the Capability Registry does not define.
A connector may provide data only through approved connector services, not direct ad hoc HTTP.
```

---

## 6. Google Workspace Connector Shape

Future package shape:

```text
google_workspace
├─ identity
├─ gmail
├─ calendar
├─ drive
├─ docs
├─ sheets
└─ contacts
```

Each sub-connector must have independent scopes and capability mappings.

Do not build one broad Google connector with blanket authority.

Suggested internal service boundaries:

```text
GoogleIdentityService
GoogleOAuthService
ConnectorRegistry
OAuthTokenStore
ConnectorPermissionPolicy
ConnectorMediator
GoogleCalendarConnector
GoogleGmailConnector
GoogleDriveConnector
GoogleDocsConnector
GoogleSheetsConnector
GoogleContactsConnector
GoogleReceiptMapper
```

No assistant, brain, router, or UI code should call Google APIs directly.
All connector work should route through the connector mediator and the same governance spine as other external effects.

---

## 7. Runtime Flow Boundary

Google connector execution must fit Nova's execution spine.

Read/context flow:

```text
User request
→ Brain / router classifies intent
→ capability contract selected
→ connector status and scope checked
→ GovernorMediator / Governor approves bounded read
→ NetworkMediator performs Google API call where required
→ connector normalizes result
→ ledger / receipt records read context
→ response returns with what was read and what was not changed
```

Draft/action flow:

```text
User request
→ context read if needed
→ draft/action proposal created
→ confirmation required if action affects external systems or creates a remote/local draft
→ Governor checks confirmation and capability
→ ExecuteBoundary executes approved action
→ NetworkMediator used for Google API writes if any
→ receipt records exact outcome
```

Hard rule:

```text
No Google connector may become a back door around GovernorMediator, CapabilityRegistry, ExecuteBoundary, NetworkMediator, or LedgerWriter.
```

---

## 8. Recommended Implementation Order

Do not build all Google connectors at once.

Recommended sequence:

```text
1. Static Google connector contracts
2. Connector registry foundation
3. Connector status API and read-only UI surface
4. Google Sign-In identity only
5. Secure token storage
6. Connected Apps / connector status UI
7. Calendar read-only
8. Gmail read-only
9. Gmail read context → Cap 64 local draft handoff
10. Drive / Docs / Sheets read-only
11. Contacts read-only
12. Calendar event proposals / drafts
13. Gmail API draft creation after approval
14. Confirmed writes only after receipts and approval queue are strong
15. Gmail send last, if ever
```

Calendar read-only should likely come before Gmail because it is lower risk, high daily value, useful for voice-first summaries, and easier to explain.

Implementation should be gated. Do not move to a higher-authority phase until lower-authority phases have tests, receipts, UI visibility, and fail-closed behavior.

---

## 9. Capability Ladder

### Phase 1 — Connection Layer

```text
Connect Google button
OAuth redirect flow
identity-only sign-in
token storage foundation
connected account status
disconnect / revoke
permission summary UI
```

### Phase 2 — Read Utilities

```text
today calendar snapshot
upcoming calendar summary
calendar availability check
selected Gmail thread summary
important email digest
search my email
find next event
```

### Phase 3 — Draft / Assist Layer

```text
prepare email replies
create local mail draft through Cap 64
create calendar event proposal
rewrite email professionally
summarize long threads
suggest follow-ups
```

### Phase 4 — Governed Actions

```text
create approved Gmail draft
create approved calendar event
archive emails after approval
label messages after approval
send approved email only if later explicitly implemented and certified
```

### Phase 5 — Business Workflow Layer

```text
Website / Auralis lead reply workflows
client onboarding emails
appointment scheduling
quote follow-ups
Pour Social event inquiry handling
reminder systems
owner command center surfaces
```

---

## 10. Capability Contracts

Before implementation, add static contracts for each Google capability.

Each contract must define:

```text
capability_id or planned_id
name
status
connector_required
required_scopes
authority_class
risk_level
can
cannot
requires_confirmation
allowed_inputs
blocked_inputs
expected_receipts
network_policy
privacy_policy
fallbacks
known_failure_modes
test_requirements
```

Minimum planned contracts:

```text
google_signin_identity
google_connector_registry
google_oauth_connection
google_connector_status
google_connector_revoke
google_calendar_read_only
google_calendar_availability_read
gmail_read_only
gmail_thread_summary
gmail_context_for_email_draft
google_drive_read_only
google_docs_read_only
google_sheets_read_only
google_contacts_read_only
```

Write/send contracts must remain future until read-only contracts are proven.

---

## 11. Gmail Model

Start with Gmail read-only.

Read capabilities:

```text
gmail_inbox_snapshot
gmail_thread_summary
gmail_multi_email_summary
gmail_action_extraction
gmail_followup_detection
```

Draft capabilities:

```text
gmail_draft_reply
gmail_draft_new_email
gmail_context_for_email_draft
```

Confirmed mailbox modifications:

```text
gmail_label_confirmed
gmail_archive_confirmed
gmail_mark_read_confirmed
```

High-risk capabilities:

```text
gmail_send_confirmed
gmail_delete_confirmed
```

Initial scope preference:

```text
gmail.readonly first
gmail.compose later for draft creation
avoid full mail scope early
```

Gmail read-only can:

```text
search Gmail metadata
read selected message/thread bodies
summarize selected messages/threads
return Gmail web links when available
show sender, subject, date, snippet, and labels
identify attachment metadata
use selected thread context to prepare a draft response
```

Gmail read-only cannot:

```text
send email
delete email
archive email
mark read/unread
label email
forward email
download attachments without separate approval
modify Gmail settings
read all mail silently
watch inbox silently by default
```

Strong default:

```text
Nova drafts. User sends.
```

Gmail read boundary:

```text
Search results should show enough metadata for user selection.
Full message/thread bodies should be read only when needed for the user request or selected by the user.
Bulk inbox analysis should be bounded by count, date range, labels, or explicit query.
```

---

## 12. Calendar Model

Start with Calendar read-only.

Read capabilities:

```text
google_calendar_snapshot
google_calendar_availability
google_calendar_conflict_check
```

Draft capability:

```text
google_calendar_event_draft
```

Confirmed write capabilities:

```text
google_calendar_event_create_confirmed
google_calendar_event_update_confirmed
google_calendar_event_delete_confirmed
```

Initial scope preference:

```text
calendar.readonly
calendar.freebusy where appropriate
```

Calendar read-only can:

```text
read today's schedule
read upcoming events
summarize day/week
show conflicts
suggest available times
use calendar context for morning briefs and planning
```

Calendar read-only cannot:

```text
create events
update events
delete events
invite attendees
respond to invitations
change calendar settings
silently monitor calendar without an approved routine
```

User-facing rule:

```text
Nova may read and summarize your calendar.
Calendar changes require approval.
```

Calendar read boundary:

```text
Default window should be bounded, such as today, tomorrow, this week, or an explicit requested range.
Do not read all historical calendar data for ordinary planning requests.
```

---

## 13. Drive / Docs / Sheets Model

Drive read capabilities:

```text
google_drive_search_read
google_drive_asset_snapshot
```

Drive confirmed write/share capabilities:

```text
google_drive_share_confirmed
google_drive_write_confirmed
```

Docs capabilities:

```text
google_doc_read
google_doc_draft_create
google_doc_update_confirmed
```

Sheets capabilities:

```text
google_sheet_read
google_sheet_prepare_update
google_sheet_update_confirmed
```

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
Sheets read scopes only when Sheets-specific access is required
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
update sheet values
```

Drive / Docs / Sheets boundary:

```text
Prefer user-selected files or search-result-selected files.
Do not crawl entire Drive by default.
Do not export, publish, or share files without separate confirmation.
```

---

## 14. Contacts Model

Start with contacts read-only.

Can do:

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

Contacts boundary:

```text
Lookup for a named recipient is acceptable after connector enablement.
Exporting or bulk-reading contact lists should require explicit purpose and stronger review.
```

---

## 15. Cap 64 Relationship

Cap 64 must remain draft-only unless a future capability explicitly changes that after review.

Correct relationship:

```text
Gmail read-only supplies selected source context.
Nova summarizes the selected email/thread.
Nova prepares reply text.
Cap 64 opens a local mailto draft after confirmation.
Human reviews and sends manually.
Receipts record what happened.
```

Incorrect relationship:

```text
Gmail read context exists.
Nova sends email automatically.
```

Important distinction:

```text
Current Cap 64 = local mail client draft only.
Future Gmail API draft = higher authority than local draft and requires its own scope, contract, approval, and receipt.
Future Gmail send = highest risk and should be last, if ever.
```

Cap 64 handoff receipt should include:

```text
source connector used, if any
source thread/message identifier or safe reference
recipient proposed
subject proposed
confirmation shown
local draft opened
email not sent by Nova
```

---

## 16. Daily Operating Brief Workflow

Target future workflow:

```text
User: Nova, what do I need to handle today?

→ Nova checks connected apps and permissions
→ Calendar read-only reads today's events
→ Gmail read-only summarizes selected important threads
→ Nova identifies follow-ups, meeting prep, conflicts, and suggested blocks
→ Nova presents a plan
→ Nova states what it did and did not do
→ receipt records reads/summaries
```

Trust line:

```text
Nova read your calendar and summarized selected inbox items.
Nothing was sent, deleted, moved, or changed.
```

This should remain read/context behavior unless the user creates an explicit approved routine.

Brief boundaries:

```text
Default to today's calendar and a bounded email window.
Show source counts.
Show skipped unavailable connectors.
Do not imply inbox completeness if only a limited query was read.
```

---

## 17. Business Workflow Overlays

Google Workspace is the generic connector layer.
Business agents apply domain logic on top.

### Website / Auralis Lead Intake

```text
New inquiry arrives in Gmail
→ Nova summarizes the lead
→ extracts business name, need, budget/timeline clues
→ checks Calendar availability
→ drafts reply
→ user approves local/Gmail draft
→ user sends manually
→ optional approved tracker update later
```

### Pour Social Event Inquiry

```text
Event inquiry arrives
→ Nova reads selected email thread
→ extracts date, location, guest count, service type
→ checks calendar conflicts
→ finds relevant menu/contract docs from Drive later
→ drafts reply or quote request
→ user reviews/sends
```

### Meeting Prep

```text
User: prep me for my 2 PM meeting
→ read Calendar event
→ identify attendees
→ find related Gmail threads
→ summarize context
→ pull linked Drive docs if connected later
→ produce briefing
→ no external changes
```

Business overlay rule:

```text
Domain logic can prioritize and format work.
Domain logic cannot expand connector scopes or bypass confirmation.
```

---

## 18. Approval Model

Default authority tiers:

```text
READ → allowed after connector enablement and scope check
DRAFT → allowed or approval-gated depending on connector and destination
LOCAL_RECORD → may be allowed if governed and visible
REMOTE_MUTATION → approval required
EXTERNAL_WRITE → approval required
DESTRUCTIVE → hard approval or blocked in early versions
FINANCIAL → blocked unless separately designed and certified
```

Read operations after connector enablement:

```text
Calendar read
selected Gmail read
selected Drive/Docs/Sheets read
Contacts lookup
```

Draft/preparation operations:

```text
prepare email reply
prepare calendar event proposal
prepare document update
prepare sheet update
```

Confirmed operations:

```text
create Gmail draft
create calendar event
archive email
label email
move/share/update file
update doc/sheet
```

High-risk operations:

```text
send email
delete email
delete files
bulk inbox actions
calendar invite/send changes
contact export or mass messaging
```

Confirmation quality bar:

```text
Show target account.
Show exact action.
Show affected object.
Show whether this is read, draft, write, or destructive.
Show what will not happen.
Require a fresh user confirmation for write/send/destructive actions.
```

---

## 19. Receipts / Ledger Events

Expected Google identity and connector events:

```text
GOOGLE_SIGNIN_STARTED
GOOGLE_SIGNIN_COMPLETED
GOOGLE_SIGNIN_FAILED
CONNECTOR_CONNECT_STARTED
CONNECTOR_CONNECTED
CONNECTOR_CONNECT_FAILED
CONNECTOR_DISCONNECTED
CONNECTOR_REVOKED
CONNECTOR_SCOPE_GRANTED
CONNECTOR_SCOPE_DENIED
CONNECTOR_TOKEN_REFRESHED
CONNECTOR_STATUS_VIEWED
CONNECTOR_ACTION_BLOCKED
```

Expected Gmail events:

```text
GMAIL_SEARCH_PERFORMED
GMAIL_THREAD_READ
GMAIL_MESSAGE_SUMMARIZED
GMAIL_CONTEXT_USED_FOR_DRAFT
GMAIL_DRAFT_CREATED
GMAIL_ACTION_BLOCKED
GMAIL_SEND_CONFIRMED
GMAIL_DELETE_CONFIRMED
```

Expected Calendar events:

```text
CALENDAR_EVENTS_READ
CALENDAR_SUMMARY_CREATED
CALENDAR_CONTEXT_USED_FOR_BRIEF
CALENDAR_EVENT_PROPOSED
CALENDAR_EVENT_CREATED_CONFIRMED
CALENDAR_EVENT_UPDATED_CONFIRMED
CALENDAR_EVENT_DELETED_CONFIRMED
```

Receipts should be able to say:

```text
Nova read today's calendar.
Nova summarized 3 email threads.
Nova created 1 draft after approval.
Nova did not send any emails.
Nova did not delete or modify files.
```

Receipt redaction rules:

```text
Never store OAuth access tokens or refresh tokens.
Do not store full email bodies by default.
Do not store full document contents by default.
Store safe identifiers, source labels, action summaries, timestamps, and outcome.
Redact secrets, credentials, verification codes, and payment details where detected.
```

---

## 20. Token Storage Rules

Tokens are secrets.

Rules:

```text
do not log access tokens
do not log refresh tokens
do not show tokens in UI
encrypt refresh tokens at rest
track token expiration
refresh only when needed
support disconnect
support revoke
record connector use without exposing secrets
```

Preferred local OS storage targets:

```text
Windows: Credential Manager
macOS: Keychain
Linux: Secret Service / keyring
```

Development fallback may use encrypted local storage.
Plain JSON refresh tokens should not be product design.

Token handling failure modes:

```text
missing token → show reconnect path
expired token → refresh if allowed, otherwise reconnect
refresh denied → mark connector degraded/disconnected
scope missing → explain missing permission, do not auto-upscope
revoke requested → delete local token and mark connector revoked
```

---

## 21. Background / Offline Access

Offline access must be explicit.

User-facing setting:

```text
Allow Nova to access this connector when I am not actively using Nova?

[No, only when I am using Nova]
[Yes, for scheduled summaries]
```

Default:

```text
No background access.
No silent inbox monitoring.
No silent calendar monitoring.
```

Scheduled summaries require:

```text
explicit routine setup
visible scope
revocable permission
receipts for each run
clear last-used timestamps
bounded query windows
user-visible failure state
```

A scheduled routine may read only what the routine contract permits.
A scheduled routine may not mutate Google data unless a later separately certified automation system allows that exact action.

---

## 22. Connected Apps UI Requirements

Nova should expose a Connected Apps screen showing:

```text
connected account
connected apps
status per app
scopes granted
last used
last token refresh
allowed actions
blocked actions
actions requiring approval
disconnect
revoke
recent receipts
```

Consent card language should include:

```text
what Nova can do
what Nova cannot do
what permission is being requested
what requires approval
how to disconnect later
```

Example Gmail consent language:

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

Required UI states:

```text
not connected
connecting
connected
connected with limited scopes
token expired
reconnect required
revoked
disabled by policy
error / degraded
```

---

## 23. Threat Model

Google integration introduces high-trust data. The design must explicitly defend against:

```text
over-broad OAuth scopes
token leakage through logs, UI, receipts, memory, or prompts
assistant layer bypassing governance
silent background monitoring
unbounded inbox or Drive crawling
prompt injection from email/document content
malicious links or attachments in email
wrong-account actions
bulk destructive actions
stale approval reused for a later action
cloud reasoning receiving private email/calendar data without approval
receipts exposing sensitive content
```

Required mitigations:

```text
minimal scopes
scope-to-capability mapping
connector mediator only
NetworkMediator only for Google API calls
bounded reads
explicit source selection where practical
content sanitization before model use
no token material in prompts
no raw secret material in receipts
fresh confirmation for write/send/destructive actions
visible account labels on every approval
local-first summarization where possible
cloud/deep reasoning privacy gate for sensitive content
```

Prompt injection rule:

```text
Email, calendar descriptions, docs, sheets, and Drive content are untrusted data.
They may inform the answer but must not override Nova system policy, connector policy, or user approvals.
```

---

## 24. Privacy / Cloud Reasoning Policy

Default behavior should be local-first when processing Gmail, Calendar, Drive, Docs, Sheets, or Contacts content.

Cloud/deep reasoning may use Google-derived content only if policy permits and the user is clearly informed or the content is redacted according to an approved privacy tier.

Sensitive content categories:

```text
OAuth tokens
passwords
verification codes
financial data
medical data
legal documents
private messages
client/customer data
personally identifying contact exports
```

Default rule:

```text
Do not send sensitive Google-derived content to external reasoning providers without explicit privacy-tier approval.
```

---

## 25. Failure And Fallback Behavior

If Google is not connected:

```text
Say the connector is not connected.
Offer manual paste/upload fallback where appropriate.
Do not pretend to have checked Gmail or Calendar.
```

If scope is missing:

```text
Say which permission is missing.
Explain what can still be done.
Do not auto-request broader scope unless the user starts that connector flow.
```

If token refresh fails:

```text
Mark connector as reconnect required.
Do not retry indefinitely.
Do not continue using stale assumptions.
```

If Google API fails:

```text
Return partial results if safe.
Show degraded connector status.
Write failure receipt if an action was attempted.
```

If user asks for unsupported write/send:

```text
State that Nova can prepare a draft or proposal.
Do not claim it can send/write unless that capability exists and is certified.
```

---

## 26. Test Plan

Minimum test classes before any Google connector is treated as shipped:

```text
unit tests for connector registry records
unit tests for scope-to-capability policy
unit tests for token store redaction / no logging
unit tests for disconnected / expired / revoked states
unit tests for Gmail read-only allow paths
unit tests for Gmail write/send deny paths
unit tests for Calendar read-only allow paths
unit tests for Calendar write deny paths
unit tests for Cap 64 Gmail-context handoff
unit tests for receipts redacting sensitive content
integration tests for OAuth callback mocked flow
integration tests for NetworkMediator routing
integration tests for Governor denial on missing confirmation
UI tests for Connected Apps state rendering
adversarial tests for prompt injection in email/doc content
```

Required negative tests:

```text
Gmail send requested without send capability → blocked
Gmail delete requested with read-only scope → blocked
Calendar create requested with read-only scope → blocked
Drive share requested with read-only scope → blocked
assistant tries direct Google API call → blocked by architecture/tests
expired token used as connected → blocked
scope missing but connector connected → blocked
receipt tries to include token → blocked/redacted
email content says ignore policy → ignored
stale confirmation reused → blocked
```

---

## 27. Runtime Truth / Documentation Gates

A Google connector milestone is not complete until docs and runtime truth agree.

Gate checklist:

```text
registry.json updated if new runtime capability exists
capability reference updated
connector contract added
ledger event allowlist updated
runtime truth regenerated
current runtime docs updated by generator, not hand-edited
README / WHAT_WORKS_TODAY updated honestly
future docs updated if implementation changes the plan
manual smoke result recorded
```

Status language must remain honest:

```text
planned
implemented but disabled
implemented read-only
implemented draft-only
implemented confirmed write
implemented send-capable
```

Do not use vague status labels like `Google integration complete`.

---

## 28. What Not To Build First

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
Google account access wired directly into brain/router code
```

---

## 29. MVP Definition

### MVP 1 — Google Identity Only

```text
Continue with Google
Create local Nova profile
Show Connected Apps screen
No Gmail/Calendar/Drive/Contacts access yet
Local-only mode still available
```

Exit criteria:

```text
identity scopes only
profile stored locally
connectors show not_connected
logout works
no app scopes requested
```

### MVP 2 — Connector Registry + Connected Apps

```text
Connector status API
Connected Apps UI
connect/disconnect/revoke state model
scope display
recent connector receipts
```

Exit criteria:

```text
states render correctly
revoked/expired states fail closed
no token values displayed
```

### MVP 3 — Calendar Read-Only

```text
Connect Calendar
Read today/upcoming events
Summarize schedule
No event creation
No event editing
Receipt says calendar was read
```

Exit criteria:

```text
calendar.readonly or freebusy only
bounded date window
no write methods available
write requests blocked
```

### MVP 4 — Gmail Read-Only

```text
Connect Gmail
Summarize selected inbox/thread data
Extract tasks
No sending
No deleting
No labels/archive yet
```

Exit criteria:

```text
gmail.readonly only
bounded search/read
no send/delete/archive/label actions
unsupported write requests blocked
```

### MVP 5 — Gmail Context + Cap 64

```text
User asks to reply to a selected email
Nova reads selected Gmail context
Nova prepares reply
Nova asks approval before opening local draft
Cap 64 opens local mailto draft
User sends manually
Receipt says draft created / not sent
```

Exit criteria:

```text
source context shown
confirmation required
local draft only
receipt says email was not sent by Nova
```

### MVP 6 — Drive / Docs / Sheets / Contacts Read-Only

```text
Find and summarize selected files
Read selected docs/sheets
Find contacts for draft addressing
No mutation
```

Exit criteria:

```text
user-selected or bounded search only
no share/edit/delete/export mutation
read receipts created
```

---

## 30. Success Standard

This integration is successful when a normal user can:

```text
connect Google identity in under two minutes
understand exactly what Nova can access
connect only the apps they want
see granted scopes and recent use
revoke access anytime
get useful Calendar/Gmail summaries
prepare drafts without hidden sending
see receipts proving what happened
feel no risk or confusion
```

Engineering success requires:

```text
no direct Google API bypasses
no token leakage
fail-closed scope checks
bounded reads
governor-mediated writes
accurate runtime truth
negative tests for forbidden actions
```

---

## 31. Final Recommendation

Build Google onboarding as:

```text
identity-first
connector-second
governance-always
```

Final product rule:

```text
Google connects data.
Nova governs action.
```

The correct first implementation path is not Gmail send.
It is connector contracts, connector registry, Google identity, Connected Apps UI, secure token storage, Calendar read-only, Gmail read-only, and then Gmail context into Cap 64 local draft creation.

Read first.
Draft second.
Send/write later, if ever.

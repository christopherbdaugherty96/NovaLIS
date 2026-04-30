# Nova Google Connector Model

This document defines the recommended Google integration path for Nova.

The correct direction is:

```text
Google read/context connector first.
Email sending later, if ever.
```

Nova should not jump from local email draft creation to full Gmail send/write authority.

Google should enter Nova as a governed context source before it becomes an action surface.

---

## Core Principle

Google integration must preserve Nova's core rule:

```text
Intelligence is not authority.
```

Google can provide context.

Google context can help Nova summarize, search, prepare, and draft.

Google context must not authorize actions.

Sending, deleting, archiving, labeling, calendar editing, Drive writes, account changes, or other external effects require separate governed capabilities, explicit boundaries, confirmation when needed, and receipts.

---

## Why Google Read-Only Comes Before Email Sending

Cap 64 currently creates a local email draft through the user's mail client after confirmation.

That is intentionally safer than direct email sending.

But Nova cannot yet support higher-value email workflows such as:

```text
Summarize the email from Sarah.
Find the thread about the website project.
Draft a reply to that message.
Show me the source email.
Link the draft back to the original thread.
Prepare a follow-up from the thread context.
```

Those workflows require read/context access before send/write access.

The stronger path is:

```text
Gmail read-only
→ selected email/thread context
→ source link/proof
→ response draft
→ Cap 64 draft-only confirmation
→ user manually reviews/sends
```

This improves usefulness while preserving human authority.

---

## Recommended Capability Split

Google should be split into narrow capabilities instead of one broad connector.

Suggested future capabilities:

```text
google_oauth_connection
gmail_read_only
calendar_read_only
gmail_context_for_email_draft
```

Possible later capabilities, not first:

```text
gmail_label_modify
gmail_archive
gmail_send
calendar_create_event
calendar_update_event
drive_read_only
drive_write
```

Each write/action capability should be separate, confirmation-aware, and receipt-backed.

---

## Capability 1 — Google OAuth Connection

Purpose:

```text
Allow the user to connect a Google account for specific, scoped Nova capabilities.
```

Can do:

```text
start OAuth connection
store/refresh tokens using secure local storage
list which Google scopes are active
revoke connection
show connection status
```

Cannot do:

```text
read Gmail by itself
read Calendar by itself
send email
modify calendar
write Drive files
request broad scopes without explanation
```

Required user visibility:

```text
which account is connected
which scopes are granted
which Nova capabilities can use those scopes
how to revoke access
```

Expected receipts:

```text
GOOGLE_CONNECTION_STARTED
GOOGLE_CONNECTION_COMPLETED
GOOGLE_CONNECTION_REVOKED
GOOGLE_SCOPES_CHANGED
```

---

## Capability 2 — Gmail Read-Only

Purpose:

```text
Let Nova search, read, summarize, and link selected Gmail messages/threads as context.
```

Can do:

```text
search Gmail metadata
read selected message/thread bodies
summarize selected messages/threads
return Gmail web links when available
show sender, subject, date, snippet, and labels
identify attachment metadata
use selected thread context to prepare a draft response
```

Cannot do:

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

Required setup:

```text
Google OAuth connection
Gmail read-only scope
configured account identity
user-visible scope status
```

Expected receipts:

```text
GMAIL_SEARCH_PERFORMED
GMAIL_THREAD_READ
GMAIL_MESSAGE_SUMMARIZED
GMAIL_CONTEXT_USED_FOR_DRAFT
```

Fallbacks:

```text
ask user to paste email text manually
ask user to export/upload message text
prepare a generic draft without reading Gmail
```

---

## Capability 3 — Calendar Read-Only

Purpose:

```text
Let Nova read calendar context for daily briefs, schedule summaries, and meeting preparation.
```

Can do:

```text
read upcoming events
summarize today/week
show event title, time, location, description, and attendees where allowed
link to event when available
use calendar context for morning briefs and planning
```

Cannot do:

```text
create events
update events
delete events
invite attendees
respond to invitations
change calendar settings
silently monitor calendar without an approved routine
```

Required setup:

```text
Google OAuth connection
Calendar read-only scope
configured account identity
user-visible scope status
```

Expected receipts:

```text
CALENDAR_EVENTS_READ
CALENDAR_SUMMARY_CREATED
CALENDAR_CONTEXT_USED_FOR_BRIEF
```

Fallbacks:

```text
ask user to paste schedule manually
use local calendar connector if configured
prepare a non-calendar daily brief
```

---

## Capability 4 — Gmail Context For Email Draft

Purpose:

```text
Use Gmail read-only context to improve Cap 64 local email drafts.
```

This is not Gmail sending.

Recommended flow:

```text
1. User asks Nova to reply to an email/thread.
2. Nova searches Gmail read-only.
3. Nova shows the selected message/thread and link.
4. Nova summarizes the relevant context.
5. Nova drafts a reply.
6. Nova states that Cap 64 is draft-only.
7. User confirms draft creation.
8. Nova opens a local mailto draft.
9. User manually reviews/sends or closes it.
10. Receipts record what happened.
```

Can do:

```text
use selected Gmail thread context for draft text
link draft context back to source email/thread
show what source context was used
hand off to Cap 64 for local draft creation
```

Cannot do:

```text
send the reply
modify the source Gmail thread
mark the thread as replied
archive/label/delete the email
assume consent from prior memory
```

Expected receipts:

```text
GMAIL_CONTEXT_USED_FOR_DRAFT
EMAIL_DRAFT_CONFIRMATION_SHOWN
EMAIL_DRAFT_CREATED
EMAIL_DRAFT_FAILED
```

---

## Required Brain Behavior

The Brain should classify Google tasks by environment and authority.

Examples:

```text
Summarize the email from Sarah.
→ environment: gmail_read_only
→ authority: account_read
→ capability: gmail_read_only
→ confirmation: may be required depending on scope/session policy
→ proof: Gmail source link + read receipt
```

```text
Reply to the email about the website project.
→ environment: gmail_read_only + email_draft
→ authority: account_read + external_effect_draft
→ capabilities: gmail_read_only + Cap 64 send_email_draft
→ confirmation: required before opening draft
→ proof: Gmail context receipt + email draft receipt
```

```text
Send the reply.
→ environment: gmail_write/send
→ authority: external send
→ current status: not supported by default
→ fallback: open local draft for manual review/send
```

---

## Scope and Privacy Rules

Google scopes should be minimal.

Start with read-only scopes only.

The user should be able to inspect:

```text
connected account
active scopes
last access time
recent Google receipts
which capability used the data
how to revoke access
```

Sensitive data should not be sent to cloud/deep reasoning without explicit privacy-tier approval.

Recommended default:

```text
local summarize when possible
ask before cloud/deep reasoning on email/calendar content
redact secrets and sensitive tokens
never include OAuth tokens in receipts or Obsidian presence notes
```

---

## What Not To Build First

Do not start with:

```text
Gmail send
Gmail delete
Gmail archive
Gmail label changes
Calendar write
Calendar invite/send
Drive write
Contact write
silent inbox monitoring
broad all-Google account access
```

These are higher-authority surfaces and should require later capability contracts, tests, confirmations, and proof.

---

## Relationship To Cap 64

Cap 64 should remain draft-only.

Google read integration should make Cap 64 more useful, not more autonomous.

Correct relationship:

```text
Gmail read-only supplies context.
Cap 64 opens a local draft after confirmation.
Human sends manually.
```

Incorrect relationship:

```text
Gmail read context exists.
Nova sends email automatically.
```

---

## Relationship To Daily Briefs

Google read-only connectors are useful for the Daily Operating Layer.

Possible brief sections:

```text
today's calendar
recent important email threads
follow-ups waiting for user
meetings needing preparation
client messages to review
business reminders
```

This should remain read/context behavior unless an approved automation routine is explicitly created.

---

## Relationship To Capability Contracts

Before implementation, add static contracts for:

```text
google_oauth_connection
gmail_read_only
calendar_read_only
gmail_context_for_email_draft
```

Each contract should include:

```text
can
cannot
required setup
OAuth scopes
authority tier
confirmation rules
expected receipts
fallbacks
known failure modes
```

---

## Implementation Order

Recommended order:

```text
1. Finish Cap 16 search reliability.
2. Add static Capability Contracts for existing high-priority capabilities.
3. Add Google connector contracts as future/static definitions.
4. Implement Google OAuth connection foundation.
5. Implement Gmail read-only search/read/link.
6. Implement Calendar read-only summary.
7. Connect Gmail read-only context to Cap 64 draft-only flow.
8. Add daily brief integration using read-only Google context.
9. Consider write/send capabilities only after separate proof and review.
```

---

## Current Truth

Current Nova behavior:

```text
Cap 64 opens local mail client drafts after confirmation.
Nova does not send email.
Nova does not access Gmail inboxes through Cap 64.
Nova does not use SMTP.
Google read-only connector is not implemented yet unless separately verified in runtime truth.
```

Future direction:

```text
Google read-only context connector
Gmail thread search/read/link
Calendar read-only summaries
Gmail context used for draft-only replies
No Gmail send/write by default
```

---

## Final Framing

Google integration should begin as a governed read/context connector, not an action connector.

The goal is to let Nova understand the user's email and calendar context while keeping real-world authority visible and bounded.

```text
Read first.
Draft second.
Send/write later, if ever.
```

Nova should help the user understand, prepare, and review.

The user remains the actor for sending and other external effects unless a future governed capability explicitly proves otherwise.

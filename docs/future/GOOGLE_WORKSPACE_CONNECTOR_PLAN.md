# Google Workspace Connector Plan

Status: future connector design / not implemented

This document defines how Google Workspace (Gmail, Calendar, Drive, Docs, Sheets) should be integrated into Nova using governed connector packages and capability-scoped access.

---

## Design Principle

Google integration must follow Nova's core rule:

```text
Intelligence is not authority.
```

Nova should not have blanket access to a user's Google account. All access must be:

- scoped by product (Gmail, Calendar, etc.)
- scoped by capability
- routed through NetworkMediator
- governed by the Capability Registry
- approval-aware for write/send operations
- logged to the ledger

---

## Connector Structure

```text
google_workspace
├─ gmail
├─ calendar
├─ drive
├─ docs
└─ sheets
```

Each sub-connector has independent scopes and capability mappings.

---

## Gmail Capability Model

Read:
- gmail_inbox_snapshot
- gmail_thread_summary
- gmail_multi_email_summary
- gmail_action_extraction
- gmail_followup_detection

Draft:
- gmail_draft_reply
- gmail_draft_new_email

Mailbox modification (confirmed):
- gmail_label_confirmed
- gmail_archive_confirmed
- gmail_mark_read_confirmed

High risk:
- gmail_send_confirmed
- gmail_delete_confirmed

---

## Calendar Capability Model

Read:
- google_calendar_snapshot
- google_calendar_availability
- google_calendar_conflict_check

Draft:
- google_calendar_event_draft

Write (confirmed):
- google_calendar_event_create_confirmed
- google_calendar_event_update_confirmed
- google_calendar_event_delete_confirmed

---

## Drive / Docs / Sheets Model

Drive:
- google_drive_search_read
- google_drive_asset_snapshot
- google_drive_share_confirmed

Docs:
- google_doc_read
- google_doc_draft_create
- google_doc_update_confirmed

Sheets:
- google_sheet_read
- google_sheet_prepare_update
- google_sheet_update_confirmed

---

## Multi-Email Coordination Requirement

Email is not a single-item feature. Nova must support multi-email coordination.

Core capability:

```text
gmail_multi_email_summary
```

This should:

- load multiple threads
- group by domain (personal, Auralis, Pour Social, etc.)
- summarize each thread
- detect required actions
- identify missing information
- suggest replies
- suggest calendar coordination
- produce an action board

---

## Business Overlay

Google Workspace is a generic layer. Domain agents apply business logic.

Auralis example:

- lead intake from Gmail
- project tracker from Sheets
- assets from Drive
- briefs from Docs
- calls from Calendar

Pour Social example:

- event inquiries from Gmail
- scheduling from Calendar
- contracts and menus from Docs/Drive

---

## Approval Model

Read operations: allowed after connector enablement

Draft operations: require review

Write operations: require explicit approval

High-risk operations: require strong confirmation and receipt

---

## Implementation Order

1. Gmail + Calendar read-only
2. Multi-email summary
3. Draft replies + draft events
4. Batch approval support
5. Confirmed writes
6. High-risk operations (last)

---

## Honest Framing

```text
Nova integrates with Google Workspace through governed, capability-scoped connectors.

It can read, summarize, and prepare work across Gmail and Calendar, but sending emails, modifying events, or changing data always requires explicit approval.
```

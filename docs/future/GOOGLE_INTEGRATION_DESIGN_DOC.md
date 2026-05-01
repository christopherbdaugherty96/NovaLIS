# Google Integration Design Doc

Status: future implementation design / not implemented runtime connector

Date: 2026-04-30

Second-pass hardening: 2026-04-30
Third-pass apply: 2026-04-30

Purpose: define Nova's Google integration clearly enough that future implementation stays aligned with Nova's governance model, security model, runtime truth discipline, and product UX.

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
- SOURCE MUST BE EXPLICITLY LABELED (local | ics | google)
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

---

## 2. Core Rule

```text
Google connects data.
Nova governs action.
```

---

## 3. Execution Spine Insertion (CRITICAL)

```text
User
→ GovernorMediator
→ CapabilityRegistry
→ Connector Check (NEW)
→ Governor
→ ExecuteBoundary
→ ConnectorMediator (NEW)
→ NetworkMediator
→ Executor
→ Ledger
```

---

## 4. Connector Registry (REQUIRED)

### JSON Schema

```json
{
  "connector_id": "string",
  "provider": "google",
  "account_email": "string",
  "account_subject_id": "string",
  "status": "not_connected | connected | expired | revoked | error",
  "scopes_granted": ["string"],
  "token_status": "valid | expired | missing",
  "token_storage_backend": "os_keychain | encrypted_local",
  "last_connected_at": "timestamp",
  "last_used_at": "timestamp",
  "allowed_actions": ["string"],
  "blocked_actions": ["string"],
  "requires_approval_for": ["string"],
  "background_access_policy": "disabled | scheduled_only",
  "fail_closed": true
}
```

---

## 5. Scope → Capability Mapping (REQUIRED)

```text
gmail.readonly → gmail_read_only ONLY
calendar.readonly → calendar_read_only ONLY
calendar.freebusy → calendar_availability_read ONLY
drive.readonly → drive_read_only ONLY
contacts.readonly → contacts_read_only ONLY
```

Future:

```text
gmail.compose → gmail_api_draft_confirmed ONLY
calendar.events → calendar_write_confirmed ONLY
```

---

## 6. Token Storage

```text
no logs
no UI exposure
encrypted storage only
```

---

## 7. Bounded Reads (MANDATORY)

```text
no unbounded inbox
no full drive crawl
no unlimited calendar history
```

---

## 8. Cap 64 Boundary

```text
local draft only
no Gmail API
no send
```

---

## 9. Roadmap Alignment

```text
Phase 8 → connector foundation
Phase 9 → Gmail read + draft
Phase 10 → file/contacts read
Phase 11+ → confirmed writes
```

---

## 10. Threat Model

```text
token leakage
prompt injection
overbroad scopes
silent monitoring
```

---

## 11. Test Minimum

```text
write actions blocked
scope mismatch blocked
expired token blocked
```

---

## 12. Final Rule

```text
Read first.
Draft second.
Send/write later, if ever.
```

# Google Connector Implementation RoadMAP

Status: implementation planning (aligned to GOOGLE_INTEGRATION_DESIGN_DOC)

Date: 2026-04-30

Purpose: translate the Google integration design into an executable, phase-ordered roadmap with strict safety gates.

---

## Core Principle

```text
Google connects data.
Nova governs action.

Read first.
Draft second.
Send/write later, if ever.
```

---

## Phase 8.1 — Connector Foundation (REQUIRED FIRST)

Build before any OAuth or Google API work.

### Deliverables

```text
- ConnectorRegistry (code + validation)
- Scope → Capability mapping (enforced table)
- Connector check inserted into GovernorMediator path
- Calendar source labeling (local | ics | google)
```

### Exit Criteria

```text
- ConnectorRegistry loads and validates at runtime
- Missing/expired connector fails closed
- Scope mismatch blocks execution
- Capability without connector blocks execution
- calendar_snapshot includes source label
```

### Do NOT Build Yet

```text
- OAuth
- Gmail
- Calendar API
- UI
```

---

## Phase 8.2 — Identity + Connected Apps UI

### Deliverables

```text
- Google Sign-In (openid, email, profile ONLY)
- Local Nova user profile
- Connected Apps screen
- Connector states (not_connected, connected, expired, revoked)
- Disconnect / revoke actions
```

### Exit Criteria

```text
- No app scopes requested
- UI accurately reflects connector state
- Disconnect removes local token reference
- No token values exposed anywhere
```

---

## Phase 8.3 — Secure Token Handling

### Deliverables

```text
- OS-backed token storage (Credential Manager / Keychain / Secret Service)
- Token lifecycle handling (valid, expired, revoked)
- No token logging / no token in receipts
```

### Exit Criteria

```text
- Tokens never appear in logs, UI, or prompts
- Expired tokens block connector usage
- Reconnect flow works cleanly
```

---

## Phase 9 — Read-Only Connectors

### Calendar (FIRST)

```text
- today / tomorrow / this week
- availability (freebusy)
- summaries
- no create/update/delete
```

### Gmail (SECOND)

```text
- bounded search
- selected thread read
- summaries
- task extraction
- no send/delete/archive/label
```

### Exit Criteria

```text
- All reads are bounded
- No write endpoints exist
- Unsupported actions are blocked
- Receipts show read-only activity
```

---

## Phase 9.5 — Gmail → Cap 64 Draft Flow

### Flow

```text
- Gmail read provides context
- Nova drafts reply
- User confirms
- Cap 64 opens local mailto draft
- User sends manually
```

### Exit Criteria

```text
- Draft requires confirmation
- Draft is local only
- Receipt explicitly states "not sent"
```

---

## Phase 10 — Files + Contacts (Read-Only)

```text
- Drive search + selected file read
- Docs / Sheets read
- Contacts lookup
- no edits, no sharing, no deletion
```

### Exit Criteria

```text
- All reads are user-bounded or query-bounded
- No mutation endpoints exist
```

---

## Phase 11+ — Confirmed Writes (Future)

```text
- Gmail API draft creation
- Calendar event creation
- Drive edits / shares
- Email send (last, if ever)
```

### Requirements Before Entering

```text
- Approval UX is strong and clear
- Receipt system proven
- Negative tests cover all write-deny paths
```

---

## Scope → Capability Matrix (MUST IMPLEMENT)

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

## Required Tests (Minimum)

```text
- Gmail send requested → blocked
- Calendar write requested → blocked
- Missing scope → blocked
- Expired token → blocked
- Prompt injection → ignored
- Direct API bypass → blocked
```

---

## Do Not Build First

```text
- Gmail send
- Calendar auto-booking
- Drive mutation
- broad OAuth scopes
- background monitoring
```

---

## Success Definition

```text
- User understands what is connected
- User sees exactly what Nova can do
- User can revoke access anytime
- Reads are useful and bounded
- Drafts are helpful but safe
- No hidden actions occur
```

---

## Final Rule

```text
If it cannot be governed, it cannot be shipped.
```

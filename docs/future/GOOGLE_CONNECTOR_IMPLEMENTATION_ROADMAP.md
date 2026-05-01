# Google Connector Implementation Roadmap

Status: implementation planning (aligned to GOOGLE_INTEGRATION_DESIGN_DOC)

Date: 2026-04-30

Fourth-pass hardening: 2026-04-30

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

## Architecture Rule

The connector layer is not a feature.

It is part of Nova's execution spine.

Google work must never become a side-channel around governance.

Correct flow:

```text
User
→ GovernorMediator
→ CapabilityRegistry
→ ConnectorRegistry / Connector Check
→ Governor
→ ExecuteBoundary
→ ConnectorMediator
→ NetworkMediator
→ Executor
→ Ledger
```

Wrong flow:

```text
Brain / router / LLM
→ Google API directly
```

---

## Non-Negotiable Invariants

These must be enforced in code, not only described in docs.

```text
1. Connector check happens before Governor approval.
2. Scope → capability mapping is machine-enforced at runtime.
3. ConnectorRegistry is authoritative runtime state, not helper/cache state.
4. Missing connector, invalid token, or missing scope fails closed.
5. NetworkMediator validates connector intent, endpoint, and request class.
6. Cap 64 remains permanently local-only.
7. Reads are bounded at executor level, not just prompt/UI level.
8. Google content is untrusted input and cannot authorize action.
9. UI connector state must be derived from live connector state, not stale display state.
10. Background access defaults to disabled.
```

---

## Phase 8.1 — Connector Foundation (REQUIRED FIRST)

Build before any OAuth or Google API work.

No partial overlap with OAuth work. Finish this foundation first.

### Deliverables

```text
- ConnectorRegistry (code + validation)
- Scope → Capability mapping (enforced table)
- Connector check inserted into GovernorMediator path BEFORE Governor approval
- Calendar source labeling (local | ics | google)
- NetworkMediator connector validation hook
```

### Exit Criteria

```text
- ConnectorRegistry loads and validates at runtime
- Missing/expired connector fails closed
- Scope mismatch blocks execution
- Capability without connector blocks execution
- NetworkMediator rejects disallowed Google endpoints/request classes
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
- UI state is live-derived from ConnectorRegistry
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
- Tokens never appear in logs, UI, receipts, or prompts
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
- All reads are bounded at executor level
- No write endpoints exist
- Unsupported actions are blocked before execution
- Receipts show read-only activity
- Prompt injection inside email/calendar content cannot trigger action
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
- Draft requires fresh confirmation
- Draft is local only
- Cap 64 never calls Gmail API
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
- All reads are user-bounded or query-bounded at executor level
- No mutation endpoints exist
- Drive cannot crawl entire account by default
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
- Stale approvals cannot be reused
- Each write capability has a separate contract
```

---

## Scope → Capability Matrix (MUST IMPLEMENT)

This table must be executable policy, not documentation only.

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

Hard rule:

```text
A scope can never unlock multiple authority tiers.
```

---

## Required Tests (Minimum)

```text
- Gmail send requested → blocked
- Calendar write requested → blocked
- Missing scope → blocked
- Expired token → blocked
- Missing connector → blocked
- Prompt injection → ignored
- Direct API bypass → blocked
- NetworkMediator rejects disallowed Google endpoint/request class
- Cap 64 cannot call Gmail API
- UI shows expired/revoked connector accurately
```

---

## Do Not Build First

```text
- Gmail send
- Calendar auto-booking
- Drive mutation
- broad OAuth scopes
- background monitoring
- direct Google API calls from brain/router/UI code
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
- Runtime truth and docs agree
```

---

## Final Rule

```text
If it cannot be governed, it cannot be shipped.
```

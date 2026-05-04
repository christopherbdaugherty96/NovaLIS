# Google Read-Only Connector Foundation

Date: 2026-05-03
Status: **Planning only** — no Google OAuth, no Gmail API, no Calendar API runtime connector exists.
This document describes design direction and a concrete implementation sequence.
No claims in this doc are runtime truth until code, tests, and proof docs prove them.

Related:
- [`NOVA_GOOGLE_CONNECTOR_DIRECTION_FINAL_LOCK_2026-04-26.md`](NOVA_GOOGLE_CONNECTOR_DIRECTION_FINAL_LOCK_2026-04-26.md)
- [`NOVA_CONNECTOR_REGISTRY_PLAN_2026-04-27.md`](NOVA_CONNECTOR_REGISTRY_PLAN_2026-04-27.md)
- [`NOVA_CONNECTOR_RISK_CLASSIFICATION_TABLE_2026-04-28.md`](NOVA_CONNECTOR_RISK_CLASSIFICATION_TABLE_2026-04-28.md)
- [`../../nova_backend/src/config/connector_packages.json`](../../nova_backend/src/config/connector_packages.json)

---

## Core Rule (inherited from Final Lock doc)

> **Google connects data. Nova governs action.**

Google OAuth grants scoped access. The Nova governance layer (GovernorMediator, CapabilityRegistry,
ContextPack, receipts) decides what can happen with that access.

Connector access is not connector authority.

---

## Prerequisites Before Any Google Connector Work Starts

All of these must be true before implementation begins:

| Prerequisite | Status |
|---|---|
| Connector package registry exists in runtime | **Done** — `connector_packages.json` + `ConnectorPackageRegistry` active |
| Cost posture metadata on capabilities | **Done** — PR #99 2026-05-03 |
| ContextPack live in prompt path | **Done** — PR #89 2026-05-02 |
| Non-authorizing receipts pattern established | **Done** — RoutineReceipt, MemoryReceipt |
| Connector risk classification defined | **Done** — `NOVA_CONNECTOR_RISK_CLASSIFICATION_TABLE_2026-04-28.md` |
| Memory loop with explicit user saves | **Done** — PR #82 2026-05-02 |
| Approval boundary pattern (PlanMyWeekProposal) | **Done** — PR #98 2026-05-03 |
| Gmail write / send / draft authority | **Blocked** — must not exist before read-only is proven stable |
| OpenClaw browser/computer-use expansion | **Blocked** — frozen until hardening gaps are closed |

The prerequisites are now met for planning. Implementation requires one additional gate:

> **Connector governance spec must be clear about credential storage, scope issuance, and
> revocation before any OAuth flow touches production.**

---

## What Read-Only Means — Scope Map

"Google read-only connector" is shorthand. The actual scope required for each service is
different and must be granted separately:

| Service | Intended scope | Risk class | What it enables |
|---|---|---|---|
| Google Calendar | `https://www.googleapis.com/auth/calendar.readonly` | Class 1 (private read-only) | Read events, time blocks, free/busy; no create/edit/delete |
| Gmail | `https://www.googleapis.com/auth/gmail.readonly` | Class 1 (private read-only) | Read thread summaries, subject, sender, snippet; no send/draft/delete/label |
| Google Drive | `https://www.googleapis.com/auth/drive.readonly` | Class 1 (private read-only) | List files by name/type/date; read text content; no write/share/delete |
| Google Contacts | `https://www.googleapis.com/auth/contacts.readonly` | Class 1 (private read-only) | Read name/email/phone; no create/edit/delete |
| Google Identity | `openid email profile` | Class 0 (public read-only) | User identity only; no data access |

Read-only is **not** a trust guarantee — it is a scope constraint. A read-only connector
can still surface sensitive data. ContextPack authority labels (`source: google_calendar`,
`authority: user_provided`) must be applied to everything sourced from a Google connector.

---

## What This Connector Does NOT Authorize

No Google connector in this plan grants authority to:

```text
- send any email (Gmail send scope excluded)
- create, edit, or delete calendar events
- upload, share, modify, or delete Drive files
- act on behalf of the user in any Google Workspace app
- store OAuth tokens outside a credential store with explicit scope audit
- pass Google data to any external surface without explicit receipt
- run background polling or sync without user approval
```

These must be enforced by the governance layer, not left to caller discipline.

---

## Architecture: How It Fits the Existing Runtime

The connector must integrate with three existing subsystems:

### 1. ConnectorPackageRegistry (`connector_packages.json`)

A new package entry for each Google surface:

```json
{
  "id": "google_calendar_readonly",
  "label": "Google Calendar (Read Only)",
  "status": "design",
  "integration_mode": "official_api",
  "authority_class": "read_only_network",
  "requires_explicit_enable": true,
  "uses_official_api": true,
  "credential_mode": "oauth2_token",
  "capability_ids": [],
  "scopes": ["https://www.googleapis.com/auth/calendar.readonly"],
  "write_scopes_excluded": true,
  "description": "Read-only Google Calendar context. Reads events and free/busy; does not create, edit, or delete events."
}
```

Key addition vs Shopify: `credential_mode: "oauth2_token"` and `scopes` / `write_scopes_excluded`
fields. These are new fields to add to the connector package schema.

### 2. ContextPack (`compose_context_pack`)

Google Calendar data surfaces as `ContextItem` with:

```python
ContextItem(
    label="Google Calendar",
    content="<compact event summary>",
    source="google_calendar",          # new source label
    authority="user_provided",         # user explicitly connected
    freshness="live",
    weight=2,
)
```

The `source` label registry in `context_pack.py` must be extended to include
`google_calendar`, `gmail_summary`, `google_drive_summary`, `google_contacts`.

### 3. CapabilityRegistry (`registry.json`)

A new capability must be registered for each Google surface before any executor can run it:

```json
{
  "id": 66,
  "name": "google_calendar_context",
  "status": "design",
  "phase_introduced": "10",
  "risk_level": "low",
  "data_exfiltration": true,
  "enabled": false,
  "authority_class": "read_only_network",
  "requires_confirmation": false,
  "reversible": true,
  "external_effect": false,
  "cost_posture": "free_tier",
  "description": "Read-only Google Calendar context. Reads upcoming events and free/busy via the Calendar API and surfaces them in ContextPack. No write, create, edit, or delete authority."
}
```

Capability IDs 66+ are reserved for Google connector surfaces. Do not assign until
implementation is approved and scopes are confirmed.

---

## Credential Storage Design Constraint

OAuth tokens must not be stored in plain environment variables. The Shopify approach
(`NOVA_SHOPIFY_ACCESS_TOKEN` in env) is acceptable for a static API key because the key
doesn't expire and can be rotated by the user at any time.

OAuth 2.0 tokens are different:
- Access tokens expire (typically 1 hour)
- Refresh tokens are long-lived and highly sensitive
- Token refresh must happen automatically or via explicit user action

**Required before any Google OAuth flow can be shipped:**

1. A local credential store (`nova_backend/src/credentials/`) with:
   - encrypted-at-rest access token + refresh token
   - expiry tracking
   - explicit revoke path
   - per-connector scope record
2. A token refresh path (silent, governed — logs a `CONNECTOR_TOKEN_REFRESHED` ledger event)
3. A "connected / disconnected / scopes" visible status in the UI

This is different from a password manager. The credential store is Nova-local and must
never sync to a remote service without explicit user approval.

---

## Implementation Sequence (When Approved)

The minimum first slice (Phase 10 candidate, after Stage 6 is complete):

### Step 1 — Schema extension
- Add `scopes`, `write_scopes_excluded`, `credential_mode: "oauth2_token"` fields to
  `connector_packages.json` schema and `ConnectorPackageRegistry` validator.
- No OAuth flow yet — schema only.
- Tests: validator rejects packages that claim `oauth2_token` mode without `scopes`.

### Step 2 — Credential store foundation
- `nova_backend/src/credentials/credential_store.py` — local encrypted store for OAuth tokens.
- Store, read, refresh, revoke operations.
- Ledger events: `CREDENTIAL_STORED`, `CREDENTIAL_REFRESHED`, `CREDENTIAL_REVOKED`.
- No Google-specific code yet — generic store.
- Tests: round-trip store/read/revoke; token expiry detection.

### Step 3 — Google Calendar read-only executor (design phase)
- `nova_backend/src/connectors/google_calendar_connector.py` — read-only Calendar API client.
- Calls `credentials.CredentialStore.get_token("google_calendar_readonly")`.
- Returns `CalendarSnapshot` (same shape as existing ICS-backed CalendarSkill output).
- Passes through `NetworkMediator` (all external HTTP must).
- Does not register capability until tests and proof pass.
- Tests: mock API response round-trip; malformed token error handling; empty calendar edge case.

### Step 4 — Capability registration + ContextPack source label
- Add `google_calendar_context` capability (ID TBD, status `active`) to `registry.json`.
- Add `google_calendar` source label to `context_pack.py` `ALLOWED_SOURCES`.
- Wire executor into `GovernorMediator` routing.
- Add `cost_posture: "free_tier"` (Calendar API has a generous free quota).
- Tests: cap ID loads; disabled by default; source label validates.

### Step 5 — OAuth consent flow (UI)
- "Connect Google Calendar" button in Settings → Connected Apps.
- Opens OAuth consent page; user approves read-only scope.
- Token stored in CredentialStore.
- `CONNECTOR_CONNECTED` ledger event.
- Connector package status promoted from `design` to `active`.
- Tests: mock OAuth callback; token stored; ledger event emitted; status visible.

### Step 6 — Proof
- Run a Daily Brief with Google Calendar connected → events appear in Context Pack.
- Prove: no write calls emitted; receipt exists; source label is `google_calendar`;
  connector status shows in UI; revoke disconnects and clears token.

---

## What Comes After (Not In This Plan)

Gmail read-only, Drive read-only, and Contacts read-only follow the same pattern as
Calendar but are separate connectors with separate capability IDs and consent flows.

None of these are in scope until Google Calendar read-only is proven stable.

Gmail draft (Class 2) and send (Class 5) are not read-only and are explicitly
out of scope for this foundation plan.

---

## Hard Constraints That Must Not Be Violated

```text
1. No Google write scope may be requested in the same consent flow as a read scope.
2. OAuth tokens must not be stored in plain env vars.
3. Every Google API call must pass through NetworkMediator.
4. Every connector action must emit a ledger event.
5. Google context in the prompt must carry source="google_*" authority label.
6. Connector status (connected / scopes / last used) must be visible in UI before
   any Google connector is shipped.
7. Revoke must clear tokens and remove connector from active status immediately.
8. No background polling without explicit user approval and a receipted scheduler entry.
```

---

## Not Runtime Truth

Nothing in this document represents implemented behavior. This is a planning artifact.
Actual implementation requires: code, tests, proof docs, and generated runtime doc
confirmation before any claim moves from "planning" to "implemented".

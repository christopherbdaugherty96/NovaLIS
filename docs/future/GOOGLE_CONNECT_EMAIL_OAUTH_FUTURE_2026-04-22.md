# TODO — Google Connect / Email OAuth Integration (2026-04-22)

## Core Idea
Allow users to connect a Google account inside Nova through a familiar sign-in flow instead of manual setup.

Target experience:
1. User clicks **Connect Google**
2. Google sign-in opens
3. User verifies identity
4. User approves specific permissions
5. Nova stores access securely
6. Nova shows connected status and available capabilities

This should feel smooth, clear, and permission-based.

---

## Strategic Meaning
This is not just an email feature.
This is an account-connection foundation that can later power:
- Gmail
n- Calendar
- Contacts
- Drive (future if desired)
- business workflows tied to Google accounts

A clean OAuth connection system creates leverage for many later integrations.

---

## Correct Nova Framing
Not:
- silent access to user accounts
- hidden background monitoring
- automatic authority over inboxes

Yes:
- explicit connection by the user
- visible permissions
- revocable access
- clear connected/disconnected state
- approval-bound write actions
- read-first assistance model

---

## Best Capability Ladder
### Phase 1 — Connection Layer
- Connect Google button
- OAuth redirect flow
- token storage
- connected account status
- disconnect button
- permission summary UI

### Phase 2 — Read Utilities
- unread email summary
- today calendar snapshot
- important messages digest
- search my email
- find next event

### Phase 3 — Draft / Assist Layer
- draft email replies
- create calendar event draft
- rewrite email professionally
- summarize long threads
- follow-up suggestions

### Phase 4 — Governed Actions
- send approved draft
- create approved event
- archive emails
- label messages
- set reminders with confirmation

### Phase 5 — Business Workflow Layer
For Website LLC / Pour Social / future ventures:
- lead reply workflows
- client onboarding emails
- appointment scheduling
- quote follow-ups
- reminder systems
- owner command center surfaces

---

## Realistic Gaps Before Building
1. Google Cloud project setup
2. OAuth consent screen configuration
3. Secure token storage model
4. Scope minimization strategy
5. Reconnect / expired token handling
6. Disconnect and revoke flow
7. UI connection settings page
8. Governance rules for read vs write actions
9. Multi-account handling (future)
10. Privacy messaging and trust UX

---

## Current Priority Reminder
This is a legitimate future feature, but should not outrank immediate revenue engines unless directly needed now.

Near-term business focus remains:
1. Website LLC
2. Pour Social
3. Nova internal leverage tools
4. Expanded Google integrations later

---

## Success Standard
This feature is successful when a normal user can connect Google in under two minutes, understand what Nova can access, revoke it anytime, and gain real day-to-day utility without feeling risk or confusion.

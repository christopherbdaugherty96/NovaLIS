# Live Test Checklist — Cap 64: send_email_draft
Phase 5 of 6 · Priority: HIGH (external_effect=True, persistent_change)

## Pre-conditions
- [ ] Nova is running at `http://localhost:8000`
- [ ] A mail client is installed and configured on your machine
  (Outlook, Gmail in browser, Apple Mail, Thunderbird, etc.)
- [ ] Chat tab is open

---

## Test 1 — Full draft: recipient + subject

1. Type in Nova chat:
   ```
   draft an email to test@example.com about the quarterly review
   ```
2. Nova asks for confirmation — click **Confirm** (or type "confirmed")
3. ✅ Your mail client opens
4. ✅ **To:** field contains `test@example.com`
5. ✅ **Subject:** contains "quarterly review" or similar
6. ✅ **Body** contains a coherent, relevant email (not blank, not an error message)
7. Close the draft — **do NOT send**

---

## Test 2 — Shorthand: recipient only

1. Type: `email sarah@company.com`
2. Confirm when prompted
3. ✅ Mail client opens with `sarah@company.com` in the To field
4. ✅ No crash, no Python traceback in the Nova console

---

## Test 3 — Full phrase with body hint

1. Type:
   ```
   compose an email to boss@work.com about scheduling a team meeting next week
   ```
2. Confirm
3. ✅ Mail client opens
4. ✅ Body mentions "meeting" or "schedule" — shows LLM used the hint
5. Close without sending

---

## Test 4 — Ledger verification

1. Go to **Trust** page in Nova (`http://localhost:8000/trust`)
2. Find the ledger section
3. ✅ At least one `EMAIL_DRAFT_CREATED` event is logged from your tests above
4. ✅ The event shows the recipient email address

---

## Test 5 — Confirmation gate

1. Type: `draft an email to anyone@example.com about anything`
2. Do **NOT** confirm — dismiss or ignore the confirmation prompt
3. ✅ The mail client does NOT open
4. ✅ Nova shows a "requires confirmation" message

---

## Sign-off

When all 5 tests pass, run:
```
python scripts/certify_capability.py live-signoff 64
```

Then lock it:
```
python scripts/certify_capability.py lock 64
```

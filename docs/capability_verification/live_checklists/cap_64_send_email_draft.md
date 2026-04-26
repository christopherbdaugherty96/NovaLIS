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

---

## Troubleshooting

**Mail client does not open**
- Confirm a default mail client is registered with the OS. On Windows: Settings → Apps → Default apps → Mail.
- If using Gmail in a browser, Chrome/Edge must be set as the default browser and Gmail must be set as the mailto handler (Chrome: Settings → Privacy and security → Site settings → Additional permissions → Protocol handlers).
- Check the Nova console for any Python traceback. If `webbrowser.open` fails silently, set the `BROWSER` env var to a known browser path.

**To: field is empty or wrong**
- The executor encodes the recipient into the `mailto:` URI. Confirm the intent contained an email address (e.g. `to test@example.com`).
- If `@` appears encoded as `%40`, that is correct RFC 6068 behavior — most mail clients handle it.

**Body is blank or placeholder text**
- The body is LLM-generated. A very short prompt ("email someone about something") produces a generic body. Use a more specific prompt for a meaningful body (Test 3 is designed for this).

**Test 4 — Trust page not loading**
- The Trust Panel UI is not yet built. Use `http://localhost:8000/api/trust/receipts` directly in a browser — the JSON response contains `EMAIL_DRAFT_CREATED` entries.
- If no entries appear, run at least one email draft test first, then refresh.

**Test 5 — Confirmation prompt not appearing**
- The prompt is a UI element in the dashboard chat tab. If you are calling via the API directly (not via the chat UI), the confirmation gate works differently.
- Use the chat tab at `http://localhost:8000` for this test.

**certify_capability.py errors**
- Run from `C:\Nova-Project` (the repo root), not from inside `nova_backend/`.
- If the command reports phase mismatch, check `python scripts/certify_capability.py status` to see current phase state.

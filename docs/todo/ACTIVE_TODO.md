# Active TODO — Nova

**Updated:** 2026-04-28
**Sprint goal:** Non-developer installs and runs Nova in 5 minutes.
**Authoritative sprint detail:**
[4-15-26 NEW ROADMAP/Now.md](../../4-15-26%20NEW%20ROADMAP/Now.md)

---

## Next Tasks (ordered by ROI)

- [ ] **Cap 64 P5 live signoff + lock** —
  run [live checklist](../capability_verification/live_checklists/cap_64_send_email_draft.md),
  then `certify_capability.py live-signoff 64` + `lock 64`
- [ ] **Dashboard trust card** —
  pull from `GET /api/trust/receipts`, render last 5 actions inline; backend is live
- [ ] **Windows installer VM validation** —
  run clean install, capture `C:\Program Files\Nova\bootstrap.log`, fix root cause
- [ ] **Formspree waitlist activation** — enable the landing page waitlist endpoint
- [ ] **README demo asset** — add screenshot or GIF of a governed action completing
- [ ] **Cap 65 P5 live signoff** —
  requires `NOVA_SHOPIFY_SHOP_DOMAIN` + `NOVA_SHOPIFY_ACCESS_TOKEN`;
  run [live checklist](../capability_verification/live_checklists/cap_65_shopify_intelligence_report.md)

---

## Paused (do not start)

| Item | Blocker |
|------|---------|
| Cap 65 P5 | Shopify credentials not set in this environment |
| Windows installer validation | Requires clean VM |
| GitHub Actions CI | Account billing locked |
| Solo Business Assistant shell (Tier 2) | Tier 1 not yet closed |
| Auralis merger planning | Explicitly paused — do not expand |
| Google OAuth connector | Future lane; not needed now |
| Voice / ElevenLabs | Paused — no timeline |

---

## Completed This Sprint

- Cap 64 confirmation gate fixed (commit `93be5ff`)
- Cap 64–65 trust receipt backend + loopback guard + 18 tests
- RequestUnderstanding formatter + integration + 25 tests
- OpenClaw governance hardening Steps 1–7
- Cap 65 P1–P4 certified (84 tests pass)
- Windows CI job + `verify_windows.ps1`
- Stale branch cleanup
- README, QUICKSTART, and BackLog updated

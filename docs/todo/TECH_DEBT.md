# Technical Debt — Nova

**Updated:** 2026-04-28
**Source:** Distilled from `NOVA_RECONCILIATION_TODO_2026-04-22.md` (archived); only still-open items kept.

---

## Open

### agent_scheduler.py lifecycle repair
**File:** `nova_backend/src/openclaw/agent_scheduler.py`

The April 2026 scheduler rework added failure recording but lost lifecycle observability.

Restore:
- suppression recording (outcome + reason + log event)
- trigger logging (emit `SCHEDULE_TRIGGERED` before execution)
- completion logging (emit `COMPLETED` after success)
- deprecated direct-run logging (emit `OPENCLAW_DEPRECATED_DIRECT_RUN` if legacy path used)
- hourly delivery counter increment after success
- duplicate-window protection (anti-spam gate)

Keep current improvements (failure recording for missing template / envelope refusal / execution error).

**Risk:** medium — needs careful diff against prior behavior before merging.

---

### PR discipline
Future changesets should separate behavior changes, tests, docs, and generated artifacts into distinct commits. Broad diffs increase reconciliation risk.

---

## Resolved (for reference)

| Item | Resolved |
|------|---------|
| runtime_auditor.py cap 65 probe coverage | 2026-04-21 — Shopify probes added |
| capability_locks.json cap 65 metadata | 2026-04-25 — P1–P4 tests verified |
| stale branch cleanup | 2026-04-26 — all stale branches deleted |
| generated runtime docs rebuild | 2026-04-26 — regenerated after code fixes |

# 04 — Capability Truth (what exists, its state, its maturity)

**Status: mixed — runtime-backed for enablement, current for maturity/lock state.** Enablement
is generated; maturity and lock/certification status are hand-maintained and dated.

## Sources of record

- **Enabled/disabled (generated, authoritative):**
  [`../current_runtime/CURRENT_RUNTIME_STATE.md`](../current_runtime/CURRENT_RUNTIME_STATE.md)
  and [`../current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`](../current_runtime/RUNTIME_CAPABILITY_REFERENCE.md).
- **What works today (readiness levels):**
  [`../product/WHAT_WORKS_TODAY.md`](../product/WHAT_WORKS_TODAY.md).
- **Maturity ladder:** [`../product/CAPABILITY_MATURITY.md`](../product/CAPABILITY_MATURITY.md).
- **Known limits:** [`../product/KNOWN_LIMITATIONS.md`](../product/KNOWN_LIMITATIONS.md).
- **Live-verified inventory (canonical, evidence-backed):**
  [`../capability_verification/CAPABILITY_INVENTORY.md`](../capability_verification/CAPABILITY_INVENTORY.md).
- **Certification progress:**
  [`../capability_verification/STATUS.md`](../capability_verification/STATUS.md) and
  [`../capability_verification/FRAMEWORK.md`](../capability_verification/FRAMEWORK.md).

## The three distinct states (do not conflate)

Per the repo audits: **active ≠ certified ≠ locked.**

- **Active** — enabled in the registry and runnable (generated truth).
- **Certified** — passed the P1–P5 verification framework.
- **Locked** — certified and pinned; `capability_locks.json` is the authority.

## Locked capabilities (current)

| Cap | Name | Locked | Scope |
| --- | --- | --- | --- |
| 16 | governed_web_search | 2026-05-10 | governed search + citations |
| 22 | open_file_folder | 2026-05-20 | confirmation-bound, path-root limited |
| 64 | send_email_draft | 2026-05-20 | confirmation-bound `mailto:` draft only — no SMTP, no inbox, no autonomous send |
| 65 | shopify_intelligence_report | 2026-05-22 | read-only intelligence — no Shopify writes |

## Explicit non-capabilities (labelled so no one over-claims)

- **No Google connector** — no Gmail, Calendar OAuth, Drive, Contacts, or Gmail-send runtime.
  Calendar snapshot is not a Google Calendar connector.
- **No autonomous send / write / post** anywhere.
- **No broad browser / computer-use** — OpenClaw stays bounded and manual-first.
- Screen capture / analysis is **experimental**.

## Where live verification lives

Per `CAPABILITY_INVENTORY.md`, verification **updates that one file** rather than spawning
scattered docs, and follows **QA Rule #1**: confirm the running process matches current `main`
before testing. Latest live check:
[`../capability_verification/LIVE_VERIFICATION_2026-07-07.md`](../capability_verification/LIVE_VERIFICATION_2026-07-07.md).

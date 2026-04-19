# Nova - Capability Verification Status
Updated: 2026-04-18

> **Live status:** `python scripts/certify_capability.py status`
> **Framework:** [FRAMEWORK.md](FRAMEWORK.md)
> **Checklists:** [live_checklists/](live_checklists/)

---

## Phase Legend

| Symbol | Meaning |
|---|---|
| `OK` / `pass` | Phase complete and verified |
| `..` / `pending` | Not started or in progress |
| `LOCK` / `locked` | All 6 phases passed - regression guard active |
| `OPEN` / `open` | Not yet locked |

## Phases

| Phase | Type | Description |
|---|---|---|
| P1 Unit | Automated | Executor isolated - validate, execute, ledger, ActionResult fields |
| P2 Routing | Automated | GovernorMediator -> correct cap_id + params |
| P3 Integration | Automated | Full Governor spine through real governor |
| P4 API | Automated | HTTP/WebSocket endpoint shape |
| P5 Live | **Manual** | User runs command, verifies output, signs off |
| P6 Lock | Automated | CI regression guard enforces all phases on every commit |

---

## Status Table (as of 2026-04-18)

| ID | Capability | P1 | P2 | P3 | P4 | P5 | Lock | Priority |
|---|---|---|---|---|---|---|---|---|
| 16 | governed_web_search | pending | pending | pending | pending | pending | open | Medium |
| 17 | open_website | pending | pending | pending | pending | pending | open | Medium |
| 18 | speak_text | pending | pending | pending | pending | pending | open | Medium |
| 19 | volume_up_down | pending | pending | pending | pending | pending | open | Medium |
| 20 | media_play_pause | pending | pending | pending | pending | pending | open | Medium |
| 21 | brightness_control | pending | pending | pending | pending | pending | open | Medium |
| 22 | open_file_folder | pending | pending | pending | pending | pending | open | Medium |
| 31 | response_verification | pending | pending | pending | pending | pending | open | Medium |
| 32 | os_diagnostics | pending | pending | pending | pending | pending | open | Medium |
| 48 | multi_source_reporting | pending | pending | pending | pending | pending | open | Medium |
| 49 | headline_summary | pending | pending | pending | pending | pending | open | Medium |
| 50 | intelligence_brief | pending | pending | pending | pending | pending | open | Medium |
| 51 | topic_memory_map | pending | pending | pending | pending | pending | open | Medium |
| 52 | story_tracker_update | pending | pending | pending | pending | pending | open | High |
| 53 | story_tracker_view | pending | pending | pending | pending | pending | open | Medium |
| 54 | analysis_document | pending | pending | pending | pending | pending | open | Medium |
| 55 | weather_snapshot | pending | pending | pending | pending | pending | open | Medium |
| 56 | news_snapshot | pending | pending | pending | pending | pending | open | Medium |
| 57 | calendar_snapshot | pending | pending | pending | pending | pending | open | Medium |
| 58 | screen_capture | pending | pending | pending | pending | pending | open | High |
| 59 | screen_analysis | pending | pending | pending | pending | pending | open | Medium |
| 60 | explain_anything | pending | pending | pending | pending | pending | open | Medium |
| 61 | memory_governance | pending | pending | pending | pending | pending | open | **High** |
| 62 | external_reasoning_review | pending | pending | pending | pending | pending | open | Medium |
| 63 | openclaw_execute | pending | pending | pending | pending | pending | open | Medium |
| 64 | send_email_draft | pass | pass | pass | pass | pending | open | **Highest** |

---

## Next Steps to Lock Cap 64 (send_email_draft)

Cap 64 is the highest priority - it is the first external-write capability.

```text
# 1. Run the live checklist:
#    docs/capability_verification/live_checklists/cap_64_send_email_draft.md

# 2. Sign off:
python scripts/certify_capability.py live-signoff 64

# 3. Lock:
python scripts/certify_capability.py lock 64
```

---

## Notes

- The STATUS.md table is updated manually after `certify_capability.py` commands.
  For live status, always use: `python scripts/certify_capability.py status`
- The regression guard (`tests/certification/test_lock_regression_guard.py`) runs
  automatically on every `pytest` invocation.
- No capability can be marked `locked=true` in the JSON unless all 5 phases are `pass`.
  The regression guard test enforces this.

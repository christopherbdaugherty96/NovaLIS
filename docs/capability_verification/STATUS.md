# Nova — Capability Verification Status
Updated: 2026-04-17

> **Live status:** `python scripts/certify_capability.py status`
> **Framework:** [FRAMEWORK.md](FRAMEWORK.md)
> **Checklists:** [live_checklists/](live_checklists/)

---

## Phase Legend

| Symbol | Meaning |
|---|---|
| ✅ pass | Phase complete and verified |
| ⏳ pending | Not started or in progress |
| 🔒 locked | All 6 phases passed — regression guard active |
| 🔓 open | Not yet locked |

## Phases

| Phase | Type | Description |
|---|---|---|
| P1 Unit | Automated | Executor isolated — validate, execute, ledger, ActionResult fields |
| P2 Routing | Automated | GovernorMediator → correct cap_id + params |
| P3 Integration | Automated | Full Governor spine through real governor |
| P4 API | Automated | HTTP/WebSocket endpoint shape |
| P5 Live | **Manual** | User runs command, verifies output, signs off |
| P6 Lock | Automated | CI regression guard enforces all phases on every commit |

---

## Status Table (as of 2026-04-17)

| ID | Capability | P1 | P2 | P3 | P4 | P5 | Lock | Priority |
|---|---|---|---|---|---|---|---|---|
| 16 | governed_web_search | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | 🔓 | Medium |
| 17 | open_website | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | 🔓 | Medium |
| 18 | speak_text | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | 🔓 | Medium |
| 19 | volume_up_down | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | 🔓 | Medium |
| 20 | media_play_pause | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | 🔓 | Medium |
| 21 | brightness_control | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | 🔓 | Medium |
| 22 | open_file_folder | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | 🔓 | Medium |
| 31 | response_verification | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | 🔓 | Medium |
| 32 | os_diagnostics | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | 🔓 | Medium |
| 48 | multi_source_reporting | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | 🔓 | Medium |
| 49 | headline_summary | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | 🔓 | Medium |
| 50 | intelligence_brief | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | 🔓 | Medium |
| 51 | topic_memory_map | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | 🔓 | Medium |
| 52 | story_tracker_update | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | 🔓 | High |
| 53 | story_tracker_view | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | 🔓 | Medium |
| 54 | analysis_document | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | 🔓 | Medium |
| 55 | weather_snapshot | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | 🔓 | Medium |
| 56 | news_snapshot | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | 🔓 | Medium |
| 57 | calendar_snapshot | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | 🔓 | Medium |
| 58 | screen_capture | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | 🔓 | High |
| 59 | screen_analysis | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | 🔓 | Medium |
| 60 | explain_anything | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | 🔓 | Medium |
| 61 | memory_governance | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | 🔓 | **High** |
| 62 | external_reasoning_review | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | 🔓 | Medium |
| 63 | openclaw_execute | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | 🔓 | Medium |
| 64 | send_email_draft | ✅ | ✅ | ⏳ | ⏳ | ⏳ | 🔓 | **Highest** |

---

## Next Steps to Lock Cap 64 (send_email_draft)

Cap 64 is the highest priority — it's the first external-write capability.

```
# 1. Advance P3 (integration tests exist):
python scripts/certify_capability.py advance 64 p3_integration

# 2. Advance P4 (API test written — needs live brain_server):
python scripts/certify_capability.py advance 64 p4_api

# 3. Run the live checklist:
#    docs/capability_verification/live_checklists/cap_64_send_email_draft.md

# 4. Sign off:
python scripts/certify_capability.py live-signoff 64

# 5. Lock:
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

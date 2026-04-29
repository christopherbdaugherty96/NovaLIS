# Proof Index - 2026-04-28 User Test

## Package Location

```text
docs/demo_proof/2026-04-28_user_test/
```

## Report Files

| File | Purpose |
| --- | --- |
| `USER_TEST_REPORT.md` | Main findings from startup, dashboard, chat, Trust, email draft, memory, and setup testing |
| `DEMO_SCRIPT.md` | Short demo flow and narration based on observed runtime behavior |
| `SCREENSHOT_CHECKLIST.md` | Screenshot inventory and local recapture instructions |
| `FRICTION_LOG.md` | Prioritized friction and blockers before deeper feature work |
| `PROOF_INDEX.md` | Index of proof artifacts |

## Screenshot Proof

| Artifact | Proof Use |
| --- | --- |
| `screenshots/01_dashboard_home.png` | Initial load proof |
| `screenshots/02_intro_setup_surface.png` | Intro/local-first setup proof |
| `screenshots/03_workspace_home.png` | Simplified Home friction proof |
| `screenshots/04_full_ui_dashboard.png` | Full dashboard proof |
| `screenshots/05_chat_area_before_prompt.png` | Chat surface proof |
| `screenshots/06_chat_what_works_today.png` | Basic prompt plus token-budget blocker proof |
| `screenshots/07_trust_receipts.png` | Trust page empty visible receipt state proof |
| `screenshots/08_trust_after_refresh.png` | Trust page after refresh still empty proof |
| `screenshots/09_email_draft_attempt_chat.png` | Email draft/no-send boundary proof |
| `screenshots/10_memory_context_boundary.png` | Memory is explicit/inspectable/revocable proof |
| `screenshots/11_settings_setup_usage.png` | Settings/local-first/setup/budget surfaces proof |

## Video Proof

| Artifact | Proof Use |
| --- | --- |
| `video/nova_user_test_demo_flow.webm` | Real recorded browser flow through Intro, full UI, Chat, email draft prompt, Trust, and Memory |

## Command/API Evidence

### Startup

Command:

```powershell
.\start_nova.bat
```

Observed output:

```text
[Nova] Already running at http://127.0.0.1:8000
```

### Phase Status

Endpoint:

```text
http://127.0.0.1:8000/phase-status
```

Observed summary:

```text
phase: 8
status: active
execution_enabled: true
delegated_runtime_enabled: false
```

### Trust Receipts API

Endpoint:

```text
http://127.0.0.1:8000/api/trust/receipts?limit=10
```

Observed receipt summary:

```text
OPENCLAW_AGENT_RUN_COMPLETED
template_id: morning_brief
delivery_mode: hybrid
delivery_channels: widget/chat
estimated_total_tokens: 160
```

Important discrepancy:

- The API returned receipt data.
- The Trust UI did not visibly render recent governed actions in this pass.

## Current Proof Status

| Question | Status | Evidence |
| --- | --- | --- |
| Can a user start Nova? | partial pass | `start_nova.bat` verified already-running runtime |
| Can a user understand what Nova is? | pass | Intro and Settings screenshots |
| Can a user use the dashboard? | partial pass | Full UI works; simplified Home is weak |
| Can a user see receipts/proof? | partial fail | API works; Trust UI did not render receipts |
| Can a user test a governed action? | partial pass | Email draft prompt produced boundary text; no fresh receipt proof |
| Can a user understand email draft does not send email? | pass | Chat response states manual review/send boundary |
| Can a user understand memory/context are not authority? | pass | Memory page states explicit, inspectable, revocable memory |
| What blocks trust/demo quality? | documented | See `FRICTION_LOG.md` |

## Local-First Follow-Up Pass - 2026-04-28

### New Screenshot Evidence

| Artifact | Proof Use |
| --- | --- |
| `screenshots/local_first_followup/level0_dashboard_connection_status.png` | Dashboard loaded after websocket status settled to `LOCAL-ONLY` |
| `screenshots/local_first_followup/level1_intro_after_modal_close.png` | Intro/onboarding after closing first-run modal |
| `screenshots/local_first_followup/level1_surface_chat.png` | Chat surface loads |
| `screenshots/local_first_followup/level1_surface_news.png` | News surface loads with optional data state |
| `screenshots/local_first_followup/level1_surface_intro.png` | Intro surface loads |
| `screenshots/local_first_followup/level1_surface_home.png` | Home surface loads with useful widgets visible |
| `screenshots/local_first_followup/level1_surface_workspace.png` | Workspace surface loads |
| `screenshots/local_first_followup/level1_surface_memory.png` | Memory surface loads |
| `screenshots/local_first_followup/level1_surface_policy.png` | Rules/Policies surface loads |
| `screenshots/local_first_followup/level1_surface_trust.png` | Trust page renders Action Receipts and boundary panels |
| `screenshots/local_first_followup/level1_surface_settings.png` | Settings surface loads |
| `screenshots/local_first_followup/level2_what_works.png` | `What works today?` answered by local fallback despite exhausted budget |
| `screenshots/local_first_followup/level2_memory_authority.png` | Memory-authority answer says memory cannot authorize actions |
| `screenshots/local_first_followup/level4_system_status.png` | Safe local `system status` action proof |
| `screenshots/local_first_followup/level5_cap64_confirmation_boundary.png` | Cap 64 email draft confirmation boundary; not sent and not executed past confirmation |
| `screenshots/local_first_followup/level6_shopify_report.png` | Shopify missing-credentials behavior is clean and read-only |
| `screenshots/local_first_followup/level3_trust_receipts_api.png` | Direct receipts API JSON proof |
| `screenshots/local_first_followup/level3_trust_summary_api.png` | Direct receipts summary API JSON proof |

### New Command/API Evidence

Startup and environment:

```powershell
git status --short
git rev-parse --abbrev-ref HEAD
git rev-parse HEAD
python --version
node --version
```

Observed:

```text
branch: main
commit: a51b5fa52427531eda8462dbb9cc0e63507275fb
Python 3.10.9
Node v24.13.0
```

Health:

```text
http://127.0.0.1:8000/phase-status
phase: 8
status: active
execution_enabled: true
delegated_runtime_enabled: false
```

Receipts:

```text
http://127.0.0.1:8000/api/trust/receipts?limit=10
http://127.0.0.1:8000/api/trust/receipts/summary
```

Observed:

- API returned JSON receipts.
- Trust UI rendered Action Receipts.
- Latest receipts included local `ACTION_ATTEMPTED` events and completed read-only local `calendar_snapshot` receipts.

### Updated Proof Status

| Question | Status | Evidence |
| --- | --- | --- |
| Can a user start Nova? | pass with friction | start daemon now handles stale Nova listener/PID mismatch; health endpoint active |
| Can a user understand what Nova is? | pass | Intro/Home/Settings screenshots |
| Can a user use the dashboard? | pass with minor friction | all main surfaces loaded; optional network degradation remains confusing |
| Can a user see receipts/proof? | pass with label friction | API works and Trust UI renders receipts |
| Can a user test a governed action? | partial pass | `system status` works; Cap 64 tested only to confirmation boundary |
| Can a user understand email draft does not send email? | pass | Cap 64 confirmation boundary says review/send manually |
| Can a user understand memory/context are not authority? | pass | live chat memory-authority answer and Memory page |
| What blocks trust/demo quality? | documented | See follow-up friction log |

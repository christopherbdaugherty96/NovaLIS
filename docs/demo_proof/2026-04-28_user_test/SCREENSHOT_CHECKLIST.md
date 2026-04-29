# Screenshot Checklist - 2026-04-28 User Test

## Captured Screenshots

All screenshots below are real captures from `http://127.0.0.1:8000`.

| File | Status | What It Shows |
| --- | --- | --- |
| `screenshots/01_dashboard_home.png` | captured | Initial dashboard/Intro state after load |
| `screenshots/02_intro_setup_surface.png` | captured | Intro setup surface after closing first-run modal |
| `screenshots/03_workspace_home.png` | captured | Simplified Home view, mostly empty except chrome and `Show full UI` |
| `screenshots/04_full_ui_dashboard.png` | captured | Full UI Home dashboard with navigation, operational context, and workspace surfaces |
| `screenshots/05_chat_area_before_prompt.png` | captured | Chat area before prompt |
| `screenshots/06_chat_what_works_today.png` | captured | Basic conversation attempt blocked by token budget |
| `screenshots/07_trust_receipts.png` | captured | Trust page with empty visible receipt state |
| `screenshots/08_trust_after_refresh.png` | captured | Trust page after `Refresh trust`, still empty visible receipt state |
| `screenshots/09_email_draft_attempt_chat.png` | captured | Email draft prompt and visible draft-only/no-send boundary message |
| `screenshots/10_memory_context_boundary.png` | captured | Memory page explaining explicit, inspectable, revocable memory |
| `screenshots/11_settings_setup_usage.png` | captured | Settings setup, local-first mode, governed permissions, budget/route surfaces |

## Not Captured As Screenshots

| Item | Status | Reason |
| --- | --- | --- |
| Terminal after successful startup | needs local capture | Shell output was captured as command output, but no terminal image was captured in this environment |
| Local mail client draft window | needs local capture | Headless browser could not visually verify an OS mail client window |
| Cold-start timing stopwatch | needs local capture | Nova was already running when the test began |

## Recommended Local Capture Steps

1. Stop Nova with `.\stop_nova.bat`.
2. Open a visible PowerShell terminal.
3. Run `.\start_nova.bat`.
4. Capture terminal after it reports the local URL.
5. Open `http://127.0.0.1:8000` in a visible browser.
6. Repeat the screenshot sequence above.
7. For email proof, use a machine with a configured mail client and capture the draft window before closing it without sending.

## Local-First Follow-Up Pass - 2026-04-28

All screenshots below are real captures from `http://127.0.0.1:8000` and are stored in `screenshots/local_first_followup/`.

| File | Status | What It Shows |
| --- | --- | --- |
| `level0_dashboard_connection_status.png` | captured | Dashboard loaded with header settled to `LOCAL-ONLY` |
| `level1_intro_after_modal_close.png` | captured | Intro surface after closing the first-run modal |
| `level1_full_ui_after_toggle.png` | captured | Full UI navigation available after toggling out of simplified mode |
| `level1_surface_chat.png` | captured | Chat surface |
| `level1_surface_news.png` | captured | News surface |
| `level1_surface_intro.png` | captured | Intro surface |
| `level1_surface_home.png` | captured | Home surface with useful widgets visible |
| `level1_surface_workspace.png` | captured | Workspace surface |
| `level1_surface_memory.png` | captured | Memory surface |
| `level1_surface_policy.png` | captured | Rules/Policies surface |
| `level1_surface_trust.png` | captured | Trust page with rendered Action Receipts |
| `level1_surface_settings.png` | captured | Settings surface |
| `level2_prompt_1_error.png` | captured | Pre-fix proof that `What works today?` hit daily token budget |
| `level2_what_works.png` | captured | Post-fix proof that `What works today?` returns a local fallback |
| `level2_memory_authority.png` | captured | Post-fix proof that memory cannot authorize actions |
| `level4_system_status.png` | captured | Safe local `system status` action |
| `level5_cap64_confirmation_boundary.png` | captured | Cap 64 email draft confirmation boundary |
| `level6_shopify_report.png` | captured | Shopify not-configured/read-only behavior |
| `level3_trust_receipts_api.png` | captured | Direct receipts API JSON |
| `level3_trust_summary_api.png` | captured | Direct receipts summary API JSON |

Not captured in this follow-up:

| Item | Status | Reason |
| --- | --- | --- |
| New video | needs local capture | This pass focused on friction fixes and screenshots; no new `.webm` was recorded |
| Local mail client draft window | needs action-time approval/local capture | The Cap 64 test stopped at the confirmation boundary and did not open the mail client |
| Browser Use screenshot | blocked | Node REPL browser runtime crashed on invalid `C:\Users\Chris\package.json`; Playwright fallback was used |

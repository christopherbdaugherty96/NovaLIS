# GOVERNANCE_MATRIX_TREE

Deterministic generated tree diagram derived from allowlisted runtime sources.

```mermaid
graph TD
  Runtime[Phase-4 Runtime]
  Runtime --> Enabled[Enabled IDs: [16, 17, 18, 19, 20, 21, 22, 31, 32, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65]]
  Runtime --> Disabled[Disabled IDs: []]
  Runtime --> Gov[Governor Guards]
  Gov --> EG[execution_gate: True]
  Gov --> SAQ[single_action_queue: True]
  Gov --> LA[ledger_allowlist: True]
  Gov --> DNS[dns_rebinding_guard: True]
  Gov --> TO[timeout_guard: True]
  Runtime --> Caps[Capabilities]
  Caps --> C16[16:governed_web_search]
  C16 --> C16A[authority=read_only_network, risk=low, confirm=False, reversible=True, external=False, network=True, surface=Governor -> NetworkMediator]
  Caps --> C17[17:open_website]
  C17 --> C17A[authority=reversible_local, risk=low, confirm=False, reversible=True, external=False, network=False, surface=Governor -> Executor]
  Caps --> C18[18:speak_text]
  C18 --> C18A[authority=reversible_local, risk=low, confirm=False, reversible=True, external=False, network=False, surface=Governor -> Speech]
  Caps --> C19[19:volume_up_down]
  C19 --> C19A[authority=reversible_local, risk=low, confirm=False, reversible=True, external=False, network=False, surface=Governor -> Executor]
  Caps --> C20[20:media_play_pause]
  C20 --> C20A[authority=reversible_local, risk=low, confirm=False, reversible=True, external=False, network=False, surface=Governor -> Executor]
  Caps --> C21[21:brightness_control]
  C21 --> C21A[authority=reversible_local, risk=low, confirm=False, reversible=True, external=False, network=False, surface=Governor -> Executor]
  Caps --> C22[22:open_file_folder]
  C22 --> C22A[authority=reversible_local, risk=confirm, confirm=True, reversible=True, external=False, network=False, surface=Governor -> Executor]
  Caps --> C31[31:response_verification]
  C31 --> C31A[authority=read_only_local, risk=low, confirm=False, reversible=True, external=False, network=False, surface=Governor -> Executor]
  Caps --> C32[32:os_diagnostics]
  C32 --> C32A[authority=read_only_local, risk=low, confirm=False, reversible=True, external=False, network=False, surface=Governor -> Executor]
  Caps --> C48[48:multi_source_reporting]
  C48 --> C48A[authority=read_only_network, risk=low, confirm=False, reversible=True, external=False, network=True, surface=Governor -> NetworkMediator]
  Caps --> C49[49:headline_summary]
  C49 --> C49A[authority=read_only_network, risk=low, confirm=False, reversible=True, external=False, network=True, surface=Governor -> NetworkMediator]
  Caps --> C50[50:intelligence_brief]
  C50 --> C50A[authority=read_only_network, risk=low, confirm=False, reversible=True, external=False, network=True, surface=Governor -> NetworkMediator]
  Caps --> C51[51:topic_memory_map]
  C51 --> C51A[authority=read_only_local, risk=low, confirm=False, reversible=True, external=False, network=True, surface=Governor -> NetworkMediator]
  Caps --> C52[52:story_tracker_update]
  C52 --> C52A[authority=persistent_change, risk=low, confirm=False, reversible=False, external=False, network=False, surface=Governor -> Executor]
  Caps --> C53[53:story_tracker_view]
  C53 --> C53A[authority=read_only_local, risk=low, confirm=False, reversible=True, external=False, network=False, surface=Governor -> Executor]
  Caps --> C54[54:analysis_document]
  C54 --> C54A[authority=read_only_local, risk=low, confirm=False, reversible=True, external=False, network=False, surface=Governor -> Executor]
  Caps --> C55[55:weather_snapshot]
  C55 --> C55A[authority=read_only_network, risk=low, confirm=False, reversible=True, external=False, network=True, surface=Governor -> NetworkMediator]
  Caps --> C56[56:news_snapshot]
  C56 --> C56A[authority=read_only_network, risk=low, confirm=False, reversible=True, external=False, network=True, surface=Governor -> NetworkMediator]
  Caps --> C57[57:calendar_snapshot]
  C57 --> C57A[authority=read_only_local, risk=low, confirm=False, reversible=True, external=False, network=False, surface=Governor -> Executor]
  Caps --> C58[58:screen_capture]
  C58 --> C58A[authority=persistent_change, risk=low, confirm=False, reversible=False, external=False, network=False, surface=Governor -> Executor]
  Caps --> C59[59:screen_analysis]
  C59 --> C59A[authority=read_only_local, risk=low, confirm=False, reversible=True, external=False, network=False, surface=Governor -> Executor]
  Caps --> C60[60:explain_anything]
  C60 --> C60A[authority=read_only_local, risk=low, confirm=False, reversible=True, external=False, network=False, surface=Governor -> Executor]
  Caps --> C61[61:memory_governance]
  C61 --> C61A[authority=persistent_change, risk=low, confirm=False, reversible=False, external=False, network=False, surface=Governor -> Executor]
  Caps --> C62[62:external_reasoning_review]
  C62 --> C62A[authority=read_only_local, risk=low, confirm=False, reversible=True, external=False, network=False, surface=Governor -> Executor]
  Caps --> C63[63:openclaw_execute]
  C63 --> C63A[authority=read_only_network, risk=low, confirm=False, reversible=True, external=True, network=True, surface=Governor -> NetworkMediator]
  Caps --> C64[64:send_email_draft]
  C64 --> C64A[authority=persistent_change, risk=confirm, confirm=True, reversible=False, external=True, network=False, surface=Governor -> Executor]
  Caps --> C65[65:shopify_intelligence_report]
  C65 --> C65A[authority=read_only_network, risk=low, confirm=False, reversible=True, external=True, network=True, surface=Governor -> NetworkMediator]
  Runtime --> Routes[Skill Routes]
  Routes --> R54_analysis_document[analysis_document -> capability 54]
  Routes --> R21_brightness[brightness -> capability 21]
  Routes --> R57_calendar_snapshot[calendar_snapshot -> capability 57]
  Routes --> R32_diagnostics[diagnostics -> capability 32]
  Routes --> R60_explain_anything[explain_anything -> capability 60]
  Routes --> R62_external_reasoning_review[external_reasoning_review -> capability 62]
  Routes --> R49_headline_summary[headline_summary -> capability 49]
  Routes --> R50_intelligence_brief[intelligence_brief -> capability 50]
  Routes --> R20_media[media -> capability 20]
  Routes --> R61_memory_governance[memory_governance -> capability 61]
  Routes --> R56_news_snapshot[news_snapshot -> capability 56]
  Routes --> R22_open_folder[open_folder -> capability 22]
  Routes --> R17_open_website[open_website -> capability 17]
  Routes --> R63_openclaw_execute[openclaw_execute -> capability 63]
  Routes --> R49_report[report -> capability 49]
  Routes --> R31_response_verification[response_verification -> capability 31]
  Routes --> R59_screen_analysis[screen_analysis -> capability 59]
  Routes --> R58_screen_capture[screen_capture -> capability 58]
  Routes --> R48_search[search -> capability 48]
  Routes --> R64_send_email_draft[send_email_draft -> capability 64]
  Routes --> R65_shopify_intelligence_report[shopify_intelligence_report -> capability 65]
  Routes --> R18_speak[speak -> capability 18]
  Routes --> R52_story_tracker_update[story_tracker_update -> capability 52]
  Routes --> R53_story_tracker_view[story_tracker_view -> capability 53]
  Routes --> R51_topic_memory_map[topic_memory_map -> capability 51]
  Routes --> R19_volume[volume -> capability 19]
  Routes --> R55_weather_snapshot[weather_snapshot -> capability 55]
  Runtime --> LLM[Conversation/Model Surfaces]
  LLM --> src_conversation_deepseek_bridge_py[src/conversation/deepseek_bridge.py uses llm_gateway.generate_chat]
  LLM --> src_skills_general_chat_py[src/skills/general_chat.py uses llm_gateway.generate_chat]
  LLM --> src_openclaw_agent_runner_py[src/openclaw/agent_runner.py uses llm_gateway.generate_chat]
```

```text
Runtime
|- Enabled IDs: [16, 17, 18, 19, 20, 21, 22, 31, 32, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65]
|- Disabled IDs: []
|- Governor Guards
|  |- execution_gate: True
|  |- single_action_queue: True
|  |- ledger_allowlist: True
|  |- dns_rebinding_guard: True
|  |- timeout_guard: True
|- Capabilities
|  |- 16 governed_web_search (authority=read_only_network, risk=low, network=True, exfil=True, confirm=False, surface=Governor -> NetworkMediator)
|  |- 17 open_website (authority=reversible_local, risk=low, network=False, exfil=False, confirm=False, surface=Governor -> Executor)
|  |- 18 speak_text (authority=reversible_local, risk=low, network=False, exfil=False, confirm=False, surface=Governor -> Speech)
|  |- 19 volume_up_down (authority=reversible_local, risk=low, network=False, exfil=False, confirm=False, surface=Governor -> Executor)
|  |- 20 media_play_pause (authority=reversible_local, risk=low, network=False, exfil=False, confirm=False, surface=Governor -> Executor)
|  |- 21 brightness_control (authority=reversible_local, risk=low, network=False, exfil=False, confirm=False, surface=Governor -> Executor)
|  |- 22 open_file_folder (authority=reversible_local, risk=confirm, network=False, exfil=False, confirm=True, surface=Governor -> Executor)
|  |- 31 response_verification (authority=read_only_local, risk=low, network=False, exfil=False, confirm=False, surface=Governor -> Executor)
|  |- 32 os_diagnostics (authority=read_only_local, risk=low, network=False, exfil=False, confirm=False, surface=Governor -> Executor)
|  |- 48 multi_source_reporting (authority=read_only_network, risk=low, network=True, exfil=True, confirm=False, surface=Governor -> NetworkMediator)
|  |- 49 headline_summary (authority=read_only_network, risk=low, network=True, exfil=True, confirm=False, surface=Governor -> NetworkMediator)
|  |- 50 intelligence_brief (authority=read_only_network, risk=low, network=True, exfil=True, confirm=False, surface=Governor -> NetworkMediator)
|  |- 51 topic_memory_map (authority=read_only_local, risk=low, network=True, exfil=False, confirm=False, surface=Governor -> NetworkMediator)
|  |- 52 story_tracker_update (authority=persistent_change, risk=low, network=False, exfil=False, confirm=False, surface=Governor -> Executor)
|  |- 53 story_tracker_view (authority=read_only_local, risk=low, network=False, exfil=False, confirm=False, surface=Governor -> Executor)
|  |- 54 analysis_document (authority=read_only_local, risk=low, network=False, exfil=False, confirm=False, surface=Governor -> Executor)
|  |- 55 weather_snapshot (authority=read_only_network, risk=low, network=True, exfil=True, confirm=False, surface=Governor -> NetworkMediator)
|  |- 56 news_snapshot (authority=read_only_network, risk=low, network=True, exfil=True, confirm=False, surface=Governor -> NetworkMediator)
|  |- 57 calendar_snapshot (authority=read_only_local, risk=low, network=False, exfil=False, confirm=False, surface=Governor -> Executor)
|  |- 58 screen_capture (authority=persistent_change, risk=low, network=False, exfil=False, confirm=False, surface=Governor -> Executor)
|  |- 59 screen_analysis (authority=read_only_local, risk=low, network=False, exfil=False, confirm=False, surface=Governor -> Executor)
|  |- 60 explain_anything (authority=read_only_local, risk=low, network=False, exfil=False, confirm=False, surface=Governor -> Executor)
|  |- 61 memory_governance (authority=persistent_change, risk=low, network=False, exfil=False, confirm=False, surface=Governor -> Executor)
|  |- 62 external_reasoning_review (authority=read_only_local, risk=low, network=False, exfil=False, confirm=False, surface=Governor -> Executor)
|  |- 63 openclaw_execute (authority=read_only_network, risk=low, network=True, exfil=False, confirm=False, surface=Governor -> NetworkMediator)
|  |- 64 send_email_draft (authority=persistent_change, risk=confirm, network=False, exfil=True, confirm=True, surface=Governor -> Executor)
|  |- 65 shopify_intelligence_report (authority=read_only_network, risk=low, network=True, exfil=False, confirm=False, surface=Governor -> NetworkMediator)
|- Skill -> capability routes
|  |- analysis_document -> 54
|  |- brightness -> 21
|  |- calendar_snapshot -> 57
|  |- diagnostics -> 32
|  |- explain_anything -> 60
|  |- external_reasoning_review -> 62
|  |- headline_summary -> 49
|  |- intelligence_brief -> 50
|  |- media -> 20
|  |- memory_governance -> 61
|  |- news_snapshot -> 56
|  |- open_folder -> 22
|  |- open_website -> 17
|  |- openclaw_execute -> 63
|  |- report -> 49
|  |- response_verification -> 31
|  |- screen_analysis -> 59
|  |- screen_capture -> 58
|  |- search -> 48
|  |- send_email_draft -> 64
|  |- shopify_intelligence_report -> 65
|  |- speak -> 18
|  |- story_tracker_update -> 52
|  |- story_tracker_view -> 53
|  |- topic_memory_map -> 51
|  |- volume -> 19
|  |- weather_snapshot -> 55
|- Conversation/model surfaces
   |- src/conversation/deepseek_bridge.py -> llm_gateway.generate_chat
   |- src/skills/general_chat.py -> llm_gateway.generate_chat
   |- src/openclaw/agent_runner.py -> llm_gateway.generate_chat
```

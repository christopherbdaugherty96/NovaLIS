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
  C16 --> C16A[authority=read_only_network, risk=low, cost=free_tier, confirm=False, reversible=True, external=False, network=True, surface=Governor -> NetworkMediator]
  Caps --> C17[17:open_website]
  C17 --> C17A[authority=reversible_local, risk=low, cost=free, confirm=False, reversible=True, external=False, network=False, surface=Governor -> Executor]
  Caps --> C18[18:speak_text]
  C18 --> C18A[authority=reversible_local, risk=low, cost=free, confirm=False, reversible=True, external=False, network=False, surface=Governor -> Speech]
  Caps --> C19[19:volume_up_down]
  C19 --> C19A[authority=reversible_local, risk=low, cost=free, confirm=False, reversible=True, external=False, network=False, surface=Governor -> Executor]
  Caps --> C20[20:media_play_pause]
  C20 --> C20A[authority=reversible_local, risk=low, cost=free, confirm=False, reversible=True, external=False, network=False, surface=Governor -> Executor]
  Caps --> C21[21:brightness_control]
  C21 --> C21A[authority=reversible_local, risk=low, cost=free, confirm=False, reversible=True, external=False, network=False, surface=Governor -> Executor]
  Caps --> C22[22:open_file_folder]
  C22 --> C22A[authority=reversible_local, risk=confirm, cost=free, confirm=True, reversible=True, external=False, network=False, surface=Governor -> Executor]
  Caps --> C31[31:response_verification]
  C31 --> C31A[authority=read_only_local, risk=low, cost=free, confirm=False, reversible=True, external=False, network=False, surface=Governor -> Executor]
  Caps --> C32[32:os_diagnostics]
  C32 --> C32A[authority=read_only_local, risk=low, cost=free, confirm=False, reversible=True, external=False, network=False, surface=Governor -> Executor]
  Caps --> C48[48:multi_source_reporting]
  C48 --> C48A[authority=read_only_network, risk=confirm, cost=free, confirm=True, reversible=True, external=False, network=True, surface=Governor -> NetworkMediator]
  Caps --> C49[49:headline_summary]
  C49 --> C49A[authority=read_only_network, risk=low, cost=free, confirm=False, reversible=True, external=False, network=True, surface=Governor -> NetworkMediator]
  Caps --> C50[50:intelligence_brief]
  C50 --> C50A[authority=read_only_network, risk=low, cost=free, confirm=False, reversible=True, external=False, network=True, surface=Governor -> NetworkMediator]
  Caps --> C51[51:topic_memory_map]
  C51 --> C51A[authority=read_only_local, risk=low, cost=free, confirm=False, reversible=True, external=False, network=True, surface=Governor -> NetworkMediator]
  Caps --> C52[52:story_tracker_update]
  C52 --> C52A[authority=persistent_change, risk=low, cost=free, confirm=False, reversible=False, external=False, network=False, surface=Governor -> Executor]
  Caps --> C53[53:story_tracker_view]
  C53 --> C53A[authority=read_only_local, risk=low, cost=free, confirm=False, reversible=True, external=False, network=False, surface=Governor -> Executor]
  Caps --> C54[54:analysis_document]
  C54 --> C54A[authority=read_only_local, risk=low, cost=free, confirm=False, reversible=True, external=False, network=False, surface=Governor -> Executor]
  Caps --> C55[55:weather_snapshot]
  C55 --> C55A[authority=read_only_network, risk=low, cost=free_tier, confirm=False, reversible=True, external=False, network=True, surface=Governor -> NetworkMediator]
  Caps --> C56[56:news_snapshot]
  C56 --> C56A[authority=read_only_network, risk=low, cost=free_tier, confirm=False, reversible=True, external=False, network=True, surface=Governor -> NetworkMediator]
  Caps --> C57[57:calendar_snapshot]
  C57 --> C57A[authority=read_only_local, risk=low, cost=free, confirm=False, reversible=True, external=False, network=False, surface=Governor -> Executor]
  Caps --> C58[58:screen_capture]
  C58 --> C58A[authority=persistent_change, risk=low, cost=free, confirm=False, reversible=False, external=False, network=False, surface=Governor -> Executor]
  Caps --> C59[59:screen_analysis]
  C59 --> C59A[authority=read_only_local, risk=low, cost=free, confirm=False, reversible=True, external=False, network=False, surface=Governor -> Executor]
  Caps --> C60[60:explain_anything]
  C60 --> C60A[authority=read_only_local, risk=low, cost=free, confirm=False, reversible=True, external=False, network=False, surface=Governor -> Executor]
  Caps --> C61[61:memory_governance]
  C61 --> C61A[authority=persistent_change, risk=low, cost=free, confirm=False, reversible=False, external=False, network=False, surface=Governor -> Executor]
  Caps --> C62[62:external_reasoning_review]
  C62 --> C62A[authority=read_only_network, risk=low, cost=paid, confirm=False, reversible=True, external=True, network=True, surface=Governor -> NetworkMediator]
  Caps --> C63[63:openclaw_execute]
  C63 --> C63A[authority=read_only_network, risk=low, cost=unknown_cost, confirm=False, reversible=True, external=True, network=True, surface=Governor -> NetworkMediator]
  Caps --> C64[64:send_email_draft]
  C64 --> C64A[authority=persistent_change, risk=confirm, cost=free, confirm=True, reversible=False, external=True, network=False, surface=Governor -> Executor]
  Caps --> C65[65:shopify_intelligence_report]
  C65 --> C65A[authority=read_only_network, risk=low, cost=free_tier, confirm=False, reversible=True, external=True, network=True, surface=Governor -> NetworkMediator]
  Runtime --> Routes[Skill Routes]
  Routes --> R22_open_folder[open_folder -> capability 22]
  Runtime --> LLM[Conversation/Model Surfaces]
  LLM --> src_conversation_deepseek_bridge_py[src/conversation/deepseek_bridge.py uses llm_gateway.generate_chat only for explicit local fallback]
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
|  |- 16 governed_web_search (authority=read_only_network, risk=low, cost=free_tier, network=True, exfil=True, confirm=False, surface=Governor -> NetworkMediator)
|  |- 17 open_website (authority=reversible_local, risk=low, cost=free, network=False, exfil=False, confirm=False, surface=Governor -> Executor)
|  |- 18 speak_text (authority=reversible_local, risk=low, cost=free, network=False, exfil=False, confirm=False, surface=Governor -> Speech)
|  |- 19 volume_up_down (authority=reversible_local, risk=low, cost=free, network=False, exfil=False, confirm=False, surface=Governor -> Executor)
|  |- 20 media_play_pause (authority=reversible_local, risk=low, cost=free, network=False, exfil=False, confirm=False, surface=Governor -> Executor)
|  |- 21 brightness_control (authority=reversible_local, risk=low, cost=free, network=False, exfil=False, confirm=False, surface=Governor -> Executor)
|  |- 22 open_file_folder (authority=reversible_local, risk=confirm, cost=free, network=False, exfil=False, confirm=True, surface=Governor -> Executor)
|  |- 31 response_verification (authority=read_only_local, risk=low, cost=free, network=False, exfil=False, confirm=False, surface=Governor -> Executor)
|  |- 32 os_diagnostics (authority=read_only_local, risk=low, cost=free, network=False, exfil=False, confirm=False, surface=Governor -> Executor)
|  |- 48 multi_source_reporting (authority=read_only_network, risk=confirm, cost=free, network=True, exfil=True, confirm=True, surface=Governor -> NetworkMediator)
|  |- 49 headline_summary (authority=read_only_network, risk=low, cost=free, network=True, exfil=True, confirm=False, surface=Governor -> NetworkMediator)
|  |- 50 intelligence_brief (authority=read_only_network, risk=low, cost=free, network=True, exfil=True, confirm=False, surface=Governor -> NetworkMediator)
|  |- 51 topic_memory_map (authority=read_only_local, risk=low, cost=free, network=True, exfil=False, confirm=False, surface=Governor -> NetworkMediator)
|  |- 52 story_tracker_update (authority=persistent_change, risk=low, cost=free, network=False, exfil=False, confirm=False, surface=Governor -> Executor)
|  |- 53 story_tracker_view (authority=read_only_local, risk=low, cost=free, network=False, exfil=False, confirm=False, surface=Governor -> Executor)
|  |- 54 analysis_document (authority=read_only_local, risk=low, cost=free, network=False, exfil=False, confirm=False, surface=Governor -> Executor)
|  |- 55 weather_snapshot (authority=read_only_network, risk=low, cost=free_tier, network=True, exfil=True, confirm=False, surface=Governor -> NetworkMediator)
|  |- 56 news_snapshot (authority=read_only_network, risk=low, cost=free_tier, network=True, exfil=True, confirm=False, surface=Governor -> NetworkMediator)
|  |- 57 calendar_snapshot (authority=read_only_local, risk=low, cost=free, network=False, exfil=False, confirm=False, surface=Governor -> Executor)
|  |- 58 screen_capture (authority=persistent_change, risk=low, cost=free, network=False, exfil=False, confirm=False, surface=Governor -> Executor)
|  |- 59 screen_analysis (authority=read_only_local, risk=low, cost=free, network=False, exfil=False, confirm=False, surface=Governor -> Executor)
|  |- 60 explain_anything (authority=read_only_local, risk=low, cost=free, network=False, exfil=False, confirm=False, surface=Governor -> Executor)
|  |- 61 memory_governance (authority=persistent_change, risk=low, cost=free, network=False, exfil=False, confirm=False, surface=Governor -> Executor)
|  |- 62 external_reasoning_review (authority=read_only_network, risk=low, cost=paid, network=True, exfil=True, confirm=False, surface=Governor -> NetworkMediator)
|  |- 63 openclaw_execute (authority=read_only_network, risk=low, cost=unknown_cost, network=True, exfil=False, confirm=False, surface=Governor -> NetworkMediator)
|  |- 64 send_email_draft (authority=persistent_change, risk=confirm, cost=free, network=False, exfil=True, confirm=True, surface=Governor -> Executor)
|  |- 65 shopify_intelligence_report (authority=read_only_network, risk=low, cost=free_tier, network=True, exfil=False, confirm=False, surface=Governor -> NetworkMediator)
|- Skill -> capability routes
|  |- open_folder -> 22
|- Conversation/model surfaces
   |- src/conversation/deepseek_bridge.py uses llm_gateway.generate_chat only for explicit local fallback
   |- src/skills/general_chat.py uses llm_gateway.generate_chat
   |- src/openclaw/agent_runner.py uses llm_gateway.generate_chat
```

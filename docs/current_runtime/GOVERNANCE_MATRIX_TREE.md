# GOVERNANCE_MATRIX_TREE

Deterministic generated tree diagram derived from allowlisted runtime sources.

```mermaid
graph TD
  Runtime[Phase-4 Runtime]
  Runtime --> Enabled[Enabled IDs: [16, 17, 18, 19, 20, 21, 32]]
  Runtime --> Disabled[Disabled IDs: [22, 48]]
  Runtime --> Gov[Governor Guards]
  Gov --> EG[execution_gate: True]
  Gov --> SAQ[single_action_queue: True]
  Gov --> LA[ledger_allowlist: True]
  Gov --> DNS[dns_rebinding_guard: True]
  Gov --> TO[timeout_guard: True]
  Runtime --> Caps[Capabilities]
  Caps --> C16[16:governed_web_search]
  C16 --> C16A[authority=read_only, risk=low, network=True, exfil=True, confirm=False, surface=Governor â†’ NetworkMediator]
  Caps --> C17[17:open_website]
  C17 --> C17A[authority=system_action, risk=low, network=False, exfil=False, confirm=False, surface=Governor â†’ Executor]
  Caps --> C18[18:speak_text]
  C18 --> C18A[authority=speech_output, risk=low, network=False, exfil=False, confirm=False, surface=Governor â†’ Speech]
  Caps --> C19[19:volume_up_down]
  C19 --> C19A[authority=system_action, risk=low, network=False, exfil=False, confirm=False, surface=Governor â†’ Executor]
  Caps --> C20[20:media_play_pause]
  C20 --> C20A[authority=system_action, risk=low, network=False, exfil=False, confirm=False, surface=Governor â†’ Executor]
  Caps --> C21[21:brightness_control]
  C21 --> C21A[authority=system_action, risk=low, network=False, exfil=False, confirm=False, surface=Governor â†’ Executor]
  Caps --> C22[22:open_file_folder]
  C22 --> C22A[authority=confirm_required, risk=confirm, network=False, exfil=False, confirm=True, surface=Governor â†’ Executor]
  Caps --> C32[32:os_diagnostics]
  C32 --> C32A[authority=system_action, risk=low, network=False, exfil=False, confirm=False, surface=Governor â†’ Executor]
  Caps --> C48[48:multi_source_reporting]
  C48 --> C48A[authority=read_only, risk=low, network=True, exfil=True, confirm=False, surface=Governor â†’ NetworkMediator]
  Runtime --> Routes[Skill Routes]
  Routes --> R21_brightness[brightness -> capability 21]
  Routes --> R32_diagnostics[diagnostics -> capability 32]
  Routes --> R20_media[media -> capability 20]
  Routes --> R17_open_website[open_website -> capability 17]
  Routes --> R16_search[search -> capability 16]
  Routes --> R18_speak[speak -> capability 18]
  Routes --> R19_volume[volume -> capability 19]
  Runtime --> LLM[Conversation/Model Surfaces]
  LLM --> src_conversation_deepseek_bridge_py[src/conversation/deepseek_bridge.py uses llm_gateway.generate_chat]
  LLM --> src_skills_general_chat_py[src/skills/general_chat.py uses llm_gateway.generate_chat]
```

```text
Runtime
â”œâ”€ Enabled IDs: [16, 17, 18, 19, 20, 21, 32]
â”œâ”€ Disabled IDs: [22, 48]
â”œâ”€ Governor Guards
â”‚  â”œâ”€ execution_gate: True
â”‚  â”œâ”€ single_action_queue: True
â”‚  â”œâ”€ ledger_allowlist: True
â”‚  â”œâ”€ dns_rebinding_guard: True
â”‚  â””â”€ timeout_guard: True
â”œâ”€ Capabilities
â”‚  â”œâ”€ 16 governed_web_search (authority=read_only, risk=low, network=True, exfil=True, confirm=False, surface=Governor â†’ NetworkMediator)
â”‚  â”œâ”€ 17 open_website (authority=system_action, risk=low, network=False, exfil=False, confirm=False, surface=Governor â†’ Executor)
â”‚  â”œâ”€ 18 speak_text (authority=speech_output, risk=low, network=False, exfil=False, confirm=False, surface=Governor â†’ Speech)
â”‚  â”œâ”€ 19 volume_up_down (authority=system_action, risk=low, network=False, exfil=False, confirm=False, surface=Governor â†’ Executor)
â”‚  â”œâ”€ 20 media_play_pause (authority=system_action, risk=low, network=False, exfil=False, confirm=False, surface=Governor â†’ Executor)
â”‚  â”œâ”€ 21 brightness_control (authority=system_action, risk=low, network=False, exfil=False, confirm=False, surface=Governor â†’ Executor)
â”‚  â”œâ”€ 22 open_file_folder (authority=confirm_required, risk=confirm, network=False, exfil=False, confirm=True, surface=Governor â†’ Executor)
â”‚  â”œâ”€ 32 os_diagnostics (authority=system_action, risk=low, network=False, exfil=False, confirm=False, surface=Governor â†’ Executor)
â”‚  â”œâ”€ 48 multi_source_reporting (authority=read_only, risk=low, network=True, exfil=True, confirm=False, surface=Governor â†’ NetworkMediator)
â”œâ”€ Skill â†’ capability routes
â”‚  â”œâ”€ brightness -> 21
â”‚  â”œâ”€ diagnostics -> 32
â”‚  â”œâ”€ media -> 20
â”‚  â”œâ”€ open_website -> 17
â”‚  â”œâ”€ search -> 16
â”‚  â”œâ”€ speak -> 18
â”‚  â”œâ”€ volume -> 19
â””â”€ Conversation/model surfaces
   â”œâ”€ src/conversation/deepseek_bridge.py -> llm_gateway.generate_chat
   â”œâ”€ src/skills/general_chat.py -> llm_gateway.generate_chat
```

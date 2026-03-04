# BYPASS_SURFACES

Read-only truth report of detectable bypass indicators from allowlisted runtime sources.

## Direct ollama.chat outside llm_manager

- nova_backend/src/conversation/deepseek_bridge.py
- nova_backend/src/skills/general_chat.py

## requests/network usage outside NetworkMediator

- None detected.

## Executor callable paths outside governor

- Architectural constraint: executors exist as importable callables, but governed runtime routes execution through Governor branches.
- nova_backend/src/executors/brightness_executor.py
- nova_backend/src/executors/media_executor.py
- nova_backend/src/executors/multi_source_reporting_executor.py
- nova_backend/src/executors/open_folder_executor.py
- nova_backend/src/executors/os_diagnostics_executor.py
- nova_backend/src/executors/tts_executor.py
- nova_backend/src/executors/volume_executor.py
- nova_backend/src/executors/web_search_executor.py
- nova_backend/src/executors/webpage_launch_executor.py

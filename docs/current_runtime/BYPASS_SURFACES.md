# BYPASS_SURFACES

Read-only truth report of detectable bypass indicators from allowlisted runtime sources.

## Direct ollama.chat outside llm gateway

- None detected.

## requests/network usage outside NetworkMediator

- None detected.

## Executor callable paths outside governor

- Architectural constraint: executors exist as importable callables, but governed runtime routes execution through Governor branches.
- nova_backend/src/executors/analysis_document_executor.py
- nova_backend/src/executors/brightness_executor.py
- nova_backend/src/executors/explain_anything_executor.py
- nova_backend/src/executors/external_reasoning_executor.py
- nova_backend/src/executors/info_snapshot_executor.py
- nova_backend/src/executors/media_executor.py
- nova_backend/src/executors/memory_governance_executor.py
- nova_backend/src/executors/multi_source_reporting_executor.py
- nova_backend/src/executors/news_intelligence_executor.py
- nova_backend/src/executors/news_synthesis_async.py
- nova_backend/src/executors/news_synthesis_cache.py
- nova_backend/src/executors/open_folder_executor.py
- nova_backend/src/executors/openclaw_execute_executor.py
- nova_backend/src/executors/os_diagnostics_executor.py
- nova_backend/src/executors/response_verification_executor.py
- nova_backend/src/executors/screen_analysis_executor.py
- nova_backend/src/executors/screen_capture_executor.py
- nova_backend/src/executors/send_email_draft_executor.py
- nova_backend/src/executors/shopify_intelligence_report_executor.py
- nova_backend/src/executors/story_tracker_executor.py
- nova_backend/src/executors/tts_executor.py
- nova_backend/src/executors/volume_executor.py
- nova_backend/src/executors/web_search_executor.py
- nova_backend/src/executors/webpage_launch_executor.py

## requests-based direct-network classification

This classification covers paths detectable by the existing requests-library scanner over the auditor's existing allowlist. It does not prove the absence of every possible network mechanism.

- Known requests-based exceptions: None detected.

- Unclassified requests-based direct-network paths: None detected.

## Supported Data-Out mechanism dispositions

This exact-call-site registry is static regression enforcement, not proof of runtime denial, filesystem locality, or complete Data-Out closure.

- Detected exact sites: 104
- Governed sites: 12
- Unresolved sites: 92
- Frozen-scope exclusions: 0
- Unregistered sites: 0
- Stale dispositions: 0

Unresolved closure families:
- `F02_external_read_and_setup`: Caller-level typed-adapter and zero-attempt proof remains incomplete for every supported external-read and setup route.
- `F03_openclaw_provider_routes`: Every reachable OpenClaw tool and alternate provider caller still requires exact disclosure and zero-attempt proof.
- `F04_installer_acquisition`: Installer acquisition admission is implemented; trusted evidence locality and Windows installer acceptance proof remain required for family closure.
- `F05_non_ollama_delegation`: Non-Ollama children and application handoffs require exact command/environment admission and truthful delegated outcomes.
- `F06_trusted_runtime_roots`: General trusted runtime and evidence-root enrollment remains blocked on the Slice 5A Windows proof.
- `F07_installation_state_roots`: Installation-relative goal, story, repository, and setup state require locality proof before target access.
- `F08_user_and_temp_paths`: Temporary, calendar, audio, selected-file, and working-context paths require locality proof before first access.
- `F09_executable_discovery_roots`: PATH and browser-candidate roots require locality classification before executable discovery.
- `F10_setup_shell_folders`: Start Menu and desktop destinations require locality classification before probe or shortcut creation.
- `F11_storage_diagnostics_roots`: Storage-health roots require locality classification before disk probing.

# BYPASS_SURFACES

Read-only truth report of detectable bypass indicators from allowlisted runtime sources.

## Direct ollama.chat outside llm gateway

- None detected.

## requests/network usage outside NetworkMediator

- nova_backend/src/api/connections_api.py

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

- `nova_backend/src/api/connections_api.py`
  - classification: `local_administrative_health_probe`
  - disposition: `pending_explicit_runtime_governance_disposition`
  - reason: Provider-health requests are local administrative connection checks, not registered governed capability execution. The requests-based direct network path remains visible and does not become implicitly approved.

- Unclassified requests-based direct-network paths: None detected.

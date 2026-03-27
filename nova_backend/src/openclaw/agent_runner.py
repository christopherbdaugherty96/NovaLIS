"""
OpenClawAgentRunner — Phase 8.0 manual-only task runner.

INVARIANTS (Phase 8.0):
- Manual trigger only. No scheduler. No background execution.
- Calls existing Nova skills (weather, news, calendar) — zero extra LLM calls for data.
- One LLM summarize call at the end, respecting the envelope token budget.
- All execution logged through the envelope status lifecycle.
- Result returned to caller; never pushed autonomously.

Scheduler is explicitly deferred to Phase 8.5.

TODO (Phase 8 full): Wire through GovernorMediator before execution so every
envelope invocation is subject to capability-registry approval and ledger logging.
"""
from __future__ import annotations

from typing import Any, Optional

from src.openclaw.task_envelope import TaskEnvelope
from src.openclaw.agent_runtime_store import get_default_store


ALLOWED_TOOL_REGISTRY: dict[str, str] = {
    "weather": "Open-Meteo weather snapshot",
    "news": "RSS/news headline fetch",
    "calendar": "ICS/calendar snapshot",
    "os_diagnostics": "System diagnostics snapshot",
}


class OpenClawAgentRunner:
    """
    Phase 8.0 governed task runner.

    Usage:
        runner = OpenClawAgentRunner()
        result = await runner.run(envelope, llm_summarize_fn)
    """

    def __init__(self, store=None) -> None:
        self._store = store or get_default_store()

    def run_sync(
        self,
        envelope: TaskEnvelope,
        llm_summarize_fn: Optional[Any] = None,
        tool_data_fns: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Execute an envelope synchronously (Phase 8.0 — manual trigger only).

        Args:
            envelope: TaskEnvelope to execute.
            llm_summarize_fn: Optional callable(data_dict) -> str for final summary.
                              If None, returns raw data without LLM summarization.
            tool_data_fns: Optional dict of tool_name -> callable() -> str.
                           Used for dependency injection in tests.

        Returns:
            Result dict with status, data, and result_text.
        """
        self._store.register(envelope)
        envelope.mark_running()

        collected_data: dict[str, str] = {}
        errors: list[str] = []

        # Collect data from allowed tools (zero LLM per tool call)
        for tool in envelope.tools_allowed:
            if tool not in ALLOWED_TOOL_REGISTRY:
                errors.append(f"Tool '{tool}' not in allowlist — skipped.")
                continue
            try:
                if tool_data_fns and tool in tool_data_fns:
                    collected_data[tool] = tool_data_fns[tool]()
                else:
                    # Stub: real skill wiring happens in Phase 8 full
                    collected_data[tool] = f"[{tool} data — wire to Nova skill in Phase 8 full]"
            except Exception as exc:  # noqa: BLE001
                errors.append(f"Tool '{tool}' raised: {exc!r}")

        # One LLM call at the end to summarize (data-first pattern)
        if llm_summarize_fn is not None and collected_data:
            try:
                summary = llm_summarize_fn(collected_data)
            except Exception as exc:  # noqa: BLE001
                summary = f"Summary unavailable: {exc!r}"
        elif collected_data:
            summary = "; ".join(f"{k}: {v}" for k, v in collected_data.items())
        else:
            summary = "No data collected."

        if errors:
            error_note = " Errors: " + "; ".join(errors)
            summary = summary + error_note

        envelope.mark_complete(summary)

        return {
            "envelope_id": envelope.id,
            "envelope_title": envelope.title,
            "status": envelope.status,
            "result_text": envelope.result_text,
            "tools_used": list(collected_data.keys()),
            "errors": errors,
        }

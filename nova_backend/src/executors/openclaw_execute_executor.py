# src/executors/openclaw_execute_executor.py
"""
OpenClaw Execute Executor — cap 63 (openclaw_execute)

Runs a home-agent template through the governed execution path.
This is the canonical Phase-8 execution surface for the OpenClaw home agent.

Params:
    template_id (str): The template to run (e.g. "morning_brief", "evening_digest", "market_watch")
    triggered_by (str, optional): Source label for audit. Defaults to "governed_invocation".

Authority class: read_only_network
Risk: low — reads from weather/news/calendar APIs and produces a local summary.
"""
from __future__ import annotations

import asyncio
from typing import Any

from src.actions.action_result import ActionResult


class OpenClawExecuteExecutor:
    """
    Governed execution gateway for OpenClaw home-agent template runs.

    Bridges the synchronous governor dispatch layer to the async agent runner.
    Runs in the governor's thread-pool executor via run_with_timeout, so each
    invocation gets its own event loop via asyncio.run().
    """

    def execute(self, req) -> ActionResult:
        params = dict(req.params or {})
        template_id = str(params.get("template_id") or "").strip()
        if not template_id:
            return ActionResult.failure(
                "No template_id provided for openclaw_execute. "
                "Specify a template such as 'morning_brief', 'evening_digest', or 'market_watch'.",
                request_id=req.request_id,
            )

        triggered_by = str(params.get("triggered_by") or "governed_invocation").strip()

        try:
            result_data = asyncio.run(self._run_template(template_id, triggered_by=triggered_by))
        except RuntimeError as exc:
            # Template is not runnable yet (e.g. inbox_check)
            return ActionResult.failure(
                str(exc),
                request_id=req.request_id,
            )
        except KeyError:
            return ActionResult.failure(
                f"Unknown template '{template_id}'. "
                "Available templates: morning_brief, evening_digest, market_watch.",
                request_id=req.request_id,
            )
        except Exception as exc:
            return ActionResult.failure(
                f"Home-agent template '{template_id}' could not complete: {exc}",
                request_id=req.request_id,
            )

        summary = str(result_data.get("summary") or result_data.get("content") or "").strip()
        if not summary:
            summary = f"Home-agent template '{template_id}' completed with no summary output."

        return ActionResult.ok(
            summary,
            data={
                "template_id": template_id,
                "triggered_by": triggered_by,
                "template_label": result_data.get("template_label", template_id),
                "token_count": result_data.get("token_count", 0),
                "route": result_data.get("route", ""),
                "started_at": result_data.get("started_at", ""),
                "completed_at": result_data.get("completed_at", ""),
            },
            request_id=req.request_id,
            authority_class="read_only_network",
            external_effect=True,
            reversible=True,
        )

    @staticmethod
    async def _run_template(template_id: str, *, triggered_by: str) -> dict[str, Any]:
        from src.openclaw.agent_runner import openclaw_agent_runner

        return await openclaw_agent_runner.run_template(template_id, triggered_by=triggered_by)

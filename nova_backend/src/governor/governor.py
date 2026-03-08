# src/governor/governor.py

"""
Governor – constitutional authority spine.
Phase‑4 integration: owns all execution‑related components, but they are lazily loaded
to preserve Phase‑3.5 safety until the unlock.
"""

from __future__ import annotations

import time
from typing import Dict, Any

from src.actions.action_result import ActionResult
from src.governor.execute_boundary.execute_boundary import (
    ExecuteBoundary,
    MAX_EXECUTION_TIME,
    ExecutionCPUExceededError,
)
from src.governor.single_action_queue import SingleActionQueue
import src.ledger.writer as ledger_mod
from src.governor.exceptions import (
    CapabilityRegistryError,
    NetworkMediatorError,
    LedgerWriteFailed,
)
from src.actions.action_request import ActionRequest


class Governor:
    """
    Single authority choke point.
    - Owns execute boundary and queue unconditionally.
    - Lazily loads registry, network mediator, ledger on first use.
    """

    def __init__(self):
        self._execute_boundary = ExecuteBoundary()
        self._queue = SingleActionQueue()

        # Lazy‑loaded Phase‑4 components (initially None)
        self._registry = None
        self._network = None
        self._ledger = None

    @property
    def execute_boundary(self) -> ExecuteBoundary:
        return self._execute_boundary

    @property
    def registry(self):
        """Lazy load CapabilityRegistry."""
        if self._registry is None:
            from src.governor.capability_registry import CapabilityRegistry
            self._registry = CapabilityRegistry()
        return self._registry

    @property
    def network(self):
        """Lazy load NetworkMediator."""
        if self._network is None:
            from src.governor.network_mediator import NetworkMediator
            self._network = NetworkMediator()
        return self._network

    @property
    def ledger(self):
        """Lazy load LedgerWriter."""
        if self._ledger is None:
            self._ledger = ledger_mod.LedgerWriter()
        return self._ledger

    def handle_governed_invocation(
        self,
        capability_id: int,
        params: Dict[str, Any],
    ) -> ActionResult:
        try:
            cap = self.registry.get(capability_id)
        except CapabilityRegistryError as e:
            return ActionResult.failure(f"I can’t do that. {e}")

        if not self.registry.is_enabled(capability_id):
            return ActionResult.failure("I can’t do that yet.")

        if getattr(cap, "risk_level", "low") == "confirm" and not bool((params or {}).get("confirmed")):
            return ActionResult.refusal("This action requires confirmation before I can proceed.")

        if not self._execute_boundary.allow_execution():
            return ActionResult.failure("That requires a specific action, which I can’t perform right now.")

        if self._queue.has_pending():
            return ActionResult.failure("I can’t do that right now.")

        try:
            self.ledger.log_event(
                "ACTION_ATTEMPTED",
                {"capability_id": capability_id, "capability_name": cap.name},
            )
        except Exception:
            return ActionResult.failure("I can’t do that right now.")

        req = ActionRequest(capability_id=capability_id, params=params)

        try:
            return self._execute(req)
        except (NetworkMediatorError, LedgerWriteFailed):
            return ActionResult.failure("I can’t do that right now.", request_id=req.request_id)
        except Exception:
            return ActionResult.failure("I can’t do that right now.", request_id=req.request_id)

    def _execute(self, req: ActionRequest) -> ActionResult:
        self._queue.set_pending(req.request_id)
        self._execute_boundary.enter_execution()
        start_time = time.monotonic()

        try:
            if req.capability_id == 16:
                query = req.params.get("query")
                if query:
                    try:
                        self.ledger.log_event("SEARCH_QUERY", {"query": query})
                    except LedgerWriteFailed:
                        pass

            result = self._execute_boundary.run_with_timeout(
                lambda: self._dispatch_capability(req),
                timeout_seconds=MAX_EXECUTION_TIME,
            )
            self._execute_boundary.enforce_memory_limits()
            self._execute_boundary.enforce_cpu_limits()

            elapsed = time.monotonic() - start_time
            if elapsed > MAX_EXECUTION_TIME:
                try:
                    self.ledger.log_event(
                        "EXECUTION_TIMEOUT",
                        {"capability_id": req.capability_id, "request_id": req.request_id, "elapsed_seconds": round(elapsed, 3)},
                    )
                except LedgerWriteFailed:
                    pass
                return ActionResult.refusal("Execution exceeded allowed time.", request_id=req.request_id)

            try:
                self.ledger.log_event(
                    "ACTION_COMPLETED",
                    {
                        "capability_id": req.capability_id,
                        "request_id": req.request_id,
                        "success": result.success,
                    },
                )
            except LedgerWriteFailed:
                pass

            return result

        except TimeoutError:
            return ActionResult.refusal(
                "The request took too long and was cancelled.",
                request_id=req.request_id,
            )
        except MemoryError:
            try:
                self.ledger.log_event(
                    "EXECUTION_MEMORY_EXCEEDED",
                    {"capability_id": req.capability_id, "request_id": req.request_id},
                )
            except LedgerWriteFailed:
                pass
            return ActionResult.refusal(
                "Execution exceeded allowed memory.",
                request_id=req.request_id,
            )
        except ExecutionCPUExceededError:
            try:
                self.ledger.log_event(
                    "EXECUTION_CPU_EXCEEDED",
                    {"capability_id": req.capability_id, "request_id": req.request_id},
                )
            except LedgerWriteFailed:
                pass
            return ActionResult.refusal(
                "Execution exceeded allowed CPU budget.",
                request_id=req.request_id,
            )
        except Exception:
            return ActionResult.refusal(
                "I can’t do that right now.",
                request_id=req.request_id,
            )
        finally:
            self._execute_boundary.exit_execution()
            self._queue.clear()

    def _dispatch_capability(self, req: ActionRequest) -> ActionResult:
        if req.capability_id == 16:
            from src.executors.web_search_executor import WebSearchExecutor
            executor = WebSearchExecutor(self.network, self._execute_boundary)
            return executor.execute(req)

        elif req.capability_id == 17:
            from src.executors.webpage_launch_executor import WebpageLaunchExecutor
            executor = WebpageLaunchExecutor(self.ledger)
            return executor.execute(req)

        elif req.capability_id == 18:
            from src.executors.tts_executor import execute_tts
            return execute_tts(req, ActionResult)

        elif req.capability_id == 19:
            from src.executors.volume_executor import VolumeExecutor
            return VolumeExecutor().execute(req)

        elif req.capability_id == 20:
            from src.executors.media_executor import MediaExecutor
            return MediaExecutor().execute(req)

        elif req.capability_id == 21:
            from src.executors.brightness_executor import BrightnessExecutor
            return BrightnessExecutor().execute(req)

        elif req.capability_id == 22:
            from src.executors.open_folder_executor import OpenFolderExecutor
            return OpenFolderExecutor().execute(req)

        elif req.capability_id == 32:
            from src.executors.os_diagnostics_executor import OSDiagnosticsExecutor
            return OSDiagnosticsExecutor().execute(req)

        elif req.capability_id == 48:
            from src.executors.multi_source_reporting_executor import MultiSourceReportingExecutor
            return MultiSourceReportingExecutor(self.network).execute(req)

        elif req.capability_id == 49:
            from src.executors.news_intelligence_executor import NewsIntelligenceExecutor
            return NewsIntelligenceExecutor(self.network).execute_summary(req)

        elif req.capability_id == 50:
            from src.executors.news_intelligence_executor import NewsIntelligenceExecutor
            return NewsIntelligenceExecutor(self.network).execute_brief(req)

        elif req.capability_id == 51:
            from src.executors.news_intelligence_executor import NewsIntelligenceExecutor
            return NewsIntelligenceExecutor(self.network).execute_topic_map(req)

        elif req.capability_id == 52:
            from src.executors.story_tracker_executor import StoryTrackerExecutor
            return StoryTrackerExecutor().execute_update(req)

        elif req.capability_id == 53:
            from src.executors.story_tracker_executor import StoryTrackerExecutor
            return StoryTrackerExecutor().execute_view(req)

        elif req.capability_id == 54:
            from src.executors.analysis_document_executor import AnalysisDocumentExecutor
            return AnalysisDocumentExecutor().execute(req)

        elif req.capability_id == 31:
            from src.executors.response_verification_executor import ResponseVerificationExecutor
            return ResponseVerificationExecutor().execute(req)

        return ActionResult.refusal(
            "Execution path not implemented yet.",
            request_id=req.request_id,
        )

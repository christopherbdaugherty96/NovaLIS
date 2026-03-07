# src/governor/governor.py

"""
Governor – constitutional authority spine.
Phase‑4 integration: owns all execution‑related components, but they are lazily loaded
to preserve Phase‑3.5 safety until the unlock.
"""

from __future__ import annotations

import sys
import time
from typing import Optional, Dict, Any

# resource is Unix-only; gracefully degrade on Windows
try:
    import resource
except ImportError:
    resource = None

from src.actions.action_result import ActionResult
from src.governor.execute_boundary.execute_boundary import ExecuteBoundary, MAX_EXECUTION_TIME, MAX_MEMORY_MB
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

    @staticmethod
    def _rss_mb() -> Optional[float]:
        if resource is None:
            return None
        try:
            usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            if sys.platform == "darwin":
                return usage / (1024 * 1024)
            return usage / 1024
        except Exception:
            return None

    def _execute(self, req: ActionRequest) -> ActionResult:
        self._queue.set_pending(req.request_id)
        self._execute_boundary.enter_execution()
        start_time = time.monotonic()
        before_rss = self._rss_mb()

        try:
            if req.capability_id == 16:
                query = req.params.get("query")
                if query:
                    try:
                        self.ledger.log_event("SEARCH_QUERY", {"query": query})
                    except LedgerWriteFailed:
                        pass

            if req.capability_id == 16:
                from src.executors.web_search_executor import WebSearchExecutor
                executor = WebSearchExecutor(self.network, self._execute_boundary)
                result = executor.execute(req)

            elif req.capability_id == 17:
                from src.executors.webpage_launch_executor import WebpageLaunchExecutor
                executor = WebpageLaunchExecutor(self.ledger)
                result = executor.execute(req)

            elif req.capability_id == 18:
                from src.executors.tts_executor import execute_tts
                result = execute_tts(req, ActionResult)

            elif req.capability_id == 19:
                from src.executors.volume_executor import VolumeExecutor
                result = VolumeExecutor().execute(req)

            elif req.capability_id == 20:
                from src.executors.media_executor import MediaExecutor
                result = MediaExecutor().execute(req)

            elif req.capability_id == 21:
                from src.executors.brightness_executor import BrightnessExecutor
                result = BrightnessExecutor().execute(req)

            elif req.capability_id == 22:
                from src.executors.open_folder_executor import OpenFolderExecutor
                result = OpenFolderExecutor().execute(req)

            elif req.capability_id == 32:
                from src.executors.os_diagnostics_executor import OSDiagnosticsExecutor
                result = OSDiagnosticsExecutor().execute(req)

            elif req.capability_id == 48:
                from src.executors.multi_source_reporting_executor import MultiSourceReportingExecutor
                result = MultiSourceReportingExecutor(self.network).execute(req)

            elif req.capability_id == 49:
                from src.executors.news_intelligence_executor import NewsIntelligenceExecutor
                result = NewsIntelligenceExecutor().execute_summary(req)

            elif req.capability_id == 50:
                from src.executors.news_intelligence_executor import NewsIntelligenceExecutor
                result = NewsIntelligenceExecutor().execute_brief(req)

            elif req.capability_id == 51:
                from src.executors.news_intelligence_executor import NewsIntelligenceExecutor
                result = NewsIntelligenceExecutor().execute_topic_map(req)

            elif req.capability_id == 52:
                from src.executors.story_tracker_executor import StoryTrackerExecutor
                result = StoryTrackerExecutor().execute_update(req)

            elif req.capability_id == 53:
                from src.executors.story_tracker_executor import StoryTrackerExecutor
                result = StoryTrackerExecutor().execute_view(req)

            elif req.capability_id == 54:
                from src.executors.analysis_document_executor import AnalysisDocumentExecutor
                result = AnalysisDocumentExecutor().execute(req)

            elif req.capability_id == 31:
                from src.executors.response_verification_executor import ResponseVerificationExecutor
                result = ResponseVerificationExecutor().execute(req)

            else:
                result = ActionResult.refusal(
                    "Execution path not implemented yet.",
                    request_id=req.request_id,
                )

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

            after_rss = self._rss_mb()
            if before_rss is not None and after_rss is not None and (after_rss - before_rss) > MAX_MEMORY_MB:
                try:
                    self.ledger.log_event(
                        "EXECUTION_MEMORY_EXCEEDED",
                        {
                            "capability_id": req.capability_id,
                            "request_id": req.request_id,
                            "rss_delta_mb": round(after_rss - before_rss, 3),
                        },
                    )
                except LedgerWriteFailed:
                    pass
                return ActionResult.refusal("Execution exceeded allowed memory.", request_id=req.request_id)

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
        except Exception:
            return ActionResult.refusal(
                "I can’t do that right now.",
                request_id=req.request_id,
            )
        finally:
            self._execute_boundary.exit_execution()
            self._queue.clear()

# src/governor/governor.py

"""
Governor - constitutional authority spine.
Phase-4 integration: owns all execution-related components, but they are lazily loaded
to preserve Phase-3.5 safety until the unlock.
"""

from __future__ import annotations

import time
from typing import Any, Dict

import src.ledger.writer as ledger_mod
from src.actions.action_request import ActionRequest
from src.actions.action_result import ActionResult
from src.governor.exceptions import (
    CapabilityRegistryError,
    LedgerWriteFailed,
    NetworkMediatorError,
)
from src.governor.execute_boundary.execute_boundary import (
    MAX_EXECUTION_TIME,
    ExecuteBoundary,
    ExecutionCPUExceededError,
)
from src.governor.single_action_queue import SingleActionQueue


CAPABILITY_TIMEOUT_OVERRIDES = {
    31: 90.0,  # Response verification may need local-model cold-start time.
    54: 150.0,  # Analysis documents need more time for local-model long-form generation.
}


class Governor:
    """
    Single authority choke point.
    - Owns execute boundary and queue unconditionally.
    - Lazily loads registry, network mediator, ledger on first use.
    """

    def __init__(self):
        self._execute_boundary = ExecuteBoundary()
        self._queue = SingleActionQueue()

        # Lazy-loaded runtime components.
        self._registry = None
        self._network = None
        self._ledger = None
        self._policy_validator = None
        self._capability_topology = None
        self._policy_executor_gate = None

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

    @property
    def policy_validator(self):
        """Lazy load the Phase-6 atomic policy validator."""
        if self._policy_validator is None:
            from src.policies.policy_validator import PolicyValidator

            self._policy_validator = PolicyValidator(self.registry)
        return self._policy_validator

    @property
    def capability_topology(self):
        """Lazy load capability topology metadata for delegated-policy decisions."""
        if self._capability_topology is None:
            from src.governor.capability_topology import CapabilityTopology

            self._capability_topology = CapabilityTopology(self.registry)
        return self._capability_topology

    @property
    def policy_executor_gate(self):
        """Lazy load the Phase-6 policy executor gate."""
        if self._policy_executor_gate is None:
            from src.governor.policy_executor_gate import PolicyExecutorGate

            self._policy_executor_gate = PolicyExecutorGate(
                self.registry,
                self.policy_validator,
                self.capability_topology,
            )
        return self._policy_executor_gate

    def validate_atomic_policy(self, policy: Dict[str, Any]) -> Any:
        """Validate a disabled-by-default atomic delegated policy draft."""
        return self.policy_validator.validate(policy)

    def simulate_atomic_policy(self, policy_item: Dict[str, Any]) -> Any:
        """Run a read-only delegated-policy simulation through the executor gate."""
        decision = self.policy_executor_gate.simulate(policy_item)
        try:
            self.ledger.log_event(
                "POLICY_SIMULATED",
                {
                    "policy_id": str(policy_item.get("policy_id") or ""),
                    "capability_id": int(dict(policy_item.get("action") or {}).get("capability_id") or 0),
                    "allowed": bool(decision.allowed),
                    "readiness_label": str(decision.readiness_label),
                },
            )
        except Exception:
            pass
        return decision

    def run_atomic_policy_once(self, policy_item: Dict[str, Any]) -> tuple[Any, ActionResult]:
        """Explicitly execute one manual delegated-policy run through the executor gate."""
        decision = self.policy_executor_gate.authorize_manual_run(policy_item)
        policy_id = str(policy_item.get("policy_id") or "").strip()
        capability_id = int(dict(policy_item.get("action") or {}).get("capability_id") or 0)
        action_params = dict(dict(policy_item.get("action") or {}).get("input") or {})

        try:
            self.ledger.log_event(
                "POLICY_EXECUTION_ATTEMPTED",
                {
                    "policy_id": policy_id,
                    "capability_id": capability_id,
                    "allowed": bool(decision.allowed),
                },
            )
        except Exception:
            pass

        if not decision.allowed:
            try:
                self.ledger.log_event(
                    "POLICY_EXECUTION_BLOCKED",
                    {
                        "policy_id": policy_id,
                        "capability_id": capability_id,
                        "reason": str(decision.blocked_reason or "blocked"),
                    },
                )
            except Exception:
                pass
            blocked = ActionResult.refusal(
                str(decision.governor_verdict),
                data={"simulation": decision.as_dict()},
                authority_class="read_only",
                external_effect=False,
                reversible=True,
            )
            return decision, blocked

        result = self.handle_governed_invocation(capability_id, action_params)
        try:
            self.ledger.log_event(
                "POLICY_EXECUTION_COMPLETED",
                {
                    "policy_id": policy_id,
                    "capability_id": capability_id,
                    "request_id": str(result.request_id or ""),
                    "success": bool(result.success),
                },
            )
        except Exception:
            pass
        if result.data is None:
            result.data = {}
        result.data["simulation"] = decision.as_dict()
        result.data["policy_id"] = policy_id
        return decision, result

    def handle_governed_invocation(
        self,
        capability_id: int,
        params: Dict[str, Any],
    ) -> ActionResult:
        try:
            cap = self.registry.get(capability_id)
        except CapabilityRegistryError as exc:
            return ActionResult.failure(f"I can't do that. {exc}")

        if not self.registry.is_enabled(capability_id):
            return ActionResult.failure("I can't do that yet.")

        if getattr(cap, "risk_level", "low") == "confirm" and not bool((params or {}).get("confirmed")):
            return ActionResult.refusal("This action requires confirmation before I can proceed.")

        if not self._execute_boundary.allow_execution():
            return ActionResult.failure("That requires a specific action, which I can't perform right now.")

        if self._queue.has_pending():
            return ActionResult.failure("I couldn't do that right now.")

        try:
            self.ledger.log_event(
                "ACTION_ATTEMPTED",
                {"capability_id": capability_id, "capability_name": cap.name},
            )
        except Exception:
            return ActionResult.failure("I couldn't do that right now.")

        req = ActionRequest(capability_id=capability_id, params=params)

        try:
            return self._execute(req)
        except (NetworkMediatorError, LedgerWriteFailed):
            return ActionResult.failure("I couldn't do that right now.", request_id=req.request_id)
        except Exception:
            return ActionResult.failure("I couldn't do that right now.", request_id=req.request_id)

    def _execute(self, req: ActionRequest) -> ActionResult:
        self._queue.set_pending(req.request_id)
        self._execute_boundary.enter_execution()
        start_time = time.monotonic()
        timeout_seconds = self._execution_timeout_seconds(req.capability_id)

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
                timeout_seconds=timeout_seconds,
            )
            self._execute_boundary.enforce_memory_limits()
            self._execute_boundary.enforce_cpu_limits()

            elapsed = time.monotonic() - start_time
            if elapsed > timeout_seconds:
                try:
                    self.ledger.log_event(
                        "EXECUTION_TIMEOUT",
                        {
                            "capability_id": req.capability_id,
                            "request_id": req.request_id,
                            "elapsed_seconds": round(elapsed, 3),
                        },
                    )
                except LedgerWriteFailed:
                    pass
                return ActionResult.refusal("Execution exceeded allowed time.", request_id=req.request_id)

            try:
                completion_metadata = {
                    "capability_id": req.capability_id,
                    "request_id": req.request_id,
                    "success": result.success,
                    "external_effect": bool(result.external_effect),
                    "reversible": bool(result.reversible),
                }
                if not result.success:
                    failure_reason = str(result.message or "").strip()
                    if failure_reason:
                        completion_metadata["failure_reason"] = failure_reason[:240]
                self.ledger.log_event(
                    "ACTION_COMPLETED",
                    completion_metadata,
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
                "I couldn't do that right now.",
                request_id=req.request_id,
            )
        finally:
            self._execute_boundary.exit_execution()
            self._queue.clear()

    @staticmethod
    def _execution_timeout_seconds(capability_id: int) -> float:
        return float(CAPABILITY_TIMEOUT_OVERRIDES.get(int(capability_id), MAX_EXECUTION_TIME))

    def allow_notification_delivery(self, metadata: Dict[str, Any]) -> tuple[bool, str]:
        schedule_id = str((metadata or {}).get("schedule_id") or "").strip()
        kind = str((metadata or {}).get("kind") or "").strip()
        title = str((metadata or {}).get("title") or "").strip()

        if not schedule_id or not kind or not title:
            return False, "invalid_notification_metadata"
        if self._queue.has_pending():
            return False, "action_pending"
        if not self._execute_boundary.allow_execution():
            return False, "execution_boundary_closed"
        return True, "allowed"

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

        elif req.capability_id == 55:
            from src.executors.info_snapshot_executor import WeatherSnapshotExecutor

            return WeatherSnapshotExecutor(self.network).execute(req)

        elif req.capability_id == 56:
            from src.executors.info_snapshot_executor import NewsSnapshotExecutor

            return NewsSnapshotExecutor(self.network).execute(req)

        elif req.capability_id == 57:
            from src.executors.info_snapshot_executor import CalendarSnapshotExecutor

            return CalendarSnapshotExecutor().execute(req)

        elif req.capability_id == 58:
            from src.executors.screen_capture_executor import ScreenCaptureExecutor

            return ScreenCaptureExecutor(ledger=self.ledger).execute(req)

        elif req.capability_id == 59:
            from src.executors.screen_analysis_executor import ScreenAnalysisExecutor

            return ScreenAnalysisExecutor(ledger=self.ledger).execute(req)

        elif req.capability_id == 60:
            from src.executors.explain_anything_executor import ExplainAnythingExecutor

            return ExplainAnythingExecutor(ledger=self.ledger).execute(req)

        elif req.capability_id == 61:
            from src.executors.memory_governance_executor import MemoryGovernanceExecutor

            return MemoryGovernanceExecutor(ledger=self.ledger).execute(req)

        elif req.capability_id == 31:
            from src.executors.response_verification_executor import ResponseVerificationExecutor

            return ResponseVerificationExecutor().execute(req)

        return ActionResult.refusal(
            "Execution path not implemented yet.",
            request_id=req.request_id,
        )

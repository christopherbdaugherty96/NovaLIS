# src/governor/governor.py

"""
Governor - constitutional authority spine.
Phase-4 integration: owns all execution-related components, but they are lazily loaded
to preserve Phase-3.5 safety until the unlock.
"""

from __future__ import annotations

import hashlib
import time
from typing import Any, Dict

import src.ledger.writer as ledger_mod
from src.actions.action_request import ActionRequest
from src.actions.action_result import ActionResult
from src.durability.maintenance import authoritative_mutation
from src.governor.approval_grants import (
    DEFAULT_APPROVAL_TTL_SECONDS,
    ApprovalAuthorityMetadataError,
    ApprovalCapabilityDisabledError,
    ApprovalGrant,
    ApprovalGrantError,
    ApprovalGrantStore,
    canonical_action_snapshot,
)
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
from src.trust.session_activity import normalize_activity_origin

CAPABILITY_TIMEOUT_OVERRIDES = {
    16: 20.0,  # Governed web search may need search, source reads, and bounded synthesis.
    49: 30.0,  # Headline summaries may need source reads plus local-model synthesis.
    50: 35.0,  # Daily brief generation may need clustered source reads plus synthesis.
    31: 90.0,  # Response verification may need local-model cold-start time.
    62: 90.0,  # Governed external reasoning review may need local-model cold-start time.
    54: 150.0,  # Analysis documents need more time for local-model long-form generation.
    63: 45.0,  # Home-agent templates may need network round-trips across multiple sources.
    64: 60.0,  # Email draft composes body via local LLM — allow cold-start time.
}

# Capabilities subject to daily usage/budget enforcement because they consume
# metered external or network resources.  This is NOT the same as cost_posture —
# a capability can be budget-gated (metered) while its cost_posture is free_tier.
_BUDGET_GATED_CAP_IDS: frozenset[int] = frozenset({16, 48, 49, 50, 55, 56, 62, 63, 65})


class Governor:
    """
    Single authority choke point.
    - Owns execute boundary and queue unconditionally.
    - Lazily loads registry, network mediator, ledger on first use.
    """

    def __init__(self):
        self._execute_boundary = ExecuteBoundary()
        self._queue = SingleActionQueue()
        self._approval_grants = ApprovalGrantStore()

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

    def issue_approval_grant(
        self,
        *,
        session_id: str,
        capability_id: int,
        params: Dict[str, Any],
        ttl_seconds: float = DEFAULT_APPROVAL_TTL_SECONDS,
    ) -> ApprovalGrant:
        cap = self.registry.get(capability_id)
        if not self.registry.is_enabled(capability_id):
            raise ApprovalCapabilityDisabledError("Cannot approve a disabled capability.")
        action_params = canonical_action_snapshot(params)
        grant = self._approval_grants.issue(
            session_id=session_id,
            capability_id=capability_id,
            params=action_params,
            ttl_seconds=ttl_seconds,
        )
        try:
            self.ledger.log_event(
                "APPROVAL_GRANTED",
                {
                    "approval_fingerprint": hashlib.sha256(
                        grant.approval_id.encode("utf-8")
                    ).hexdigest()[:16],
                    "session_id": grant.session_id,
                    "capability_id": int(capability_id),
                    "capability_name": str(cap.name),
                    "action_hash": grant.action_hash,
                    "issued_at": grant.issued_at,
                    "expires_at": grant.expires_at,
                },
            )
        except Exception as exc:
            self._approval_grants.revoke_unissued(grant.approval_id)
            raise ApprovalGrantError(
                "Approval receipt could not be persisted; approval was not issued."
            ) from exc
        return grant

    @staticmethod
    def _requires_approval(cap: Any, capability_id: int, params: Dict[str, Any]) -> bool:
        if bool(getattr(cap, "requires_confirmation", False)) or str(
            getattr(cap, "risk_level", "low")
        ) == "confirm":
            return True
        if int(capability_id) == 61:
            return str(params.get("action") or "").strip().lower() in {
                "delete",
                "unlock",
                "supersede",
            }
        return False

    def _approval_refusal(self, capability_id: int, reason: str) -> ActionResult:
        messages = {
            "missing": (
                "This action requires confirmation through an approval grant before I can proceed."
            ),
            "unknown": "The approval grant is unknown or no longer available.",
            "replayed": "That approval grant has already been used.",
            "expired": "That approval grant has expired.",
            "session_mismatch": "That approval grant belongs to a different session.",
            "capability_mismatch": "That approval grant belongs to a different capability.",
            "action_mismatch": "The action changed after approval, so a new approval is required.",
            "invalidated": "That approval grant is no longer valid.",
            "invalid_action_parameters": "The action parameters are not valid for approval.",
            "caller_confirmation_metadata": (
                "Caller-supplied confirmation metadata cannot authorize execution."
            ),
            "untrusted_approval_metadata": (
                "Approval IDs must be supplied through the trusted Governor invocation context."
            ),
        }
        return self._normalize_action_result(
            ActionResult.refusal(
                messages.get(reason, "This action does not have valid approval."),
                data={"approval_reason": str(reason)},
            ),
            capability_id=capability_id,
        )

    @authoritative_mutation
    def handle_governed_invocation(
        self,
        capability_id: int,
        params: Dict[str, Any],
        *,
        session_id: str | None = None,
        approval_id: str | None = None,
        activity_origin: str = "user_action",
    ) -> ActionResult:
        trusted_session_id = str(session_id or "").strip()[:128]
        trusted_activity_origin = normalize_activity_origin(activity_origin)
        try:
            cap = self.registry.get(capability_id)
        except CapabilityRegistryError as exc:
            return self._normalize_action_result(
                ActionResult.failure(f"I can't do that. {exc}"),
                capability_id=capability_id,
            )

        if not self.registry.is_enabled(capability_id):
            return self._normalize_action_result(
                ActionResult.failure("I can't do that yet."),
                capability_id=capability_id,
            )

        try:
            action_params = canonical_action_snapshot(params)
        except ApprovalAuthorityMetadataError as exc:
            reason = (
                "caller_confirmation_metadata"
                if exc.key == "confirmed"
                else "untrusted_approval_metadata"
            )
            return self._approval_refusal(capability_id, reason)
        except ApprovalGrantError:
            return self._approval_refusal(capability_id, "invalid_action_parameters")

        requires_approval = self._requires_approval(cap, capability_id, action_params)
        if requires_approval or approval_id:
            decision = self._approval_grants.consume(
                approval_id=str(approval_id or ""),
                session_id=trusted_session_id,
                capability_id=capability_id,
                params_snapshot=action_params,
            )
            if not decision.allowed:
                return self._approval_refusal(capability_id, decision.reason)

        if not self._execute_boundary.allow_execution():
            capability_label = str(getattr(cap, "name", "that action") or "that action").replace("_", " ").strip()
            if capability_id == 62:
                message = (
                    "External reasoning is currently unavailable. "
                    "Nova can continue without a second opinion."
                )
            else:
                message = (
                    f"I recognized the action '{capability_label}', but this runtime can't execute it right now. "
                    "Try again with a more specific local command or retry when execution is available."
                )
            return self._normalize_action_result(
                ActionResult.failure(message),
                capability_id=capability_id,
            )

        budget_block = self._check_network_budget(capability_id)
        if budget_block is not None:
            return budget_block

        if self._queue.has_pending():
            return self._normalize_action_result(
                ActionResult.failure("I couldn't do that right now."),
                capability_id=capability_id,
            )

        req = ActionRequest(
            capability_id=capability_id,
            params=action_params,
            approval_id=str(approval_id or "").strip() or None,
        )

        try:
            self.ledger.log_event(
                "ACTION_ATTEMPTED",
                {
                    "capability_id": capability_id,
                    "capability_name": cap.name,
                    "request_id": req.request_id,
                    "session_id": trusted_session_id,
                    "activity_origin": trusted_activity_origin,
                },
            )
        except Exception:
            return self._normalize_action_result(
                ActionResult.failure(
                    "I couldn't do that right now.",
                    request_id=req.request_id,
                ),
                capability_id=capability_id,
                request_id=req.request_id,
            )

        try:
            return self._execute(
                req,
                session_id=trusted_session_id,
                activity_origin=trusted_activity_origin,
            )
        except (NetworkMediatorError, LedgerWriteFailed):
            return self._normalize_action_result(
                ActionResult.failure("I couldn't do that right now.", request_id=req.request_id),
                capability_id=capability_id,
                request_id=req.request_id,
            )
        except Exception:
            return self._normalize_action_result(
                ActionResult.failure("I couldn't do that right now.", request_id=req.request_id),
                capability_id=capability_id,
                request_id=req.request_id,
            )

    def _execute(
        self,
        req: ActionRequest,
        *,
        session_id: str = "",
        activity_origin: str = "user_action",
    ) -> ActionResult:
        entered_execution = False
        self._queue.set_pending(req.request_id)

        try:
            self._execute_boundary.enter_execution()
            entered_execution = True
            start_time = time.monotonic()
            timeout_seconds = self._execution_timeout_seconds(req.capability_id)

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
            result = self._normalize_action_result(
                result,
                capability_id=req.capability_id,
                request_id=req.request_id,
            )
            if req.capability_id in _BUDGET_GATED_CAP_IDS:
                try:
                    from src.usage.provider_usage_store import provider_usage_store

                    snap = provider_usage_store.snapshot()
                    if result.data is None:
                        result.data = {}
                    result.data["budget_state"] = str(snap.get("budget_state") or "normal")
                    result.data["budget_remaining_tokens"] = int(snap.get("budget_remaining_tokens") or 0)
                    result.data["budget_state_label"] = str(snap.get("budget_state_label") or "Normal")
                    result.data["budget_warning"] = str(snap.get("budget_state") or "normal") == "warning"
                except Exception:
                    pass
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
                    "session_id": str(session_id or "").strip()[:128],
                    "activity_origin": normalize_activity_origin(activity_origin),
                    "success": result.success,
                    "status": str(result.status or ""),
                    "external_effect": bool(result.external_effect),
                    "reversible": bool(result.reversible),
                }
                try:
                    topology_entry = self.capability_topology.get(req.capability_id)
                except Exception:
                    topology_entry = None
                if topology_entry is not None:
                    completion_metadata["authority_class"] = str(topology_entry.authority_class)
                    completion_metadata["requires_confirmation"] = bool(
                        topology_entry.requires_confirmation
                    )
                if not result.success:
                    failure_reason = str(result.outcome_reason or result.message or "").strip()
                    if failure_reason:
                        completion_metadata["failure_reason"] = failure_reason[:240]
                outcome_reason = str(result.outcome_reason or "").strip()
                if outcome_reason:
                    completion_metadata["outcome_reason"] = outcome_reason[:240]
                structured_result = result.structured_data if hasattr(result, "structured_data") else {}
                if isinstance(structured_result, dict):
                    outcome_state = str(structured_result.get("outcome_state") or "").strip()
                    if outcome_state:
                        completion_metadata["outcome_state"] = outcome_state[:80]
                    for field_name in (
                        "request_accepted",
                        "effect_verified",
                        "launch_request_accepted",
                        "visible_effect_verified",
                    ):
                        value = structured_result.get(field_name)
                        if isinstance(value, bool):
                            completion_metadata[field_name] = value
                    for field_name in (
                        "reasoning_provider",
                        "reasoning_provider_label",
                        "reasoning_route",
                        "reasoning_route_label",
                        "reasoning_mode",
                        "reasoning_authority",
                        "reasoning_authority_label",
                        "reasoning_governance_note",
                        "launch_result_reason",
                    ):
                        value = str(structured_result.get(field_name) or "").strip()
                        if value:
                            completion_metadata[field_name] = value[:240]
                    launcher_returncode = structured_result.get("launcher_returncode")
                    if type(launcher_returncode) is int:
                        completion_metadata["launcher_returncode"] = launcher_returncode
                self.ledger.log_event(
                    "ACTION_COMPLETED",
                    completion_metadata,
                )
            except LedgerWriteFailed:
                # The completion receipt did not persist. Flag audit degradation
                # without ever contradicting the executor outcome: a successful
                # effect becomes completed_degraded (never a clean success), and a
                # failed/refused result keeps its original status and reason.
                result.mark_audit_degraded(
                    "Completion receipt failed to persist; action outcome unchanged."
                )

            return result

        except TimeoutError:
            # The execution boundary stops waiting, but a worker thread that has
            # already started cannot be force-cancelled — the effect may still
            # complete. Report the honest state (outcome unknown), never "cancelled".
            return self._normalize_action_result(
                ActionResult.refusal(
                    "The request timed out; its final outcome could not be verified. "
                    "Do not retry until the status is checked.",
                    request_id=req.request_id,
                    outcome_reason="timed_out_outcome_unknown",
                ),
                capability_id=req.capability_id,
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
            return self._normalize_action_result(
                ActionResult.refusal(
                    "Execution exceeded allowed memory.",
                    request_id=req.request_id,
                ),
                capability_id=req.capability_id,
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
            return self._normalize_action_result(
                ActionResult.refusal(
                    "Execution exceeded allowed CPU budget.",
                    request_id=req.request_id,
                ),
                capability_id=req.capability_id,
                request_id=req.request_id,
            )
        except Exception:
            return self._normalize_action_result(
                ActionResult.refusal(
                    "I couldn't do that right now.",
                    request_id=req.request_id,
                ),
                capability_id=req.capability_id,
                request_id=req.request_id,
            )
        finally:
            if entered_execution:
                self._execute_boundary.exit_execution()
            self._queue.clear()

    @staticmethod
    def _execution_timeout_seconds(capability_id: int) -> float:
        return float(CAPABILITY_TIMEOUT_OVERRIDES.get(int(capability_id), MAX_EXECUTION_TIME))

    def _authority_class_for(self, capability_id: int) -> str | None:
        try:
            return str(self.capability_topology.get(capability_id).authority_class)
        except Exception:
            return None

    def _check_network_budget(self, capability_id: int) -> ActionResult | None:
        """Return a refusal if the daily token budget is exhausted for budget-gated caps."""
        if capability_id not in _BUDGET_GATED_CAP_IDS:
            return None
        try:
            from src.usage.provider_usage_store import provider_usage_store

            snapshot = provider_usage_store.snapshot()
            if str(snapshot.get("budget_state") or "normal") == "limit":
                return self._normalize_action_result(
                    ActionResult.refusal(
                        "Daily token budget reached. This action requires external tokens. "
                        "Reset the budget in Settings → Usage or wait until tomorrow.",
                        data={
                            "budget_state": "limit",
                            "budget_remaining_tokens": int(snapshot.get("budget_remaining_tokens") or 0),
                            "budget_state_label": str(snapshot.get("budget_state_label") or "Budget reached"),
                        },
                    ),
                    capability_id=capability_id,
                )
        except Exception:
            pass
        return None

    def _topology_entry_for(self, capability_id: int):
        try:
            return self.capability_topology.get(capability_id)
        except Exception:
            return None

    def _normalize_action_result(
        self,
        result: ActionResult,
        *,
        capability_id: int,
        request_id: str | None = None,
    ) -> ActionResult:
        topology_entry = self._topology_entry_for(capability_id)
        return result.normalize(
            request_id=request_id,
            capability_id=capability_id,
            authority_class=str(getattr(topology_entry, "authority_class", "")) if topology_entry else None,
            external_effect=bool(getattr(topology_entry, "external_effect")) if topology_entry and hasattr(topology_entry, "external_effect") else None,
            reversible=bool(getattr(topology_entry, "reversible")) if topology_entry and hasattr(topology_entry, "reversible") else None,
        )

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

        elif req.capability_id == 62:
            from src.executors.external_reasoning_executor import ExternalReasoningExecutor

            return ExternalReasoningExecutor().execute(req)

        elif req.capability_id == 31:
            from src.executors.response_verification_executor import ResponseVerificationExecutor

            return ResponseVerificationExecutor().execute(req)

        elif req.capability_id == 63:
            from src.executors.openclaw_execute_executor import OpenClawExecuteExecutor

            return OpenClawExecuteExecutor().execute(req)

        elif req.capability_id == 64:
            from src.executors.send_email_draft_executor import SendEmailDraftExecutor

            return SendEmailDraftExecutor(ledger=self.ledger).execute(req)

        elif req.capability_id == 65:
            from src.executors.shopify_intelligence_report_executor import (
                ShopifyIntelligenceReportExecutor,
            )

            return ShopifyIntelligenceReportExecutor().execute(req)

        return ActionResult.refusal(
            "Execution path not implemented yet.",
            request_id=req.request_id,
        )

"""Read-only OpenClaw workflow proof adapter.

This module proves a narrow Project Foreman Brief through OpenClawMediator.
It is deterministic and uses only caller-provided sample input. It does not
execute OpenClaw, call Governor, call capabilities, read or write files, open a
browser, make network calls, or touch external accounts.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any

from src.openclaw.openclaw_mediator import (
    OpenClawDelegationEnvelope,
    OpenClawMediator,
    OpenClawMediatorDecision,
    OpenClawMediatorReceipt,
)

_AUTHORITY_EFFECT_NONE = "none"
_WORKFLOW_NAME = "Project Foreman Brief"


@dataclass(frozen=True)
class ProjectForemanBriefInput:
    project_name: str
    allowed_input_scope: tuple[str, ...]
    project_summary: str
    current_focus: tuple[str, ...] = ()
    known_blockers: tuple[str, ...] = ()
    recent_decisions: tuple[str, ...] = ()
    next_safe_steps: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "project_name", str(self.project_name or "").strip())
        object.__setattr__(self, "allowed_input_scope", _clean_tuple(self.allowed_input_scope))
        object.__setattr__(self, "project_summary", str(self.project_summary or "").strip())
        object.__setattr__(self, "current_focus", _clean_tuple(self.current_focus))
        object.__setattr__(self, "known_blockers", _clean_tuple(self.known_blockers))
        object.__setattr__(self, "recent_decisions", _clean_tuple(self.recent_decisions))
        object.__setattr__(self, "next_safe_steps", _clean_tuple(self.next_safe_steps))

    def to_dict(self) -> dict[str, Any]:
        return _to_primitive(self)


@dataclass(frozen=True)
class ReadOnlyOpenClawWorkflowReceipt:
    receipt_type: str
    workflow_name: str
    mediator_decision: str
    did_happen: tuple[str, ...]
    did_not_happen: tuple[str, ...]
    non_action_statement: str
    authority_effect: str = _AUTHORITY_EFFECT_NONE
    execution_performed: bool = False
    authorization_granted: bool = False
    openclaw_called: bool = False
    governor_called: bool = False
    capabilities_called: bool = False
    filesystem_write_performed: bool = False
    browser_opened: bool = False
    network_called: bool = False

    def __post_init__(self) -> None:
        if self.receipt_type != "first_read_only_openclaw_workflow_proof":
            raise ValueError("ReadOnlyOpenClawWorkflowReceipt has an invalid receipt type.")
        if self.authority_effect != _AUTHORITY_EFFECT_NONE:
            raise ValueError("ReadOnlyOpenClawWorkflowReceipt must remain non-authorizing.")
        if self.execution_performed:
            raise ValueError("ReadOnlyOpenClawWorkflowReceipt must not record OpenClaw execution.")
        if self.authorization_granted:
            raise ValueError("ReadOnlyOpenClawWorkflowReceipt must not grant authorization.")
        if self.openclaw_called:
            raise ValueError("ReadOnlyOpenClawWorkflowReceipt must not call OpenClaw.")
        if self.governor_called:
            raise ValueError("ReadOnlyOpenClawWorkflowReceipt must not call Governor.")
        if self.capabilities_called:
            raise ValueError("ReadOnlyOpenClawWorkflowReceipt must not call capabilities.")
        if self.filesystem_write_performed:
            raise ValueError("ReadOnlyOpenClawWorkflowReceipt must not record filesystem writes.")
        if self.browser_opened:
            raise ValueError("ReadOnlyOpenClawWorkflowReceipt must not open browsers.")
        if self.network_called:
            raise ValueError("ReadOnlyOpenClawWorkflowReceipt must not make network calls.")
        if "OpenClaw was not executed." not in self.did_not_happen:
            raise ValueError("Receipt must state that OpenClaw was not executed.")

    def to_dict(self) -> dict[str, Any]:
        return _to_primitive(self)


@dataclass(frozen=True)
class ProjectForemanBriefProof:
    workflow_name: str
    input: ProjectForemanBriefInput
    mediator_envelope: OpenClawDelegationEnvelope
    mediator_decision: OpenClawMediatorDecision
    mediator_receipt: OpenClawMediatorReceipt
    brief: str
    receipt: ReadOnlyOpenClawWorkflowReceipt
    proof_output_rendered: bool
    authority_effect: str = _AUTHORITY_EFFECT_NONE
    execution_performed: bool = False
    authorization_granted: bool = False

    def __post_init__(self) -> None:
        if self.workflow_name != _WORKFLOW_NAME:
            raise ValueError("ProjectForemanBriefProof has an invalid workflow name.")
        if self.authority_effect != _AUTHORITY_EFFECT_NONE:
            raise ValueError("ProjectForemanBriefProof must remain non-authorizing.")
        if self.execution_performed:
            raise ValueError("ProjectForemanBriefProof must not record OpenClaw execution.")
        if self.authorization_granted:
            raise ValueError("ProjectForemanBriefProof must not grant authorization.")
        if self.proof_output_rendered and self.mediator_decision.decision != "preview_allowed":
            raise ValueError("Proof output rendering requires a preview_allowed mediator decision.")

    def to_dict(self) -> dict[str, Any]:
        return _to_primitive(self)


def build_project_foreman_brief_proof(
    sample_input: ProjectForemanBriefInput,
    *,
    mediator: OpenClawMediator | None = None,
    request_text: str = "Prepare a read-only Project Foreman Brief from provided sample input.",
    requested_actions: tuple[str, ...] = ("prepare project foreman brief from caller-provided sample input",),
    browser_use: bool = False,
    computer_use: bool = False,
    filesystem_write: bool = False,
    external_write: bool = False,
    email_action: bool = False,
    calendar_action: bool = False,
    shopify_action: bool = False,
    account_action: bool = False,
    direct_cap63_shortcut: bool = False,
) -> ProjectForemanBriefProof:
    """Return a deterministic read-only workflow proof payload."""

    envelope = OpenClawDelegationEnvelope(
        request_text=request_text,
        requested_actions=requested_actions,
        allowed_input_scope=sample_input.allowed_input_scope,
        read_only=True,
        browser_use=browser_use,
        computer_use=computer_use,
        filesystem_write=filesystem_write,
        external_write=external_write,
        email_action=email_action,
        calendar_action=calendar_action,
        shopify_action=shopify_action,
        account_action=account_action,
        direct_cap63_shortcut=direct_cap63_shortcut,
        metadata={"workflow_name": _WORKFLOW_NAME, "input_source": "caller_provided_sample"},
    )
    active_mediator = mediator or OpenClawMediator()
    decision, mediator_receipt = active_mediator.evaluate_with_receipt(envelope)
    proof_output_rendered = bool(decision.preview_allowed)
    brief = _render_project_foreman_brief(sample_input) if proof_output_rendered else ""
    receipt = _workflow_receipt(decision=decision, proof_output_rendered=proof_output_rendered)

    return ProjectForemanBriefProof(
        workflow_name=_WORKFLOW_NAME,
        input=sample_input,
        mediator_envelope=envelope,
        mediator_decision=decision,
        mediator_receipt=mediator_receipt,
        brief=brief,
        receipt=receipt,
        proof_output_rendered=proof_output_rendered,
    )


def _render_project_foreman_brief(sample_input: ProjectForemanBriefInput) -> str:
    lines = [
        f"Project Foreman Brief: {sample_input.project_name or 'Sample Project'}",
        "",
        sample_input.project_summary or "No project summary was provided.",
    ]
    _add_section(lines, "Current focus", sample_input.current_focus)
    _add_section(lines, "Known blockers", sample_input.known_blockers or ("No active blocker in provided sample input.",))
    _add_section(lines, "Recent decisions", sample_input.recent_decisions)
    _add_section(lines, "Next safe steps", sample_input.next_safe_steps)
    lines.extend(
        [
            "",
            "Boundary: This proof output was rendered from caller-provided sample input only.",
            "No OpenClaw execution, capability call, filesystem write, browser action, network call, or external account action occurred.",
        ]
    )
    return "\n".join(lines).strip()


def _workflow_receipt(
    *,
    decision: OpenClawMediatorDecision,
    proof_output_rendered: bool,
) -> ReadOnlyOpenClawWorkflowReceipt:
    did_happen = (
        "OpenClawMediator evaluated the Project Foreman Brief envelope.",
        "OpenClawMediator returned a policy decision.",
        "A deterministic read-only proof output was rendered from caller-provided sample input."
        if proof_output_rendered
        else "No proof output was rendered because the mediator blocked the envelope.",
        "A receipt/non-action statement was constructed.",
    )
    did_not_happen = (
        "OpenClaw was not executed.",
        "No Governor call was made.",
        "No capability was called.",
        "No Cap 63 shortcut was used.",
        "No browser or computer-use action was performed.",
        "No filesystem write was performed.",
        "No network request was made.",
        "No email, calendar, Shopify, account, or external write action was performed.",
        "No workflow automation was expanded.",
    )
    return ReadOnlyOpenClawWorkflowReceipt(
        receipt_type="first_read_only_openclaw_workflow_proof",
        workflow_name=_WORKFLOW_NAME,
        mediator_decision=decision.decision,
        did_happen=did_happen,
        did_not_happen=did_not_happen,
        non_action_statement=(
            "This receipt records a deterministic read-only workflow proof through "
            "OpenClawMediator. It is not OpenClaw execution or authorization."
        ),
    )


def _add_section(lines: list[str], title: str, values: tuple[str, ...]) -> None:
    if not values:
        return
    lines.extend(["", f"{title}:"])
    lines.extend(f"- {value}" for value in values)


def _clean_tuple(values: tuple[str, ...] | list[str] | Any) -> tuple[str, ...]:
    if values is None:
        return ()
    if isinstance(values, str):
        values = (values,)
    try:
        iterable = tuple(values)
    except TypeError:
        iterable = (values,)
    return tuple(str(item or "").strip() for item in iterable if str(item or "").strip())


def _to_primitive(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if hasattr(value, "__dataclass_fields__"):
        return {key: _to_primitive(item) for key, item in asdict(value).items()}
    if isinstance(value, tuple):
        return [_to_primitive(item) for item in value]
    if isinstance(value, list):
        return [_to_primitive(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _to_primitive(item) for key, item in value.items()}
    return value


__all__ = [
    "ProjectForemanBriefInput",
    "ProjectForemanBriefProof",
    "ReadOnlyOpenClawWorkflowReceipt",
    "build_project_foreman_brief_proof",
]

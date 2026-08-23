"""Wave B2 regressions for non-authorizing capability narration truth."""
from __future__ import annotations

from src.identity.capability_truth import (
    CAPABILITY_TRUTH_FIELDS,
    capability_truth_status,
    project_capability_truth,
)


def _registry(*capabilities: dict) -> dict:
    return {"capabilities": list(capabilities)}


def _cap(
    capability_id: int,
    *,
    name: str = "test_capability",
    enabled: bool = True,
    authority_class: str = "read_only_network",
    requires_confirmation: bool = False,
) -> dict:
    return {
        "id": capability_id,
        "name": name,
        "description": "Test capability",
        "status": "active",
        "enabled": enabled,
        "authority_class": authority_class,
        "requires_confirmation": requires_confirmation,
    }


def _locks(*, locked: bool = False, all_pass: bool = False) -> dict:
    state = "pass" if all_pass else "pending"
    return {
        "capabilities": {
            "16": {
                "locked": locked,
                **{
                    key: {"status": state}
                    for key in ("p1_unit", "p2_routing", "p3_integration", "p4_api", "p5_live")
                },
            }
        }
    }


def test_enabled_but_unconfigured_is_not_available_or_ready() -> None:
    item = project_capability_truth(
        registry_payload=_registry(_cap(16)),
        lock_payload=_locks(),
        provider_snapshot=[{"caps": ["16"], "has_key": False, "health_ok": None}],
        path_capability_ids={16},
    )[0]

    assert item.enabled is True
    assert item.configured is False
    assert item.available_on_this_path is False
    assert "ready" not in capability_truth_status(item).lower()


def test_configured_but_unverified_health_is_not_connected_or_available() -> None:
    item = project_capability_truth(
        registry_payload=_registry(_cap(16)),
        lock_payload=_locks(),
        provider_snapshot=[{"caps": ["16"], "has_key": True, "health_ok": None}],
        path_capability_ids={16},
    )[0]

    assert item.configured is True
    assert item.verification_status == "unverified"
    assert item.available_on_this_path is None
    assert "connected" not in capability_truth_status(item).lower()


def test_confirmation_and_authority_remain_visible() -> None:
    item = project_capability_truth(
        registry_payload=_registry(
            _cap(
                22,
                name="open_file_folder",
                authority_class="reversible_local",
                requires_confirmation=True,
            )
        ),
        lock_payload={},
        provider_snapshot=[],
        path_capability_ids={22},
    )[0]

    assert item.requires_approval is True
    assert item.authority_class == "reversible_local"
    rendered = capability_truth_status(item)
    assert "exists=yes" in rendered
    assert "enabled=yes" in rendered
    assert "approval_required=yes" in rendered
    assert "authority=reversible_local" in rendered


def test_locked_and_unverified_remain_distinct() -> None:
    locked = project_capability_truth(
        registry_payload=_registry(_cap(16)),
        lock_payload=_locks(locked=True, all_pass=True),
        provider_snapshot=[],
    )[0]
    unverified = project_capability_truth(
        registry_payload=_registry(_cap(16)),
        lock_payload=_locks(),
        provider_snapshot=[],
    )[0]

    assert locked.verification_status == "locked"
    assert unverified.verification_status == "unverified"


def test_missing_configuration_verification_and_path_evidence_stays_unknown() -> None:
    raw = _cap(65, name="shopify_intelligence_report")
    raw.pop("requires_confirmation")
    item = project_capability_truth(
        registry_payload=_registry(raw),
        lock_payload={},
        provider_snapshot=[],
        path_capability_ids=None,
    )[0]

    assert item.configured is None
    assert item.verification_status == "unknown"
    assert item.available_on_this_path is None
    assert item.requires_approval is None


def test_disabled_runtime_permission_makes_path_unavailable() -> None:
    item = project_capability_truth(
        registry_payload=_registry(_cap(62, name="external_reasoning_review")),
        lock_payload={},
        provider_snapshot=[],
        runtime_permission_snapshot={"external_reasoning_enabled": False},
        path_capability_ids={62},
    )[0]

    assert item.enabled is True
    assert item.available_on_this_path is False


def test_projection_never_exposes_static_authorized_field() -> None:
    item = project_capability_truth(
        registry_payload=_registry(_cap(16)),
        lock_payload={},
        provider_snapshot=[],
    )[0]

    assert set(CAPABILITY_TRUTH_FIELDS).issubset(item.as_dict())
    assert "authorized" not in item.as_dict()


def test_self_awareness_and_deterministic_help_share_projection_semantics() -> None:
    from src.conversation.meta_intent_handler import _build_what_can_you_do
    from src.identity.nova_self_awareness import _capabilities_block

    item = next(
        item
        for item in project_capability_truth()
        if item.name == "open_file_folder"
    )
    status = capability_truth_status(item)

    assert status in _capabilities_block()
    assert status in _build_what_can_you_do()

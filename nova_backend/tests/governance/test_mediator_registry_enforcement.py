from src.audit.runtime_auditor import _enabled_registry_ids, _load_registry, _mediator_surface_map
from src.governor.governor_mediator import GovernorMediator


def test_mediator_routes_only_enabled_capabilities():
    routed = GovernorMediator.parse_governed_invocation("open documents")
    assert routed is not None
    assert routed.capability_id == 22
    routed = GovernorMediator.parse_governed_invocation("report market update")
    assert routed is not None
    assert routed.capability_id == 48


def test_mediator_mapped_ids_subset_of_registry_enabled_ids():
    registry_enabled = set(_enabled_registry_ids(_load_registry()))
    mapped = set(_mediator_surface_map()["mapped_capability_ids"])
    assert mapped <= registry_enabled


def test_runtime_auditor_maps_shopify_capability_65():
    mapped = set(_mediator_surface_map()["mapped_capability_ids"])
    assert 65 in mapped

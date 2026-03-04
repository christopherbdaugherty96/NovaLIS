from src.audit.runtime_auditor import _enabled_registry_ids, _load_registry, _mediator_surface_map
from src.governor.governor_mediator import GovernorMediator


def test_mediator_does_not_route_disabled_capabilities():
    assert GovernorMediator.parse_governed_invocation("open documents") is None
    assert GovernorMediator.parse_governed_invocation("report market update") is None


def test_mediator_mapped_ids_subset_of_registry_enabled_ids():
    registry_enabled = set(_enabled_registry_ids(_load_registry()))
    mapped = set(_mediator_surface_map()["mapped_capability_ids"])
    assert mapped <= registry_enabled

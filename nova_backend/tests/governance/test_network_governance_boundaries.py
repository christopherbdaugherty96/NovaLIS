import inspect

import src.governor.network_mediator as network_module
from src.governor.network_mediator import NetworkMediator


def test_network_mediator_requires_explicit_capability_id():
    sig = inspect.signature(NetworkMediator.request)
    cap_param = sig.parameters.get("capability_id")
    assert cap_param is not None
    assert cap_param.default is inspect._empty

    source = inspect.getsource(NetworkMediator.request)
    assert "capability_id is None" not in source
    assert "non_capability" not in source


def test_no_module_level_network_mediator_singleton():
    assert not hasattr(network_module, "network_mediator")

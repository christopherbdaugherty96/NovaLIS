from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import inspect

from src.governor import network_mediator as network_module
from src.governor.network_mediator import NetworkMediator


def test_network_mediator_requires_capability_id_not_none():
    sig = inspect.signature(NetworkMediator.request)
    cap_param = sig.parameters.get("capability_id")
    assert cap_param is not None, "NetworkMediator.request must define capability_id"
    assert cap_param.default is inspect._empty, "capability_id must be required"

    source = inspect.getsource(NetworkMediator.request)
    assert "capability_id is None" not in source, "NetworkMediator must not support capability_id=None path"
    assert "non_capability" not in source, "NetworkMediator bypass bucket must not exist"


def test_no_module_level_network_mediator_singleton():
    assert not hasattr(network_module, "network_mediator"), (
        "Module-level network_mediator singleton bypass is prohibited; "
        "all network access must be governor-scoped and capability-bound."
    )

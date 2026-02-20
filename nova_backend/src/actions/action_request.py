# src/actions/action_request.py

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Dict, Mapping
from uuid import uuid4
from datetime import datetime, timezone


@dataclass(frozen=True)
class ActionRequest:
    """
    Immutable description of a user‑requested governed action.
    Created only in governor.py.

    The params dictionary is converted to an immutable mapping
    to prevent any modification after creation.
    """
    capability_id: int
    params: Mapping[str, Any]  # read‑only view after freezing

    # System metadata
    request_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def __post_init__(self):
        """
        Freeze the params dictionary by replacing it with an immutable proxy.
        This ensures that once the ActionRequest is created, its parameters
        cannot be altered by any component.
        """
        # Convert the params dict to an immutable mapping.
        # If params is already a mapping (but not a dict), we still wrap it.
        object.__setattr__(self, 'params', MappingProxyType(dict(self.params)))
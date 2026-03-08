from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any


def _freeze(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({str(k): _freeze(v) for k, v in sorted(value.items(), key=lambda kv: str(kv[0]))})
    if isinstance(value, list):
        return tuple(_freeze(v) for v in value)
    return value


def _to_plain(value: Any) -> Any:
    if isinstance(value, MappingProxyType):
        return {k: _to_plain(v) for k, v in value.items()}
    if isinstance(value, tuple):
        return [_to_plain(v) for v in value]
    return value


@dataclass(frozen=True)
class AgentContextSnapshot:
    data: MappingProxyType
    context_hash: str

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "AgentContextSnapshot":
        frozen = _freeze(payload)
        plain = _to_plain(frozen)
        digest = hashlib.sha256(json.dumps(plain, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
        return cls(data=frozen, context_hash=digest)

    def to_plain_dict(self) -> dict[str, Any]:
        return _to_plain(self.data)

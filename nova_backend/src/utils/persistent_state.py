from __future__ import annotations

import json
import os
from pathlib import Path
from threading import Lock, RLock
from typing import Any
from uuid import uuid4

_REGISTRY_LOCK = Lock()
_PATH_LOCKS: dict[str, RLock] = {}


def _path_key(path: str | Path) -> str:
    target = Path(path)
    try:
        resolved = target.resolve()
    except Exception:
        resolved = target.absolute()
    key = str(resolved)
    return key.lower() if os.name == "nt" else key


def shared_path_lock(path: str | Path) -> RLock:
    key = _path_key(path)
    with _REGISTRY_LOCK:
        existing = _PATH_LOCKS.get(key)
        if existing is not None:
            return existing
        created = RLock()
        _PATH_LOCKS[key] = created
        return created


def write_json_atomic(path: str | Path, payload: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = target.with_name(f"{target.name}.{uuid4().hex}.tmp")
    tmp_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")
    tmp_path.replace(target)

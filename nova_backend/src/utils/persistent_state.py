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


def runtime_root(anchor: str | Path) -> Path:
    """Return the writable runtime root for mutable Nova state.

    The root is the ``src/`` package directory inside ``nova_backend/``.
    All callers — regardless of their own depth under ``src/`` — get the
    same directory so that every store writes to ``src/data/nova_state/…``.

    Override with the ``NOVA_RUNTIME_DIR`` environment variable.
    """
    override = os.getenv("NOVA_RUNTIME_DIR", "").strip()
    if override:
        root = Path(override).expanduser()
    else:
        # Walk upward from the anchor file until we find the ``src`` package
        # directory.  This makes the result independent of caller depth.
        current = Path(anchor).resolve().parent
        while current != current.parent:
            if current.name == "src" and (current / "brain_server.py").exists():
                root = current
                break
            current = current.parent
        else:
            # Fallback: best-effort two levels up (original behaviour).
            root = Path(anchor).resolve().parents[1]

        if not os.access(root, os.W_OK):
            local_appdata = Path(os.getenv("LOCALAPPDATA") or (Path.home() / "AppData" / "Local"))
            root = local_appdata / "Nova"
    root.mkdir(parents=True, exist_ok=True)
    return root


def runtime_path(anchor: str | Path, *parts: str) -> Path:
    return runtime_root(anchor).joinpath(*parts)

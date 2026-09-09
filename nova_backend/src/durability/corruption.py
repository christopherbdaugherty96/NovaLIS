from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class StateCorruptError(RuntimeError):
    """Persisted state exists but cannot be trusted."""

    def __init__(self, store_id: str, path: Path, cause: BaseException | str):
        self.store_id = store_id
        self.path = Path(path)
        self.cause = cause
        detail = str(cause) or type(cause).__name__
        super().__init__(f"Corrupt state for {store_id} at {self.path}: {detail}")


def read_json_state(path: Path, store_id: str) -> Any:
    """Read existing JSON, preserving FileNotFoundError as the absent signal."""

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise StateCorruptError(store_id, path, exc) from exc


def require_state(condition: bool, store_id: str, path: Path, detail: str) -> None:
    if not condition:
        raise StateCorruptError(store_id, path, detail)

"""Read-only ledger health checks for rotation/relocation planning."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

DEFAULT_LEDGER_ROTATION_THRESHOLD_BYTES = 100 * 1024 * 1024


@dataclass(frozen=True)
class LedgerHealth:
    path: Path
    exists: bool
    size_bytes: int
    rotation_threshold_bytes: int
    rotation_recommended: bool
    package_data_path: bool

    @property
    def size_mb(self) -> float:
        return round(self.size_bytes / (1024 * 1024), 2)

    @property
    def relocation_recommended(self) -> bool:
        return self.package_data_path

    def as_dict(self) -> dict[str, object]:
        return {
            "path": str(self.path),
            "exists": self.exists,
            "size_bytes": self.size_bytes,
            "size_mb": self.size_mb,
            "rotation_threshold_bytes": self.rotation_threshold_bytes,
            "rotation_recommended": self.rotation_recommended,
            "package_data_path": self.package_data_path,
            "relocation_recommended": self.relocation_recommended,
        }


def is_package_data_path(path: Path) -> bool:
    parts = tuple(part.lower() for part in path.resolve().parts)
    for index in range(len(parts) - 2):
        if parts[index:index + 3] == ("nova_backend", "src", "data"):
            return True
    return False


def inspect_ledger_health(
    path: Path,
    *,
    rotation_threshold_bytes: int = DEFAULT_LEDGER_ROTATION_THRESHOLD_BYTES,
) -> LedgerHealth:
    resolved = Path(path)
    exists = resolved.exists()
    size_bytes = resolved.stat().st_size if exists else 0
    return LedgerHealth(
        path=resolved,
        exists=exists,
        size_bytes=size_bytes,
        rotation_threshold_bytes=rotation_threshold_bytes,
        rotation_recommended=size_bytes >= rotation_threshold_bytes,
        package_data_path=is_package_data_path(resolved),
    )

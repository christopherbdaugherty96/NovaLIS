from __future__ import annotations

import platform


def get_system_context() -> dict[str, str]:
    """Read-only platform snapshot."""
    return {
        "os": str(platform.system() or "Unknown"),
        "os_release": str(platform.release() or ""),
        "hostname": str(platform.node() or ""),
    }

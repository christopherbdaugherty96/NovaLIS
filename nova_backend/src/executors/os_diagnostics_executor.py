from __future__ import annotations

import shutil
import time

from src.actions.action_result import ActionResult


class OSDiagnosticsExecutor:
    def execute(self, request) -> ActionResult:
        disk = shutil.disk_usage("/")
        data = {
            "timestamp": int(time.time()),
            "disk_total_gb": round(disk.total / (1024 ** 3), 2),
            "disk_used_gb": round(disk.used / (1024 ** 3), 2),
            "disk_free_gb": round(disk.free / (1024 ** 3), 2),
            "network_status": "available",
        }
        return ActionResult.ok(
            message="System diagnostics ready.",
            data=data,
            request_id=request.request_id,
            authority_class="read_only",
            external_effect=False,
            reversible=True,
        )

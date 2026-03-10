from __future__ import annotations

import platform
import shutil
import time
from pathlib import Path

import psutil

from src.actions.action_result import ActionResult


class OSDiagnosticsExecutor:
    @staticmethod
    def _network_status() -> tuple[str, int, str]:
        try:
            stats = psutil.net_if_stats()
            active_non_loopback = 0
            for name, details in stats.items():
                if not details.isup:
                    continue
                lowered = (name or "").lower()
                if lowered.startswith("loopback") or lowered == "lo":
                    continue
                active_non_loopback += 1
            if active_non_loopback > 0:
                return ("available", active_non_loopback, "Interface-level check")
            return ("offline", 0, "No active non-loopback interfaces")
        except Exception:
            return ("unknown", 0, "Interface stats unavailable")

    @staticmethod
    def _disk_root() -> str:
        anchor = Path.home().anchor
        return anchor or "/"

    @staticmethod
    def _health_state(cpu_percent: float, memory_percent: float, disk_percent: float) -> str:
        if cpu_percent >= 90.0 or memory_percent >= 90.0 or disk_percent >= 95.0:
            return "critical"
        if cpu_percent >= 75.0 or memory_percent >= 80.0 or disk_percent >= 85.0:
            return "watch"
        return "healthy"

    def execute(self, request) -> ActionResult:
        disk = shutil.disk_usage(self._disk_root())
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        cpu_percent = round(float(psutil.cpu_percent(interval=0.12)), 1)
        uptime_seconds = max(0, int(time.time() - float(psutil.boot_time())))
        process_count = len(psutil.pids())
        network_status, active_interfaces, network_note = self._network_status()
        disk_total_gb = round(disk.total / (1024 ** 3), 2)
        disk_used_gb = round(disk.used / (1024 ** 3), 2)
        disk_free_gb = round(disk.free / (1024 ** 3), 2)
        disk_percent = round((disk.used / disk.total) * 100.0, 1) if disk.total else 0.0
        memory_total_gb = round(memory.total / (1024 ** 3), 2)
        memory_used_gb = round(memory.used / (1024 ** 3), 2)
        memory_available_gb = round(memory.available / (1024 ** 3), 2)
        memory_percent = round(float(memory.percent), 1)
        swap_total_gb = round(swap.total / (1024 ** 3), 2)
        swap_used_gb = round(swap.used / (1024 ** 3), 2)
        swap_percent = round(float(swap.percent), 1)
        health_state = self._health_state(cpu_percent, memory_percent, disk_percent)

        data = {
            "timestamp": int(time.time()),
            "checked_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "platform": platform.system(),
            "platform_release": platform.release(),
            "hostname": platform.node(),
            "uptime_seconds": uptime_seconds,
            "process_count": process_count,
            "cpu_percent": cpu_percent,
            "memory_total_gb": memory_total_gb,
            "memory_used_gb": memory_used_gb,
            "memory_available_gb": memory_available_gb,
            "memory_percent": memory_percent,
            "swap_total_gb": swap_total_gb,
            "swap_used_gb": swap_used_gb,
            "swap_percent": swap_percent,
            "disk_total_gb": disk_total_gb,
            "disk_used_gb": disk_used_gb,
            "disk_free_gb": disk_free_gb,
            "disk_percent": disk_percent,
            "network_status": network_status,
            "network_interfaces_up": active_interfaces,
            "network_note": network_note,
            "health_state": health_state,
        }
        message = (
            f"System checks complete: {health_state}. "
            f"CPU {cpu_percent:.0f}%, memory {memory_percent:.0f}%, "
            f"disk {disk_percent:.0f}%, network {network_status}."
        )
        return ActionResult.ok(
            message=message,
            data=data,
            request_id=request.request_id,
            authority_class="read_only",
            external_effect=False,
            reversible=True,
        )

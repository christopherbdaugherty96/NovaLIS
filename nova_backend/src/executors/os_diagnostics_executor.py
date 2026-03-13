from __future__ import annotations

import json
import platform
import shutil
import time
from pathlib import Path

import psutil

from src.actions.action_result import ActionResult


class OSDiagnosticsExecutor:
    @staticmethod
    def _enabled_capabilities() -> list[int]:
        registry_path = Path(__file__).resolve().parents[1] / "config" / "registry.json"
        try:
            payload = json.loads(registry_path.read_text(encoding="utf-8"))
        except Exception:
            return []

        enabled: list[int] = []
        for item in payload.get("capabilities", []):
            if item.get("enabled") is True and item.get("id") is not None:
                try:
                    enabled.append(int(item.get("id")))
                except Exception:
                    continue
        return sorted(set(enabled))

    @staticmethod
    def _model_availability() -> str:
        try:
            from src.llm.llm_manager import llm_manager
            if bool(getattr(llm_manager, "inference_blocked", False)):
                return "blocked"
            return "available" if bool(llm_manager.health_check()) else "unavailable"
        except Exception:
            return "unknown"

    @staticmethod
    def _model_status_details() -> tuple[str, str, str, bool]:
        try:
            from src.llm.llm_manager import llm_manager

            endpoint_available = bool(llm_manager.health_check())
            inference_blocked = bool(getattr(llm_manager, "inference_blocked", False))

            if inference_blocked:
                if endpoint_available:
                    return (
                        "blocked",
                        "Local model is reachable, but inference is locked pending explicit confirmation.",
                        "Run 'confirm model update' to re-enable local inference.",
                        False,
                    )
                return (
                    "blocked",
                    "Local inference is locked pending explicit confirmation, and the model endpoint is not currently reachable.",
                    "Start the local model service, then run 'confirm model update'.",
                    False,
                )

            if endpoint_available:
                return (
                    "available",
                    "Local model endpoint is reachable and inference is enabled.",
                    "",
                    True,
                )

            return (
                "unavailable",
                "Local model endpoint did not respond or the configured model is missing.",
                "Start the local model service and verify the configured model is installed.",
                False,
            )
        except Exception:
            return (
                "unknown",
                "Model readiness could not be determined.",
                "",
                False,
            )

    @staticmethod
    def _tone_status_details() -> tuple[str, str, str, int]:
        try:
            from src.personality.tone_profile_store import ToneProfileStore

            snapshot = ToneProfileStore().snapshot()
            global_profile = str(snapshot.get("global_profile") or "balanced").strip().lower()
            summary = str(snapshot.get("summary") or "").strip()
            override_count = int(snapshot.get("override_count") or 0)
            return global_profile, summary, str(snapshot.get("updated_at") or ""), override_count
        except Exception:
            return "balanced", "Tone settings unavailable.", "", 0

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
        enabled_capability_ids = self._enabled_capabilities()
        model_availability, model_note, model_remediation, model_ready = self._model_status_details()
        tone_global_profile, tone_summary, tone_updated_at, tone_override_count = self._tone_status_details()

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
            "active_capabilities_count": len(enabled_capability_ids),
            "active_capability_ids": enabled_capability_ids,
            "model_availability": model_availability,
            "model_ready": model_ready,
            "model_note": model_note,
            "model_remediation": model_remediation,
            "tone_global_profile": tone_global_profile,
            "tone_summary": tone_summary,
            "tone_updated_at": tone_updated_at,
            "tone_override_count": tone_override_count,
            "health_state": health_state,
        }
        message = (
            f"System checks complete: {health_state}. "
            f"CPU {cpu_percent:.0f}%, memory {memory_percent:.0f}%, "
            f"disk {disk_percent:.0f}%, network {network_status}, "
            f"model {model_availability}, tone {tone_global_profile}, "
            f"capabilities {len(enabled_capability_ids)}."
        )
        if model_note:
            message = f"{message} {model_note}"
        return ActionResult.ok(
            message=message,
            data=data,
            request_id=request.request_id,
            authority_class="read_only",
            external_effect=False,
            reversible=True,
        )

from __future__ import annotations

import json
import platform
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path

import psutil

from src.actions.action_result import ActionResult
from src.build_phase import BUILD_PHASE


class OSDiagnosticsExecutor:
    @staticmethod
    def _enabled_capability_entries() -> list[dict[str, object]]:
        registry_path = Path(__file__).resolve().parents[1] / "config" / "registry.json"
        try:
            payload = json.loads(registry_path.read_text(encoding="utf-8"))
        except Exception:
            return []

        enabled: list[dict[str, object]] = []
        for item in payload.get("capabilities", []):
            if item.get("enabled") is True and item.get("id") is not None:
                try:
                    enabled.append(
                        {
                            "id": int(item.get("id")),
                            "name": str(item.get("name") or "").strip(),
                            "risk_level": str(item.get("risk_level") or "").strip().lower(),
                            "status": str(item.get("status") or "").strip().lower(),
                        }
                    )
                except Exception:
                    continue
        return sorted(enabled, key=lambda item: int(item.get("id") or 0))

    @staticmethod
    def _enabled_capabilities() -> list[int]:
        return sorted(
            {
                int(item.get("id"))
                for item in OSDiagnosticsExecutor._enabled_capability_entries()
                if item.get("id") is not None
            }
        )

    @staticmethod
    def _capability_surface(
        enabled_entries: list[dict[str, object]],
    ) -> tuple[list[dict[str, object]], str, int]:
        capability_map = {
            "governed_web_search": {
                "category": "Research",
                "action": "Search the web",
                "prompt": "search the web for the latest AI policy updates",
            },
            "response_verification": {
                "category": "Research",
                "action": "Verify or pressure-check an answer",
                "prompt": "verify this answer",
            },
            "multi_source_reporting": {
                "category": "Research",
                "action": "Create a research brief",
                "prompt": "create a research brief on AI regulation",
            },
            "topic_memory_map": {
                "category": "Research",
                "action": "Map a topic and its relationships",
                "prompt": "map the topic of AI regulation",
            },
            "headline_summary": {
                "category": "News and Briefing",
                "action": "Summarize headlines",
                "prompt": "summarize all headlines",
            },
            "intelligence_brief": {
                "category": "News and Briefing",
                "action": "Create a daily brief",
                "prompt": "daily brief",
            },
            "story_tracker_update": {
                "category": "News and Briefing",
                "action": "Update tracked stories",
                "prompt": "update tracked stories",
            },
            "story_tracker_view": {
                "category": "News and Briefing",
                "action": "Review tracked stories",
                "prompt": "review tracked stories",
            },
            "weather_snapshot": {
                "category": "News and Briefing",
                "action": "Check the weather",
                "prompt": "weather",
            },
            "news_snapshot": {
                "category": "News and Briefing",
                "action": "Get the latest news",
                "prompt": "news",
            },
            "calendar_snapshot": {
                "category": "News and Briefing",
                "action": "Review today's calendar",
                "prompt": "calendar",
            },
            "analysis_document": {
                "category": "Documents",
                "action": "Create an analysis document",
                "prompt": "create analysis report on AI regulation",
            },
            "explain_anything": {
                "category": "Documents",
                "action": "Explain a file, page, or document",
                "prompt": "explain this",
            },
            "screen_capture": {
                "category": "Screen",
                "action": "Capture the current screen region",
                "prompt": "capture this screen",
            },
            "screen_analysis": {
                "category": "Screen",
                "action": "Analyze visible screen content",
                "prompt": "analyze this screen",
            },
            "open_website": {
                "category": "Computer",
                "action": "Open a website",
                "prompt": "open github",
            },
            "open_file_folder": {
                "category": "Computer",
                "action": "Open a file or folder",
                "prompt": "open documents",
            },
            "volume_up_down": {
                "category": "Computer",
                "action": "Adjust volume",
                "prompt": "volume up",
            },
            "media_play_pause": {
                "category": "Computer",
                "action": "Control media playback",
                "prompt": "pause",
            },
            "brightness_control": {
                "category": "Computer",
                "action": "Adjust screen brightness",
                "prompt": "brightness down",
            },
            "os_diagnostics": {
                "category": "System",
                "action": "Show system status and diagnostics",
                "prompt": "system status",
            },
            "speak_text": {
                "category": "Voice",
                "action": "Speak responses aloud",
                "prompt": "speak that",
            },
            "memory_governance": {
                "category": "Memory",
                "action": "Save and review governed memory",
                "prompt": "memory overview",
            },
        }
        category_order = [
            "Research",
            "News and Briefing",
            "Documents",
            "Screen",
            "Computer",
            "System",
            "Voice",
            "Memory",
        ]

        grouped: dict[str, dict[str, object]] = {}
        for item in enabled_entries:
            name = str(item.get("name") or "").strip()
            mapping = capability_map.get(name)
            if not mapping:
                continue
            category = str(mapping.get("category") or "").strip()
            action = str(mapping.get("action") or "").strip()
            prompt = str(mapping.get("prompt") or "").strip()
            bucket = grouped.setdefault(
                category,
                {
                    "category": category,
                    "actions": [],
                    "items": [],
                    "capability_ids": [],
                    "capability_names": [],
                },
            )
            actions = bucket["actions"]
            if action not in actions:
                actions.append(action)
            items = bucket["items"]
            capability_id = int(item.get("id") or 0)
            if action and not any(existing.get("action") == action for existing in items):
                items.append(
                    {
                        "action": action,
                        "prompt": prompt,
                        "capability_id": capability_id,
                        "capability_name": name,
                    }
                )
            capability_ids = bucket["capability_ids"]
            capability_names = bucket["capability_names"]
            if capability_id and capability_id not in capability_ids:
                capability_ids.append(capability_id)
            if name not in capability_names:
                capability_names.append(name)

        surface: list[dict[str, object]] = []
        for category in category_order:
            bucket = grouped.get(category)
            if bucket:
                surface.append(bucket)

        total_actions = sum(len(list(group.get("actions") or [])) for group in surface)
        if surface:
            summary = (
                f"{total_actions} live actions across {len(surface)} areas are currently "
                "available through the Governor."
            )
        else:
            summary = "No governed capabilities are currently exposed in the active runtime."

        return surface, summary, total_actions

    @staticmethod
    def _recent_runtime_activity(
        enabled_entries: list[dict[str, object]],
        *,
        limit: int = 6,
    ) -> tuple[list[dict[str, str]], str]:
        try:
            from src.ledger.writer import LEDGER_PATH

            path = Path(LEDGER_PATH)
            if not path.exists():
                return [], "No ledger-backed runtime activity yet."

            capability_lookup = {
                int(item.get("id")): str(item.get("name") or "").strip()
                for item in enabled_entries
                if item.get("id") is not None
            }
            raw_lines = path.read_text(encoding="utf-8").splitlines()
            items: list[dict[str, str]] = []

            for raw_line in reversed(raw_lines):
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                item = OSDiagnosticsExecutor._recent_activity_item(entry, capability_lookup)
                if not item:
                    continue
                items.append(item)
                if len(items) >= max(1, limit):
                    break

            if not items:
                return [], "No reviewable runtime activity yet."

            return items, f"Showing the latest {len(items)} ledger-backed runtime events."
        except Exception:
            return [], "Recent runtime activity is unavailable."

    @staticmethod
    def _recent_activity_item(
        entry: dict[str, object],
        capability_lookup: dict[int, str],
    ) -> dict[str, str] | None:
        event_type = str(entry.get("event_type") or "").strip().upper()
        if not event_type or event_type.startswith("WORKING_CONTEXT_"):
            return None

        timestamp_label = OSDiagnosticsExecutor._recent_activity_timestamp(
            str(entry.get("timestamp_utc") or "")
        )
        detail = ""
        title = ""
        kind = "system"

        if event_type.startswith("ACTION_") and event_type.endswith("_COMPLETED"):
            kind = "action"
            title = "Action completed"
            detail = OSDiagnosticsExecutor._capability_label_from_entry(entry, capability_lookup)
        elif event_type.startswith("ACTION_") and event_type.endswith("_ATTEMPTED"):
            return None
        elif event_type == "EXTERNAL_NETWORK_CALL":
            kind = "network"
            title = "External request"
            detail = OSDiagnosticsExecutor._domain_from_entry(entry)
        elif event_type == "MODEL_NETWORK_CALL":
            kind = "model"
            title = "Model readiness check"
            detail = OSDiagnosticsExecutor._domain_from_entry(entry) or "Local model endpoint"
        elif event_type.startswith("MEMORY_ITEM_"):
            kind = "memory"
            title = event_type.replace("_", " ").title()
            detail = str(entry.get("summary") or "Governed memory activity").strip()
        elif event_type.startswith("NOTIFICATION_"):
            kind = "schedule"
            title = event_type.replace("_", " ").title()
            active_count = int(entry.get("active_count") or 0)
            due_count = int(entry.get("due_count") or 0)
            if active_count or due_count:
                detail = f"Active {active_count}, due {due_count}"
            else:
                detail = "Notification scheduling activity"
        elif event_type.startswith("PATTERN_"):
            kind = "pattern"
            title = event_type.replace("_", " ").title()
            detail = "Pattern review activity"
        elif event_type.startswith("POLICY_"):
            kind = "policy"
            title = event_type.replace("_", " ").title()
            detail = str(entry.get("policy_id") or "Draft policy event").strip()
        elif event_type.startswith("TONE_PROFILE_"):
            kind = "tone"
            title = event_type.replace("_", " ").title()
            detail = str(entry.get("global_profile") or "Response style change").strip()
        elif event_type in {"SCREEN_CAPTURE_COMPLETED", "SCREEN_ANALYSIS_COMPLETED", "EXPLAIN_ANYTHING_COMPLETED"}:
            kind = "screen"
            title = event_type.replace("_", " ").title()
            detail = "Screen and explanation workflow"
        elif event_type in {"PROJECT_THREAD_CREATED", "PROJECT_THREAD_UPDATED", "PROJECT_THREAD_RESUMED", "PROJECT_THREAD_MAP_VIEWED"}:
            kind = "thread"
            title = event_type.replace("_", " ").title()
            detail = str(entry.get("thread_title") or "Project thread activity").strip()
        elif event_type in {"SEARCH_QUERY", "WEBPAGE_LAUNCH", "WEBPAGE_PREVIEW", "SPEECH_RENDERED"}:
            kind = "action"
            title = event_type.replace("_", " ").title()
            detail = str(entry.get("query") or entry.get("url") or "Governed action").strip()
        else:
            return None

        detail = detail or "Runtime activity"
        return {
            "event_type": event_type,
            "kind": kind,
            "title": title,
            "detail": detail,
            "timestamp": timestamp_label,
        }

    @staticmethod
    def _recent_activity_timestamp(raw_value: str) -> str:
        raw = str(raw_value or "").strip()
        if not raw:
            return ""
        try:
            timestamp = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            return raw
        return timestamp.astimezone().strftime("%b %d, %I:%M %p").replace(" 0", " ")

    @staticmethod
    def _capability_label_from_entry(
        entry: dict[str, object],
        capability_lookup: dict[int, str],
    ) -> str:
        name = str(entry.get("capability_name") or "").strip()
        if name:
            return name.replace("_", " ")
        capability_id = entry.get("capability_id")
        try:
            if capability_id is not None:
                resolved = capability_lookup.get(int(capability_id))
                if resolved:
                    return resolved.replace("_", " ")
        except Exception:
            pass
        return "Governed capability"

    @staticmethod
    def _domain_from_entry(entry: dict[str, object]) -> str:
        raw_url = str(entry.get("url") or entry.get("original_url") or "").strip()
        if not raw_url:
            return ""
        trimmed = raw_url.split("://", 1)[-1]
        return trimmed.split("/", 1)[0].strip() or raw_url

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
    def _memory_status_details() -> tuple[str, int, str, str]:
        try:
            from src.memory.governed_memory_store import GovernedMemoryStore

            overview = GovernedMemoryStore().summarize_overview()
            total_count = int(overview.get("total_count") or 0)
            recent_items = list(overview.get("recent_items") or [])
            last_write = ""
            if recent_items:
                last_write = str(dict(recent_items[0]).get("updated_at") or "")
            summary = (
                f"Persistent memory enabled with {total_count} item(s)."
                if total_count
                else "Persistent memory enabled with no saved items yet."
            )
            return "enabled", total_count, last_write, summary
        except Exception:
            return "unknown", 0, "", "Persistent memory status unavailable."

    @staticmethod
    def _notification_schedule_details() -> tuple[str, bool, str, int, int, int]:
        try:
            from src.tasks.notification_schedule_store import NotificationScheduleStore

            snapshot = NotificationScheduleStore().summarize()
            policy = dict(snapshot.get("policy") or {})
            policy_summary = str(snapshot.get("policy_summary") or "").strip()
            return (
                policy_summary or "Notification policy unavailable.",
                bool(policy.get("quiet_hours_enabled")),
                str(policy.get("quiet_hours_label") or "Off"),
                int(policy.get("max_deliveries_per_hour") or 0),
                int(snapshot.get("active_count") or 0),
                int(snapshot.get("due_count") or 0),
            )
        except Exception:
            return ("Notification policy unavailable.", False, "Off", 0, 0, 0)

    @staticmethod
    def _policy_status_details() -> tuple[str, str, int, int, int, int, int]:
        try:
            from src.policies.atomic_policy_store import AtomicPolicyStore

            overview = AtomicPolicyStore().overview()
            active_count = int(overview.get("active_count") or 0)
            draft_count = int(overview.get("draft_count") or 0)
            disabled_count = int(overview.get("disabled_count") or 0)
            simulation_count = int(overview.get("simulation_count") or 0)
            manual_run_count = int(overview.get("manual_run_count") or 0)
            summary = str(overview.get("summary") or "").strip()
            return "manual_review_ready", summary, active_count, draft_count, disabled_count, simulation_count, manual_run_count
        except Exception:
            return "unknown", "Policy draft status unavailable.", 0, 0, 0, 0, 0

    @staticmethod
    def _ledger_status_details() -> tuple[str, int, str]:
        try:
            from src.ledger.writer import LEDGER_PATH

            path = Path(LEDGER_PATH)
            if not path.exists():
                return "ok", 0, "None"

            today = datetime.now(timezone.utc).date()
            entries_today = 0
            last_event = "None"

            with path.open("r", encoding="utf-8") as handle:
                for raw_line in handle:
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    event_type = str(entry.get("event_type") or "").strip() or "UNKNOWN"
                    last_event = event_type
                    raw_ts = str(entry.get("timestamp_utc") or "").strip()
                    try:
                        timestamp = datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
                    except ValueError:
                        continue
                    if timestamp.astimezone(timezone.utc).date() == today:
                        entries_today += 1

            return "ok", entries_today, last_event
        except Exception:
            return "unavailable", 0, "Unknown"

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

    @staticmethod
    def _phase_display() -> str:
        if BUILD_PHASE >= 5:
            return "5 closed / 6 foundation"
        return f"{BUILD_PHASE}"

    @staticmethod
    def _blocked_conditions(*, model_availability: str) -> list[dict[str, str]]:
        items = [
            {
                "area": "autonomy",
                "label": "Autonomy",
                "status": "disabled",
                "reason": "Nova remains invocation-bound. Delegated runtime is not active.",
            },
            {
                "area": "delegated_trigger_runtime",
                "label": "Delegated trigger runtime",
                "status": "disabled",
                "reason": "Background delegated policy execution is still disabled. Manual review runs are allowed separately.",
            },
            {
                "area": "background_monitoring",
                "label": "Background monitoring",
                "status": "disabled",
                "reason": "Trigger runtime is not active.",
            },
            {
                "area": "wake_word",
                "label": "Wake word",
                "status": "disabled",
                "reason": "Wake-word runtime remains planned, not active.",
            },
            {
                "area": "external_effect_policies",
                "label": "External-effect delegation",
                "status": "disabled",
                "reason": "Only low-risk delegated classes are candidates for future enablement.",
            },
        ]
        if model_availability == "blocked":
            items.append(
                {
                    "area": "model_inference",
                    "label": "Model inference",
                    "status": "blocked",
                    "reason": "Local inference is locked pending explicit confirmation.",
                }
            )
        return items

    @staticmethod
    def _system_reasons(
        *,
        model_availability: str,
        model_note: str,
        model_remediation: str,
    ) -> list[dict[str, str]]:
        reasons = [
            {
                "area": "execution_authority",
                "status": "restricted",
                "reason": "Phase-5 trust layer is active and delegated runtime remains locked.",
            },
            {
                "area": "policy_execution",
                "status": "manual_review_only",
                "reason": "Policy drafts can be validated, simulated, and manually review-run once through the executor gate.",
            },
            {
                "area": "background_monitoring",
                "status": "disabled",
                "reason": "Trigger-only monitoring is not active, so no background policy runtime exists.",
            },
            {
                "area": "network_access",
                "status": "mediated",
                "reason": "External requests route through the NetworkMediator rather than direct executor access.",
            },
            {
                "area": "wake_word",
                "status": "disabled",
                "reason": "Wake-word input remains planned and is not part of active runtime truth.",
            },
        ]
        if model_availability != "available":
            reasons.append(
                {
                    "area": "model",
                    "status": model_availability or "unknown",
                    "reason": model_remediation or model_note or "Model readiness is limited.",
                }
            )
        return reasons

    @staticmethod
    def _operator_health_summary(
        *,
        health_state: str,
        model_availability: str,
        policy_draft_count: int,
        policy_simulation_count: int,
        blocked_count: int,
    ) -> str:
        model_label = model_availability or "unknown"
        return (
            f"Phase {OSDiagnosticsExecutor._phase_display()} · "
            f"Health {health_state} · "
            f"Model {model_label} · "
            f"Policy drafts {policy_draft_count} · "
            f"Simulations {policy_simulation_count} · "
            f"Locks {blocked_count}."
        )

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
        enabled_capability_entries = self._enabled_capability_entries()
        enabled_capability_ids = [
            int(item.get("id"))
            for item in enabled_capability_entries
            if item.get("id") is not None
        ]
        (
            available_capability_surface,
            capability_surface_summary,
            available_capability_action_count,
        ) = self._capability_surface(enabled_capability_entries)
        recent_runtime_activity, trust_review_summary = self._recent_runtime_activity(
            enabled_capability_entries
        )
        model_availability, model_note, model_remediation, model_ready = self._model_status_details()
        tone_global_profile, tone_summary, tone_updated_at, tone_override_count = self._tone_status_details()
        memory_status, memory_total_count, memory_last_write, memory_summary = self._memory_status_details()
        (
            notification_policy_summary,
            notification_quiet_hours_enabled,
            notification_quiet_hours_label,
            notification_rate_limit_per_hour,
            notification_active_count,
            notification_due_count,
        ) = self._notification_schedule_details()
        (
            policy_foundation_status,
            policy_summary,
            policy_active_count,
            policy_draft_count,
            policy_disabled_count,
            policy_simulation_count,
            policy_manual_run_count,
        ) = self._policy_status_details()
        ledger_integrity, ledger_entries_today, ledger_last_event = self._ledger_status_details()
        blocked_conditions = self._blocked_conditions(model_availability=model_availability)
        system_reasons = self._system_reasons(
            model_availability=model_availability,
            model_note=model_note,
            model_remediation=model_remediation,
        )
        operator_health_summary = self._operator_health_summary(
            health_state=health_state,
            model_availability=model_availability,
            policy_draft_count=policy_draft_count,
            policy_simulation_count=policy_simulation_count,
            blocked_count=len(blocked_conditions),
        )

        data = {
            "timestamp": int(time.time()),
            "checked_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "build_phase": BUILD_PHASE,
            "phase_display": self._phase_display(),
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
            "network_mediator_status": "active",
            "active_capabilities_count": len(enabled_capability_ids),
            "active_capability_ids": enabled_capability_ids,
            "capability_registry_status": "loaded" if enabled_capability_ids else "unavailable",
            "available_capability_surface": available_capability_surface,
            "available_capability_surface_count": len(available_capability_surface),
            "available_capability_action_count": available_capability_action_count,
            "capability_surface_summary": capability_surface_summary,
            "capability_surface_source": "registry_enabled_capabilities",
            "recent_runtime_activity": recent_runtime_activity,
            "recent_runtime_activity_count": len(recent_runtime_activity),
            "trust_review_summary": trust_review_summary,
            "governor_status": "active",
            "execution_boundary_status": "enforced",
            "delegated_runtime_status": "manual_review_only",
            "model_availability": model_availability,
            "model_ready": model_ready,
            "model_note": model_note,
            "model_remediation": model_remediation,
            "voice_status": "ready",
            "voice_note": "Push-to-talk and TTS are available. Wake word remains disabled.",
            "wake_word_status": "disabled",
            "memory_status": memory_status,
            "memory_total_count": memory_total_count,
            "memory_last_write": memory_last_write,
            "memory_summary": memory_summary,
            "tone_global_profile": tone_global_profile,
            "tone_summary": tone_summary,
            "tone_updated_at": tone_updated_at,
            "tone_override_count": tone_override_count,
            "notification_policy_summary": notification_policy_summary,
            "notification_quiet_hours_enabled": notification_quiet_hours_enabled,
            "notification_quiet_hours_label": notification_quiet_hours_label,
            "notification_rate_limit_per_hour": notification_rate_limit_per_hour,
            "notification_active_count": notification_active_count,
            "notification_due_count": notification_due_count,
            "schedule_configured_count": notification_active_count,
            "policy_foundation_status": policy_foundation_status,
            "policy_summary": policy_summary,
            "policy_active_count": policy_active_count,
            "policy_draft_count": policy_draft_count,
            "policy_disabled_count": policy_disabled_count,
            "policy_enabled_count": 0,
            "policy_simulation_count": policy_simulation_count,
            "policy_manual_run_count": policy_manual_run_count,
            "ledger_integrity": ledger_integrity,
            "ledger_entries_today": ledger_entries_today,
            "ledger_last_event": ledger_last_event,
            "blocked_conditions": blocked_conditions,
            "locks_active_count": len(blocked_conditions),
            "system_reasons": system_reasons,
            "operator_health_summary": operator_health_summary,
            "health_state": health_state,
        }
        message = (
            f"System checks complete: {health_state}. "
            f"CPU {cpu_percent:.0f}%, memory {memory_percent:.0f}%, "
            f"disk {disk_percent:.0f}%, network {network_status}, "
            f"model {model_availability}, tone {tone_global_profile}, "
            f"notifications {notification_quiet_hours_label}, "
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

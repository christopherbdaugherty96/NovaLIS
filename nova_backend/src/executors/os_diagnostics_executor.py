from __future__ import annotations

import json
import os
import platform
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path

import psutil

from src.actions.action_result import ActionResult
from src.build_phase import BUILD_PHASE
from src.openclaw.agent_runtime_store import openclaw_agent_runtime_store
from src.settings.runtime_settings_store import runtime_settings_store
from src.usage.provider_usage_store import provider_usage_store


class OSDiagnosticsExecutor:
    @staticmethod
    def _voice_status_details() -> tuple[str, str]:
        try:
            from src.voice.tts_engine import inspect_voice_runtime

            snapshot = inspect_voice_runtime()
        except Exception:
            return "unknown", "Voice runtime could not be inspected. Wake word remains disabled."

        preferred_status = str(snapshot.get("preferred_status") or "unknown").strip().lower()
        stt_status = str(snapshot.get("stt_status") or "unknown").strip().lower()
        if preferred_status == "ready" and stt_status == "ready":
            overall = "ready"
        elif preferred_status in {"ready", "degraded"} or stt_status in {"ready", "degraded"}:
            overall = "degraded"
        else:
            overall = "unavailable"
        note = str(snapshot.get("summary") or "Voice runtime status is unavailable.").strip()
        if note:
            note = f"{note} Wake word remains disabled."
        else:
            note = "Wake word remains disabled."
        return overall, note

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
            "external_reasoning_review": {
                "category": "Research",
                "action": "Get a governed second opinion",
                "prompt": "second opinion",
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

            for line_number, raw_line in reversed(list(enumerate(raw_lines, start=1))):
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                entry["_ledger_line"] = line_number
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
        outcome = OSDiagnosticsExecutor._recent_activity_outcome(entry)
        reason = ""
        effect = ""
        request_id = OSDiagnosticsExecutor._recent_activity_request_id(entry)
        ledger_ref = OSDiagnosticsExecutor._recent_activity_ledger_ref(entry)
        capability_id = OSDiagnosticsExecutor._recent_activity_capability_id(entry)
        capability_name = (
            capability_lookup.get(capability_id, "") if capability_id is not None else ""
        )
        status = str(entry.get("status") or "").strip().lower()
        authority_class = str(entry.get("authority_class") or "").strip()
        reversible = entry.get("reversible")
        external_effect = entry.get("external_effect")

        if event_type.startswith("ACTION_") and event_type.endswith("_COMPLETED"):
            kind = "action"
            title = "Action completed" if outcome != "issue" else "Action needs attention"
            detail = OSDiagnosticsExecutor._capability_label_from_entry(entry, capability_lookup)
            reason = str(entry.get("failure_reason") or entry.get("outcome_reason") or "").strip()
            if not reason:
                reason = OSDiagnosticsExecutor._recent_activity_allow_reason(entry)
            effect = OSDiagnosticsExecutor._recent_activity_effect(entry)
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
            if outcome == "issue":
                title = title.replace("Completed", "Needs Attention")
            detail = "Screen and explanation workflow"
            reason = str(entry.get("error") or "").strip()
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
            "outcome": outcome,
            "reason": reason,
            "effect": effect,
            "request_id": request_id,
            "ledger_ref": ledger_ref,
            "status": status,
            "capability_id": str(capability_id) if capability_id is not None else "",
            "capability_name": capability_name,
            "authority_class": authority_class,
            "reversible": "" if not isinstance(reversible, bool) else ("yes" if reversible else "no"),
            "external_effect": "" if not isinstance(external_effect, bool) else ("yes" if external_effect else "no"),
            "reasoning_provider": str(entry.get("reasoning_provider_label") or entry.get("reasoning_provider") or "").strip(),
            "reasoning_route": str(entry.get("reasoning_route_label") or entry.get("reasoning_route") or "").strip(),
            "reasoning_mode": str(entry.get("reasoning_mode") or "").strip(),
            "reasoning_authority": str(entry.get("reasoning_authority_label") or entry.get("reasoning_authority") or "").strip(),
            "reasoning_governance_note": str(entry.get("reasoning_governance_note") or "").strip(),
            "reasoning_summary_line": str(entry.get("reasoning_summary_line") or "").strip(),
            "top_issue": str(entry.get("top_issue") or "").strip(),
            "top_correction": str(entry.get("top_correction") or "").strip(),
        }

    @staticmethod
    def _recent_activity_outcome(entry: dict[str, object]) -> str:
        success = entry.get("success")
        if isinstance(success, bool):
            return "success" if success else "issue"
        status = str(entry.get("status") or "").strip().lower()
        if status == "completed":
            return "success"
        if status in {"failed", "refused"}:
            return "issue"
        return "info"

    @staticmethod
    def _recent_activity_effect(entry: dict[str, object]) -> str:
        external_effect = entry.get("external_effect")
        reversible = entry.get("reversible")

        if not isinstance(external_effect, bool) and not isinstance(reversible, bool):
            return ""

        parts: list[str] = []
        if isinstance(external_effect, bool):
            parts.append("External effect" if external_effect else "No external effect")
        if isinstance(reversible, bool):
            parts.append("Reversible" if reversible else "Not reversible")
        return ", ".join(parts)

    @staticmethod
    def _recent_activity_allow_reason(entry: dict[str, object]) -> str:
        authority_class = str(entry.get("authority_class") or "").strip().lower()
        if not authority_class:
            return ""

        label_map = {
            "read_only_local": "read-only local",
            "read_only_network": "read-only network",
            "reversible_local": "reversible local",
            "persistent_change": "persistent-change",
            "external_effect": "external-effect",
            "read_only": "read-only",
        }
        authority_label = label_map.get(authority_class, authority_class.replace("_", " "))
        requires_confirmation = entry.get("requires_confirmation")
        if isinstance(requires_confirmation, bool) and requires_confirmation:
            return f"Allowed after explicit confirmation as a {authority_label} action."
        return f"Allowed as an explicit {authority_label} action."

    @staticmethod
    def _recent_activity_request_id(entry: dict[str, object]) -> str:
        return str(entry.get("request_id") or "").strip()

    @staticmethod
    def _recent_activity_capability_id(entry: dict[str, object]) -> int | None:
        raw_value = entry.get("capability_id")
        try:
            if raw_value is None or str(raw_value).strip() == "":
                return None
            return int(raw_value)
        except Exception:
            return None

    @staticmethod
    def _recent_activity_ledger_ref(entry: dict[str, object]) -> str:
        line_number = entry.get("_ledger_line")
        try:
            if line_number is not None:
                resolved = int(line_number)
                if resolved > 0:
                    return f"L{resolved}"
        except Exception:
            pass
        return ""

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

            active_model = str(getattr(llm_manager, "active_model", llm_manager.model))
            using_fallback = bool(getattr(llm_manager, "_using_fallback", False))
            endpoint_available = bool(llm_manager.health_check())
            inference_blocked = bool(getattr(llm_manager, "inference_blocked", False))

            if inference_blocked:
                if endpoint_available:
                    return (
                        "blocked",
                        f"Local model ({active_model}) is reachable, but inference is locked pending explicit confirmation.",
                        "Run 'confirm model update' to re-enable local inference.",
                        False,
                    )
                return (
                    "blocked",
                    f"Local inference is locked pending explicit confirmation, and the model endpoint ({active_model}) is not currently reachable.",
                    "Start the local model service, then run 'confirm model update'.",
                    False,
                )

            if using_fallback:
                return (
                    "fallback",
                    f"Local model ({active_model}) is running on the fallback model after primary failures.",
                    "Check the primary model and restart if available.",
                    True,
                )

            if endpoint_available:
                return (
                    "available",
                    f"Local model ({active_model}) is reachable and inference is enabled.",
                    "",
                    True,
                )

            return (
                "unavailable",
                f"Local model endpoint ({active_model}) did not respond or the configured model is missing.",
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
        if BUILD_PHASE >= 8:
            return "7 complete / 8 active"
        if BUILD_PHASE >= 7:
            return "7 complete / 8 design"
        if BUILD_PHASE >= 6:
            return "6 complete / 7 partial"
        if BUILD_PHASE >= 5:
            return "5 closed / 6 foundation"
        return f"{BUILD_PHASE}"

    @staticmethod
    def _external_reasoning_status_details() -> dict[str, object]:
        enabled_entries = OSDiagnosticsExecutor._enabled_capability_entries()
        enabled_ids = {
            int(item.get("id"))
            for item in enabled_entries
            if item.get("id") is not None
        }
        capability_enabled = 62 in enabled_ids
        reasoning_permission_enabled = runtime_settings_store.is_permission_enabled(
            "external_reasoning_enabled"
        )
        settings_snapshot = runtime_settings_store.snapshot()
        usage_snapshot = provider_usage_store.snapshot()
        model_availability, _, model_remediation, model_ready = OSDiagnosticsExecutor._model_status_details()

        last_used = ""
        last_outcome = ""
        last_request_id = ""
        last_provider = "DeepSeek"
        last_route = "Governed second-opinion lane"
        last_mode = "second_opinion"
        reasoning_summary_line = ""
        top_issue = ""
        top_correction = ""

        try:
            from src.ledger.writer import LEDGER_PATH

            path = Path(LEDGER_PATH)
            if path.exists():
                raw_lines = path.read_text(encoding="utf-8").splitlines()
                for raw_line in reversed(raw_lines):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    try:
                        capability_id = int(entry.get("capability_id") or 0)
                    except Exception:
                        capability_id = 0
                    if capability_id != 62:
                        continue
                    event_type = str(entry.get("event_type") or "").strip().upper()
                    if event_type not in {"ACTION_COMPLETED", "ACTION_ATTEMPTED"}:
                        continue
                    last_used = OSDiagnosticsExecutor._recent_activity_timestamp(
                        str(entry.get("timestamp_utc") or "")
                    )
                    success = entry.get("success")
                    if isinstance(success, bool):
                        last_outcome = "Ready" if success else "Needs attention"
                    else:
                        last_outcome = "Ready"
                    last_request_id = OSDiagnosticsExecutor._recent_activity_request_id(entry)
                    last_provider = str(entry.get("reasoning_provider_label") or entry.get("reasoning_provider") or last_provider).strip() or last_provider
                    last_route = str(entry.get("reasoning_route_label") or entry.get("reasoning_route") or last_route).strip() or last_route
                    last_mode = str(entry.get("reasoning_mode") or last_mode).strip() or last_mode
                    reasoning_summary_line = str(entry.get("reasoning_summary_line") or "").strip()
                    top_issue = str(entry.get("top_issue") or "").strip()
                    top_correction = str(entry.get("top_correction") or "").strip()
                    break
        except Exception:
            pass

        if capability_enabled and model_ready and reasoning_permission_enabled:
            status = "available"
            summary = (
                "Governed second opinion is available. Nova can ask the DeepSeek reasoning lane to review an answer without granting it any execution authority."
            )
        elif capability_enabled and not reasoning_permission_enabled:
            status = "paused"
            summary = (
                "Governed second opinion is paused in Settings. Re-enable it when you want advisory-only review help again."
            )
        elif capability_enabled:
            status = "limited"
            summary = (
                "Governed second opinion is wired in, but the reasoning lane is limited until the current model route is healthy."
            )
        else:
            status = "disabled"
            summary = "Governed second opinion is not enabled in this runtime."

        usage_note = str(usage_snapshot.get("summary") or "").strip()
        if usage_note:
            summary = f"{summary} {usage_note}".strip()

        return {
            "status": status,
            "summary": summary,
            "provider": "DeepSeek",
            "provider_label": last_provider,
            "route": "Governor -> ExternalReasoningExecutor -> DeepSeekBridge -> llm_gateway",
            "route_label": last_route,
            "authority": "analysis_only",
            "authority_label": "Advisory only",
            "capability_id": "62" if capability_enabled else "",
            "mode": last_mode,
            "available": "yes" if capability_enabled and model_ready and reasoning_permission_enabled else "no",
            "switching_note": "Provider switching arrives later. Today's second-opinion lane stays inside Nova's governed route.",
            "governance_note": "Second opinions can critique and clarify, but they cannot execute actions or widen authority.",
            "reasoning_summary_line": reasoning_summary_line,
            "top_issue": top_issue,
            "top_correction": top_correction,
            "settings_permission": "enabled" if reasoning_permission_enabled else "paused",
            "settings_setup_mode": str(settings_snapshot.get("setup_mode_label") or ""),
            "last_used": last_used or "Not used yet",
            "last_outcome": last_outcome or (
                "Available"
                if capability_enabled and reasoning_permission_enabled
                else "Paused"
                if capability_enabled
                else "Not enabled"
            ),
            "last_request_id": last_request_id or "Not recorded",
            "model_status": model_availability,
            "model_remediation": model_remediation,
            "usage_summary": usage_note,
            "usage_measurement_label": str(usage_snapshot.get("measurement_label") or "Estimated tokens"),
            "usage_event_count": int(usage_snapshot.get("event_count") or 0),
            "usage_estimated_total_tokens": int(usage_snapshot.get("estimated_total_tokens") or 0),
            "usage_budget_state": str(usage_snapshot.get("budget_state") or "normal"),
            "usage_budget_state_label": str(usage_snapshot.get("budget_state_label") or "Normal"),
            "usage_budget_remaining_tokens": int(usage_snapshot.get("budget_remaining_tokens") or 0),
            "usage_cost_tracking_label": str(usage_snapshot.get("cost_tracking_label") or "Exact cost tracking is not live yet"),
            "usage_last_event_at": str(usage_snapshot.get("last_event_at") or ""),
            "status_label": (
                "Available"
                if status == "available"
                else "Paused"
                if status == "paused"
                else "Limited"
                if status == "limited"
                else "Disabled"
            ),
        }

    @staticmethod
    def _openai_status_details() -> dict[str, object]:
        settings_snapshot = runtime_settings_store.snapshot()
        permissions = dict(settings_snapshot.get("permissions") or {})
        provider_policy = dict(settings_snapshot.get("provider_policy") or {})
        usage_budget = dict(settings_snapshot.get("usage_budget") or {})
        provider_usage_store.configure_budget(
            daily_token_budget=int(usage_budget.get("daily_metered_token_budget") or 4000),
            warning_ratio=float(usage_budget.get("warning_ratio") or 0.8),
        )
        usage_snapshot = provider_usage_store.snapshot()

        api_key_configured = bool(str(os.getenv("OPENAI_API_KEY", "") or "").strip())
        permission_enabled = bool(permissions.get("metered_openai_enabled"))
        routing_mode = str(provider_policy.get("routing_mode") or "local_first").strip() or "local_first"
        routing_label = str(provider_policy.get("routing_mode_label") or "Local-first").strip() or "Local-first"
        preferred_model = str(provider_policy.get("preferred_openai_model") or "gpt-5.4-mini").strip() or "gpt-5.4-mini"
        preferred_model_label = str(
            provider_policy.get("preferred_openai_model_label") or preferred_model
        ).strip() or preferred_model
        daily_budget = int(usage_budget.get("daily_metered_token_budget") or usage_snapshot.get("budget_tokens") or 0)
        budget_state_label = str(
            usage_snapshot.get("budget_state_label") or "Normal"
        ).strip() or "Normal"

        if api_key_configured and permission_enabled and budget_state_label == "Budget reached":
            status = "limited"
            status_label = "Budget reached"
            summary = (
                f"OpenAI is configured, but today's metered budget has been reached. Nova stays local-first until the budget resets "
                f"or you raise the daily limit."
            )
        elif api_key_configured and permission_enabled:
            status = "available"
            status_label = "Available"
            summary = (
                f"OpenAI is configured as a governed metered lane. Nova still routes local-first, with "
                f"{preferred_model_label} preferred when the OpenAI lane is used."
            )
        elif api_key_configured:
            status = "paused"
            status_label = "Paused"
            summary = (
                "OpenAI is configured but paused in Settings. Nova remains local-first until you explicitly enable the metered lane."
            )
        else:
            status = "not_configured"
            status_label = "Not configured"
            summary = (
                "OpenAI is optional and not configured right now. Nova remains local-first and offline-first unless you add an API key later."
            )

        return {
            "status": status,
            "status_label": status_label,
            "summary": summary,
            "api_key_configured": api_key_configured,
            "settings_permission": "enabled" if permission_enabled else "paused",
            "routing_mode": routing_mode,
            "routing_mode_label": routing_label,
            "preferred_model": preferred_model,
            "preferred_model_label": preferred_model_label,
            "daily_budget_tokens": daily_budget,
            "budget_state_label": budget_state_label,
            "budget_remaining_tokens": int(usage_snapshot.get("budget_remaining_tokens") or 0),
            "token_visibility_label": str(
                usage_snapshot.get("cost_tracking_label") or "Exact cost tracking is not live yet"
            ).strip() or "Exact cost tracking is not live yet",
            "token_summary": str(usage_snapshot.get("summary") or "").strip(),
            "local_first_boundary": (
                "Local tools and local models should be attempted before OpenAI, unless you explicitly choose the metered lane."
            ),
        }

    @staticmethod
    def _bridge_token_value() -> str:
        for key in ("NOVA_OPENCLAW_BRIDGE_TOKEN", "NOVA_BRIDGE_TOKEN"):
            value = str(os.getenv(key, "") or "").strip()
            if value:
                return value
        return ""

    @staticmethod
    def _bridge_status_details() -> dict[str, object]:
        token = OSDiagnosticsExecutor._bridge_token_value()
        bridge_permission_enabled = runtime_settings_store.is_permission_enabled(
            "remote_bridge_enabled"
        )
        token_configured = bool(token)
        enabled = bool(token and bridge_permission_enabled)
        if enabled:
            status = "enabled"
            summary = (
                "OpenClaw bridge is enabled. Token-authenticated remote requests can enter Nova through the governed bridge "
                "without widening execution authority."
            )
        elif token_configured:
            status = "paused"
            summary = (
                "OpenClaw bridge is configured but paused in Settings. Remote requests stay blocked until you re-enable the bridge."
            )
        else:
            status = "disabled"
            summary = "OpenClaw bridge is disabled until a bridge token is configured."
        return {
            "status": status,
            "enabled": enabled,
            "token_configured": token_configured,
            "summary": summary,
            "name": "OpenClaw Bridge",
            "transport": "HTTP",
            "auth": "Token required" if token_configured else "Token not configured",
            "scope": "Read and reasoning only",
            "effectful_actions": "Blocked",
            "continuity": "Stateless stage-1 bridge",
            "endpoint": "/api/openclaw/bridge/message",
            "status_label": (
                "Enabled" if enabled else "Paused" if token_configured else "Disabled"
            ),
            "auth_label": "Configured" if token_configured else "Missing",
            "settings_permission": "enabled" if bridge_permission_enabled else "paused",
        }

    @staticmethod
    def _openclaw_agent_status_details() -> dict[str, object]:
        snapshot = openclaw_agent_runtime_store.snapshot()
        enabled = runtime_settings_store.is_permission_enabled("home_agent_enabled")
        scheduler_enabled = runtime_settings_store.is_permission_enabled("home_agent_scheduler_enabled")
        status = "enabled" if enabled else "paused"
        summary = str(snapshot.get("summary") or "").strip()
        if not enabled:
            summary = (
                "OpenClaw home-agent foundations are paused in Settings. "
                "Manual brief templates stay unavailable until you re-enable them."
            )
        return {
            "status": status,
            "status_label": "Enabled" if enabled else "Paused",
            "enabled": enabled,
            "summary": summary,
            "execution_mode": "Manual foundation only",
            "scheduler_permission_enabled": scheduler_enabled,
            "scheduler_status_label": "Enabled" if scheduler_enabled else "Paused",
            "delivery_model_summary": str(snapshot.get("delivery_model_summary") or "").strip(),
            "delivery_summary": str(snapshot.get("delivery_summary") or "").strip(),
            "delivery_ready_count": int(snapshot.get("delivery_ready_count") or 0),
            "personality_summary": str(snapshot.get("personality_summary") or "").strip(),
            "schedule_summary": str(snapshot.get("schedule_summary") or "").strip(),
            "scheduled_enabled_count": int(snapshot.get("scheduled_enabled_count") or 0),
            "strict_foundation_label": str(snapshot.get("strict_foundation_label") or "").strip(),
            "strict_foundation_summary": str(snapshot.get("strict_foundation_summary") or "").strip(),
            "template_count": int(snapshot.get("template_count") or 0),
            "manual_run_count": int(snapshot.get("manual_run_count") or 0),
            "recent_runs": list(snapshot.get("recent_runs") or [])[:4],
            "settings_permission": "enabled" if enabled else "paused",
        }

    @staticmethod
    def _connection_status_details() -> dict[str, object]:
        model_availability, model_note, _, _ = OSDiagnosticsExecutor._model_status_details()
        reasoning_runtime = OSDiagnosticsExecutor._external_reasoning_status_details()
        openai_runtime = OSDiagnosticsExecutor._openai_status_details()
        bridge_runtime = OSDiagnosticsExecutor._bridge_status_details()
        agent_runtime = OSDiagnosticsExecutor._openclaw_agent_status_details()
        settings_snapshot = runtime_settings_store.snapshot()
        usage_snapshot = provider_usage_store.snapshot()

        configured_keys = [
            label
            for env_name, label in (
                ("OPENAI_API_KEY", "OpenAI"),
                ("ANTHROPIC_API_KEY", "Anthropic"),
                ("DEEPSEEK_API_KEY", "DeepSeek"),
            )
            if str(os.getenv(env_name, "") or "").strip()
        ]

        items = [
            {
                "label": "Setup mode",
                "value": str(settings_snapshot.get("setup_mode_label") or "Local Mode"),
                "note": str(settings_snapshot.get("setup_mode_description") or "").strip(),
            },
            {
                "label": "Local model route",
                "value": model_availability.title(),
                "note": model_note,
            },
            {
                "label": "Governed second opinion",
                "value": str(reasoning_runtime.get("status_label") or reasoning_runtime.get("status") or "Unknown"),
                "note": str(reasoning_runtime.get("summary") or "").strip(),
            },
            {
                "label": "AI routing mode",
                "value": str(openai_runtime.get("routing_mode_label") or "Local-first"),
                "note": str(openai_runtime.get("local_first_boundary") or "").strip(),
            },
            {
                "label": "OpenAI metered lane",
                "value": str(openai_runtime.get("status_label") or "Not configured"),
                "note": str(openai_runtime.get("summary") or "").strip(),
            },
            {
                "label": "OpenAI preferred model",
                "value": str(openai_runtime.get("preferred_model_label") or "GPT-5 mini"),
                "note": "This only affects the optional metered lane. Local-first routing remains the default boundary.",
            },
            {
                "label": "BYO provider keys",
                "value": ", ".join(configured_keys) if configured_keys else "Not configured",
                "note": "Environment-based key detection is live now. In-app key entry arrives later and should stay explicit.",
            },
            {
                "label": "OpenClaw bridge",
                "value": str(bridge_runtime.get("status_label") or "Disabled"),
                "note": str(bridge_runtime.get("summary") or "").strip(),
            },
            {
                "label": "Bridge scope",
                "value": str(bridge_runtime.get("scope") or "Read and reasoning only"),
                "note": "Remote bridge requests stay token-gated and cannot take quiet local actions yet.",
            },
            {
                "label": "Home agent foundation",
                "value": str(agent_runtime.get("status_label") or "Unknown"),
                "note": str(agent_runtime.get("summary") or "").strip(),
            },
            {
                "label": "Agent delivery model",
                "value": str(agent_runtime.get("execution_mode") or "Manual foundation only"),
                "note": str(agent_runtime.get("delivery_model_summary") or "").strip(),
            },
            {
                "label": "Agent scheduler",
                "value": str(agent_runtime.get("scheduler_status_label") or "Paused"),
                "note": str(agent_runtime.get("schedule_summary") or "").strip(),
            },
            {
                "label": "Agent deliveries ready",
                "value": str(int(agent_runtime.get("delivery_ready_count") or 0)),
                "note": str(agent_runtime.get("delivery_summary") or "").strip(),
            },
            {
                "label": "Agent strict foundation",
                "value": str(agent_runtime.get("strict_foundation_label") or "Manual preflight active"),
                "note": str(agent_runtime.get("strict_foundation_summary") or "").strip(),
            },
            {
                "label": "Reasoning usage today",
                "value": f"{int(usage_snapshot.get('estimated_total_tokens') or 0):,} estimated tokens",
                "note": str(usage_snapshot.get("summary") or "").strip(),
            },
            {
                "label": "Usage budget state",
                "value": str(usage_snapshot.get("budget_state_label") or "Normal"),
                "note": str(usage_snapshot.get("cost_tracking_label") or "Exact cost tracking is not live yet"),
            },
            {
                "label": "Metered budget",
                "value": f"{int(openai_runtime.get('daily_budget_tokens') or 0):,} tokens/day",
                "note": "This cap applies only to metered providers such as OpenAI. Local routes stay outside it.",
            },
        ]

        summary_parts = [
            str(settings_snapshot.get("summary") or "").strip(),
            "Local model route is " + model_availability + ".",
            str(openai_runtime.get("summary") or "").strip(),
            ("BYO provider keys are configured." if configured_keys else "BYO provider keys are not configured."),
            str(bridge_runtime.get("summary") or "").strip(),
            str(agent_runtime.get("summary") or "").strip(),
            str(usage_snapshot.get("summary") or "").strip(),
        ]
        return {
            "summary": " ".join(part for part in summary_parts if part).strip(),
            "items": items,
            "configured_provider_count": len(configured_keys),
            "configured_provider_labels": configured_keys,
            "bridge_enabled": bool(bridge_runtime.get("enabled")),
            "setup_mode": str(settings_snapshot.get("setup_mode") or "local"),
            "openai_runtime": openai_runtime,
            "agent_runtime": agent_runtime,
            "usage_runtime": usage_snapshot,
        }

    @staticmethod
    def _blocked_conditions(*, model_availability: str) -> list[dict[str, str]]:
        items = [
            {
                "area": "autonomy",
                "label": "Autonomy",
                "status": "disabled",
                "reason": "Nova remains invocation-bound. Delegated runtime is not active.",
                "next_step": "Use the Policy Review Center for simulations and one-shot review runs.",
            },
            {
                "area": "delegated_trigger_runtime",
                "label": "Delegated trigger runtime",
                "status": "disabled",
                "reason": "Background delegated policy execution is still disabled. Manual review runs are allowed separately.",
                "next_step": "Review drafts in Policies instead of expecting background runs.",
            },
            {
                "area": "background_monitoring",
                "label": "Background monitoring",
                "status": "disabled",
                "reason": "Trigger runtime is not active.",
                "next_step": "Ask explicitly when you want Nova to run a snapshot or review.",
            },
            {
                "area": "wake_word",
                "label": "Wake word",
                "status": "disabled",
                "reason": "Wake-word runtime remains planned, not active.",
                "next_step": "Use push-to-talk or typed commands for now.",
            },
            {
                "area": "external_effect_policies",
                "label": "External-effect delegation",
                "status": "disabled",
                "reason": "Only low-risk delegated classes are candidates for future enablement.",
                "next_step": "Keep effectful actions explicit and user-invoked.",
            },
        ]
        if model_availability == "blocked":
            items.append(
                {
                    "area": "model_inference",
                    "label": "Model inference",
                    "status": "blocked",
                    "reason": "Local inference is locked pending explicit confirmation.",
                    "next_step": "Use local control and review surfaces, then retry once the model is available.",
                }
            )
        return items

    @staticmethod
    def _policy_capability_readiness() -> dict[str, object]:
        try:
            from src.governor.capability_registry import CapabilityRegistry
            from src.governor.capability_topology import CapabilityTopology
        except Exception:
            return {
                "summary": "Capability delegation rules are unavailable right now.",
                "current_authority_limit": "unknown",
                "safe_now": [],
                "allowed_later": [],
                "manual_only": [],
            }

        try:
            topology = CapabilityTopology(CapabilityRegistry())
            safe_now: list[dict[str, str]] = []
            allowed_later: list[dict[str, str]] = []
            manual_only: list[dict[str, str]] = []
            current_limit = str(topology.current_delegated_authority_limit() or "unknown").strip() or "unknown"

            for entry in topology.all_entries():
                row = {
                    "capability_id": str(entry.capability_id),
                    "name": str(entry.name),
                    "authority_class": str(entry.authority_class),
                    "delegation_class": str(entry.delegation_class),
                    "policy_delegatable": "yes" if entry.policy_delegatable else "no",
                    "network_required": "yes" if entry.requires_network_mediator else "no",
                    "persistent_change": "yes" if entry.persistent_change else "no",
                    "external_effect": "yes" if entry.external_effect else "no",
                    "envelope_notes": str(entry.envelope_notes or "").strip(),
                    "within_current_limit": "yes" if topology.is_within_current_limit(entry.capability_id) else "no",
                }
                if entry.policy_delegatable and topology.is_within_current_limit(entry.capability_id):
                    row["why"] = "Safe for review-run now under the current delegated authority limit."
                    safe_now.append(row)
                elif entry.policy_delegatable:
                    row["why"] = "Lawful later, but still above the current delegated authority limit."
                    allowed_later.append(row)
                else:
                    row["why"] = "Remains explicit-user only in the current Phase-6 review model."
                    manual_only.append(row)

            summary = (
                f"{len(safe_now)} capability{'ies' if len(safe_now) != 1 else 'y'} can be review-run now, "
                f"{len(allowed_later)} {'are' if len(allowed_later) != 1 else 'is'} lawful later when delegation widens, "
                f"and {len(manual_only)} remain explicit-user only."
            )
            return {
                "summary": summary,
                "current_authority_limit": current_limit,
                "safe_now": safe_now,
                "allowed_later": allowed_later,
                "manual_only": manual_only,
            }
        except Exception:
            return {
                "summary": "Capability delegation rules are unavailable right now.",
                "current_authority_limit": "unknown",
                "safe_now": [],
                "allowed_later": [],
                "manual_only": [],
            }

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
        policy_capability_readiness = self._policy_capability_readiness()
        reasoning_runtime = self._external_reasoning_status_details()
        bridge_runtime = self._bridge_status_details()
        connection_runtime = self._connection_status_details()
        voice_status, voice_note = self._voice_status_details()
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
            "reasoning_runtime": reasoning_runtime,
            "reasoning_summary": str(reasoning_runtime.get("summary") or "").strip(),
            "bridge_runtime": bridge_runtime,
            "bridge_summary": str(bridge_runtime.get("summary") or "").strip(),
            "connection_runtime": connection_runtime,
            "connection_summary": str(connection_runtime.get("summary") or "").strip(),
            "voice_status": voice_status,
            "voice_note": voice_note,
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
            "policy_capability_readiness": policy_capability_readiness,
            "policy_current_authority_limit": str(
                policy_capability_readiness.get("current_authority_limit") or "unknown"
            ).strip()
            or "unknown",
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
            structured_data=data,
            speakable_text=message,
            request_id=request.request_id,
            authority_class="read_only",
            external_effect=False,
            reversible=True,
        )

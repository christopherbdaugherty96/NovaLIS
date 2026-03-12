from __future__ import annotations

import re
from typing import Any


def infer_task_type(text: str, *, intent_family: str = "") -> str:
    lowered = str(text or "").strip().lower()
    family = str(intent_family or "").strip().lower()

    if any(token in lowered for token in ("help me do this", "help me do it", "walk me through", "guide me through", "what should i click")):
        return "workflow_guidance"
    if any(token in lowered for token in ("download", "installer", "install", "setup")):
        return "software_install"
    if any(token in lowered for token in ("error", "traceback", "exception", "keyerror", "modulenotfounderror")):
        return "error_debugging"
    if any(token in lowered for token in ("chart", "graph", "plot", "trend")):
        return "chart_analysis"
    if any(token in lowered for token in ("file", "document", "pdf", "section")):
        return "document_review"
    if any(token in lowered for token in ("code", "function", "module", "python", "bug")):
        return "code_analysis"
    if family in {"research", "analysis"}:
        return "research"
    if family in {"task", "work", "question", "followup"}:
        return family
    return ""


def infer_step(text: str) -> str:
    lowered = str(text or "").strip().lower()
    if any(token in lowered for token in ("help me do this", "help me do it", "walk me through", "guide me through", "what should i do next", "what should i click")):
        return "execution_guidance"
    if any(token in lowered for token in ("download", "choose", "which one")):
        return "selection"
    if any(token in lowered for token in ("explain", "what is this", "analyze")):
        return "analysis"
    if any(token in lowered for token in ("install", "run installer")):
        return "execution_guidance"
    if any(token in lowered for token in ("error", "traceback")):
        return "diagnosis"
    if any(token in lowered for token in ("summarize", "review")):
        return "summary"
    return ""


def infer_goal_from_turn(text: str) -> str:
    compact = re.sub(r"\s+", " ", str(text or "")).strip()
    if len(compact) <= 220:
        return compact
    return compact[:217].rstrip() + "..."


def snapshot_to_fields(snapshot: dict[str, Any] | None) -> dict[str, str]:
    payload = dict(snapshot or {})
    active_window = dict(payload.get("active_window") or {})
    browser = dict(payload.get("browser") or {})
    system = dict(payload.get("system") or {})

    active_app = str(active_window.get("app") or "").strip()
    active_window_title = str(active_window.get("title") or "").strip()
    active_url = str(browser.get("url") or "").strip()
    page_title = str(browser.get("page_title") or "").strip()
    selected_text = str(browser.get("selected_text") or "").strip()

    cursor_target = page_title or active_window_title
    if not cursor_target and selected_text:
        cursor_target = selected_text

    fields: dict[str, str] = {
        "active_app": active_app,
        "active_window": active_window_title,
        "active_url": active_url,
        "selected_text": selected_text,
        "cursor_target": cursor_target,
    }

    os_name = str(system.get("os") or "").strip()
    os_release = str(system.get("os_release") or "").strip()
    hostname = str(system.get("hostname") or "").strip()
    system_context: dict[str, str] = {}
    if os_name:
        system_context["os"] = os_name
    if os_release:
        system_context["os_release"] = os_release
    if hostname:
        system_context["hostname"] = hostname
    return fields

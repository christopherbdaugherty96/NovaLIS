"""Nova self-awareness context builder.

Generates a dynamic context block that gives Nova real-time knowledge of
its own identity, capabilities, active tools, connected services, and
current status. Injected into the system prompt so the LLM knows what
Nova actually is and can do — not as a static description, but as a
live snapshot of the running system.
"""
from __future__ import annotations

import logging
import platform
import time
from typing import Any

logger = logging.getLogger(__name__)

_boot_time = time.monotonic()

# Cache only the stable/expensive sections so volatile runtime truth stays fresh.
_static_cache: dict[str, Any] = {"sections": None, "expires": 0.0}
_CACHE_TTL = 60.0


def build_self_awareness_block() -> str:
    """Build a compact self-awareness context block for system prompt injection.

    Returns a multi-line string describing Nova's current state, capabilities,
    tools, connections, and model info. Designed to be appended to the system
    prompt so the LLM has accurate self-knowledge.

    Stable capability and tool sections are cached briefly, but volatile
    runtime state is rebuilt every call so this stays truthful.
    """
    sections = _stable_sections()

    # --- Connected services ---
    connections_block = _connections_block()
    if connections_block:
        sections.append(connections_block)

    # --- Model & runtime status ---
    status_block = _status_block()
    if status_block:
        sections.append(status_block)

    return "\n\n".join(sections)


def _stable_sections() -> list[str]:
    """Return cached stable sections that do not need per-message refresh."""
    now = time.monotonic()
    cached_sections = _static_cache.get("sections")
    if cached_sections and now < float(_static_cache.get("expires") or 0.0):
        return list(cached_sections)

    sections: list[str] = [_identity_block()]

    cap_block = _capabilities_block()
    if cap_block:
        sections.append(cap_block)

    tools_block = _tools_block()
    if tools_block:
        sections.append(tools_block)

    _static_cache["sections"] = tuple(sections)
    _static_cache["expires"] = now + _CACHE_TTL
    return list(sections)


def _identity_block() -> str:
    return (
        "WHO YOU ARE RIGHT NOW:\n"
        "You are Nova, running locally on this computer. "
        "You are a real, functioning personal assistant — not a generic chatbot. "
        "The capability list below is an evidence-scoped status view, not authorization. "
        "Never turn existence or enablement into a claim that a capability is configured, verified, "
        "available on the current path, or approved for a request."
    )


def _capabilities_block() -> str:
    """List Governor capabilities using the shared truth projection."""
    try:
        from src.identity.capability_truth import (
            capability_truth_status,
            project_capability_truth,
        )

        caps = project_capability_truth()
    except Exception as exc:
        logger.debug("Could not load capability truth: %s", exc)
        return ""

    if not caps:
        return ""

    # Group by functional category
    groups: dict[str, list[str]] = {
        "Information & Research": [],
        "Device Control": [],
        "Analysis & Intelligence": [],
        "Memory & Continuity": [],
        "Communication": [],
        "System": [],
    }

    for cap in caps:
        name = cap.name.replace("_", " ").title()
        entry = f"{name}: {capability_truth_status(cap)}"

        cid = cap.capability_id
        if cid in (16, 48, 49, 50, 51, 52, 53, 55, 56, 57):
            groups["Information & Research"].append(entry)
        elif cid in (17, 18, 19, 20, 21, 22):
            groups["Device Control"].append(entry)
        elif cid in (31, 54, 58, 59, 60, 62):
            groups["Analysis & Intelligence"].append(entry)
        elif cid in (61,):
            groups["Memory & Continuity"].append(entry)
        elif cid in (63,):
            groups.setdefault("Automation", []).append(entry)
        elif cid in (32,):
            groups["System"].append(entry)
        else:
            groups["System"].append(entry)

    lines = ["YOUR CAPABILITY TRUTH (status evidence; never static authorization):"]
    for group_name, entries in groups.items():
        if entries:
            lines.append(f"  {group_name}:")
            for e in entries:
                lines.append(f"    - {e}")

    return "\n".join(lines)


def _tools_block() -> str:
    """List only tools exposed by the actual OpenClaw freeform allowlist."""
    try:
        from src.openclaw.agent_runner import freeform_goal_allowed_tools
        from src.openclaw.tool_registry import get_tool_registry
        registry = get_tool_registry()
        tools = registry.filtered(allowed=freeform_goal_allowed_tools()).all_capabilities()
    except Exception as exc:
        logger.debug("Could not load tool registry: %s", exc)
        return ""

    if not tools:
        return ""

    lines = ["OPENCLAW FREEFORM TOOLS EXPOSED ON THAT PATH (not authorization):"]
    for name, meta in tools.items():
        desc = meta.get("description", "")
        category = meta.get("category", "")
        lines.append(f"  - {name}: {desc} [{category}]")

    return "\n".join(lines)


def _connections_block() -> str:
    """Show configuration separately from last-known provider health."""
    try:
        from src.connections.connections_store import connections_store
        store = connections_store
        providers = store.snapshot()
    except Exception as exc:
        logger.debug("Could not load connections: %s", exc)
        return ""

    if not providers:
        return ""

    lines = ["YOUR CONNECTION CONFIGURATION (configuration is not capability or authority):"]
    for provider in providers:
        label = str(provider.get("label") or provider.get("id") or "Provider")
        if not provider.get("has_key"):
            state = "not configured"
        elif provider.get("health_ok") is True:
            state = "configured; provider health verified"
        elif provider.get("health_ok") is False:
            state = "configured; provider health check failed"
        else:
            state = "configured; provider health unverified"
        lines.append(f"  - {label}: {state}")

    return "\n".join(lines)


def _status_block() -> str:
    """Current runtime status snapshot."""
    lines = ["YOUR CURRENT STATUS:"]

    # Platform
    lines.append(f"  - Running on: {platform.system()} {platform.release()}")

    # Uptime
    uptime_s = int(time.monotonic() - _boot_time)
    if uptime_s < 60:
        lines.append(f"  - Uptime: {uptime_s}s")
    elif uptime_s < 3600:
        lines.append(f"  - Uptime: {uptime_s // 60}m")
    else:
        lines.append(f"  - Uptime: {uptime_s // 3600}h {(uptime_s % 3600) // 60}m")

    # Model info
    try:
        from src.llm.llm_manager import llm_manager
        model = getattr(llm_manager, "model", "unknown")
        using_fallback = getattr(llm_manager, "_using_fallback", False)
        blocked = getattr(llm_manager, "inference_blocked", False)
        lines.append(f"  - LLM model: {model}" + (" (fallback active)" if using_fallback else ""))
        if blocked:
            lines.append("  - WARNING: Inference is currently blocked (model version mismatch)")
        else:
            lines.append("  - Model status: ready")
    except Exception:
        lines.append("  - Model: loading...")

    # Runtime settings
    try:
        from src.settings.runtime_settings_store import runtime_settings_store
        settings = runtime_settings_store
        home_agent = settings.is_permission_enabled("home_agent_enabled")
        scheduler = settings.is_permission_enabled("home_agent_scheduler_enabled")
        external = settings.is_permission_enabled("external_reasoning_enabled")
        lines.append(f"  - Home agent permission setting: {'enabled' if home_agent else 'disabled'}")
        lines.append(f"  - Scheduler permission setting: {'enabled' if scheduler else 'disabled'}")
        lines.append(
            f"  - External reasoning permission setting: {'enabled' if external else 'disabled'}"
        )
    except Exception:
        pass

    return "\n".join(lines)

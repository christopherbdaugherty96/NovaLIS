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


def build_self_awareness_block() -> str:
    """Build a compact self-awareness context block for system prompt injection.

    Returns a multi-line string describing Nova's current state, capabilities,
    tools, connections, and model info. Designed to be appended to the system
    prompt so the LLM has accurate self-knowledge.
    """
    sections: list[str] = []

    # --- Identity ---
    sections.append(_identity_block())

    # --- Active capabilities ---
    cap_block = _capabilities_block()
    if cap_block:
        sections.append(cap_block)

    # --- Tool registry (OpenClaw agent tools) ---
    tools_block = _tools_block()
    if tools_block:
        sections.append(tools_block)

    # --- Connected services ---
    connections_block = _connections_block()
    if connections_block:
        sections.append(connections_block)

    # --- Model & runtime status ---
    status_block = _status_block()
    if status_block:
        sections.append(status_block)

    return "\n\n".join(sections)


def _identity_block() -> str:
    return (
        "WHO YOU ARE RIGHT NOW:\n"
        "You are Nova, running locally on this computer. "
        "You are a real, functioning personal assistant — not a generic chatbot. "
        "You have actual tools and capabilities you can use. "
        "When someone asks what you can do, tell them from this list — these are real, not hypothetical."
    )


def _capabilities_block() -> str:
    """List active Governor capabilities grouped by function."""
    try:
        from src.governor.capability_registry import CapabilityRegistry
        registry = CapabilityRegistry()
        caps = registry.all_capabilities()
    except Exception as exc:
        logger.debug("Could not load capability registry: %s", exc)
        return ""

    active = [c for c in caps if c.status == "active" and c.enabled]
    if not active:
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

    for cap in active:
        name = cap.name.replace("_", " ").title()
        desc = cap.description[:80] if cap.description else ""
        entry = f"{name}: {desc}" if desc else name

        cid = cap.id
        if cid in (16, 48, 49, 50, 51, 52, 53, 55, 56):
            groups["Information & Research"].append(entry)
        elif cid in (17, 18, 19, 20, 21, 22):
            groups["Device Control"].append(entry)
        elif cid in (31, 54, 58, 59, 60, 62):
            groups["Analysis & Intelligence"].append(entry)
        elif cid in (61,):
            groups["Memory & Continuity"].append(entry)
        elif cid in (32,):
            groups["System"].append(entry)
        else:
            groups["System"].append(entry)

    lines = ["YOUR ACTIVE CAPABILITIES (these are real and working):"]
    for group_name, entries in groups.items():
        if entries:
            lines.append(f"  {group_name}:")
            for e in entries:
                lines.append(f"    - {e}")

    return "\n".join(lines)


def _tools_block() -> str:
    """List OpenClaw agent tools from the tool registry."""
    try:
        from src.openclaw.tool_registry import get_tool_registry
        registry = get_tool_registry()
        tools = registry.all_capabilities()
    except Exception as exc:
        logger.debug("Could not load tool registry: %s", exc)
        return ""

    if not tools:
        return ""

    lines = ["YOUR QUICK-ACCESS TOOLS (you can use these directly):"]
    for name, meta in tools.items():
        desc = meta.get("description", "")
        category = meta.get("category", "")
        lines.append(f"  - {name}: {desc} [{category}]")

    return "\n".join(lines)


def _connections_block() -> str:
    """Show which external services are connected."""
    try:
        from src.connections.connections_store import ConnectionsStore
        store = ConnectionsStore()
        providers = store.snapshot()
    except Exception as exc:
        logger.debug("Could not load connections: %s", exc)
        return ""

    connected = [p for p in providers if p.get("connected")]
    disconnected = [p for p in providers if not p.get("connected")]

    if not connected and not disconnected:
        return ""

    lines = ["YOUR CONNECTIONS:"]
    if connected:
        for p in connected:
            lines.append(f"  - {p['label']}: connected")
    if disconnected:
        names = ", ".join(p["label"] for p in disconnected)
        lines.append(f"  - Not connected: {names}")

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
        from src.settings.runtime_settings_store import RuntimeSettingsStore
        settings = RuntimeSettingsStore()
        home_agent = settings.is_enabled("home_agent_enabled")
        scheduler = settings.is_enabled("home_agent_scheduler_enabled")
        external = settings.is_enabled("external_reasoning_enabled")
        lines.append(f"  - Home agent: {'active' if home_agent else 'off'}")
        lines.append(f"  - Scheduled tasks: {'active' if scheduler else 'off'}")
        lines.append(f"  - External reasoning: {'available' if external else 'off'}")
    except Exception:
        pass

    return "\n".join(lines)

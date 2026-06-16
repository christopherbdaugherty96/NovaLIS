from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RouteProtection:
    prefix: str
    classification: str
    reason: str


LOCAL_ONLY_ROUTE_PROTECTIONS: tuple[RouteProtection, ...] = (
    RouteProtection("/api/goals", "local_only", "Goal persistence is an operator-local planning surface."),
    RouteProtection("/api/memory", "local_only", "Memory endpoints read and mutate durable local memory."),
    RouteProtection("/api/settings", "local_only", "Settings endpoints read and mutate runtime configuration."),
    RouteProtection("/api/trust", "local_only", "Trust receipts expose local execution history."),
    RouteProtection("/api/workspace", "local_only", "Workspace endpoints expose local project context."),
    RouteProtection("/api/openclaw/agent", "local_only", "OpenClaw agent endpoints manage local runs and delivery state."),
    RouteProtection("/api/openclaw/approve-action", "local_only", "Approval stub state must not be remotely reachable."),
    RouteProtection("/api/openclaw/bridge/status", "local_only", "Bridge status exposes settings and connection state."),
    RouteProtection("/api/profile", "local_only", "Profile endpoints persist identity and mirror it into governed memory."),
    RouteProtection("/api/live-screen", "local_only", "Live-screen analysis accepts sensitive screen images."),
    RouteProtection("/api/token/budget", "local_only", "Token budget status exposes local provider usage."),
    RouteProtection("/stt", "local_only", "Speech-to-text accepts sensitive audio uploads."),
    RouteProtection("/phase-status", "local_only", "Phase status exposes runtime governance state."),
    RouteProtection("/system/audit", "local_only", "Runtime audit endpoints expose internal topology."),
)

REMOTE_TOKEN_GATED_ROUTE_PREFIXES: tuple[str, ...] = (
    "/api/openclaw/bridge/message",
)

PUBLIC_ROUTE_PREFIXES: tuple[str, ...] = (
    "/",
    "/landing",
    "/static",
)


def local_only_prefixes() -> tuple[str, ...]:
    return tuple(item.prefix for item in LOCAL_ONLY_ROUTE_PROTECTIONS)


def is_local_only_path(path: str) -> bool:
    clean = str(path or "").strip()
    return clean.startswith(local_only_prefixes())

"""Per-user tool permission layer for OpenClaw.

Controls which tools each user profile can access, integrated with
the Governor's authority model. Permissions are additive: a tool is
allowed only if explicitly granted (deny-by-default).

Design constraints:
  - Governor remains the ultimate execution authority
  - Permissions are checked before tool execution, not after
  - Default profile allows the safe baseline tools (weather, calendar, news)
  - Custom profiles can expand or restrict tool access
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# Permission levels
# ------------------------------------------------------------------

@dataclass
class ToolPermission:
    """Permission entry for a single tool."""
    tool_name: str
    allowed: bool = True
    max_calls_per_run: int = -1  # -1 = unlimited
    requires_confirmation: bool = False


@dataclass
class UserToolProfile:
    """A user's complete tool permission set."""
    user_id: str
    profile_name: str = "default"
    permissions: dict[str, ToolPermission] = field(default_factory=dict)
    deny_unlisted: bool = True  # If True, tools not in permissions dict are denied

    def is_allowed(self, tool_name: str) -> bool:
        perm = self.permissions.get(tool_name)
        if perm is None:
            return not self.deny_unlisted
        return perm.allowed

    def needs_confirmation(self, tool_name: str) -> bool:
        perm = self.permissions.get(tool_name)
        if perm is None:
            return False
        return perm.requires_confirmation

    def call_limit(self, tool_name: str) -> int:
        perm = self.permissions.get(tool_name)
        if perm is None:
            return -1
        return perm.max_calls_per_run


# ------------------------------------------------------------------
# Default profiles
# ------------------------------------------------------------------

_DEFAULT_SAFE_TOOLS = ("weather", "calendar", "news")


def default_profile(user_id: str = "default") -> UserToolProfile:
    """Baseline profile: only safe collection tools allowed."""
    return UserToolProfile(
        user_id=user_id,
        profile_name="default",
        permissions={
            name: ToolPermission(tool_name=name, allowed=True)
            for name in _DEFAULT_SAFE_TOOLS
        },
        deny_unlisted=True,
    )


def open_profile(user_id: str = "default") -> UserToolProfile:
    """All tools allowed (for testing / trusted contexts)."""
    return UserToolProfile(
        user_id=user_id,
        profile_name="open",
        permissions={},
        deny_unlisted=False,
    )


# ------------------------------------------------------------------
# Permission checker (stateless, integrates into runner)
# ------------------------------------------------------------------

class UserToolPermissions:
    """Check and enforce per-user tool access.

    Usage:
        perms = UserToolPermissions()
        perms.load_profile(default_profile("user_123"))
        if perms.check("user_123", "weather"):
            # proceed with tool execution
    """

    def __init__(self) -> None:
        self._profiles: dict[str, UserToolProfile] = {}

    def load_profile(self, profile: UserToolProfile) -> None:
        self._profiles[profile.user_id] = profile

    def get_profile(self, user_id: str) -> UserToolProfile | None:
        return self._profiles.get(user_id)

    def check(self, user_id: str, tool_name: str) -> bool:
        """Return True if the user may use this tool."""
        profile = self._profiles.get(user_id)
        if profile is None:
            # No profile loaded — fall back to default (deny unlisted)
            logger.debug("No profile for user '%s', using default", user_id)
            profile = default_profile(user_id)
            self._profiles[user_id] = profile

        return profile.is_allowed(tool_name)

    def check_or_raise(self, user_id: str, tool_name: str) -> None:
        """Raise if the user may not use this tool."""
        if not self.check(user_id, tool_name):
            raise PermissionError(
                f"User '{user_id}' is not permitted to use tool '{tool_name}'"
            )

    def allowed_tools(self, user_id: str, available: list[str]) -> list[str]:
        """Filter a list of tool names to only those this user may access."""
        return [t for t in available if self.check(user_id, t)]

    def summary(self, user_id: str) -> dict[str, Any]:
        profile = self._profiles.get(user_id)
        if profile is None:
            return {"user_id": user_id, "profile": "none_loaded"}
        return {
            "user_id": user_id,
            "profile_name": profile.profile_name,
            "deny_unlisted": profile.deny_unlisted,
            "explicit_permissions": {
                name: {"allowed": p.allowed, "requires_confirmation": p.requires_confirmation}
                for name, p in profile.permissions.items()
            },
        }

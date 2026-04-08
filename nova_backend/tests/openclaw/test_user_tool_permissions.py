import pytest

from src.openclaw.user_tool_permissions import (
    ToolPermission,
    UserToolPermissions,
    UserToolProfile,
    default_profile,
    open_profile,
)


def test_default_profile_allows_safe_tools():
    profile = default_profile("u1")
    assert profile.is_allowed("weather") is True
    assert profile.is_allowed("calendar") is True
    assert profile.is_allowed("news") is True


def test_default_profile_denies_unlisted():
    profile = default_profile("u1")
    assert profile.is_allowed("dangerous_tool") is False


def test_open_profile_allows_everything():
    profile = open_profile("u1")
    assert profile.is_allowed("anything") is True
    assert profile.is_allowed("weather") is True


def test_permissions_check():
    perms = UserToolPermissions()
    perms.load_profile(default_profile("u1"))

    assert perms.check("u1", "weather") is True
    assert perms.check("u1", "stocks") is False


def test_check_or_raise():
    perms = UserToolPermissions()
    perms.load_profile(default_profile("u1"))

    perms.check_or_raise("u1", "weather")  # should not raise
    with pytest.raises(PermissionError, match="not permitted"):
        perms.check_or_raise("u1", "stocks")


def test_auto_creates_default_profile():
    perms = UserToolPermissions()
    # No profile loaded for "new_user"
    assert perms.check("new_user", "weather") is True
    assert perms.check("new_user", "stocks") is False


def test_allowed_tools_filters():
    perms = UserToolPermissions()
    perms.load_profile(default_profile("u1"))

    available = ["weather", "calendar", "news", "stocks", "crypto"]
    allowed = perms.allowed_tools("u1", available)
    assert allowed == ["weather", "calendar", "news"]


def test_custom_profile():
    profile = UserToolProfile(
        user_id="power_user",
        profile_name="custom",
        permissions={
            "weather": ToolPermission(tool_name="weather", allowed=True),
            "stocks": ToolPermission(tool_name="stocks", allowed=True, requires_confirmation=True),
            "news": ToolPermission(tool_name="news", allowed=False),
        },
        deny_unlisted=True,
    )
    assert profile.is_allowed("weather") is True
    assert profile.is_allowed("stocks") is True
    assert profile.is_allowed("news") is False
    assert profile.needs_confirmation("stocks") is True
    assert profile.needs_confirmation("weather") is False


def test_summary():
    perms = UserToolPermissions()
    perms.load_profile(default_profile("u1"))

    s = perms.summary("u1")
    assert s["profile_name"] == "default"
    assert s["deny_unlisted"] is True
    assert "weather" in s["explicit_permissions"]


def test_summary_no_profile():
    perms = UserToolPermissions()
    s = perms.summary("nobody")
    assert s["profile"] == "none_loaded"


def test_call_limit():
    profile = UserToolProfile(
        user_id="u1",
        permissions={
            "weather": ToolPermission(tool_name="weather", max_calls_per_run=5),
        },
    )
    assert profile.call_limit("weather") == 5
    assert profile.call_limit("unknown") == -1

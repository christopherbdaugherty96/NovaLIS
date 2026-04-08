import pytest

from src.openclaw.tool_registry import ToolMetadata, ToolRegistry, get_tool_registry


def test_register_and_lookup():
    reg = ToolRegistry()
    meta = ToolMetadata(
        name="test_tool",
        description="A test tool",
        category="collection",
        tags=("test", "unit"),
    )
    reg.register("test_tool", lambda: "instance", meta)
    assert reg.has("test_tool")
    assert reg.get_metadata("test_tool") is meta
    assert reg.create("test_tool") == "instance"


def test_duplicate_registration_raises():
    reg = ToolRegistry()
    meta = ToolMetadata(name="dup", description="x", category="c")
    reg.register("dup", lambda: None, meta)
    with pytest.raises(ValueError, match="already registered"):
        reg.register("dup", lambda: None, meta)


def test_find_by_tags():
    reg = ToolRegistry()
    reg.register("weather", lambda: None, ToolMetadata(
        name="weather", description="w", category="collection",
        tags=("weather", "forecast"),
    ))
    reg.register("news", lambda: None, ToolMetadata(
        name="news", description="n", category="collection",
        tags=("news", "headlines"),
    ))
    assert reg.find_by_tags("get me the weather today") == ["weather"]
    assert reg.find_by_tags("latest news headlines") == ["news"]
    assert reg.find_by_tags("unrelated query") == []


def test_find_by_category():
    reg = ToolRegistry()
    reg.register("a", lambda: None, ToolMetadata(name="a", description="", category="collection"))
    reg.register("b", lambda: None, ToolMetadata(name="b", description="", category="mutation"))
    assert reg.find_by_category("collection") == ["a"]
    assert reg.find_by_category("mutation") == ["b"]
    assert reg.find_by_category("nonexistent") == []


def test_all_capabilities():
    reg = ToolRegistry()
    reg.register("x", lambda: None, ToolMetadata(
        name="x", description="desc", category="c",
        tags=("a",), timeout_seconds=5.0, is_network_tool=True,
    ))
    caps = reg.all_capabilities()
    assert "x" in caps
    assert caps["x"]["is_network_tool"] is True
    assert caps["x"]["timeout_seconds"] == 5.0


def test_create_unknown_raises():
    reg = ToolRegistry()
    with pytest.raises(KeyError):
        reg.create("nonexistent")


def test_get_metadata_unknown_raises():
    reg = ToolRegistry()
    with pytest.raises(KeyError, match="not registered"):
        reg.get_metadata("nonexistent")


def test_tool_names_returns_registered():
    reg = ToolRegistry()
    reg.register("a", lambda: None, ToolMetadata(name="a", description="", category="c"))
    reg.register("b", lambda: None, ToolMetadata(name="b", description="", category="c"))
    assert set(reg.tool_names) == {"a", "b"}


def test_bootstrap_registry_has_three_skills():
    """The global registry should bootstrap with weather, calendar, news."""
    reg = get_tool_registry()
    assert reg.has("weather")
    assert reg.has("calendar")
    assert reg.has("news")
    assert len(reg.tool_names) >= 3
    # Verify we can create instances
    weather = reg.create("weather")
    assert weather is not None
    calendar = reg.create("calendar")
    assert calendar is not None

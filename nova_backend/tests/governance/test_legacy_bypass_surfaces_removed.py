from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
SESSION_HANDLER_PATH = SRC_ROOT / "websocket" / "session_handler.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def test_llm_manager_vlock_has_no_direct_requests_usage():
    source = _read(SRC_ROOT / "llm" / "llm_manager_vlock.py")
    assert "import requests" not in source
    assert "requests.Session" not in source
    assert "ModelNetworkMediator" in source
    assert "request_json(" in source


def test_legacy_web_search_tool_is_sealed_non_network_shim():
    source = _read(SRC_ROOT / "tools" / "web_search.py")
    assert "from ddgs import DDGS" not in source
    assert "import requests" not in source
    assert "NetworkMediator" not in source
    assert "return None" in source


def test_legacy_web_search_skill_files_are_removed_from_live_runtime():
    # web_search.py now exists as a governed skill routing through WebSearchExecutor
    # (capability 16 via NetworkMediator). Verify it does NOT bypass the mediator.
    if (SRC_ROOT / "skills" / "web_search.py").exists():
        source = _read(SRC_ROOT / "skills" / "web_search.py")
        # Must NOT import requests directly or use DDGS
        assert "import requests" not in source
        assert "from ddgs import DDGS" not in source
        # Must route through the governed executor
        assert "WebSearchExecutor" in source
    assert not (SRC_ROOT / "skills" / "web_search_skill.py").exists()


def test_session_handler_no_longer_tracks_legacy_web_search_skill_names():
    source = _read(SESSION_HANDLER_PATH)
    assert "web_search_skill" not in source

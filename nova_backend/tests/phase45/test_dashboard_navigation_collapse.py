from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CONFIG_PATH = PROJECT_ROOT / "nova_backend" / "static" / "dashboard-config.js"
INDEX_PATH = PROJECT_ROOT / "nova_backend" / "static" / "index.html"
DASHBOARD_PATH = PROJECT_ROOT / "nova_backend" / "static" / "dashboard.js"
CHAT_NEWS_PATH = PROJECT_ROOT / "nova_backend" / "static" / "dashboard-chat-news.js"


def _array_block(source: str, name: str) -> str:
    match = re.search(rf"{name}:\s*\[(.*?)\],", source, re.S)
    assert match, f"{name} not found"
    return match.group(1)


def _pages(block: str) -> set[str]:
    return set(re.findall(r'page:\s*"([^"]+)"', block))


def test_primary_navigation_is_collapsed_to_default_user_surfaces():
    source = CONFIG_PATH.read_text(encoding="utf-8")

    primary_pages = _pages(_array_block(source, "PRIMARY_NAV_ITEMS"))

    assert primary_pages == {"home", "chat", "goals", "news", "settings"}
    assert not {"agent", "policy", "trust"}.intersection(primary_pages)


def test_internal_surfaces_are_reachable_from_settings_advanced():
    source = CONFIG_PATH.read_text(encoding="utf-8")
    html = INDEX_PATH.read_text(encoding="utf-8")
    chat_news = CHAT_NEWS_PATH.read_text(encoding="utf-8")

    advanced_pages = _pages(_array_block(source, "ADVANCED_NAV_ITEMS"))

    assert {"agent", "policy", "trust"}.issubset(advanced_pages)
    assert 'class="settings-advanced-card"' in html
    assert 'id="btn-settings-open-trust"' in html
    assert 'id="btn-settings-open-agent"' in html
    assert 'id="btn-settings-open-rules"' in html
    assert 'setActivePage("trust")' in chat_news
    assert 'setActivePage("agent")' in chat_news
    assert 'setActivePage("policy")' in chat_news


def test_secondary_navigation_is_not_injected_by_default():
    source = DASHBOARD_PATH.read_text(encoding="utf-8")

    assert "secondary-nav-btn" not in source
    assert "nav-separator" not in source

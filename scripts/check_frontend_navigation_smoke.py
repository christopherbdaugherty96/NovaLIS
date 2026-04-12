from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
INDEX_HTML = ROOT / "nova_backend" / "static" / "index.html"
CONFIG_JS = ROOT / "nova_backend" / "static" / "dashboard-config.js"
CHAT_NEWS_JS = ROOT / "nova_backend" / "static" / "dashboard-chat-news.js"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_button_ids(html: str) -> set[str]:
    return set(re.findall(r'<button[^>]*id="([^"]+)"', html))


def extract_page_sections(html: str) -> set[str]:
    return set(re.findall(r'<section id="page-([a-z]+)"', html))


def extract_primary_nav_pages(js: str) -> list[str]:
    match = re.search(r"PRIMARY_NAV_ITEMS:\s*\[(.*?)\],\s*MORNING_FALLBACK_TIMEOUT_MS", js, re.S)
    if not match:
        raise AssertionError("Could not locate PRIMARY_NAV_ITEMS in dashboard-config.js")
    return re.findall(r'page:\s*"([^"]+)"', match.group(1))


def extract_dom_lookups(js: str) -> set[str]:
    return set(re.findall(r'\$\("([^"]+)"\)', js))


def extract_quick_action_switch_targets(js: str) -> set[str]:
    return set(re.findall(r'switchToPage:\s*"([^"]+)"', js))


def assert_contains(text: str, needle: str, message: str) -> None:
    if needle not in text:
        raise AssertionError(message)


def main() -> None:
    html = read_text(INDEX_HTML)
    config_js = read_text(CONFIG_JS)
    chat_news_js = read_text(CHAT_NEWS_JS)
    all_static_js = "\n".join(
        read_text(path) for path in sorted((ROOT / "nova_backend" / "static").glob("*.js"))
    )

    ids = extract_button_ids(html)
    page_sections = extract_page_sections(html)
    nav_pages = extract_primary_nav_pages(config_js)
    lookups = extract_dom_lookups(all_static_js)
    switch_targets = extract_quick_action_switch_targets(config_js)

    expected_pages = {
        "chat",
        "news",
        "intro",
        "home",
        "agent",
        "workspace",
        "memory",
        "policy",
        "trust",
        "settings",
    }

    missing_pages = expected_pages - page_sections
    if missing_pages:
        raise AssertionError(f"Missing page sections in index.html: {sorted(missing_pages)}")

    if set(nav_pages) != expected_pages:
        raise AssertionError(
            f"Primary nav pages do not match expected pages. Found={sorted(set(nav_pages))}"
        )

    invalid_switch_targets = switch_targets - expected_pages
    if invalid_switch_targets:
        raise AssertionError(
            f"Quick action switchToPage targets are invalid: {sorted(invalid_switch_targets)}"
        )

    missing_button_bindings = ids - lookups
    if missing_button_bindings:
        raise AssertionError(
            f"Button ids exist in index.html without matching JS lookup coverage: {sorted(missing_button_bindings)}"
        )

    # Important cross-page buttons that must exist for navigation confidence.
    required_ids = {
        "btn-intro-open-home",
        "btn-intro-open-settings",
        "btn-intro-open-home-ready",
        "btn-home-threads",
        "btn-agent-open-home",
        "btn-trust-center-workspace",
        "btn-settings-open-home",
        "btn-settings-open-intro",
        "btn-settings-open-trust",
        "btn-settings-open-agent",
        "btn-workspace-board-threads",
    }
    missing_ids = required_ids - ids
    if missing_ids:
        raise AssertionError(f"Missing required navigation ids in index.html: {sorted(missing_ids)}")

    if 'id="primary-nav-strip"' not in html:
        raise AssertionError("Missing primary-nav-strip container in index.html")

    # Critical page-switch behavior should keep navigation feeling correct.
    assert_contains(
        chat_news_js,
        'window.scrollTo({ top: 0, left: 0, behavior: "auto" });',
        "setActivePage no longer resets window scroll to the top.",
    )
    assert_contains(
        chat_news_js,
        'if (main) main.scrollTop = 0;',
        "setActivePage no longer resets main container scroll to the top.",
    )

    # High-value page buttons should keep their intended destination/command behavior.
    required_behavior_snippets = {
        "btn-intro-open-home": 'setActivePage("home")',
        "btn-intro-open-settings": 'setActivePage("settings")',
        "btn-intro-open-home-ready": 'setActivePage("home")',
        "btn-home-threads": 'injectUserText("show threads", "text")',
        "btn-agent-open-home": 'setActivePage("home")',
        "btn-trust-center-workspace": 'setActivePage("workspace")',
        "btn-trust-center-memory": 'setActivePage("memory")',
        "btn-trust-center-agent": 'setActivePage("agent")',
        "btn-settings-open-home": 'setActivePage("home")',
        "btn-settings-open-intro": 'setActivePage("intro")',
        "btn-settings-open-trust": 'setActivePage("trust")',
        "btn-settings-open-agent": 'setActivePage("agent")',
        "btn-workspace-board-threads": 'injectUserText("show threads", "text")',
    }
    for button_id, snippet in required_behavior_snippets.items():
        if button_id in ids:
            assert_contains(
                chat_news_js,
                f'$("{button_id}")',
                f"{button_id} exists in index.html but is not looked up in dashboard-chat-news.js.",
            )
            assert_contains(
                chat_news_js,
                snippet,
                f"Expected behavior snippet missing for {button_id}: {snippet}",
            )

    # Buttons removed from the DOM should not still have JS bindings.
    stale_ids = {
        "btn-home-memory-page",
        "btn-home-open-agent-delivery",
        "btn-home-system-status",
        "btn-intro-voice-check",
        "btn-intro-open-workspace",
        "btn-intro-open-trust",
    }
    stale_lookups = stale_ids & set(re.findall(r'\$\("([^"]+)"\)', chat_news_js))
    if stale_lookups:
        raise AssertionError(f"Stale DOM lookups remain in dashboard-chat-news.js: {sorted(stale_lookups)}")

    print("Frontend navigation smoke check passed.")


if __name__ == "__main__":
    main()

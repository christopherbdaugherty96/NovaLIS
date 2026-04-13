from __future__ import annotations

from tests._dashboard_bundle import load_dashboard_runtime_js


def test_brief_labeled_shortcuts_use_daily_brief_command():
    source = load_dashboard_runtime_js()

    assert '{ label: "Today\'s brief", command: "daily brief" }' in source
    assert '{ label: "Quick brief", command: "summarize all headlines in plain language" }' in source
    assert '{ label: "Start simple", command: "Help me start with one simple step." }' in source


def test_source_grounded_brief_entry_still_uses_todays_news():
    source = load_dashboard_runtime_js()

    assert 'case "news_summary":' in source
    assert 'requestInlineAssistantAction(`summary of article ${storyIndex}`' in source
    assert 'injectUserText("today\'s news", "text")' in source

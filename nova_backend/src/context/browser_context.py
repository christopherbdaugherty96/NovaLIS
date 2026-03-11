from __future__ import annotations

from typing import Any, Mapping


_BROWSER_HINTS = ("chrome", "firefox", "edge", "safari", "brave", "opera")


def get_browser_context(active_window: Mapping[str, Any] | None) -> dict[str, Any]:
    """
    Return browser-oriented metadata from the active window context.

    URL extraction is intentionally conservative in this scaffold build.
    More advanced browser integration can be added later via explicit
    governed capability expansion.
    """
    payload = dict(active_window or {})
    title = str(payload.get("title") or "").strip()
    app = str(payload.get("app") or "").strip()
    combined = f"{app} {title}".lower()
    is_browser = any(token in combined for token in _BROWSER_HINTS)

    return {
        "is_browser": bool(is_browser),
        "url": None,
        "page_title": title if is_browser else "",
        "selected_text": "",
    }

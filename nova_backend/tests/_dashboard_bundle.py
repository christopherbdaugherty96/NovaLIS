from __future__ import annotations

from pathlib import Path


NOVA_BACKEND_ROOT = Path(__file__).resolve().parents[1]
STATIC_ROOT = NOVA_BACKEND_ROOT / "static"
INDEX_HTML_PATH = STATIC_ROOT / "index.html"

RUNTIME_JS_FILES = [
    STATIC_ROOT / "dashboard.js",
    STATIC_ROOT / "dashboard-control-center.js",
    STATIC_ROOT / "dashboard-workspace.js",
    STATIC_ROOT / "dashboard-chat-news.js",
]

RUNTIME_CSS_FILES = [
    STATIC_ROOT / "style.phase1.css",
    STATIC_ROOT / "dashboard-surfaces.css",
]


def _read_bundle(paths: list[Path]) -> str:
    return "\n\n".join(path.read_text(encoding="utf-8") for path in paths)


def load_dashboard_runtime_js() -> str:
    return _read_bundle(RUNTIME_JS_FILES)


def load_dashboard_runtime_css() -> str:
    return _read_bundle(RUNTIME_CSS_FILES)


def load_dashboard_index_html() -> str:
    return INDEX_HTML_PATH.read_text(encoding="utf-8")

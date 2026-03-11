from __future__ import annotations

# Backward-compatible re-export for older imports.
# Canonical implementation lives in src.utils.web_target_planner.
from src.utils.web_target_planner import (  # noqa: F401
    WEB_PRESETS,
    domain_from_url,
    normalize_web_target_text,
    normalize_web_url,
    plan_web_open,
)

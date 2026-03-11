from __future__ import annotations

import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DASHBOARD_PATH = PROJECT_ROOT / "nova_backend" / "static" / "dashboard.js"


# Legacy filename retained by workspace ACL; this contract now validates auto hydration.
def test_websocket_open_hydrates_dashboard_widgets_compat():
    source = DASHBOARD_PATH.read_text(encoding="utf-8")
    match = re.search(r"ws\.onopen\s*=\s*\(\)\s*=>\s*\{(?P<body>.*?)\};", source, flags=re.DOTALL)
    assert match is not None
    body = match.group("body")
    assert "hydrateDashboardWidgets()" in body

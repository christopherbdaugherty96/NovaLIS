from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
INDEX_PATH = PROJECT_ROOT / "nova_backend" / "static" / "index.html"
DASHBOARD_PATH = PROJECT_ROOT / "nova_backend" / "static" / "dashboard.js"
STYLE_PATH = PROJECT_ROOT / "nova_backend" / "static" / "style.phase1.css"


def test_header_uses_single_weather_strip():
    source = INDEX_PATH.read_text(encoding="utf-8")
    assert 'class="header-utility-strip"' in source
    assert 'id="weather-widget"' in source
    assert 'id="news-weather-widget"' not in source


def test_dashboard_renders_header_weather_in_inline_layout():
    source = DASHBOARD_PATH.read_text(encoding="utf-8")
    assert 'const container = $("weather-widget");' in source
    assert 'layout: "header"' in source
    assert 'const newsContainer = $("news-weather-widget");' not in source


def test_styles_define_header_weather_strip_layout():
    source = STYLE_PATH.read_text(encoding="utf-8")
    assert ".header-utility-strip" in source
    assert ".weather-widget-inline" in source
    assert ".header-weather" in source

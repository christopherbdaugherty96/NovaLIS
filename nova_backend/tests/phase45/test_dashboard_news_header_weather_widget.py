from pathlib import Path

from tests._dashboard_bundle import load_dashboard_runtime_css, load_dashboard_runtime_js


PROJECT_ROOT = Path(__file__).resolve().parents[3]
INDEX_PATH = PROJECT_ROOT / "nova_backend" / "static" / "index.html"


def test_header_uses_single_weather_strip():
    source = INDEX_PATH.read_text(encoding="utf-8")
    assert 'class="header-utility-strip"' in source
    assert 'id="weather-widget"' in source
    assert 'id="news-weather-widget"' not in source


def test_dashboard_renders_header_weather_in_inline_layout():
    source = load_dashboard_runtime_js()
    assert 'const container = $("weather-widget");' in source
    assert 'layout: "header"' in source
    assert 'const newsContainer = $("news-weather-widget");' not in source


def test_styles_define_header_weather_strip_layout():
    source = load_dashboard_runtime_css()
    assert ".header-utility-strip" in source
    assert ".weather-widget-inline" in source
    assert ".header-weather" in source

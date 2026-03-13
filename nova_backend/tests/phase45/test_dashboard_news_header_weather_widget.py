from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
INDEX_PATH = PROJECT_ROOT / "nova_backend" / "static" / "index.html"
DASHBOARD_PATH = PROJECT_ROOT / "nova_backend" / "static" / "dashboard.js"
STYLE_PATH = PROJECT_ROOT / "nova_backend" / "static" / "style.phase1.css"


def test_news_page_has_compact_weather_widget_in_header():
    source = INDEX_PATH.read_text(encoding="utf-8")
    assert 'class="news-page-header"' in source
    assert 'id="news-weather-widget"' in source


def test_dashboard_renders_compact_news_weather_card():
    source = DASHBOARD_PATH.read_text(encoding="utf-8")
    assert 'const newsContainer = $("news-weather-widget");' in source
    assert 'renderWeatherCard(newsContainer, data, { compact: true, showForecast: true, showAlerts: false })' in source


def test_styles_define_news_header_weather_layout():
    source = STYLE_PATH.read_text(encoding="utf-8")
    assert ".news-page-header" in source
    assert ".news-weather-widget" in source
    assert ".weather-widget-compact" in source

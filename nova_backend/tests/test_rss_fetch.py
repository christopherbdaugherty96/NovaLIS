import asyncio

from src.governor.network_mediator import NetworkMediator
from src.tools.rss_fetch import fetch_rss_headlines


def test_fetch_rss_headlines_parses_summary_and_published(monkeypatch):
    xml = (
        "<rss><channel>"
        "<item>"
        "<title>Market alert</title>"
        "<link>https://example.com/market</link>"
        "<description><![CDATA[<p>Stocks <b>slipped</b> after policy remarks.</p>]]></description>"
        "<pubDate>Mon, 09 Mar 2026 05:30:00 GMT</pubDate>"
        "</item>"
        "</channel></rss>"
    )

    def _fake_request(self, capability_id, method, url, json_payload=None, params=None, headers=None, **kwargs):
        return {"status_code": 200, "text": xml}

    monkeypatch.setattr(NetworkMediator, "request", _fake_request)
    items = asyncio.run(fetch_rss_headlines("https://example.com/rss"))
    assert len(items) == 1
    assert items[0]["title"] == "Market alert"
    assert items[0]["url"] == "https://example.com/market"
    assert items[0]["summary"] == "Stocks slipped after policy remarks."
    assert items[0]["published"] == "Mon, 09 Mar 2026 05:30:00 GMT"


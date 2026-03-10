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
        assert headers is not None
        assert "User-Agent" in headers
        return {"status_code": 200, "text": xml}

    monkeypatch.setattr(NetworkMediator, "request", _fake_request)
    items = asyncio.run(fetch_rss_headlines("https://example.com/rss"))
    assert len(items) == 1
    assert items[0]["title"] == "Market alert"
    assert items[0]["url"] == "https://example.com/market"
    assert items[0]["summary"] == "Stocks slipped after policy remarks."
    assert items[0]["published"] == "Mon, 09 Mar 2026 05:30:00 GMT"
    assert items[0]["video_url"] == ""


def test_fetch_rss_headlines_atom_prefers_alternate_link(monkeypatch):
    atom = (
        '<feed xmlns="http://www.w3.org/2005/Atom">'
        "<entry>"
        "<title>Policy update</title>"
        '<link rel="self" href="https://example.com/self"/>'
        '<link rel="alternate" href="https://example.com/story"/>'
        "<summary>Short summary text.</summary>"
        "<updated>2026-03-09T06:00:00Z</updated>"
        "</entry>"
        "</feed>"
    )

    def _fake_request(self, capability_id, method, url, json_payload=None, params=None, headers=None, **kwargs):
        del capability_id, method, url, json_payload, params, headers, kwargs
        return {"status_code": 200, "text": atom}

    monkeypatch.setattr(NetworkMediator, "request", _fake_request)
    items = asyncio.run(fetch_rss_headlines("https://example.com/atom.xml"))
    assert len(items) == 1
    assert items[0]["title"] == "Policy update"
    assert items[0]["url"] == "https://example.com/story"


def test_fetch_rss_headlines_extracts_video_url_from_enclosure(monkeypatch):
    xml = (
        "<rss><channel>"
        "<item>"
        "<title>Briefing with video</title>"
        "<link>https://example.com/briefing</link>"
        '<enclosure url="https://cdn.example.com/briefing.mp4" type="video/mp4" />'
        "<description>Video available.</description>"
        "</item>"
        "</channel></rss>"
    )

    def _fake_request(self, capability_id, method, url, json_payload=None, params=None, headers=None, **kwargs):
        del capability_id, method, url, json_payload, params, headers, kwargs
        return {"status_code": 200, "text": xml}

    monkeypatch.setattr(NetworkMediator, "request", _fake_request)
    items = asyncio.run(fetch_rss_headlines("https://example.com/rss"))
    assert len(items) == 1
    assert items[0]["video_url"] == "https://cdn.example.com/briefing.mp4"

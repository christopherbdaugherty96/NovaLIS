# src/tools/rss_fetch.py

import asyncio
import xml.etree.ElementTree as ET
import html
import re
from typing import Dict, Any, List

from src.governor.network_mediator import NetworkMediator
from src.governor.exceptions import NetworkMediatorError

NETWORK_CAPABILITY_ID = 16
SUMMARY_CHAR_LIMIT = 260
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")
_RSS_HEADERS = {
    "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml;q=0.9, */*;q=0.8",
    "User-Agent": "Nova/1.0 (+https://local.nova)",
}


def _clean_text(value: str) -> str:
    raw = str(value or "")
    if not raw:
        return ""
    raw = raw.replace("<![CDATA[", "").replace("]]>", "")
    raw = html.unescape(raw)
    raw = _HTML_TAG_RE.sub(" ", raw)
    raw = _WS_RE.sub(" ", raw).strip()
    if len(raw) > SUMMARY_CHAR_LIMIT:
        raw = raw[: SUMMARY_CHAR_LIMIT - 3].rstrip() + "..."
    return raw


def _clean_url(value: str) -> str:
    raw = html.unescape(str(value or "")).strip()
    raw = _WS_RE.sub("", raw)
    if raw.startswith("//"):
        raw = f"https:{raw}"
    return raw


def _append_unique_result(results: list[dict], seen: set[str], payload: dict) -> None:
    title = str(payload.get("title") or "").strip()
    url = _clean_url(payload.get("url") or "")
    if not title or not url:
        return
    key = url.lower()
    if key in seen:
        return
    seen.add(key)
    results.append(
        {
            "title": title,
            "url": url,
            "summary": _clean_text(payload.get("summary") or ""),
            "published": str(payload.get("published") or "").strip(),
        }
    )


async def fetch_rss_headlines(
    feed_url: str,
    timeout: float = 8.0,
    network: NetworkMediator | None = None,
) -> List[Dict[str, Any]]:
    """
    Fetch and parse an RSS or Atom feed.

    Phase-4 Admission change:
    - All outbound HTTP routed through NetworkMediator (no direct httpx).

    Returns:
        [
            {"title": str, "url": str},
            ...
        ]
    """
    mediator = network or NetworkMediator()

    try:
        resp = await asyncio.to_thread(
            mediator.request,
            NETWORK_CAPABILITY_ID,
            "GET",
            feed_url,
            None,   # json_payload
            None,   # params
            dict(_RSS_HEADERS),
            as_json=False,  # RSS is XML/text
            timeout=timeout,
        )
        text = resp.get("text", "")
        if not text:
            return []
    except NetworkMediatorError:
        return []

    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return []

    # ----------------------------
    # RSS (<channel><item>)
    # ----------------------------
    items = root.findall(".//item")
    results: List[Dict[str, Any]] = []
    seen_urls: set[str] = set()

    for item in items:
        title = item.findtext("title")
        link = item.findtext("link") or item.findtext("guid")
        description = (
            item.findtext("description")
            or item.findtext("{http://purl.org/rss/1.0/modules/content/}encoded")
            or ""
        )
        published = (
            item.findtext("pubDate")
            or item.findtext("{http://purl.org/dc/elements/1.1/}date")
            or ""
        )
        _append_unique_result(
            results,
            seen_urls,
            {
                "title": str(title or "").strip(),
                "url": str(link or "").strip(),
                "summary": description,
                "published": published,
            },
        )

    # ----------------------------
    # Atom (<entry>)
    # ----------------------------
    if not results:
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall(".//atom:entry", ns)
        for entry in entries:
            title = entry.findtext("atom:title", default="", namespaces=ns).strip()
            href = ""
            for link_el in entry.findall("atom:link", ns):
                candidate = _clean_url(link_el.get("href") or "")
                if not candidate:
                    continue
                rel = str(link_el.get("rel") or "").strip().lower()
                if rel in {"", "alternate"}:
                    href = candidate
                    break
                if not href:
                    href = candidate
            if title and href:
                summary = entry.findtext("atom:summary", default="", namespaces=ns)
                if not summary:
                    summary = entry.findtext("atom:content", default="", namespaces=ns)
                published = (
                    entry.findtext("atom:updated", default="", namespaces=ns)
                    or entry.findtext("atom:published", default="", namespaces=ns)
                )
                _append_unique_result(
                    results,
                    seen_urls,
                    {
                        "title": title,
                        "url": href,
                        "summary": summary,
                        "published": published,
                    },
                )

    return results


# ------------------------------------------------------------
# Stable public alias (do not remove)
# ------------------------------------------------------------
fetch_rss = fetch_rss_headlines

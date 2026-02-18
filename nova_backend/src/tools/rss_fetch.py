# src/tools/rss_fetch.py

import asyncio
import xml.etree.ElementTree as ET
from typing import Dict, Any, List

from src.governor.network_mediator import network_mediator
from src.governor.exceptions import NetworkMediatorError


async def fetch_rss_headlines(
    feed_url: str,
    timeout: float = 8.0,
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
    try:
        resp = await asyncio.to_thread(
            network_mediator.request,
            None,  # capability_id=None => skill/tool bucket
            "GET",
            feed_url,
            None,   # json_payload
            None,   # params
            None,   # headers
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

    for item in items:
        title = item.findtext("title")
        link = item.findtext("link")
        if title and link:
            results.append({"title": title.strip(), "url": link.strip()})

    # ----------------------------
    # Atom (<entry>)
    # ----------------------------
    if not results:
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall(".//atom:entry", ns)
        for entry in entries:
            title = entry.findtext("atom:title", default="", namespaces=ns).strip()
            link_el = entry.find("atom:link", ns)
            href = (
                link_el.get("href").strip()
                if link_el is not None and link_el.get("href")
                else ""
            )
            if title and href:
                results.append({"title": title, "url": href})

    return results


# ------------------------------------------------------------
# Stable public alias (do not remove)
# ------------------------------------------------------------
fetch_rss = fetch_rss_headlines
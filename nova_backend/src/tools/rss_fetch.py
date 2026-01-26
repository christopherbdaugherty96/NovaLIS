import httpx
import xml.etree.ElementTree as ET
from typing import Dict, Any, List


async def fetch_rss_headlines(
    feed_url: str,
    timeout: float = 8.0
) -> List[Dict[str, Any]]:
    """
    Fetch and parse an RSS or Atom feed.

    Returns:
        [
            {"title": str, "url": str},
            ...
        ]
    """
    async with httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=True
    ) as client:
        response = await client.get(feed_url)
        response.raise_for_status()
        text = response.text

    root = ET.fromstring(text)

    # ----------------------------
    # RSS (<channel><item>)
    # ----------------------------
    items = root.findall(".//item")
    results: List[Dict[str, Any]] = []

    for item in items:
        title = item.findtext("title")
        link = item.findtext("link")

        if title and link:
            results.append({
                "title": title.strip(),
                "url": link.strip()
            })

    # ----------------------------
    # Atom (<entry>)
    # ----------------------------
    if not results:
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall(".//atom:entry", ns)

        for entry in entries:
            title = entry.findtext(
                "atom:title",
                default="",
                namespaces=ns
            ).strip()

            link_el = entry.find("atom:link", ns)
            href = (
                link_el.get("href").strip()
                if link_el is not None and link_el.get("href")
                else ""
            )

            if title and href:
                results.append({
                    "title": title,
                    "url": href
                })

    return results


# ------------------------------------------------------------
# Stable public alias (do not remove)
# ------------------------------------------------------------

fetch_rss = fetch_rss_headlines

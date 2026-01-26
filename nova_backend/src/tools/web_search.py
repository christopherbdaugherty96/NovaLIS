"""
NovaLIS Web Search Tool

Provides lightweight, on-demand web search results.

Intended use:
- NewsSkill v1 (headline discovery)
- Future Research / Browse modes (permission-based)

Design constraints:
- Stateless
- Read-only
- No background execution
- No memory writes
- No autonomy
"""

import logging
from typing import List, Dict, Optional

from ddgs import DDGS

logger = logging.getLogger("novalis.web_search")


# ==================== PUBLIC API ====================

def run_web_search(
    query: str,
    max_results: int = 3,
) -> Optional[List[Dict[str, str]]]:
    """
    Execute a simple web search.

    Returns:
        A list of normalized results:
        { title, snippet, url }
    """
    query = (query or "").strip()
    if len(query) < 2:
        return None

    try:
        with DDGS() as ddgs:
            raw = list(ddgs.text(query, max_results=max_results))

        if not raw:
            return None

        return _normalize_results(raw)

    except Exception as e:
        logger.debug(f"Web search failed for '{query}': {e}")
        return None


def get_structured_results(
    query: str,
    max_results: int = 1,
) -> Optional[List[Dict[str, str]]]:
    """
    Return structured results for UI usage.

    Derived from run_web_search to avoid duplicate requests.
    Each result contains:
        { title, url }
    """
    results = run_web_search(query, max_results=max_results)
    if not results:
        return None

    structured = []

    for r in results:
        title = r.get("title")
        url = r.get("url")

        if title and url:
            structured.append({
                "title": title,
                "url": url,
            })

    return structured or None


# ==================== INTERNAL HELPERS ====================

def _normalize_results(raw: List[Dict]) -> List[Dict[str, str]]:
    """
    Normalize raw DuckDuckGo results into a predictable structure.
    """
    normalized: List[Dict[str, str]] = []

    for r in raw:
        title = (r.get("title") or "").strip()
        snippet = (r.get("body") or "").strip()
        url = (r.get("href") or "").strip()

        if not title or not url:
            continue

        normalized.append({
            "title": title,
            "snippet": snippet,
            "url": url,
        })

    return normalized

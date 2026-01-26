"""
Deterministic fallback for NewsSkill when RSS fails.

Rules:
- One query
- One result
- No summaries
- No inference
- No retries
- No background behavior
"""


def fallback_headline(source_name: str, domain: str) -> dict | None:
    """
    Return exactly one headline from a trusted source
    when RSS is unavailable.

    This function must remain:
    - deterministic
    - stateless
    - side-effect free
    """

    if not source_name or not domain:
        return None

    # 🔒 Optional dependency — must not break skill loading
    try:
        from ddgs import DDGS
    except Exception:
        return None  # Silent, Phase-1 safe failure

    query = f"site:{domain} {source_name} latest news"

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=1))
            if not results:
                return None

            r = results[0]
            title = r.get("title")
            url = r.get("href")

            if title and url:
                return {
                    "title": title,
                    "source": source_name,
                    "url": url,
                }

    except Exception:
        pass

    return None

# src/utils/date_extractor.py

import re
from datetime import datetime
from typing import Optional
from email.utils import parsedate_to_datetime

def extract_publish_date(html: str) -> Optional[datetime]:
    """
    Attempt to extract publication date from HTML meta tags.
    Returns a timezone-aware datetime if found, else None.
    """
    patterns = [
        # <meta property="article:published_time" content="2025-02-18T10:00:00+00:00">
        (r'<meta[^>]+property="article:published_time"[^>]+content="([^"]+)"', 1),
        # <meta name="publication_date" content="2025-02-18">
        (r'<meta[^>]+name="(?:publication_date|date)"[^>]+content="([^"]+)"', 1),
        # <time datetime="2025-02-18">...</time>
        (r'<time[^>]+datetime="([^"]+)"', 1),
        # ISO 8601 in text (fallback)
        (r'\b(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:[+-]\d{2}:?\d{2})?)\b', 1),
    ]

    for pattern, group in patterns:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            date_str = match.group(group)
            try:
                # Try ISO format first
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except ValueError:
                # Try email.utils parsing (handles many formats)
                try:
                    return parsedate_to_datetime(date_str)
                except (TypeError, ValueError):
                    continue
    return None
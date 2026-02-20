# src/utils/content_extractor.py

import re

def extract_text_from_html(html: str, max_chars: int = 5000) -> str:
    """
    Very basic HTML-to-text extraction.
    Removes script/style tags, strips HTML tags, and normalizes whitespace.
    Truncates to max_chars if provided.
    """
    # Remove script and style content
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.IGNORECASE | re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.IGNORECASE | re.DOTALL)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', html)
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    if max_chars and len(text) > max_chars:
        text = text[:max_chars] + '…'
    return text
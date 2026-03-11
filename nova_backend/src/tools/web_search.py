"""
NovaLIS Legacy Web Search Tool (Sealed)

This module is retained for backward import compatibility only.
All live web-search behavior is governed through capability 16 in the Governor.

Constitutional status:
- No direct network access
- No execution authority
- No autonomous behavior
"""

from __future__ import annotations

from typing import List, Dict, Optional


def run_web_search(
    query: str,
    max_results: int = 3,
) -> Optional[List[Dict[str, str]]]:
    """
    Deprecated shim.

    Returns `None` to indicate that this legacy path is sealed.
    Use governed runtime command routing (`search for ...`) instead.
    """
    _ = (query, max_results)
    return None


def get_structured_results(
    query: str,
    max_results: int = 1,
) -> Optional[List[Dict[str, str]]]:
    """
    Deprecated shim for older callsites.

    Returns `None` because governed search is handled by capability 16.
    """
    _ = (query, max_results)
    return None

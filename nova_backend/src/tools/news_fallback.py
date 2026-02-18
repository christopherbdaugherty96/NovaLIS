"""
Deterministic fallback for NewsSkill when RSS fails.

Phase-4 safety: Fallback web-search is DISABLED.
Rationale: Any fallback that performs unmanaged outbound traffic
violates NetworkMediator unification + no implicit alternate path.
"""


def fallback_headline(source_name: str, domain: str) -> dict | None:
    """
    Return exactly one headline from a trusted source
    when RSS is unavailable.

    This function must remain:
    - deterministic
    - stateless
    - side-effect free

    Phase-4: Always returns None (fallback disabled) to avoid
    unmediated network calls.
    """
    # Fallback is disabled to maintain unified network authority.
    # No attempt is made to fetch from the web.
    return None
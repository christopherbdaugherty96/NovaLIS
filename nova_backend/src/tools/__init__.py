"""
NovaLIS Tools Package

This package contains stateless, replaceable helper utilities used by skills.

Design rules:
- Tools perform no autonomous actions
- Tools do not maintain memory or state
- Tools may access external services, but only when explicitly invoked
- Importing this package must never trigger side effects

This file intentionally contains no executable code.
"""

__all__ = []

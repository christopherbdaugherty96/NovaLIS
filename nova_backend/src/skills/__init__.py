"""
NovaLIS Backend Package

This package contains the authoritative backend implementation for NovaLIS,
including:

- brain_server (routing and control)
- skill system (deterministic capabilities)
- tools (external, replaceable helpers)
- configuration and system state

Design principles:
- Local-first
- Event-driven
- Deterministic
- No background autonomy
- No implicit side effects on import

This file intentionally performs no imports or execution.
"""

__app_name__ = "NovaLIS"
__version__ = "1.0.0"
__all__ = []

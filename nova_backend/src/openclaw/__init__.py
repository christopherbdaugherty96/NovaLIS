"""
OpenClaw — Phase 8.0 governed task execution module.

This module is the silent worker layer beneath Nova's personality surface.
Nova presents all results. The user never interacts with OpenClaw directly.

Phase 8.0 scope: manual trigger only, proposal-only, strict mode.
Scheduler and autonomous execution are explicitly deferred to Phase 8.5.
"""
from __future__ import annotations

OPENCLAW_MODULE_VERSION = "0.1.0"
OPENCLAW_PHASE = "8.0"

__all__ = ["OPENCLAW_MODULE_VERSION", "OPENCLAW_PHASE"]

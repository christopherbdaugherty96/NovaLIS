# tests/certification/cap_64_send_email_draft/test_p1_unit.py
"""
Phase 1 — Unit certification for capability 64 (send_email_draft).

This module re-runs the executor unit tests as part of the certification
pipeline. When this capability is locked, CI enforces these pass on every
commit.

The canonical unit tests live in:
  tests/executors/test_send_email_draft_executor.py
We import and re-expose them here so the certification runner sees them.
"""
# Re-export all tests from the canonical unit test module so pytest collects them.
from tests.executors.test_send_email_draft_executor import *  # noqa: F401,F403

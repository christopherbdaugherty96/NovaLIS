# tests/certification/cap_65_shopify_intelligence_report/test_p1_unit.py
"""
Phase 1 — Unit certification for capability 65 (shopify_intelligence_report).

Re-exports the canonical executor unit tests into the certification
pipeline. When this capability is locked, CI enforces these pass on
every commit.

Canonical unit tests:
  tests/executors/test_shopify_intelligence_report_executor.py
"""
from tests.executors.test_shopify_intelligence_report_executor import *  # noqa: F401,F403

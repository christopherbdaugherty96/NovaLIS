# tests/certification/cap_16_governed_web_search/test_p1_unit.py
"""
Phase 1 — Unit certification for capability 16 (governed_web_search).

Maps the canonical executor unit tests into the certification pipeline.
When this capability is locked, CI enforces these pass on every commit.

Canonical unit tests:
  tests/executors/test_web_search_executor.py
  tests/executors/test_web_search_evidence.py
"""
from tests.executors.test_web_search_executor import *  # noqa: F401,F403
from tests.executors.test_web_search_evidence import *  # noqa: F401,F403

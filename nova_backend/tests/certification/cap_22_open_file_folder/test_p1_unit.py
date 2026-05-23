# tests/certification/cap_22_open_file_folder/test_p1_unit.py
"""
Phase 1 — Unit certification for capability 22 (open_file_folder).

Re-exports the canonical executor unit tests into the certification
pipeline. When this capability is locked, CI enforces these pass on
every commit.

Canonical unit tests:
  tests/executors/test_open_folder_executor.py
"""
from tests.executors.test_open_folder_executor import *  # noqa: F401,F403

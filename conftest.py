"""Root pytest bootstrap for repo-level test execution.

Allows `python -m pytest ...` to work from the repository root by ensuring
`nova_backend/` is on sys.path, which exposes the `src` package used
throughout the existing test suite.
"""

from __future__ import annotations

import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parent / "nova_backend"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

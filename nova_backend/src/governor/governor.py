"""
Governor – constitutional authority spine (Phase‑3.5 minimal version).
Owns all execution‑related boundaries.
"""
from __future__ import annotations

from .execute_boundary import ExecuteBoundary

class Governor:
    """
    Minimal Governor for Phase‑3.5.
    Currently only owns the ExecuteBoundary; other dependencies will be added
    in GOV‑003 and GOV‑004.
    """

    def __init__(self):
        self._execute_boundary = ExecuteBoundary()  # No argument needed

    @property
    def execute_boundary(self) -> ExecuteBoundary:
        return self._execute_boundary
"""Runtime audit utilities for NovaLIS."""

from . import runtime_auditor as runtime_auditor
from .runtime_truth_instrumentation import install_runtime_truth_instrumentation

# One stable auditor import path; B1 instrumentation is installed explicitly at
# package initialization so startup generation, scripts, and tests share the
# same truth semantics.
install_runtime_truth_instrumentation(runtime_auditor)

__all__ = ["runtime_auditor"]

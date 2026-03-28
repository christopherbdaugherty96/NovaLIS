# src/governor/execute_boundary.py

"""
ExecuteBoundary – Governor‑owned execution gate.
Phase‑4 staging: enforces global phase gate and manages execution lifecycle.
Timeouts are delegated to NetworkMediator.
"""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from typing import Optional
import sys
import threading

try:
    import resource
except ImportError:  # pragma: no cover - Windows
    resource = None

from src.actions.action_request import ActionRequest
from src.actions.action_result import ActionResult

# Phase‑4 staging flag – True when execution is allowed
GOVERNED_ACTIONS_ENABLED = True

# Resource limits (Phase-4 defaults)
MAX_EXECUTION_TIME = 10
MAX_MEMORY_MB = 100                 # max per-invocation RSS delta
MAX_PROCESS_RSS_MB = 1536           # fail-closed if process is already over this
MAX_CPU_SECONDS = 8.0               # max per-invocation process CPU budget
MAX_CONCURRENT_EXECUTIONS = 1       # boundary-level concurrency cap
MAX_CONCURRENT = MAX_CONCURRENT_EXECUTIONS  # backward-compatible export


class ExecutionCPUExceededError(RuntimeError):
    """Raised when boundary CPU budget is exceeded."""


class ExecuteBoundary:
    """
    Gatekeeper for all execution. Checks the global phase gate and
    provides lifecycle hooks for execution.
    """

    def __init__(self):
        self._start_time: Optional[float] = None
        self._start_rss_mb: Optional[float] = None
        self._start_cpu_seconds: Optional[float] = None
        self._active_executions = 0
        self._release_pending = False
        self._lock = threading.Lock()

    def allow_execution(self) -> bool:
        """
        Called before any action is attempted.
        Returns True if execution is permitted in the current phase.
        """
        if not GOVERNED_ACTIONS_ENABLED:
            return False
        with self._lock:
            return self._active_executions < MAX_CONCURRENT_EXECUTIONS

    def enter_execution(self) -> None:
        """Call at the start of an executor to start timeout and memory baseline."""
        with self._lock:
            if self._active_executions >= MAX_CONCURRENT_EXECUTIONS:
                raise RuntimeError("Execution concurrency cap reached.")
            self._active_executions += 1
        self._start_time = time.time()
        self._start_rss_mb = self._rss_mb()
        self._start_cpu_seconds = self._cpu_seconds()
        current_rss = self._start_rss_mb
        if current_rss is not None and current_rss > MAX_PROCESS_RSS_MB:
            raise MemoryError("Process memory exceeds boundary cap before execution.")

    def exit_execution(self) -> None:
        """Clean up after execution."""
        self._start_time = None
        self._start_rss_mb = None
        self._start_cpu_seconds = None
        with self._lock:
            if self._release_pending:
                return
            if self._active_executions > 0:
                self._active_executions -= 1

    def _release_after_timeout(self, pool: ThreadPoolExecutor, future) -> None:
        with self._lock:
            self._release_pending = True

        def _drain() -> None:
            try:
                future.result()
            except Exception:
                pass
            finally:
                try:
                    pool.shutdown(wait=False, cancel_futures=True)
                finally:
                    self._start_time = None
                    self._start_rss_mb = None
                    self._start_cpu_seconds = None
                    with self._lock:
                        self._release_pending = False
                        if self._active_executions > 0:
                            self._active_executions -= 1

        threading.Thread(target=_drain, daemon=True).start()

    @staticmethod
    def _rss_mb() -> Optional[float]:
        if resource is None:
            return None
        try:
            usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            if sys.platform == "darwin":
                return usage / (1024 * 1024)
            return usage / 1024
        except Exception:
            return None

    @staticmethod
    def _cpu_seconds() -> float:
        # Process CPU time (user + system), cross-platform.
        return float(time.process_time())

    def run_with_timeout(self, operation, timeout_seconds: Optional[float] = None):
        """
        Execute an operation inside the boundary with timeout signaling.

        If the timeout is hit, we return promptly but keep the execution slot
        occupied until the worker thread actually drains.
        """
        timeout = float(timeout_seconds if timeout_seconds is not None else MAX_EXECUTION_TIME)
        pool = ThreadPoolExecutor(max_workers=1)
        future = pool.submit(operation)
        try:
            return future.result(timeout=timeout)
        except FutureTimeoutError as error:
            future.cancel()
            self._release_after_timeout(pool, future)
            raise TimeoutError("Execution exceeded boundary timeout.") from error
        finally:
            if not self._release_pending:
                pool.shutdown(wait=False, cancel_futures=True)

    def enforce_memory_limits(self) -> None:
        """Check post-execution memory ceilings."""
        current = self._rss_mb()
        if current is None:
            return
        if current > MAX_PROCESS_RSS_MB:
            raise MemoryError("Process memory exceeded boundary cap.")
        if self._start_rss_mb is not None and (current - self._start_rss_mb) > MAX_MEMORY_MB:
            raise MemoryError("Execution memory delta exceeded boundary cap.")

    def enforce_cpu_limits(self) -> None:
        """Check post-execution CPU budget."""
        if self._start_cpu_seconds is None:
            return
        cpu_delta = self._cpu_seconds() - self._start_cpu_seconds
        if cpu_delta > MAX_CPU_SECONDS:
            raise ExecutionCPUExceededError("Execution CPU budget exceeded.")

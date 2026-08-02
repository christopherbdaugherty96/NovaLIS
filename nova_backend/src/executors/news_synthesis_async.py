from __future__ import annotations

import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from time import monotonic
from typing import Any, Callable

from src.executors.news_synthesis_cache import cluster_fingerprint

log = logging.getLogger(__name__)

ASYNC_SYNTHESIS_TIMEOUT_SECONDS = 45.0
FAILED_RETRY_COOLDOWN_SECONDS = 10 * 60


@dataclass(frozen=True)
class NewsSynthesisFillResult:
    queued: int = 0
    skipped_active: int = 0
    skipped_failed_cooldown: int = 0
    paused: bool = False


class NewsSynthesisFillQueue:
    """Single-worker, session-triggered cache fill queue for Cap 50 synthesis."""

    def __init__(
        self,
        *,
        max_workers: int = 1,
        inline: bool = False,
        failed_retry_cooldown_seconds: float = FAILED_RETRY_COOLDOWN_SECONDS,
    ) -> None:
        self._inline = bool(inline)
        self._pool = None if self._inline else ThreadPoolExecutor(max_workers=max(1, int(max_workers)))
        self._failed_retry_cooldown_seconds = max(0.0, float(failed_retry_cooldown_seconds))
        self._lock = threading.RLock()
        self._active: set[str] = set()
        self._failed_at: dict[str, float] = {}

    def enqueue(
        self,
        clusters: list[dict[str, Any]],
        *,
        worker: Callable[[dict[str, Any]], dict[str, Any] | None],
        on_ready: Callable[[list[dict[str, Any]]], None] | None = None,
        should_pause: Callable[[], bool] | None = None,
    ) -> NewsSynthesisFillResult:
        if should_pause is not None and should_pause():
            return NewsSynthesisFillResult(paused=True)

        now = monotonic()
        queued: list[dict[str, Any]] = []
        skipped_active = 0
        skipped_failed = 0
        with self._lock:
            for cluster in clusters:
                if not isinstance(cluster, dict):
                    continue
                fingerprint = cluster_fingerprint(cluster)
                if fingerprint in self._active:
                    skipped_active += 1
                    continue
                failed_at = self._failed_at.get(fingerprint)
                if failed_at is not None and (now - failed_at) < self._failed_retry_cooldown_seconds:
                    skipped_failed += 1
                    continue
                self._active.add(fingerprint)
                queued.append(cluster)

        if not queued:
            return NewsSynthesisFillResult(
                queued=0,
                skipped_active=skipped_active,
                skipped_failed_cooldown=skipped_failed,
            )

        if self._inline:
            self._run(queued, worker=worker, on_ready=on_ready, should_pause=should_pause)
        else:
            assert self._pool is not None
            self._pool.submit(self._run, queued, worker=worker, on_ready=on_ready, should_pause=should_pause)

        return NewsSynthesisFillResult(
            queued=len(queued),
            skipped_active=skipped_active,
            skipped_failed_cooldown=skipped_failed,
        )

    def _run(
        self,
        clusters: list[dict[str, Any]],
        *,
        worker: Callable[[dict[str, Any]], dict[str, Any] | None],
        on_ready: Callable[[list[dict[str, Any]]], None] | None,
        should_pause: Callable[[], bool] | None,
    ) -> None:
        completed: list[dict[str, Any]] = []
        try:
            for cluster in clusters:
                fingerprint = cluster_fingerprint(cluster)
                if should_pause is not None and should_pause():
                    with self._lock:
                        self._active.discard(fingerprint)
                    continue
                try:
                    record = worker(cluster)
                except Exception:
                    log.exception("Async news synthesis failed for cluster")
                    record = None
                with self._lock:
                    self._active.discard(fingerprint)
                    if record:
                        self._failed_at.pop(fingerprint, None)
                    else:
                        self._failed_at[fingerprint] = monotonic()
                if record:
                    completed.append(dict(record))
        finally:
            with self._lock:
                for cluster in clusters:
                    self._active.discard(cluster_fingerprint(cluster))

        if completed and on_ready is not None:
            try:
                on_ready(completed)
            except Exception:
                log.exception("Async news synthesis ready callback failed")


news_synthesis_fill_queue = NewsSynthesisFillQueue()

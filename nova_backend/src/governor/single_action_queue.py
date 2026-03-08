# src/governor/single_action_queue.py

import threading


class SingleActionQueue:
    """
    Enforces a single pending action boundary.
    Used by Governor to prevent concurrency.
    """

    def __init__(self):
        self._pending = None
        self._lock = threading.Lock()

    def has_pending(self) -> bool:
        with self._lock:
            return self._pending is not None

    def set_pending(self, action_id: str) -> None:
        """Mark an action as pending. Raises if another action is already pending."""
        with self._lock:
            if self._pending is not None:
                raise RuntimeError("Another action is pending.")
            self._pending = action_id

    def clear(self) -> None:
        with self._lock:
            self._pending = None

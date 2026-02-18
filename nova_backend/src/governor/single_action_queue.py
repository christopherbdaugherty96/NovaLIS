# src/governor/single_action_queue.py

class SingleActionQueue:
    """
    Enforces a single pending action boundary.
    Used by Governor to prevent concurrency.
    """

    def __init__(self):
        self._pending = None

    def has_pending(self) -> bool:
        return self._pending is not None

    def set_pending(self, action_id: str) -> None:
        """Mark an action as pending. Raises if another action is already pending."""
        if self._pending is not None:
            raise RuntimeError("Another action is pending.")
        self._pending = action_id

    def clear(self) -> None:
        self._pending = None
# nova_backend/src/governor/single_action_queue.py

class SingleActionQueue:
    """
    Phase 2.1: Enforces a single pending action boundary.
    This class does NOT execute actions.
    """

    def __init__(self):
        self._pending = None

    def has_pending(self) -> bool:
        return self._pending is not None

    def clear(self):
        self._pending = None

import time
from collections import defaultdict
from typing import Optional


class ThoughtStore:
    def __init__(self, ttl: int = 300):
        self._store = defaultdict(dict)
        self.ttl = ttl

    def put(self, session_id: str, message_id: str, data: dict):
        self._store[session_id][message_id] = {"data": data, "timestamp": time.time()}

    def get(self, session_id: str, message_id: str) -> Optional[dict]:
        entry = self._store.get(session_id, {}).get(message_id)
        if entry and (time.time() - entry["timestamp"]) < self.ttl:
            return entry["data"]
        return None

    def clear_session(self, session_id: str):
        self._store.pop(session_id, None)

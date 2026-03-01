# src/audio/audio_worker.py

import threading
from typing import Callable


def run_background_speech(task: Callable[[], None]) -> None:
    """
    Run a speech task in a background daemon thread.
    This is the only allowed location for threading in the audio layer.
    """
    t = threading.Thread(target=task, daemon=True)
    t.start()
# src/audio/audio_task_runner.py

import threading
from typing import Callable


def run_speech_task(task: Callable[[], None]) -> None:
    """
    Run a speech task in a background daemon thread.
    This is the only allowed location for threading in the audio layer.
    """
    t = threading.Thread(target=task, daemon=True)
    t.start()
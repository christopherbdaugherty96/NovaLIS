from __future__ import annotations

import ctypes
import os
from datetime import datetime
from typing import Any


class WindowsResumeProbe:
    """Detect sleep elapsed time and wait for real console interaction after resume."""

    def __init__(self, *, sleep_gap_seconds: float = 5.0, recent_input_seconds: float = 15.0) -> None:
        self._sleep_gap_seconds = max(1.0, float(sleep_gap_seconds))
        self._recent_input_seconds = max(1.0, float(recent_input_seconds))
        self._last_wall: datetime | None = None
        self._last_working_seconds: float | None = None

    def observe(self, now: datetime) -> dict[str, Any]:
        if os.name != "nt":
            self._last_wall = now
            return {
                "resume_detected": False,
                "user_present": True,
                "display": "on",
                "session": "unlocked",
            }

        working_seconds = self._working_seconds()
        resume_detected = False
        if self._last_wall is not None and self._last_working_seconds is not None:
            wall_elapsed = max(0.0, (now - self._last_wall).total_seconds())
            working_elapsed = max(0.0, working_seconds - self._last_working_seconds)
            resume_detected = wall_elapsed - working_elapsed >= self._sleep_gap_seconds
        self._last_wall = now
        self._last_working_seconds = working_seconds
        user_present = self._seconds_since_input() <= self._recent_input_seconds
        return {
            "resume_detected": resume_detected,
            "user_present": user_present,
            # D1's real-device wake guard treats absence of post-resume input as
            # display-off. Session lock uses a separate Windows desktop probe.
            "display": "off" if resume_detected and not user_present else "on",
            "session": "unlocked" if self._interactive_desktop_available() else "locked",
        }

    @staticmethod
    def _interactive_desktop_available() -> bool:
        open_input_desktop = ctypes.windll.user32.OpenInputDesktop
        open_input_desktop.argtypes = [ctypes.c_uint, ctypes.c_bool, ctypes.c_uint]
        open_input_desktop.restype = ctypes.c_void_p
        desktop = open_input_desktop(0, False, 0x0100)
        if not desktop:
            return False
        try:
            switch_desktop = ctypes.windll.user32.SwitchDesktop
            switch_desktop.argtypes = [ctypes.c_void_p]
            switch_desktop.restype = ctypes.c_bool
            return bool(switch_desktop(desktop))
        finally:
            close_desktop = ctypes.windll.user32.CloseDesktop
            close_desktop.argtypes = [ctypes.c_void_p]
            close_desktop.restype = ctypes.c_bool
            close_desktop(desktop)

    @staticmethod
    def _working_seconds() -> float:
        value = ctypes.c_ulonglong()
        query = ctypes.windll.kernel32.QueryUnbiasedInterruptTime
        query.argtypes = [ctypes.POINTER(ctypes.c_ulonglong)]
        query.restype = ctypes.c_int
        succeeded = query(ctypes.byref(value))
        if not succeeded:
            raise OSError("QueryUnbiasedInterruptTime failed")
        return float(value.value) / 10_000_000.0

    @staticmethod
    def _seconds_since_input() -> float:
        class LASTINPUTINFO(ctypes.Structure):
            _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

        info = LASTINPUTINFO()
        info.cbSize = ctypes.sizeof(info)
        if not ctypes.windll.user32.GetLastInputInfo(ctypes.byref(info)):
            raise OSError("GetLastInputInfo failed")
        get_tick_count = ctypes.windll.kernel32.GetTickCount64
        get_tick_count.restype = ctypes.c_ulonglong
        elapsed_ms = (int(get_tick_count()) - int(info.dwTime)) & 0xFFFFFFFF
        return max(0.0, float(elapsed_ms) / 1000.0)

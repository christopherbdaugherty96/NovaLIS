from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DeepModeState:
    armed: bool = False

    def activate_once(self) -> None:
        self.armed = True

    def consume(self) -> bool:
        was_armed = self.armed
        self.armed = False
        return was_armed

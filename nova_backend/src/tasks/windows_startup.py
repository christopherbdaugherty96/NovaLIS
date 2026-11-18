from __future__ import annotations

import os
from pathlib import Path
from typing import Protocol, Sequence


class StartupRegistry(Protocol):
    def get(self, name: str) -> str | None: ...
    def set(self, name: str, value: str) -> None: ...
    def delete(self, name: str) -> None: ...


class _WindowsRunRegistry:
    _PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"

    def get(self, name: str) -> str | None:
        import winreg

        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self._PATH) as key:
                value, _ = winreg.QueryValueEx(key, name)
                return str(value)
        except FileNotFoundError:
            return None

    def set(self, name: str, value: str) -> None:
        import winreg

        with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, self._PATH, access=winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)

    def delete(self, name: str) -> None:
        import winreg

        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self._PATH, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, name)
        except FileNotFoundError:
            return


class WindowsStartupRegistration:
    ENTRY_NAME = "NovaLIS Reminder Backend"

    def __init__(
        self,
        executable: Path,
        registry: StartupRegistry | None = None,
        *,
        arguments: Sequence[str] = ("--background",),
        legacy_arguments: Sequence[Sequence[str]] = (),
    ) -> None:
        self._executable = Path(executable)
        self._supported = os.name == "nt" or registry is not None
        self._registry = registry or _WindowsRunRegistry()
        self._arguments = tuple(str(value) for value in arguments)
        self._legacy_arguments = tuple(
            tuple(str(value) for value in arguments)
            for arguments in legacy_arguments
        )

    def _command_for(self, arguments: Sequence[str]) -> str:
        path = str(self._executable).replace("/", "\\")
        quoted_arguments = " ".join(
            f'"{value}"' if any(character.isspace() for character in value) else value
            for value in arguments
        )
        return f'"{path}"{f" {quoted_arguments}" if quoted_arguments else ""}'

    @property
    def command(self) -> str:
        return self._command_for(self._arguments)

    @property
    def legacy_commands(self) -> frozenset[str]:
        return frozenset(self._command_for(arguments) for arguments in self._legacy_arguments)

    def migrate_legacy_entry(self) -> dict[str, object]:
        """Replace only exact prior Nova registrations with the current command."""
        if not self._supported:
            return self.status()
        if self._registry.get(self.ENTRY_NAME) in self.legacy_commands:
            self._registry.set(self.ENTRY_NAME, self.command)
        return self.status()

    def status(self) -> dict[str, object]:
        if not self._supported:
            return {
                "supported": False,
                "enabled": False,
                "entry_exists": False,
                "entry_name": self.ENTRY_NAME,
            }
        existing = self._registry.get(self.ENTRY_NAME)
        owned = existing == self.command or existing in self.legacy_commands
        return {
            "supported": True,
            "enabled": owned,
            "entry_exists": existing is not None,
            "entry_name": self.ENTRY_NAME,
            "entry_conflict": existing is not None and not owned,
            "migration_required": existing in self.legacy_commands,
        }

    def set_enabled(self, enabled: bool) -> dict[str, object]:
        if enabled and not self._supported:
            raise ValueError("Start at sign-in is available on Windows only.")
        if not self._supported:
            return self.status()
        if enabled:
            self._registry.set(self.ENTRY_NAME, self.command)
        else:
            existing = self._registry.get(self.ENTRY_NAME)
            if existing == self.command or existing in self.legacy_commands:
                self._registry.delete(self.ENTRY_NAME)
        return self.status()

    def cleanup(self) -> dict[str, object]:
        if not self._supported:
            return self.status()
        existing = self._registry.get(self.ENTRY_NAME)
        if existing == self.command or existing in self.legacy_commands:
            self._registry.delete(self.ENTRY_NAME)
        return self.status()


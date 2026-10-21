from pathlib import Path

from src.tasks.windows_startup import WindowsStartupRegistration


class _Registry:
    def __init__(self):
        self.values = {}

    def get(self, name):
        return self.values.get(name)

    def set(self, name, value):
        self.values[name] = value

    def delete(self, name):
        self.values.pop(name, None)


def test_start_at_sign_in_is_off_by_default_and_exactly_one_entry_is_removable(tmp_path):
    registry = _Registry()
    registration = WindowsStartupRegistration(
        executable=Path("C:/Nova/Nova.exe"),
        registry=registry,
    )

    assert registration.status()["enabled"] is False
    registration.set_enabled(True)
    assert list(registry.values) == ["Nova"]
    assert registry.values["Nova"] == '"C:\\Nova\\Nova.exe" --background'
    assert registration.status()["entry_exists"] is True

    registration.set_enabled(False)
    assert registry.values == {}
    assert registration.status()["enabled"] is False


def test_data_reset_can_remove_startup_entry(tmp_path):
    registry = _Registry()
    registration = WindowsStartupRegistration(Path("C:/Nova/Nova.exe"), registry=registry)
    registration.set_enabled(True)

    registration.cleanup()

    assert registry.values == {}


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
    assert list(registry.values) == ["NovaLIS Reminder Backend"]
    assert registry.values["NovaLIS Reminder Backend"] == '"C:\\Nova\\Nova.exe" --background'
    assert registration.status()["entry_exists"] is True

    registration.set_enabled(False)
    assert registry.values == {}


def test_disable_never_deletes_a_foreign_or_changed_entry():
    registry = _Registry()
    registration = WindowsStartupRegistration(Path("C:/Nova/Nova.exe"), registry=registry)
    registry.values[registration.ENTRY_NAME] = '"C:\\Other\\Nova.exe" --background'

    status = registration.set_enabled(False)

    assert registry.values[registration.ENTRY_NAME] == '"C:\\Other\\Nova.exe" --background'
    assert status["entry_conflict"] is True
    assert registration.status()["enabled"] is False


def test_data_reset_can_remove_startup_entry(tmp_path):
    registry = _Registry()
    registration = WindowsStartupRegistration(Path("C:/Nova/Nova.exe"), registry=registry)
    registration.set_enabled(True)

    registration.cleanup()

    assert registry.values == {}


def test_legacy_startup_entry_is_migrated_and_remains_removable():
    registry = _Registry()
    registration = WindowsStartupRegistration(
        Path("C:/Nova/pythonw.exe"),
        registry=registry,
        arguments=("C:/Nova/scripts/start_daemon.py", "--no-browser", "--automatic-startup"),
        legacy_arguments=(("C:/Nova/scripts/start_daemon.py", "--no-browser"),),
    )
    registry.values[registration.ENTRY_NAME] = (
        '"C:\\Nova\\pythonw.exe" C:/Nova/scripts/start_daemon.py --no-browser'
    )

    assert registration.status()["enabled"] is True
    assert registration.status()["migration_required"] is True

    registration.migrate_legacy_entry()

    assert registry.values[registration.ENTRY_NAME] == registration.command
    assert registration.status()["migration_required"] is False
    registration.set_enabled(False)
    assert registry.values == {}


def test_legacy_migration_does_not_claim_or_remove_foreign_entry():
    registry = _Registry()
    registration = WindowsStartupRegistration(
        Path("C:/Nova/pythonw.exe"),
        registry=registry,
        arguments=("C:/Nova/scripts/start_daemon.py", "--no-browser", "--automatic-startup"),
        legacy_arguments=(("C:/Nova/scripts/start_daemon.py", "--no-browser"),),
    )
    foreign = '"C:\\Other\\pythonw.exe" C:/Nova/scripts/start_daemon.py --no-browser'
    registry.values[registration.ENTRY_NAME] = foreign

    registration.migrate_legacy_entry()
    registration.cleanup()

    assert registry.values[registration.ENTRY_NAME] == foreign
    assert registration.status()["entry_conflict"] is True


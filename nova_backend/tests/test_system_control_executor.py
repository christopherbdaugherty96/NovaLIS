from pathlib import Path

from src.system_control.system_control_executor import SystemControlExecutor


def test_is_allowed_path_accepts_home_subpath():
    executor = SystemControlExecutor()
    candidate = Path.home() / "Documents" / "notes.txt"
    assert executor._is_allowed_path(candidate) is True  # noqa: SLF001


def test_is_allowed_path_rejects_parent_scope():
    executor = SystemControlExecutor()
    candidate = Path.home().parent / "__nova_forbidden_path__" / "secret.txt"
    assert executor._is_allowed_path(candidate) is False  # noqa: SLF001


def test_is_allowed_path_accepts_workspace_root_outside_home(monkeypatch, tmp_path: Path):
    workspace = tmp_path / "workspace"
    backend = workspace / "nova_backend"
    backend.mkdir(parents=True)
    (workspace / ".git").mkdir()

    monkeypatch.setattr("src.system_control.system_control_executor.Path.cwd", classmethod(lambda cls: backend))

    executor = SystemControlExecutor()
    candidate = workspace / "docs"
    candidate.mkdir()

    assert executor._is_allowed_path(candidate) is True  # noqa: SLF001


def test_open_path_uses_workspace_root_allowlist(monkeypatch, tmp_path: Path):
    workspace = tmp_path / "workspace"
    backend = workspace / "nova_backend"
    backend.mkdir(parents=True)
    (workspace / ".git").mkdir()
    target = workspace / "docs"
    target.mkdir()

    monkeypatch.setattr("src.system_control.system_control_executor.Path.cwd", classmethod(lambda cls: backend))
    monkeypatch.setattr("platform.system", lambda: "Windows")

    opened: list[str] = []

    def _fake_startfile(value: str) -> None:
        opened.append(value)

    monkeypatch.setattr("os.startfile", _fake_startfile)

    executor = SystemControlExecutor()
    assert executor.open_path(target) is True
    assert opened == [str(target)]


def test_media_and_brightness_fail_closed_on_unknown_platform(monkeypatch):
    executor = SystemControlExecutor()
    monkeypatch.setattr("platform.system", lambda: "UnknownOS")

    assert executor.control_media("play") is False
    assert executor.set_volume("mute") is False
    assert executor.set_brightness("up") is False

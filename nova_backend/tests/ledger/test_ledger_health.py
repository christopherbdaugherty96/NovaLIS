from __future__ import annotations

from pathlib import Path

from src.ledger.health import inspect_ledger_health, is_package_data_path


def test_inspect_ledger_health_recommends_rotation_when_threshold_exceeded(tmp_path):
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_bytes(b"x" * 11)

    health = inspect_ledger_health(ledger, rotation_threshold_bytes=10)

    assert health.exists is True
    assert health.size_bytes == 11
    assert health.rotation_recommended is True
    assert health.as_dict()["rotation_recommended"] is True


def test_inspect_ledger_health_does_not_create_missing_ledger(tmp_path):
    ledger = tmp_path / "missing-ledger.jsonl"

    health = inspect_ledger_health(ledger, rotation_threshold_bytes=10)

    assert health.exists is False
    assert health.size_bytes == 0
    assert health.rotation_recommended is False
    assert ledger.exists() is False


def test_package_data_path_flags_current_default_layout():
    path = Path("C:/Nova-Project/nova_backend/src/data/ledger.jsonl")

    assert is_package_data_path(path) is True


def test_runtime_directory_path_is_not_package_data():
    path = Path("C:/Users/Chris/AppData/Local/Nova/data/ledger.jsonl")

    assert is_package_data_path(path) is False

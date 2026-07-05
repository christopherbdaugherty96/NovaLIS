from __future__ import annotations

from pathlib import Path


def test_pytest_timeout_dependency_matches_configured_timeout():
    pyproject = Path(__file__).resolve().parents[2] / "pyproject.toml"
    source = pyproject.read_text(encoding="utf-8")

    assert '"pytest-timeout>=2.3"' in source
    assert "timeout = 180" in source

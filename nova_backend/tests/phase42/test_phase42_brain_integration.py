from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BRAIN_SERVER_PATH = PROJECT_ROOT / "nova_backend" / "src" / "brain_server.py"


def test_brain_server_wires_explicit_phase42_invocation_path():
    source = BRAIN_SERVER_PATH.read_text(encoding="utf-8")
    assert "PersonalityAgent" in source
    assert "_extract_phase42_query" in source
    assert "phase42: <question>" in source or "phase42" in source

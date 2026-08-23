from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BRAIN_SERVER_PATH = PROJECT_ROOT / "nova_backend" / "src" / "brain_server.py"


def test_capability_discoverability_prompt_and_categories_exist():
    source = BRAIN_SERVER_PATH.read_text(encoding="utf-8")
    assert "what can you do" in source
    assert "Here's Nova's capability truth right now" in source
    assert "capability_truth_status" in source
    assert "Configured but provider health not verified" in source
    assert "Configuration alone is not a verified connection" in source
    assert "Connected right now" not in source
    assert "Good things to try next" in source

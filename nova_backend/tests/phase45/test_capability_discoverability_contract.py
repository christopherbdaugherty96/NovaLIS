from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BRAIN_SERVER_PATH = PROJECT_ROOT / "nova_backend" / "src" / "brain_server.py"


def test_capability_discoverability_prompt_and_categories_exist():
    source = BRAIN_SERVER_PATH.read_text(encoding="utf-8")
    assert "what can you do" in source
    assert "Nova Capabilities" in source
    assert "Here's what is actually live on this device right now" in source
    assert "Local-first everyday help is ready" in source
    assert "Research and reporting" in source
    assert "Verification and review" in source
    assert "Story tracking" in source
    assert "Screen help" in source
    assert "Memory and continuity" in source
    assert "Connected live sources" in source
    assert "Good things to try next" in source

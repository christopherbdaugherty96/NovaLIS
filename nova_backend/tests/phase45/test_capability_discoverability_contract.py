from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BRAIN_SERVER_PATH = PROJECT_ROOT / "nova_backend" / "src" / "brain_server.py"


def test_capability_discoverability_prompt_and_categories_exist():
    source = BRAIN_SERVER_PATH.read_text(encoding="utf-8")
    assert "what can you do" in source
    assert "Here's what Nova can do right now" in source
    assert "Everyday help" in source
    assert "Search and research" in source
    assert "Double-check answers" in source
    assert "Story tracking" in source
    assert "Screen help" in source
    assert "Memory" in source
    assert "Connected right now" in source
    assert "Good things to try next" in source

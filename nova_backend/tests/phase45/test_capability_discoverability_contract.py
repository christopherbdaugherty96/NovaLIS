from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BRAIN_SERVER_PATH = PROJECT_ROOT / "nova_backend" / "src" / "brain_server.py"


def test_capability_discoverability_prompt_and_categories_exist():
    source = BRAIN_SERVER_PATH.read_text(encoding="utf-8")
    assert "what can you do" in source
    assert "Nova Capabilities" in source
    assert "Research" in source
    assert "Document Analysis" in source
    assert "System Diagnostics" in source
    assert "Web Search" in source
    assert "Reports" in source

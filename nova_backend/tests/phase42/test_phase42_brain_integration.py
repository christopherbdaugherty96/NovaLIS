from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BRAIN_SERVER_PATH = PROJECT_ROOT / "nova_backend" / "src" / "brain_server.py"


def test_brain_server_wires_explicit_phase42_invocation_path():
    source = BRAIN_SERVER_PATH.read_text(encoding="utf-8")
    assert "PersonalityAgent" in source
    assert "_extract_phase42_query" in source
    assert "phase42: <question>" in source or "phase42" in source


def test_brain_server_arms_deep_mode_for_phase42_path():
    source = BRAIN_SERVER_PATH.read_text(encoding="utf-8")
    assert "personality_agent.arm_deep_mode()" in source


def test_phase42_path_preserves_raw_personality_outputs():
    source = BRAIN_SERVER_PATH.read_text(encoding="utf-8")
    assert "phase42_message, apply_personality=False" in source


def test_brain_server_defers_phase42_agent_imports_when_locked():
    source = BRAIN_SERVER_PATH.read_text(encoding="utf-8")
    top_block = "\n".join(source.splitlines()[:80])
    assert "from src.agents.builder import BuilderAgent" not in top_block
    assert "if PHASE_4_2_ENABLED:" in source

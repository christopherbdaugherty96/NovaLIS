from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BRAIN_SERVER_PATH = PROJECT_ROOT / "nova_backend" / "src" / "brain_server.py"


def test_brain_server_wires_interface_personality_agent_for_chat_messages():
    source = BRAIN_SERVER_PATH.read_text(encoding="utf-8")

    assert "from src.personality.interface_agent import PersonalityInterfaceAgent" in source
    assert "interface_personality_agent = PersonalityInterfaceAgent()" in source
    assert "presented = interface_personality_agent.present(presented, domain=tone_domain)" in source

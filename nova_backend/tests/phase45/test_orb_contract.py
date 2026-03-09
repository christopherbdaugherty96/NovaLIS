from pathlib import Path


ORB_PATH = Path(__file__).resolve().parents[2] / "static" / "orb.js"


def test_orb_has_no_explicit_runtime_state_coupling_tokens():
    source = ORB_PATH.read_text(encoding="utf-8").lower()

    forbidden_tokens = [
        "processing",
        "listening",
        "thinking",
        "error",
        "success",
        "confidence",
        "websocket",
        "trust_status",
        "chat_done",
    ]
    for token in forbidden_tokens:
        assert token not in source


def test_orb_uses_continuous_animation_loop():
    source = ORB_PATH.read_text(encoding="utf-8")
    assert "requestAnimationFrame(frame)" in source
    assert "function getStateProfile()" in source

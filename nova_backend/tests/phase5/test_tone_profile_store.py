from pathlib import Path

from src.personality.tone_profile_store import ToneProfileStore


def test_tone_profile_store_supports_global_and_domain_overrides(tmp_path: Path):
    store = ToneProfileStore(tmp_path / "tone_profile.json")

    initial = store.snapshot()
    assert initial["global_profile"] == "balanced"
    assert initial["override_count"] == 0

    after_global = store.set_global_profile("concise")
    assert after_global["global_profile"] == "concise"
    assert "Global tone" in after_global["summary"]

    after_domain = store.set_domain_profile("research", "detailed")
    assert after_domain["override_count"] == 1
    assert after_domain["domain_overrides"][0]["domain"] == "research"
    assert store.effective_profile("research") == "detailed"
    assert store.effective_profile("system") == "concise"


def test_tone_profile_store_reset_actions_record_history(tmp_path: Path):
    store = ToneProfileStore(tmp_path / "tone_profile.json")

    store.set_global_profile("formal")
    store.set_domain_profile("system", "concise")
    reset_domain = store.reset_domain("system")
    assert reset_domain["override_count"] == 0
    assert any("reset to global" in str(item.get("summary") or "").lower() for item in reset_domain["history"])

    reset_all = store.reset_all()
    assert reset_all["global_profile"] == "balanced"
    assert reset_all["override_count"] == 0
    assert any("reset to the default profile" in str(item.get("summary") or "").lower() for item in reset_all["history"])

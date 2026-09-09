from __future__ import annotations

import pytest
from src.durability.corruption import StateCorruptError
from src.memory.nova_self_memory_store import NovaSelfMemoryStore
from src.personality.tone_profile_store import ToneProfileStore
from src.profiles.user_profile_store import UserProfileStore


@pytest.mark.parametrize("factory", (UserProfileStore, ToneProfileStore, NovaSelfMemoryStore))
@pytest.mark.parametrize("contents", ('{"truncated":', '[]'))
def test_low_risk_portable_corruption_is_explicit_and_preserved(tmp_path, factory, contents):
    path = tmp_path / "state.json"
    path.write_text(contents, encoding="utf-8")
    store = factory(path)
    with pytest.raises(StateCorruptError):
        store._read_state()
    assert path.read_text(encoding="utf-8") == contents


@pytest.mark.parametrize("factory", (UserProfileStore, ToneProfileStore, NovaSelfMemoryStore))
def test_low_risk_portable_missing_state_keeps_defaults(tmp_path, factory):
    store = factory(tmp_path / "missing.json")
    assert isinstance(store._read_state(), dict)


@pytest.mark.parametrize(
    "factory,mutate",
    (
        (UserProfileStore, lambda store: store.set_identity(name="Nova user")),
        (ToneProfileStore, lambda store: store.set_global_profile("balanced")),
        (NovaSelfMemoryStore, lambda store: store.record_insight("prefers concise answers")),
    ),
)
def test_low_risk_corruption_blocks_dependent_mutation(tmp_path, factory, mutate):
    path = tmp_path / "state.json"
    original = b'{"truncated":'
    path.write_bytes(original)

    with pytest.raises(StateCorruptError):
        mutate(factory(path))

    assert path.read_bytes() == original

from src.agents.context import AgentContextSnapshot


def test_agent_context_snapshot_is_immutable_and_hashed():
    payload = {"topic": "ai regulation", "items": [1, 2, 3]}
    snapshot = AgentContextSnapshot.from_dict(payload)

    assert isinstance(snapshot.context_hash, str)
    assert len(snapshot.context_hash) == 64

    plain = snapshot.to_plain_dict()
    assert plain["topic"] == "ai regulation"
    assert plain["items"] == [1, 2, 3]

    # Confirm immutability proxy for top-level dict.
    try:
        snapshot.data["topic"] = "mutated"  # type: ignore[index]
        mutated = True
    except TypeError:
        mutated = False
    assert mutated is False

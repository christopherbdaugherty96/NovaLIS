import time



def test_thought_store_expiry():
    from src.conversation.thought_store import ThoughtStore
    store = ThoughtStore(ttl=1)
    store.put("s", "m", {"reason_codes": ["LONG_QUERY"]})

    assert store.get("s", "m") is not None

    time.sleep(1.1)
    assert store.get("s", "m") is None

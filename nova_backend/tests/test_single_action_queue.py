def test_single_action_queue_blocks_concurrent():
    from src.governor.single_action_queue import SingleActionQueue

    queue = SingleActionQueue()
    queue.set_pending("cap_16")

    try:
        queue.set_pending("cap_17")
        assert False, "Queue allowed concurrent execution"
    except RuntimeError:
        assert True

from src.llm import llm_gateway


class _FakeManager:
    def __init__(self, blocked: bool) -> None:
        self.inference_blocked = blocked

    def confirm_model_update(self) -> None:
        if self.inference_blocked:
            self.inference_blocked = False


def test_confirm_model_update_unblocks_when_pending(monkeypatch):
    fake = _FakeManager(blocked=True)
    monkeypatch.setattr(llm_gateway, "llm_manager", fake)

    assert llm_gateway.is_model_update_pending() is True
    assert llm_gateway.confirm_model_update() is True
    assert llm_gateway.is_model_update_pending() is False


def test_confirm_model_update_noop_when_not_pending(monkeypatch):
    fake = _FakeManager(blocked=False)
    monkeypatch.setattr(llm_gateway, "llm_manager", fake)

    assert llm_gateway.is_model_update_pending() is False
    assert llm_gateway.confirm_model_update() is False
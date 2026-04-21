"""Unit tests for OpenClaw governance models (hardening Step 1)."""
from uuid import UUID, uuid4

import pytest

from src.openclaw.models import (
    ActionType,
    ApprovalState,
    OpenClawProposedAction,
    UserVisibleCategory,
)


def _make_action(**overrides) -> OpenClawProposedAction:
    defaults = dict(
        run_id=uuid4(),
        step_id="step-001",
        tool_name="write_file",
        action_type=ActionType.DURABLE_MUTATION,
        user_visible_category=UserVisibleCategory.FILE_CHANGE,
        authority_class="persistent_change",
        payload={"path": "/tmp/test.txt", "content": "hello"},
        expected_effect="Writes hello to /tmp/test.txt",
        reversible=False,
        requires_approval=True,
    )
    defaults.update(overrides)
    return OpenClawProposedAction(**defaults)


class TestActionType:
    def test_read_value(self):
        assert ActionType.READ == "read"

    def test_external_write_value(self):
        assert ActionType.EXTERNAL_WRITE == "external_write"

    def test_all_values_are_strings(self):
        for member in ActionType:
            assert isinstance(member.value, str)


class TestApprovalState:
    def test_auto_allowed_value(self):
        assert ApprovalState.AUTO_ALLOWED == "auto_allowed"

    def test_pending_is_default_for_proposed_action(self):
        action = _make_action()
        assert action.approval_state == ApprovalState.PENDING


class TestUserVisibleCategory:
    def test_file_change_value(self):
        assert UserVisibleCategory.FILE_CHANGE == "file_change"

    def test_network_send_value(self):
        assert UserVisibleCategory.NETWORK_SEND == "network_send"


class TestOpenClawProposedAction:
    def test_constructs_correctly(self):
        run_id = uuid4()
        action = _make_action(run_id=run_id, tool_name="http_post")
        assert action.run_id == run_id
        assert action.tool_name == "http_post"
        assert action.requires_approval is True
        assert action.approval_state == ApprovalState.PENDING

    def test_read_action_can_be_auto_allowed(self):
        action = _make_action(
            tool_name="read_file",
            action_type=ActionType.READ,
            user_visible_category=UserVisibleCategory.READ,
            authority_class="read_only_local",
            reversible=True,
            requires_approval=False,
            approval_state=ApprovalState.AUTO_ALLOWED,
        )
        assert action.requires_approval is False
        assert action.approval_state == ApprovalState.AUTO_ALLOWED

    def test_model_is_frozen(self):
        action = _make_action()
        with pytest.raises(Exception):
            action.tool_name = "other_tool"  # type: ignore[misc]

    def test_payload_is_preserved(self):
        payload = {"path": "/some/file", "mode": "wb"}
        action = _make_action(payload=payload)
        assert action.payload == payload

    def test_optional_expected_effect_defaults_to_none(self):
        action = _make_action(expected_effect=None)
        assert action.expected_effect is None

    def test_run_id_is_uuid(self):
        action = _make_action()
        assert isinstance(action.run_id, UUID)

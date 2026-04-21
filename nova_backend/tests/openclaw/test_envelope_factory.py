"""Unit tests for EnvelopeFactory (hardening Step 2)."""
import os
from unittest.mock import MagicMock

import pytest

from src.openclaw.envelope_factory import (
    EnvelopeFactory,
    EnvelopeFactoryError,
    IssuedEnvelope,
    _FEATURE_FLAG_ENV,
)


_BASE_TEMPLATE = {
    "id": "morning_brief",
    "title": "Morning Brief",
    "tools_allowed": ["weather", "news", "summarize"],
    "allowed_hostnames": ["weather.visualcrossing.com", "feeds.npr.org"],
    "max_steps": 6,
    "max_duration_s": 90,
    "max_network_calls": 8,
    "max_files_touched": 1,
    "max_bytes_read": 500_000,
    "max_bytes_written": 0,
    "delivery_mode": "widget",
}


def _factory_with_flag(enabled: bool = True, settings=None) -> EnvelopeFactory:
    os.environ[_FEATURE_FLAG_ENV] = "true" if enabled else "false"
    return EnvelopeFactory(runtime_settings=settings)


class TestEnvelopeFactoryFeatureFlag:
    def teardown_method(self):
        os.environ.pop(_FEATURE_FLAG_ENV, None)

    def test_raises_when_flag_off(self):
        factory = _factory_with_flag(enabled=False)
        with pytest.raises(EnvelopeFactoryError, match=_FEATURE_FLAG_ENV):
            factory.issue(template=_BASE_TEMPLATE, channel="manual", triggered_by="dashboard")

    def test_succeeds_when_flag_on(self):
        factory = _factory_with_flag(enabled=True)
        result = factory.issue(template=_BASE_TEMPLATE, channel="manual", triggered_by="dashboard")
        assert isinstance(result, IssuedEnvelope)


class TestEnvelopeFactoryChannelValidation:
    def setup_method(self):
        os.environ[_FEATURE_FLAG_ENV] = "true"

    def teardown_method(self):
        os.environ.pop(_FEATURE_FLAG_ENV, None)

    def test_unknown_channel_raises(self):
        factory = EnvelopeFactory()
        with pytest.raises(EnvelopeFactoryError, match="Unknown channel"):
            factory.issue(template=_BASE_TEMPLATE, channel="rogue", triggered_by="rogue")

    def test_manual_channel_accepts_dashboard_trigger(self):
        factory = EnvelopeFactory()
        result = factory.issue(template=_BASE_TEMPLATE, channel="manual", triggered_by="dashboard")
        assert result.issuing_channel == "manual"

    def test_manual_channel_rejects_scheduler_trigger(self):
        factory = EnvelopeFactory()
        with pytest.raises(EnvelopeFactoryError, match="triggered_by"):
            factory.issue(template=_BASE_TEMPLATE, channel="manual", triggered_by="scheduler")

    def test_scheduler_channel_accepts_scheduler_trigger(self):
        factory = EnvelopeFactory()
        result = factory.issue(template=_BASE_TEMPLATE, channel="scheduler", triggered_by="scheduler")
        assert result.issuing_channel == "scheduler"

    def test_bridge_channel_accepts_bridge_trigger(self):
        factory = EnvelopeFactory()
        result = factory.issue(template=_BASE_TEMPLATE, channel="bridge", triggered_by="bridge")
        assert result.issuing_channel == "bridge"


class TestEnvelopeFactoryTemplateValidation:
    def setup_method(self):
        os.environ[_FEATURE_FLAG_ENV] = "true"

    def teardown_method(self):
        os.environ.pop(_FEATURE_FLAG_ENV, None)

    def test_missing_id_raises(self):
        factory = EnvelopeFactory()
        bad = {**_BASE_TEMPLATE, "id": ""}
        with pytest.raises(EnvelopeFactoryError, match="missing required field 'id'"):
            factory.issue(template=bad, channel="manual", triggered_by="dashboard")

    def test_missing_title_raises(self):
        factory = EnvelopeFactory()
        bad = {**_BASE_TEMPLATE, "title": ""}
        with pytest.raises(EnvelopeFactoryError, match="missing required field 'title'"):
            factory.issue(template=bad, channel="manual", triggered_by="dashboard")


class TestEnvelopeFactoryHomeAgentGate:
    def setup_method(self):
        os.environ[_FEATURE_FLAG_ENV] = "true"

    def teardown_method(self):
        os.environ.pop(_FEATURE_FLAG_ENV, None)

    def test_raises_when_home_agent_disabled(self):
        settings = MagicMock()
        settings.is_permission_enabled.return_value = False
        factory = EnvelopeFactory(runtime_settings=settings)
        with pytest.raises(EnvelopeFactoryError, match="home_agent_enabled"):
            factory.issue(template=_BASE_TEMPLATE, channel="manual", triggered_by="dashboard")

    def test_succeeds_when_home_agent_enabled(self):
        settings = MagicMock()
        settings.is_permission_enabled.return_value = True
        factory = EnvelopeFactory(runtime_settings=settings)
        result = factory.issue(template=_BASE_TEMPLATE, channel="manual", triggered_by="dashboard")
        assert isinstance(result, IssuedEnvelope)


class TestIssuedEnvelope:
    def setup_method(self):
        os.environ[_FEATURE_FLAG_ENV] = "true"

    def teardown_method(self):
        os.environ.pop(_FEATURE_FLAG_ENV, None)

    def test_envelope_id_is_uuid(self):
        from uuid import UUID
        factory = EnvelopeFactory()
        result = factory.issue(template=_BASE_TEMPLATE, channel="manual", triggered_by="dashboard")
        assert isinstance(result.envelope_id, UUID)

    def test_ledger_event_has_required_fields(self):
        factory = EnvelopeFactory()
        result = factory.issue(template=_BASE_TEMPLATE, channel="manual", triggered_by="dashboard")
        event = result.ledger_event
        assert event["event_type"] == "OPENCLAW_RUN_ISSUED"
        assert event["template_id"] == "morning_brief"
        assert event["channel"] == "manual"
        assert "envelope_id" in event
        assert "issued_at" in event
        assert "expires_at" in event
        assert "settings_hash" in event

    def test_expires_at_is_after_issued_at(self):
        from datetime import timezone
        factory = EnvelopeFactory()
        result = factory.issue(template=_BASE_TEMPLATE, channel="manual", triggered_by="dashboard")
        assert result.expires_at > result.issued_at

    def test_envelope_has_correct_template_id(self):
        factory = EnvelopeFactory()
        result = factory.issue(template=_BASE_TEMPLATE, channel="manual", triggered_by="dashboard")
        assert result.envelope.template_id == "morning_brief"

    def test_feature_flags_snapshot_captured(self):
        factory = EnvelopeFactory()
        result = factory.issue(template=_BASE_TEMPLATE, channel="manual", triggered_by="dashboard")
        assert _FEATURE_FLAG_ENV in result.feature_flags_snapshot
        assert result.feature_flags_snapshot[_FEATURE_FLAG_ENV] is True

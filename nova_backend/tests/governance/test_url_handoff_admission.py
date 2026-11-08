from __future__ import annotations

from dataclasses import replace

import pytest
from src.governor import url_handoff_admission as admission
from src.governor.disclosure_policy import DisclosureDecision, DisclosureDecisionValue


class Sink:
    def __init__(self, events: list[object], *, fail_at: int | None = None):
        self.events = events
        self.fail_at = fail_at

    def append(self, event: object) -> None:
        if self.fail_at == len(self.events) + 1:
            raise OSError("evidence unavailable")
        self.events.append(event)


def test_webpage_denial_or_evidence_failure_makes_zero_handoff_attempts(monkeypatch):
    attempts: list[str] = []
    monkeypatch.setattr(admission, "_handoff_evidence_sink", lambda: Sink([], fail_at=1))

    with pytest.raises(admission.URLHandoffAdmissionError, match="evidence"):
        admission.open_governed_url_handoff(
            uri="https://example.com/private?q=secret",
            kind=admission.URLHandoffKind.WEBPAGE,
            request_id="req-web-denied",
            opener=lambda uri: attempts.append(uri) or True,
        )

    assert attempts == []


def test_policy_denial_makes_zero_handoff_attempts(monkeypatch):
    events: list[object] = []
    attempts: list[str] = []
    monkeypatch.setattr(admission, "_handoff_evidence_sink", lambda: Sink(events))
    monkeypatch.setattr(
        admission.DisclosurePolicyEvaluator,
        "evaluate_and_record",
        lambda *_args, **_kwargs: DisclosureDecision(
            DisclosureDecisionValue.DENY,
            "test_denial",
            "runtime-url-handoff-admission-v1",
            evidence_recorded=True,
        ),
    )

    with pytest.raises(admission.URLHandoffAdmissionError, match="test_denial"):
        admission.open_governed_url_handoff(
            uri="https://example.com/",
            kind=admission.URLHandoffKind.WEBPAGE,
            request_id="req-policy-denial",
            opener=lambda uri: attempts.append(uri) or True,
        )

    assert attempts == []


def test_mail_evidence_never_contains_raw_sensitive_values(monkeypatch):
    events: list[object] = []
    monkeypatch.setattr(admission, "_handoff_evidence_sink", lambda: Sink(events))
    raw_uri = (
        "mailto:secret-recipient@example.com?"
        "subject=Private%20merger&body=synthetic-secret-value"
    )

    assert admission.open_governed_url_handoff(
        uri=raw_uri,
        kind=admission.URLHandoffKind.MAIL_CLIENT,
        request_id="req-mail-1",
        session_id="session-secret",
        opener=lambda _uri: True,
    )

    serialized = "\n".join(str(getattr(item, "as_dict", lambda: item)()) for item in events)
    assert "secret-recipient" not in serialized
    assert "Private%20merger" not in serialized
    assert "synthetic-secret-value" not in serialized
    assert raw_uri not in serialized


def test_exact_uri_mutation_is_denied_before_handoff(monkeypatch):
    events: list[object] = []
    original = "https://example.com/report?account=approved"
    changed = "https://example.com/report?account=other"
    built = admission._build_admission(
        uri=original,
        kind=admission.URLHandoffKind.WEBPAGE,
        request_id="req-web-mutation",
        session_id="",
    )
    admission._record_admission(built, Sink(events))
    attempts: list[str] = []

    with pytest.raises(admission.URLHandoffAdmissionError, match="changed"):
        admission._delegate_admitted_handoff(
            built,
            uri=changed,
            sink=Sink(events),
            opener=lambda uri: attempts.append(uri) or True,
        )

    assert attempts == []


def test_browser_policy_identity_includes_query_values():
    from src.governor.disclosure_policy import TransportClass, _normalized_destination

    approved = _normalized_destination(
        "https://example.com/report?account=approved",
        TransportClass.BROWSER_HANDOFF,
    )
    changed = _normalized_destination(
        "https://example.com/report?account=other",
        TransportClass.BROWSER_HANDOFF,
    )

    assert approved != changed


def test_changed_admission_identity_is_denied_before_handoff(monkeypatch):
    events: list[object] = []
    built = admission._build_admission(
        uri="mailto:approved@example.com?subject=Approved&body=Body",
        kind=admission.URLHandoffKind.MAIL_CLIENT,
        request_id="req-mail-mutation",
        session_id="",
    )
    admission._record_admission(built, Sink(events))
    forged = replace(built, uri_fingerprint="0" * 64)
    attempts: list[str] = []

    with pytest.raises(admission.URLHandoffAdmissionError, match="changed"):
        admission._delegate_admitted_handoff(
            forged,
            uri=forged.uri,
            sink=Sink(events),
            opener=lambda uri: attempts.append(uri) or True,
        )

    assert attempts == []


@pytest.mark.parametrize(
    ("uri", "kind"),
    [
        ("javascript:alert(1)", admission.URLHandoffKind.WEBPAGE),
        ("https://user:password@example.com/", admission.URLHandoffKind.WEBPAGE),
        ("https://example.com/", admission.URLHandoffKind.MAIL_CLIENT),
    ],
)
def test_invalid_scheme_or_origin_credentials_are_denied(uri, kind):
    with pytest.raises(admission.URLHandoffAdmissionError):
        admission._build_admission(
            uri=uri,
            kind=kind,
            request_id="req-invalid",
            session_id="",
        )


def test_delegation_outcome_is_separate_from_admission(monkeypatch):
    events: list[object] = []
    monkeypatch.setattr(admission, "_handoff_evidence_sink", lambda: Sink(events))

    accepted = admission.open_governed_url_handoff(
        uri="https://example.com/",
        kind=admission.URLHandoffKind.WEBPAGE,
        request_id="req-web-outcome",
        opener=lambda _uri: False,
    )

    assert accepted is False
    outcome = events[-1].as_dict()
    assert outcome["record_kind"] == "delegated_url_handoff_outcome"
    assert outcome["outcome"] == "handoff_rejected"
    assert outcome["transport_observed"] is True


def test_outcome_evidence_failure_reports_attempted_handoff(monkeypatch):
    events: list[object] = []
    monkeypatch.setattr(
        admission,
        "_handoff_evidence_sink",
        lambda: Sink(events, fail_at=3),
    )
    attempts: list[str] = []

    with pytest.raises(admission.URLHandoffAdmissionError) as captured:
        admission.open_governed_url_handoff(
            uri="https://example.com/",
            kind=admission.URLHandoffKind.WEBPAGE,
            request_id="req-outcome-failure",
            opener=lambda uri: attempts.append(uri) or True,
        )

    assert attempts == ["https://example.com/"]
    assert captured.value.handoff_attempted is True

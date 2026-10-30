from __future__ import annotations

import dataclasses
import json
from concurrent.futures import ThreadPoolExecutor
from enum import Enum

import pytest
from src.governor.disclosure_policy import (
    CredentialCategory,
    DataCategory,
    DestinationClass,
    DisclosureDecisionValue,
    DisclosureGrant,
    DisclosurePolicy,
    DisclosurePolicyEvaluator,
    DisclosureRequest,
    InitiationClass,
    JsonlDisclosureEvidenceSink,
    ProviderClass,
    RequestShapeField,
    RequestShapeSource,
    RequestShapeStep,
    RequestShapeStepKind,
    RequestShapeValueKind,
    TransportClass,
    VerifiedLocalEvidenceTarget,
)


def _field(source: RequestShapeSource, name: str) -> RequestShapeField:
    return RequestShapeField(
        source=source,
        path=(RequestShapeStep(RequestShapeStepKind.FIELD, name),),
        value_kind=RequestShapeValueKind.SCALAR,
    )


_BASE_SHAPE = frozenset(
    {
        _field(RequestShapeSource.JSON, "model"),
        _field(RequestShapeSource.JSON, "messages"),
    }
)


def _request(**overrides) -> DisclosureRequest:
    values = {
        "caller": "deepseek_bridge",
        "purpose": "external_reasoning",
        "transport": TransportClass.HTTP,
        "destination_class": DestinationClass.EXTERNAL_PROVIDER,
        "provider_class": ProviderClass.HOSTED_MODEL,
        "derived_destination": "https://api.deepseek.com/chat/completions",
        "policy_version": "policy-v1",
        "data_categories": frozenset({DataCategory.PROMPT, DataCategory.CONVERSATION_CONTEXT}),
        "http_method": "POST",
        "request_shape": _BASE_SHAPE,
        "credential_categories": frozenset({CredentialCategory.BEARER_TOKEN}),
        "initiating_capability_id": 62,
        "request_id": "request-1",
        "session_id": "session-1",
        "declared_provider": "deepseek",
        "derived_provider": "deepseek",
        "declared_destination": "https://api.deepseek.com/chat/completions",
        "effective_route": "direct",
        "initiation": InitiationClass.APPROVED,
    }
    values.update(overrides)
    return DisclosureRequest(**values)


def _policy() -> DisclosurePolicy:
    return DisclosurePolicy(
        version="policy-v1",
        grants=(
            DisclosureGrant(
                provider="deepseek",
                provider_class=ProviderClass.HOSTED_MODEL,
                destination_class=DestinationClass.EXTERNAL_PROVIDER,
                destinations=frozenset({"https://api.deepseek.com/chat/completions"}),
                effective_routes=frozenset({"direct"}),
                transports=frozenset({TransportClass.HTTP}),
                data_categories=frozenset({DataCategory.PROMPT, DataCategory.CONVERSATION_CONTEXT}),
                http_methods=frozenset({"POST"}),
                request_shapes=frozenset({_BASE_SHAPE}),
                credential_categories=frozenset({CredentialCategory.BEARER_TOKEN}),
                purposes=frozenset({"external_reasoning"}),
                callers=frozenset({"deepseek_bridge"}),
                capability_ids=frozenset({62}),
                initiations=frozenset({InitiationClass.APPROVED}),
            ),
        ),
    )


def test_disclosure_contracts_are_immutable():
    request = _request()
    decision = DisclosurePolicyEvaluator().evaluate(request, _policy())

    with pytest.raises(dataclasses.FrozenInstanceError):
        request.caller = "changed"  # type: ignore[misc]
    with pytest.raises(dataclasses.FrozenInstanceError):
        decision.reason = "changed"  # type: ignore[misc]


def test_exact_explicit_grant_allows_and_only_allow_may_proceed():
    decision = DisclosurePolicyEvaluator().evaluate(_request(), _policy())

    assert decision.value is DisclosureDecisionValue.ALLOW
    assert decision.reason == "explicit_policy_grant"
    assert decision.may_proceed is False


def test_only_recorded_allow_may_proceed(tmp_path):
    path = tmp_path / "decisions.jsonl"
    sink = JsonlDisclosureEvidenceSink(VerifiedLocalEvidenceTarget(path, locality_verified=True))

    decision = DisclosurePolicyEvaluator().evaluate_and_record(_request(), _policy(), sink)

    assert decision.value is DisclosureDecisionValue.ALLOW
    assert decision.evidence_recorded is True
    assert decision.may_proceed is True


@pytest.mark.parametrize(
    ("disclosure_request", "reason"),
    [
        (_request(declared_provider="other"), "provider_identity_mismatch"),
        (
            _request(declared_destination="https://other.example/collect"),
            "destination_identity_mismatch",
        ),
        (_request(purpose="different"), "no_matching_policy_grant"),
        (_request(http_method="DELETE"), "no_matching_policy_grant"),
        (
            _request(
                request_shape=frozenset(
                    {_field(RequestShapeSource.QUERY, "private_document")}
                )
            ),
            "no_matching_policy_grant",
        ),
        (
            _request(derived_destination="https://api.deepseek.com/other"),
            "destination_identity_mismatch",
        ),
        (_request(effective_route="proxy:https://proxy.example"), "no_matching_policy_grant"),
        (_request(provider_class=ProviderClass.SEARCH), "no_matching_policy_grant"),
        (
            _request(data_categories=frozenset({DataCategory.DOCUMENT_TEXT})),
            "no_matching_policy_grant",
        ),
    ],
)
def test_mismatch_or_missing_grant_denies(disclosure_request, reason):
    decision = DisclosurePolicyEvaluator().evaluate(disclosure_request, _policy())

    assert decision.value is DisclosureDecisionValue.DENY
    assert decision.reason == reason
    assert decision.may_proceed is False


@pytest.mark.parametrize(
    ("disclosure_request", "policy", "reason"),
    [
        (_request(), None, "policy_unavailable"),
        (_request(policy_version="old"), _policy(), "policy_version_mismatch"),
        (
            _request(destination_class=DestinationClass.UNCLASSIFIED),
            _policy(),
            "destination_unclassified",
        ),
        (
            _request(provider_class=ProviderClass.UNCLASSIFIED),
            _policy(),
            "provider_unclassified",
        ),
        (_request(data_categories=frozenset()), _policy(), "data_categories_unclassified"),
        (
            _request(derived_destination=""),
            _policy(),
            "request_vocabulary_unclassified",
        ),
        (_request(derived_provider=""), _policy(), "request_unclassified"),
        (_request(effective_route=""), _policy(), "request_unclassified"),
        (
            _request(transport="http"),  # type: ignore[arg-type]
            _policy(),
            "request_vocabulary_unclassified",
        ),
        (
            _request(data_categories=frozenset({"prompt"})),  # type: ignore[arg-type]
            _policy(),
            "request_vocabulary_unclassified",
        ),
    ],
)
def test_unavailable_or_unclassified_input_is_unknown(disclosure_request, policy, reason):
    decision = DisclosurePolicyEvaluator().evaluate(disclosure_request, policy)

    assert decision.value is DisclosureDecisionValue.UNKNOWN
    assert decision.reason == reason
    assert decision.may_proceed is False


def test_allow_becomes_unknown_when_evidence_sink_is_unavailable():
    decision = DisclosurePolicyEvaluator().evaluate_and_record(_request(), _policy(), None)

    assert decision.value is DisclosureDecisionValue.UNKNOWN
    assert decision.reason == "evidence_unavailable"
    assert decision.may_proceed is False


def test_malformed_policy_vocabulary_is_unknown():
    malformed = DisclosurePolicy(
        version="policy-v1",
        grants=(
            DisclosureGrant(
                provider="deepseek",
                provider_class=ProviderClass.HOSTED_MODEL,
                destination_class=DestinationClass.EXTERNAL_PROVIDER,
                destinations=frozenset({"https://api.deepseek.com/chat/completions"}),
                effective_routes=frozenset({"direct"}),
                transports=frozenset({"http"}),  # type: ignore[arg-type]
                data_categories=frozenset({DataCategory.PROMPT}),
                http_methods=frozenset({"POST"}),
                request_shapes=frozenset(
                    {frozenset({_field(RequestShapeSource.JSON, "model")})}
                ),
            ),
        ),
    )

    decision = DisclosurePolicyEvaluator().evaluate(_request(), malformed)

    assert decision.value is DisclosureDecisionValue.UNKNOWN
    assert decision.reason == "policy_vocabulary_invalid"


@pytest.mark.parametrize(
    "grant_override",
    [
        {"http_methods": frozenset()},
        {"request_shapes": frozenset()},
    ],
)
def test_http_grant_without_operation_constraints_is_unknown(grant_override):
    policy = dataclasses.replace(
        _policy(),
        grants=(dataclasses.replace(_policy().grants[0], **grant_override),),
    )

    decision = DisclosurePolicyEvaluator().evaluate(_request(), policy)

    assert decision.value is DisclosureDecisionValue.UNKNOWN
    assert decision.reason == "policy_vocabulary_invalid"


def test_allow_becomes_unknown_when_evidence_write_fails():
    class _BrokenSink:
        def append(self, _record):
            raise OSError("simulated evidence failure")

    decision = DisclosurePolicyEvaluator().evaluate_and_record(_request(), _policy(), _BrokenSink())

    assert decision.value is DisclosureDecisionValue.UNKNOWN
    assert decision.reason == "evidence_write_failed"
    assert decision.may_proceed is False


def test_malformed_request_records_bounded_unknown_evidence(tmp_path):
    path = tmp_path / "disclosure-decisions.jsonl"
    sink = JsonlDisclosureEvidenceSink(VerifiedLocalEvidenceTarget(path, locality_verified=True))
    malformed = _request(
        transport="not-a-transport",  # type: ignore[arg-type]
        data_categories=frozenset({"private payload"}),  # type: ignore[arg-type]
    )

    decision = DisclosurePolicyEvaluator().evaluate_and_record(malformed, _policy(), sink)
    record = json.loads(path.read_text(encoding="utf-8"))

    assert decision.value is DisclosureDecisionValue.UNKNOWN
    assert decision.reason == "request_vocabulary_unclassified"
    assert record["transport"] == "unclassified_transport"
    assert record["data_categories"] == ["unclassified_data"]
    assert "private payload" not in path.read_text(encoding="utf-8")


def test_verified_local_target_rejects_unverified_path(tmp_path):
    with pytest.raises(ValueError, match="pre-verified local"):
        VerifiedLocalEvidenceTarget(
            tmp_path / "decisions.jsonl",
            locality_verified=False,
        )


def test_durable_evidence_is_secret_free_and_destination_sanitized(tmp_path):
    path = tmp_path / "trusted" / "disclosure-decisions.jsonl"
    sink = JsonlDisclosureEvidenceSink(VerifiedLocalEvidenceTarget(path, locality_verified=True))
    secret = "slice1-super-secret"
    request = _request(
        derived_destination=f"https://api.deepseek.com/chat/completions?key={secret}",
        declared_destination=f"https://api.deepseek.com/chat/completions?key={secret}",
        request_id="request secret/id",
    )

    decision = DisclosurePolicyEvaluator().evaluate_and_record(request, _policy(), sink)
    raw = path.read_text(encoding="utf-8")
    record = json.loads(raw)

    assert decision.value is DisclosureDecisionValue.ALLOW
    assert secret not in raw
    assert "user:" not in raw
    assert "chat/completions" not in raw
    assert record["destination"] == "https://api.deepseek.com"
    assert record["record_kind"] == "disclosure_policy_evaluation"
    assert record["transport_observed"] is False
    assert record["credential_categories"] == ["bearer_token"]
    assert record["data_categories"] == ["conversation_context", "prompt"]
    assert record["request_id"].startswith("sha256:")
    assert "request secret/id" not in raw


def test_unknown_evidence_fingerprints_policy_version_and_bounds_capability_id(tmp_path):
    path = tmp_path / "disclosure-decisions.jsonl"
    sink = JsonlDisclosureEvidenceSink(VerifiedLocalEvidenceTarget(path, locality_verified=True))
    secret = "PRIVATE_TOKEN_123"
    request = _request(
        policy_version=secret,
        initiating_capability_id=secret,  # type: ignore[arg-type]
    )

    decision = DisclosurePolicyEvaluator().evaluate_and_record(request, None, sink)
    raw = path.read_text(encoding="utf-8")
    record = json.loads(raw)

    assert decision.value is DisclosureDecisionValue.UNKNOWN
    assert secret not in raw
    assert record["policy_version"].startswith("sha256:")
    assert record["initiating_capability_id"] is None


@pytest.mark.parametrize(
    "grant_update",
    [
        {"purposes": frozenset()},
        {"callers": frozenset()},
        {"capability_ids": frozenset()},
        {"initiations": frozenset()},
    ],
)
def test_empty_grant_scopes_are_invalid_not_wildcards(grant_update):
    policy = dataclasses.replace(
        _policy(),
        grants=(dataclasses.replace(_policy().grants[0], **grant_update),),
    )

    decision = DisclosurePolicyEvaluator().evaluate(_request(), policy)

    assert decision.value is DisclosureDecisionValue.UNKNOWN
    assert decision.reason == "policy_vocabulary_invalid"


def test_initiation_requires_an_exact_grant():
    decision = DisclosurePolicyEvaluator().evaluate(
        _request(initiation=InitiationClass.USER_INITIATED),
        _policy(),
    )

    assert decision.value is DisclosureDecisionValue.DENY
    assert decision.reason == "no_matching_policy_grant"


@pytest.mark.parametrize(
    "destination", ["not-a-url", "api.example.com/path", "ftp://api.example.com/x"]
)
def test_http_destination_must_be_an_http_url(destination):
    request = _request(
        derived_destination=destination,
        declared_destination=destination,
    )

    decision = DisclosurePolicyEvaluator().evaluate(request, _policy())

    assert decision.value is DisclosureDecisionValue.UNKNOWN
    assert decision.reason == "request_vocabulary_unclassified"


@pytest.mark.parametrize(
    ("transport", "destination"),
    [
        (TransportClass.PROCESS_HANDOFF, "/opt/Approved/upload"),
        (TransportClass.NETWORK_FILESYSTEM, "/mnt/Approved/upload"),
    ],
)
def test_non_url_destination_preserves_case_for_exact_match(transport, destination):
    request = _request(
        transport=transport,
        derived_destination=destination,
        declared_destination=destination,
        http_method="",
        request_shape=frozenset(),
    )
    policy = dataclasses.replace(
        _policy(),
        grants=(
            dataclasses.replace(
                _policy().grants[0],
                transports=frozenset({transport}),
                destinations=frozenset({destination}),
                http_methods=frozenset(),
                request_shapes=frozenset(),
            ),
        ),
    )

    exact = DisclosurePolicyEvaluator().evaluate(request, policy)
    different_case = DisclosurePolicyEvaluator().evaluate(
        dataclasses.replace(
            request,
            derived_destination=destination.lower(),
            declared_destination=destination.lower(),
        ),
        policy,
    )

    assert exact.value is DisclosureDecisionValue.ALLOW
    assert different_case.value is DisclosureDecisionValue.DENY
    assert different_case.reason == "no_matching_policy_grant"


def test_filesystem_destination_preserves_significant_whitespace():
    destination = "/mnt/approved/report"
    transport = TransportClass.NETWORK_FILESYSTEM
    policy = dataclasses.replace(
        _policy(),
        grants=(
            dataclasses.replace(
                _policy().grants[0],
                transports=frozenset({transport}),
                destinations=frozenset({destination}),
                http_methods=frozenset(),
                request_shapes=frozenset(),
            ),
        ),
    )
    exact_request = _request(
        transport=transport,
        derived_destination=destination,
        declared_destination=destination,
        http_method="",
        request_shape=frozenset(),
    )
    trailing_space_request = dataclasses.replace(
        exact_request,
        derived_destination=f"{destination} ",
        declared_destination=f"{destination} ",
    )
    trailing_space_policy = dataclasses.replace(
        policy,
        grants=(
            dataclasses.replace(
                policy.grants[0],
                destinations=frozenset({f"{destination} "}),
            ),
        ),
    )

    exact = DisclosurePolicyEvaluator().evaluate(exact_request, policy)
    mismatch = DisclosurePolicyEvaluator().evaluate(trailing_space_request, policy)
    exact_with_space = DisclosurePolicyEvaluator().evaluate(
        trailing_space_request,
        trailing_space_policy,
    )

    assert exact.value is DisclosureDecisionValue.ALLOW
    assert mismatch.value is DisclosureDecisionValue.DENY
    assert mismatch.reason == "no_matching_policy_grant"
    assert exact_with_space.value is DisclosureDecisionValue.ALLOW


class _ForeignSecretEnum(str, Enum):
    VALUE = "SYNTHETIC_ENUM_SECRET_947"


@pytest.mark.parametrize(
    ("field", "fallback"),
    [
        ("transport", "unclassified_transport"),
        ("provider_class", "unclassified_provider"),
        ("destination_class", "unclassified_destination"),
        ("initiation", "unclassified_initiation"),
    ],
)
def test_foreign_enum_value_cannot_enter_unknown_evidence(tmp_path, field, fallback):
    path = tmp_path / f"{field}.jsonl"
    sink = JsonlDisclosureEvidenceSink(VerifiedLocalEvidenceTarget(path, locality_verified=True))
    request = _request(**{field: _ForeignSecretEnum.VALUE})

    decision = DisclosurePolicyEvaluator().evaluate_and_record(request, None, sink)
    raw = path.read_text(encoding="utf-8")
    record = json.loads(raw)

    assert decision.value is DisclosureDecisionValue.UNKNOWN
    assert _ForeignSecretEnum.VALUE.value not in raw
    assert record[field] == fallback


def test_denied_untrusted_taxonomy_is_fingerprinted(tmp_path):
    path = tmp_path / "disclosure-decisions.jsonl"
    sink = JsonlDisclosureEvidenceSink(VerifiedLocalEvidenceTarget(path, locality_verified=True))
    secret = "deny-side-secret-value"
    request = _request(
        caller=secret,
        purpose=secret,
        derived_provider=secret,
        declared_provider=secret,
    )

    decision = DisclosurePolicyEvaluator().evaluate_and_record(request, _policy(), sink)
    raw = path.read_text(encoding="utf-8")
    record = json.loads(raw)

    assert decision.value is DisclosureDecisionValue.DENY
    assert secret not in raw
    assert record["caller"].startswith("sha256:")
    assert record["purpose"].startswith("sha256:")
    assert record["provider"].startswith("sha256:")


def test_multiple_sink_instances_serialize_durable_writes(tmp_path):
    path = tmp_path / "disclosure-decisions.jsonl"
    target = VerifiedLocalEvidenceTarget(path, locality_verified=True)
    evaluator = DisclosurePolicyEvaluator()

    def record(index: int) -> None:
        sink = JsonlDisclosureEvidenceSink(target)
        evaluator.evaluate_and_record(
            _request(request_id=f"request-{index}"),
            _policy(),
            sink,
        )

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(record, range(40)))

    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert len(records) == 40
    assert all(item["decision"] == "allow" for item in records)


def test_ipv6_destination_is_normalized_and_sanitized_unambiguously(tmp_path):
    path = tmp_path / "disclosure-decisions.jsonl"
    sink = JsonlDisclosureEvidenceSink(VerifiedLocalEvidenceTarget(path, locality_verified=True))
    request = _request(
        derived_destination="https://[::1]:8443/chat?token=secret",
        declared_destination="https://[::1]:8443/chat?token=secret",
    )
    policy = dataclasses.replace(
        _policy(),
        grants=(
            dataclasses.replace(
                _policy().grants[0],
                destinations=frozenset({"https://[::1]:8443/chat"}),
            ),
        ),
    )

    decision = DisclosurePolicyEvaluator().evaluate_and_record(request, policy, sink)
    record = json.loads(path.read_text(encoding="utf-8"))

    assert decision.value is DisclosureDecisionValue.ALLOW
    assert record["destination"] == "https://[::1]:8443"
    assert "secret" not in path.read_text(encoding="utf-8")


def test_policy_module_has_no_transport_or_target_probe_imports():
    import ast
    import inspect

    import src.governor.disclosure_policy as module

    tree = ast.parse(inspect.getsource(module))
    forbidden = {"requests", "socket", "urllib.request", "subprocess", "webbrowser"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)

    assert imported.isdisjoint(forbidden)

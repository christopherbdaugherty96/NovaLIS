from __future__ import annotations

import asyncio

import pytest
from src.conversation.general_chat_runtime import _fetch_weather_for_brief
from src.governor.disclosure_policy import (
    CredentialCategory,
    DataCategory,
    DestinationClass,
    DisclosureGrant,
    DisclosurePolicy,
    InitiationClass,
    ProviderClass,
    TransportClass,
)
from src.governor.disclosure_transport import disclosure_facts
from src.governor.network_mediator import NetworkMediator
from src.openclaw.tool_registry import get_tool_registry
from src.services.weather_service import (
    WeatherService,
    _weather_disclosure_classifier,
)


class _Registry:
    def get(self, _capability_id: int):
        return object()

    def is_enabled(self, _capability_id: int) -> bool:
        return True


class _Sink:
    def __init__(self) -> None:
        self.records = []

    def append(self, record) -> None:
        self.records.append(record)


def _weather_facts(*, url: str, method: str = "GET", params=None, capability_id=55):
    return disclosure_facts(
        transport=TransportClass.HTTP,
        method=method,
        url=url,
        params=(
            params
            if params is not None
            else {
                "key": "synthetic-weather-secret",
                "unitGroup": "us",
                "include": "current,days,alerts",
                "contentType": "json",
            }
        ),
        capability_id=capability_id,
    )


def test_weather_classifier_binds_exact_shape_and_scoped_api_key_category():
    url = (
        "https://weather.visualcrossing.com/"
        "VisualCrossingWebServices/rest/services/timeline/Ann%20Arbor,%20MI/today"
    )
    classifier = _weather_disclosure_classifier(
        url,
        initiation=InitiationClass.USER_INITIATED,
    )

    context = classifier(_weather_facts(url=url))

    assert context is not None
    assert context.caller == "weather_service.capability_55"
    assert context.purpose == "weather_forecast_retrieval"
    assert context.provider == "visual_crossing"
    assert context.provider_class is ProviderClass.WEATHER
    assert context.data_categories == frozenset({DataCategory.LOCATION})
    assert context.credential_categories == frozenset(
        {CredentialCategory.API_KEY}
    )
    assert context.initiation is InitiationClass.USER_INITIATED

    # The generic field-name classifier must not globally treat every `key`
    # parameter as an API credential. This adapter owns that narrow mapping.
    assert _weather_facts(url=url).credential_categories == frozenset()


@pytest.mark.parametrize(
    "facts",
    [
        _weather_facts(
            url=(
                "https://weather.visualcrossing.com/"
                "VisualCrossingWebServices/rest/services/timeline/Ann%20Arbor,%20MI/today"
            ),
            method="POST",
        ),
        _weather_facts(
            url=(
                "https://weather.visualcrossing.com/"
                "VisualCrossingWebServices/rest/services/timeline/Detroit/today"
            )
        ),
        _weather_facts(
            url=(
                "https://weather.visualcrossing.com/"
                "VisualCrossingWebServices/rest/services/timeline/Ann%20Arbor,%20MI/today"
            ),
            params={"key": "synthetic-weather-secret"},
        ),
        _weather_facts(
            url=(
                "https://weather.visualcrossing.com/"
                "VisualCrossingWebServices/rest/services/timeline/Ann%20Arbor,%20MI/today"
            ),
            capability_id=16,
        ),
    ],
)
def test_weather_classifier_rejects_changed_request(facts):
    expected_url = (
        "https://weather.visualcrossing.com/"
        "VisualCrossingWebServices/rest/services/timeline/Ann%20Arbor,%20MI/today"
    )
    classifier = _weather_disclosure_classifier(
        expected_url,
        initiation=InitiationClass.USER_INITIATED,
    )

    assert classifier(facts) is None


@pytest.mark.parametrize("with_policy", [False, True])
def test_weather_default_denial_precedes_dns_and_session(
    monkeypatch,
    with_policy,
):
    monkeypatch.setenv("WEATHER_API_KEY", "synthetic-weather-secret")
    attempts = {"dns": 0, "session": 0}

    def forbidden_dns(*_args, **_kwargs):
        attempts["dns"] += 1
        raise AssertionError("weather denial must precede DNS")

    def forbidden_session(*_args, **_kwargs):
        attempts["session"] += 1
        raise AssertionError("weather denial must precede session construction")

    monkeypatch.setattr(
        "src.governor.network_mediator.socket.getaddrinfo",
        forbidden_dns,
    )
    monkeypatch.setattr(
        "src.governor.network_mediator.requests.Session",
        forbidden_session,
    )
    mediator = NetworkMediator(
        disclosure_policy=(DisclosurePolicy(version="weather-test-v1") if with_policy else None),
        disclosure_evidence_sink=None,
    )
    mediator._registry = _Registry()

    with pytest.raises(RuntimeError, match="Weather API failed"):
        asyncio.run(WeatherService(network=mediator).get_current_weather())

    assert attempts == {"dns": 0, "session": 0}


def test_weather_denial_evidence_is_sanitized_and_taxonomically_complete(
    monkeypatch,
):
    secret = "synthetic-weather-secret-must-not-persist"
    monkeypatch.setenv("WEATHER_API_KEY", secret)
    sink = _Sink()
    mediator = NetworkMediator(
        disclosure_policy=DisclosurePolicy(version="weather-test-v1"),
        disclosure_evidence_sink=sink,
    )
    mediator._registry = _Registry()

    with pytest.raises(RuntimeError, match="Weather API failed"):
        asyncio.run(WeatherService(network=mediator).get_current_weather())

    assert len(sink.records) == 1  # policy denial is not a retryable outage
    record = sink.records[0]
    assert record.data_categories == (DataCategory.LOCATION.value,)
    assert record.credential_categories == (CredentialCategory.API_KEY.value,)
    assert record.initiation == InitiationClass.USER_INITIATED.value
    assert secret not in repr(sink.records)


def test_weather_synthetic_allow_uses_injected_boundary_and_exact_taxonomy(
    monkeypatch,
):
    secret = "synthetic-weather-secret-must-not-persist"
    monkeypatch.setenv("WEATHER_API_KEY", secret)
    url = (
        "https://weather.visualcrossing.com/"
        "VisualCrossingWebServices/rest/services/timeline/Ann%20Arbor,%20MI/today"
    )
    params = {
        "key": secret,
        "unitGroup": "us",
        "include": "current,days,alerts",
        "contentType": "json",
    }
    facts = _weather_facts(url=url, params=params)
    policy = DisclosurePolicy(
        version="weather-test-v1",
        grants=(
            DisclosureGrant(
                provider="visual_crossing",
                provider_class=ProviderClass.WEATHER,
                destination_class=DestinationClass.EXTERNAL_WEB,
                destinations=frozenset({url}),
                effective_routes=frozenset({"direct"}),
                transports=frozenset({TransportClass.HTTP}),
                data_categories=frozenset({DataCategory.LOCATION}),
                http_methods=frozenset({"GET"}),
                request_shapes=frozenset({facts.request_shape}),
                credential_categories=frozenset({CredentialCategory.API_KEY}),
                purposes=frozenset({"weather_forecast_retrieval"}),
                callers=frozenset({"weather_service.capability_55"}),
                capability_ids=frozenset({55}),
                initiations=frozenset({InitiationClass.USER_INITIATED}),
            ),
        ),
    )
    sink = _Sink()
    mediator = NetworkMediator(
        disclosure_policy=policy,
        disclosure_evidence_sink=sink,
        # Prove the caller-scoped adapter composes with, rather than replaces,
        # the injected policy/evidence boundary.
        disclosure_classifier=lambda _facts: None,
    )
    mediator._registry = _Registry()
    mediator._validate_url = lambda _url: None

    class _Response:
        status_code = 200
        content = b'{"currentConditions":{"temp":70,"conditions":"Clear"}}'
        text = content.decode("utf-8")
        is_redirect = False
        is_permanent_redirect = False

        def raise_for_status(self):
            return None

        def json(self):
            return {
                "currentConditions": {"temp": 70, "conditions": "Clear"},
                "resolvedAddress": "Ann Arbor, MI",
                "days": [],
                "alerts": [],
            }

    class _Session:
        def request(self, **_kwargs):
            return _Response()

    mediator._new_session = _Session

    data = asyncio.run(WeatherService(network=mediator).get_current_weather())

    assert data["temperature"] == 70
    assert len(sink.records) == 1
    assert sink.records[0].decision == "allow"
    assert sink.records[0].credential_categories == ("api_key",)
    assert secret not in repr(sink.records)


def test_weather_preserves_injected_mediator_and_direct_initiation(monkeypatch):
    monkeypatch.setenv("WEATHER_API_KEY", "synthetic-weather-secret")

    class _CapturingMediator:
        def __init__(self) -> None:
            self.contexts = []

        def request(self, **kwargs):
            facts = _weather_facts(
                url=kwargs["url"],
                method=kwargs["method"],
                params=kwargs["params"],
                capability_id=kwargs["capability_id"],
            )
            self.contexts.append(kwargs["disclosure_classifier"](facts))
            return {
                "status_code": 200,
                "data": {
                    "currentConditions": {"temp": 70, "conditions": "Clear"},
                    "resolvedAddress": "Ann Arbor, MI",
                    "days": [],
                    "alerts": [],
                },
            }

    mediator = _CapturingMediator()
    service = WeatherService(network=mediator)

    asyncio.run(service.get_current_weather())

    assert service.network is mediator
    assert mediator.contexts[0].initiation is InitiationClass.USER_INITIATED


def test_daily_brief_weather_uses_automatic_initiation(monkeypatch):
    monkeypatch.setenv("WEATHER_API_KEY", "synthetic-weather-secret")

    class _CapturingMediator:
        def __init__(self) -> None:
            self.contexts = []

        def request(self, **kwargs):
            facts = _weather_facts(
                url=kwargs["url"],
                method=kwargs["method"],
                params=kwargs["params"],
                capability_id=kwargs["capability_id"],
            )
            self.contexts.append(kwargs["disclosure_classifier"](facts))
            return {
                "status_code": 200,
                "data": {
                    "currentConditions": {"temp": 70, "conditions": "Clear"},
                    "resolvedAddress": "Ann Arbor, MI",
                    "days": [],
                    "alerts": [],
                },
            }

    mediator = _CapturingMediator()

    result = asyncio.run(_fetch_weather_for_brief(mediator))

    assert result is not None
    assert mediator.contexts[0].initiation is InitiationClass.AUTOMATIC


def test_openclaw_weather_uses_approved_initiation():
    marker = object()

    skill = get_tool_registry().create("weather", network=marker)

    assert skill.service.network is marker
    assert skill.service.initiation is InitiationClass.APPROVED


@pytest.mark.parametrize(
    ("location", "encoded"),
    [
        ("Ann Arbor, MI", "Ann%20Arbor,%20MI"),
        ("Paris?units=metric", "Paris%3Funits%3Dmetric"),
        ("Rome#fragment", "Rome%23fragment"),
        ("100% Real", "100%25%20Real"),
        ("Montréal", "Montr%C3%A9al"),
    ],
)
def test_weather_location_is_encoded_as_one_path_segment(location, encoded):
    service = WeatherService(location=location)

    url = service._build_request_url()

    assert url == (
        "https://weather.visualcrossing.com/"
        f"VisualCrossingWebServices/rest/services/timeline/{encoded}/today"
    )


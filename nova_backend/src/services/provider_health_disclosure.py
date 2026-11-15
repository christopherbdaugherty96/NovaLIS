"""Caller-scoped Data-Out classification for fixed provider-health probes."""

from __future__ import annotations

from dataclasses import dataclass

from src.governor.disclosure_policy import (
    CredentialCategory,
    DataCategory,
    InitiationClass,
    ProviderClass,
    TransportClass,
)
from src.governor.disclosure_transport import HttpDisclosureContext


@dataclass(frozen=True)
class ProviderHealthDisclosureSpec:
    url: str
    provider: str
    provider_class: ProviderClass
    parameters: frozenset[str]
    headers: frozenset[str]
    credentials: frozenset[CredentialCategory]


PROVIDER_HEALTH_SPECS = {
    "openai": ProviderHealthDisclosureSpec(
        url="https://api.openai.com/v1/models",
        provider="openai",
        provider_class=ProviderClass.HOSTED_MODEL,
        parameters=frozenset(),
        headers=frozenset({"authorization"}),
        credentials=frozenset({CredentialCategory.BEARER_TOKEN}),
    ),
    "brave": ProviderHealthDisclosureSpec(
        url="https://api.search.brave.com/res/v1/web/search",
        provider="brave_search",
        provider_class=ProviderClass.SEARCH,
        parameters=frozenset({"count", "q"}),
        headers=frozenset({"accept", "x-subscription-token"}),
        credentials=frozenset({CredentialCategory.ORIGIN_CREDENTIAL}),
    ),
    "news": ProviderHealthDisclosureSpec(
        url="https://newsapi.org/v2/top-headlines",
        provider="newsapi",
        provider_class=ProviderClass.NEWS_SOURCE,
        parameters=frozenset({"apiKey", "country", "pageSize"}),
        headers=frozenset(),
        credentials=frozenset({CredentialCategory.API_KEY}),
    ),
    "weather": ProviderHealthDisclosureSpec(
        url=(
            "https://weather.visualcrossing.com/VisualCrossingWebServices/"
            "rest/services/timeline/london"
        ),
        provider="visual_crossing",
        provider_class=ProviderClass.WEATHER,
        parameters=frozenset({"contentType", "include", "key", "unitGroup"}),
        headers=frozenset(),
        credentials=frozenset({CredentialCategory.API_KEY}),
    ),
}


def provider_health_disclosure_classifier(provider: str):
    """Classify only one exact user-initiated settings health request."""

    provider_id = str(provider or "").strip().lower()
    spec = PROVIDER_HEALTH_SPECS.get(provider_id)

    def classify(facts):
        if (
            spec is None
            or facts.transport is not TransportClass.HTTP
            or facts.method != "GET"
            or facts.destination != spec.url
            or facts.capability_id is not None
            or not facts.shape_supported
            or facts.query_fields
            or frozenset(facts.parameter_fields) != spec.parameters
            or len(facts.parameter_fields) != len(spec.parameters)
            or frozenset(facts.header_fields) != spec.headers
            or len(facts.header_fields) != len(spec.headers)
            or facts.cookie_fields
            or facts.json_fields
            or facts.form_fields
            or not facts.credential_categories.issubset(spec.credentials)
        ):
            return None
        return HttpDisclosureContext(
            caller=f"settings_provider_health.{provider_id}",
            purpose="provider_health_verification",
            provider=spec.provider,
            provider_class=spec.provider_class,
            data_categories=frozenset({DataCategory.STRUCTURAL_METADATA}),
            credential_categories=spec.credentials,
            initiation=InitiationClass.USER_INITIATED,
        )

    return classify

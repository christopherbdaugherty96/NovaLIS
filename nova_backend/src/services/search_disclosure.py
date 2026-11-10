"""Caller-scoped Data-Out classification for Nova's fixed search providers."""

from __future__ import annotations

from src.governor.disclosure_policy import (
    CredentialCategory,
    DataCategory,
    InitiationClass,
    ProviderClass,
    TransportClass,
)
from src.governor.disclosure_transport import HttpDisclosureContext
from src.governor.exceptions import DisclosureDeniedError, NetworkMediatorError

BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"
DUCK_SEARCH_URL = "https://api.duckduckgo.com/"

_SPECS = {
    "brave": {
        "url": BRAVE_SEARCH_URL,
        "provider": "brave_search",
        "parameters": ("count", "q"),
        "headers": ("accept", "x-subscription-token"),
        "credentials": frozenset({CredentialCategory.ORIGIN_CREDENTIAL}),
    },
    "duckduckgo": {
        "url": DUCK_SEARCH_URL,
        "provider": "duckduckgo",
        "parameters": ("format", "no_html", "no_redirect", "q", "skip_disambig"),
        "headers": ("accept",),
        "credentials": frozenset(),
    },
}


def is_disclosure_denial(error: BaseException) -> bool:
    return isinstance(error, DisclosureDeniedError)


def is_network_mediator_error(error: BaseException) -> bool:
    return isinstance(error, NetworkMediatorError)


def search_disclosure_classifier(
    *,
    provider: str,
    capability_id: int,
    initiation: InitiationClass,
):
    """Classify only the exact supported Cap 16/48 fixed-search request."""

    normalized_provider = str(provider or "").strip().lower()
    spec = _SPECS.get(normalized_provider)
    expected_capability = int(capability_id)
    if expected_capability not in {16, 48}:
        spec = None
    if not isinstance(initiation, InitiationClass):
        spec = None

    def classify(facts):
        if (
            spec is None
            or facts.transport is not TransportClass.HTTP
            or facts.method != "GET"
            or facts.destination != spec["url"]
            or facts.capability_id != expected_capability
            or not facts.shape_supported
            or facts.query_fields
            or facts.parameter_fields != spec["parameters"]
            or facts.header_fields != spec["headers"]
            or facts.cookie_fields
            or facts.json_fields
            or facts.form_fields
            or facts.credential_categories != spec["credentials"]
        ):
            return None
        return HttpDisclosureContext(
            caller=f"fixed_search.capability_{expected_capability}",
            purpose="web_search_query",
            provider=str(spec["provider"]),
            provider_class=ProviderClass.SEARCH,
            data_categories=frozenset({DataCategory.SEARCH_QUERY}),
            initiation=initiation,
        )

    return classify

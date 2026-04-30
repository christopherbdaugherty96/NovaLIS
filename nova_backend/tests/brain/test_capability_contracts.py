import pytest

from src.brain.capability_contracts import (
    CapabilityContractNotFound,
    capability_contract_summary,
    get_capability_contract,
    list_capability_contracts,
    require_capability_contract,
)
from src.brain.environment_request import AuthorityTier, EnvironmentType


PRIORITY_KEYS = {
    "cap16_governed_web_search",
    "cap64_send_email_draft",
    "cap65_shopify_intelligence_report",
    "cap63_openclaw_execute",
}


def _contract(key_or_id):
    return require_capability_contract(key_or_id).contract


def _joined(values: list[str]) -> str:
    return " | ".join(values).lower()


def test_all_priority_contracts_load():
    keys = {entry.key for entry in list_capability_contracts()}

    assert PRIORITY_KEYS.issubset(keys)


def test_all_contracts_have_required_fields():
    for entry in list_capability_contracts():
        contract = entry.contract
        assert entry.key
        assert contract.capability_id is not None
        assert contract.name
        assert isinstance(contract.environment, EnvironmentType)
        assert isinstance(contract.authority_tier, AuthorityTier)
        assert contract.can
        assert contract.cannot
        assert contract.required_setup
        assert contract.expected_receipts
        assert contract.fallbacks
        assert contract.known_failure_modes


def test_cap64_cannot_send_or_read_email_and_requires_confirmation():
    contract = _contract("cap64_send_email_draft")
    cannot = _joined(contract.cannot)

    assert contract.confirmation_required is True
    assert "send email" in cannot
    assert "access inbox" in cannot
    assert "smtp" in cannot
    assert "read gmail" in cannot
    assert "archive/delete/label email" in cannot
    assert contract.authority_tier == AuthorityTier.EXTERNAL_EFFECT_DRAFT
    assert "EMAIL_DRAFT_CREATED" in contract.expected_receipts
    assert "EMAIL_DRAFT_FAILED" in contract.expected_receipts


def test_cap65_cannot_write_or_mutate_shopify():
    contract = _contract(65)
    cannot = _joined(contract.cannot)

    assert contract.name == "shopify_intelligence_report"
    assert contract.environment == EnvironmentType.SHOPIFY_READ_ONLY
    assert "write shopify" in cannot
    assert "change product price" in cannot
    assert "update products" in cannot
    assert "fulfill orders" in cannot
    assert "refund orders" in cannot
    assert "mutate store state" in cannot


def test_cap16_cannot_bypass_network_mediator_or_ungoverned_network():
    contract = _contract("governed_web_search")
    cannot = _joined(contract.cannot)

    assert contract.capability_id == 16
    assert contract.authority_tier == AuthorityTier.NETWORK_READ
    assert "bypass networkmediator" in cannot
    assert "outside the governed path" in cannot
    assert "perform account actions" in cannot


def test_cap63_cannot_bypass_governor_or_silent_personal_browser_execution():
    contract = _contract("cap63_openclaw_execute")
    cannot = _joined(contract.cannot)

    assert contract.capability_id == 63
    assert contract.confirmation_required is True
    assert "bypass governor" in cannot
    assert "silently use personal browser sessions" in cannot
    assert "perform broad autonomy by default" in cannot


def test_unknown_contract_get_fails_closed_without_summary():
    assert get_capability_contract("unknown_capability") is None

    with pytest.raises(CapabilityContractNotFound):
        require_capability_contract("unknown_capability")
    with pytest.raises(CapabilityContractNotFound):
        capability_contract_summary("unknown_capability")


def test_contract_lookup_supports_key_name_and_id_without_execution():
    by_key = get_capability_contract("cap64_send_email_draft")
    by_name = get_capability_contract("send_email_draft")
    by_id = get_capability_contract(64)

    assert by_key is by_name is by_id
    summary = capability_contract_summary(64)
    assert summary["non_authorizing"] is True
    assert "execute" not in summary
    assert summary["confirmation_required"] is True


def test_no_future_google_runtime_contracts_are_claimed_live():
    keys = {entry.key for entry in list_capability_contracts()}

    assert "google_oauth_connection" not in keys
    assert "gmail_read_only" not in keys
    assert "calendar_read_only" not in keys
    assert "gmail_context_for_email_draft" not in keys

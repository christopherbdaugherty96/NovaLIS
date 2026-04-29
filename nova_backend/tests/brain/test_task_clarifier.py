from src.brain.task_clarifier import clarify_task
from src.conversation.session_router import SessionRouter


def _response(prompt: str) -> str:
    result = clarify_task(prompt)
    assert result.matched is True
    return result.response


def test_ambiguous_contractor_task_asks_for_city_or_service_area():
    result = clarify_task("Find contractors and draft an email.")

    assert result.matched is True
    assert result.missing_fields == ["city_or_service_area"]
    assert "What city or service area should I search in?" in result.response


def test_contractor_email_prompt_does_not_claim_to_search_or_draft_immediately():
    response = _response("Find plumbers and email them.")
    lowered = response.lower()

    assert "after that" in lowered
    assert "will not open an email draft without confirmation" in lowered
    assert "i am searching" not in lowered
    assert "i drafted" not in lowered
    assert "opened" not in lowered


def test_contractor_prompt_with_explicit_location_is_not_blocked_unnecessarily():
    result = clarify_task("Find contractors in Ypsilanti and draft an email.")

    assert result.matched is False


def test_personal_account_settings_prompt_returns_hard_boundary_wording():
    response = _response("Log into my account and change my settings.")

    assert "personal account/browser/account-write environment" in response
    assert "explicit governed capability, confirmation, and proof" in response
    assert "No execution has started" in response


def test_personal_account_settings_prompt_does_not_ask_for_credentials():
    response = _response("Sign into my account and update billing.")
    lowered = response.lower()

    assert "password" not in lowered
    assert "credentials" not in lowered
    assert "send me" not in lowered


def test_browser_comparison_prompt_asks_for_urls_and_distinguishes_environments():
    response = _response("Use the browser to compare two public websites.")

    assert "Which two public websites should I compare?" in response
    assert "governed search/open-website" in response
    assert "OpenClaw isolated-browser environment" in response
    assert "governed plan/confirmation" in response


def test_browser_prompt_does_not_claim_it_will_open_tabs():
    response = _response("Open browser and compare these sites.")
    lowered = response.lower()

    assert "open tabs" not in lowered
    assert "i will open" not in lowered
    assert "opening" not in lowered


def test_shopify_write_request_says_cap65_is_read_only_no_write():
    response = _response("Change a Shopify product price.")

    assert "read-only reporting/intelligence" in response
    assert "current Cap 65 path" in response
    assert "I will not write to Shopify" in response


def test_shopify_report_prompt_says_read_only_setup_required():
    response = _response("Create a Shopify report.")

    assert "read-only Shopify intelligence report" in response
    assert "required Shopify environment variables" in response
    assert "does not change products, orders, customers, refunds, or fulfillment" in response


def test_memory_allowed_prompt_says_memory_cannot_authorize_actions():
    response = _response("What is memory allowed to do?")

    assert "Memory can help Nova understand context" in response
    assert "Memory cannot authorize actions" in response
    assert "capability checks" in response
    assert "receipts" in response


def test_cap64_complete_draft_prompt_is_not_intercepted_incorrectly():
    result = clarify_task("Draft an email to test@example.com about tomorrow's meeting.")

    assert result.matched is False


def test_email_draft_missing_recipient_asks_for_recipient_without_executing():
    result = clarify_task("Draft an email about tomorrow.")

    assert result.matched is True
    assert result.missing_fields == ["recipient"]
    assert "Who should the email draft be addressed to?" in result.response
    assert "Nova does not send email" in result.response


def test_session_router_uses_brain_clarifier_gate():
    gate = SessionRouter.evaluate_brain_task_clarifier("Log into my account and change my settings.")

    assert gate.handled is True
    assert "account-write environment" in gate.message


def test_session_router_does_not_gate_complete_email_draft():
    gate = SessionRouter.evaluate_brain_task_clarifier(
        "Draft an email to test@example.com about tomorrow's meeting."
    )

    assert gate.handled is False

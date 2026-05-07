from src.utils.web_target_planner import is_valid_web_domain, normalize_web_url, plan_web_open


def test_open_website_rejects_single_label_target_before_confirmation():
    plan = plan_web_open({"target": "notaurl"})

    assert plan["ok"] is False
    assert "couldn't verify" in plan["message"]
    assert "valid website" in plan["message"]


def test_open_website_accepts_full_domain_and_presets():
    domain_plan = plan_web_open({"target": "example.com"})
    preset_plan = plan_web_open({"target": "github"})

    assert domain_plan["ok"] is True
    assert domain_plan["url"] == "https://example.com"
    assert domain_plan["requires_confirmation"] is True
    assert preset_plan["ok"] is True
    assert preset_plan["url"] == "https://www.github.com"
    assert preset_plan["requires_confirmation"] is False


def test_domain_validation_allows_loopback_and_rejects_bad_hosts():
    assert is_valid_web_domain("localhost:8000")
    assert is_valid_web_domain("127.0.0.1:8000")
    assert normalize_web_url("notaurl") == ""
    assert normalize_web_url("example.com") == "https://example.com"

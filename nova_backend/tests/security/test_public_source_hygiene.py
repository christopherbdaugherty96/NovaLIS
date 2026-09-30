from __future__ import annotations

import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "check_public_source_hygiene.py"
SPEC = importlib.util.spec_from_file_location("check_public_source_hygiene", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_runtime_and_private_business_paths_are_rejected():
    assert MODULE.path_violation("nova_backend/src/data/ledger.jsonl")
    assert MODULE.path_violation("docs/business/private-plan.md")
    assert MODULE.path_violation(
        "docs/future/ai_ecosystem_operating_model/vault_template/03_BUSINESS/client.md"
    )


def test_credentials_and_unapproved_release_artifacts_are_rejected():
    assert MODULE.path_violation("nova_backend/.env")
    assert MODULE.path_violation("config/client_secret_real.json")
    assert MODULE.path_violation("dist/NovaSetup.exe")


def test_public_safe_source_and_synthetic_config_are_allowed():
    assert MODULE.path_violation("nova_backend/src/brain_server.py") is None
    assert MODULE.path_violation("nova_backend/.env.example") is None
    assert MODULE.path_violation("nova_backend/tests/fixtures/synthetic_profile.json") is None

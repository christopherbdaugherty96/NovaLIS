from __future__ import annotations

import ast
from pathlib import Path

from src.connectors.google_workspace.models import FOUNDATION_SCOPES

PACKAGE_ROOT = (
    Path(__file__).resolve().parents[3]
    / "src"
    / "connectors"
    / "google_workspace"
)


def _source() -> str:
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(PACKAGE_ROOT.glob("*.py"))
    )


def test_google_foundation_has_no_domain_data_scope_or_endpoint():
    source = _source().lower()

    assert FOUNDATION_SCOPES == ("openid", "email")
    for forbidden_host in (
        "tasks.googleapis.com",
        "gmail.googleapis.com",
        "calendar.googleapis.com",
        "drive.googleapis.com",
        "docs.googleapis.com",
        "sheets.googleapis.com",
    ):
        assert forbidden_host not in source
    for forbidden_scope in (
        "/auth/tasks",
        "/auth/gmail",
        "/auth/calendar",
        "/auth/drive",
        "/auth/documents",
        "/auth/spreadsheets",
    ):
        assert forbidden_scope not in source


def test_google_foundation_does_not_import_authority_execution_or_model_surfaces():
    imports: set[str] = set()
    for path in PACKAGE_ROOT.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports.update(
            node.module or ""
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        )
        imports.update(
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        )

    forbidden_roots = (
        "src.actions",
        "src.brain",
        "src.conversation",
        "src.executors",
        "src.governor.capability_registry",
        "src.governor.governor",
        "src.governor.governor_mediator",
        "src.ledger",
        "src.llm",
        "src.memory",
        "src.trust",
    )
    assert not any(
        imported == forbidden or imported.startswith(f"{forbidden}.")
        for imported in imports
        for forbidden in forbidden_roots
    )


def test_google_foundation_reuses_source_identity_but_creates_no_domain_evidence():
    source = _source()

    assert "SourceIdentity" in source
    for forbidden_contract in (
        "EvidenceEnvelope",
        "ObservedState",
        "IntendedState",
        "StateDelta",
        "OutcomeSemantics",
    ):
        assert forbidden_contract not in source


def test_google_foundation_has_no_logging_or_serialized_secret_status_fields():
    source = _source()

    assert "import logging" not in source
    assert "logger." not in source
    status_source = (PACKAGE_ROOT / "models.py").read_text(encoding="utf-8")
    status_tree = ast.parse(status_source)
    status_method = next(
        node
        for node in ast.walk(status_tree)
        if isinstance(node, ast.FunctionDef)
        and node.name == "as_dict"
        and node.lineno > 250
    )
    rendered = ast.unparse(status_method)
    for secret_name in (
        "access_token",
        "refresh_token",
        "client_secret",
        "authorization_code",
        "code_verifier",
    ):
        assert secret_name not in rendered

"""Issue #457: commit-identity check for newly introduced commits only.

Proves that a personal (non-noreply) author or committer address in the checked
range is rejected, that GitHub noreply addresses pass, and that already-accepted
historical commits outside the range are never re-litigated.
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
NOREPLY_USER = "247899793+example-user@users.noreply.github.com"
GITHUB_NOREPLY = "noreply@github.com"
# Fixture-only personal address; never a real person's address.
PERSONAL = "someone.personal@example.com"
ZERO_SHA = "0" * 40


def _load_checker():
    script = REPO_ROOT / "scripts" / "check_commit_identity.py"
    spec = importlib.util.spec_from_file_location("commit_identity_checker", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _git(repo: Path, *args: str, env: dict[str, str] | None = None) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, **(env or {})},
    )
    return result.stdout.strip()


def _commit(repo: Path, name: str, *, author: str, committer: str) -> str:
    (repo / f"{name}.txt").write_text(name, encoding="utf-8")
    _git(repo, "add", f"{name}.txt")
    _git(
        repo,
        "commit",
        "-q",
        "-m",
        name,
        env={
            "GIT_AUTHOR_NAME": "Fixture",
            "GIT_AUTHOR_EMAIL": author,
            "GIT_COMMITTER_NAME": "Fixture",
            "GIT_COMMITTER_EMAIL": committer,
        },
    )
    return _git(repo, "rev-parse", "HEAD")


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    _git(tmp_path, "init", "-q", "-b", "main")
    _git(tmp_path, "config", "commit.gpgsign", "false")
    return tmp_path


@pytest.mark.parametrize(
    ("email", "accepted"),
    (
        (NOREPLY_USER, True),
        ("login@users.noreply.github.com", True),
        ("49699333+dependabot[bot]@users.noreply.github.com", True),
        (GITHUB_NOREPLY, True),
        ("NoReply@GitHub.com", True),
        (PERSONAL, False),
        ("someone@gmail.com", False),
        ("x@users.noreply.github.com.evil.example", False),
        ("users.noreply.github.com", False),
        ("x@notusers.noreply.github.com", False),
        ("noreply@github.com.evil.example", False),
        ("", False),
    ),
)
def test_noreply_classification(email, accepted):
    checker = _load_checker()

    assert checker.is_noreply_address(email) is accepted


def test_clean_noreply_range_passes(repo):
    checker = _load_checker()
    base = _commit(repo, "base", author=NOREPLY_USER, committer=GITHUB_NOREPLY)
    _commit(repo, "one", author=NOREPLY_USER, committer=NOREPLY_USER)
    head = _commit(repo, "two", author=NOREPLY_USER, committer=GITHUB_NOREPLY)

    assert checker.check_range(repo, base, head) == []


def test_personal_author_in_range_is_rejected_without_echoing_address(repo):
    checker = _load_checker()
    base = _commit(repo, "base", author=NOREPLY_USER, committer=GITHUB_NOREPLY)
    bad = _commit(repo, "bad", author=PERSONAL, committer=GITHUB_NOREPLY)
    head = _commit(repo, "after", author=NOREPLY_USER, committer=GITHUB_NOREPLY)

    violations = checker.check_range(repo, base, head)

    assert len(violations) == 1
    assert bad in violations[0]
    assert "author" in violations[0]
    assert PERSONAL not in violations[0]


def test_personal_committer_in_range_is_rejected(repo):
    checker = _load_checker()
    base = _commit(repo, "base", author=NOREPLY_USER, committer=GITHUB_NOREPLY)
    head = _commit(repo, "bad", author=NOREPLY_USER, committer=PERSONAL)

    violations = checker.check_range(repo, base, head)

    assert len(violations) == 1
    assert head in violations[0]
    assert "committer" in violations[0]
    assert PERSONAL not in violations[0]


def test_historical_commits_before_base_are_not_rechecked(repo):
    checker = _load_checker()
    _commit(repo, "old-personal", author=PERSONAL, committer=PERSONAL)
    base = _commit(repo, "old-accepted", author=PERSONAL, committer=GITHUB_NOREPLY)
    head = _commit(repo, "new", author=NOREPLY_USER, committer=GITHUB_NOREPLY)

    assert checker.check_range(repo, base, head) == []


def test_zero_base_checks_only_the_pushed_head(repo):
    checker = _load_checker()
    _commit(repo, "old-personal", author=PERSONAL, committer=PERSONAL)
    head = _commit(repo, "new", author=NOREPLY_USER, committer=GITHUB_NOREPLY)

    assert checker.check_range(repo, ZERO_SHA, head) == []

    bad_head = _commit(repo, "bad", author=PERSONAL, committer=GITHUB_NOREPLY)
    assert len(checker.check_range(repo, ZERO_SHA, bad_head)) == 1


def test_cli_exit_codes_and_output_never_print_the_address(repo, capsys):
    checker = _load_checker()
    base = _commit(repo, "base", author=NOREPLY_USER, committer=GITHUB_NOREPLY)
    good = _commit(repo, "good", author=NOREPLY_USER, committer=GITHUB_NOREPLY)

    assert checker.main(["--repo", str(repo), "--base", base, "--head", good]) == 0
    assert "commit-identity: PASS (1 commit checked)" in capsys.readouterr().out

    bad = _commit(repo, "bad", author=PERSONAL, committer=PERSONAL)
    assert checker.main(["--repo", str(repo), "--base", base, "--head", bad]) == 1
    output = capsys.readouterr().out
    assert "commit-identity: FAIL" in output
    assert PERSONAL not in output


def test_workflow_exposes_stable_commit_identity_check():
    rendered = (REPO_ROOT / ".github" / "workflows" / "commit-identity.yml").read_text(
        encoding="utf-8"
    )
    lines = rendered.splitlines()

    # Triggers: pull requests plus pushes to main only; read-only token.
    assert "on:" in lines
    assert "  pull_request:" in lines
    assert "  push:" in lines
    assert "    branches: [main]" in lines
    assert "permissions:" in lines and "  contents: read" in lines
    # Stable job id and check name used by the ruleset.
    assert "  commit-identity:" in lines
    assert "    name: commit-identity" in lines
    # Ranges: PR-introduced commits, and only the newly pushed range on main.
    assert "github.event.pull_request.base.sha" in rendered
    assert "github.event.pull_request.head.sha" in rendered
    assert "github.event.before" in rendered
    assert "python scripts/check_commit_identity.py" in rendered


def test_unresolvable_range_fails_closed(repo, capsys):
    checker = _load_checker()
    head = _commit(repo, "only", author=NOREPLY_USER, committer=GITHUB_NOREPLY)

    assert checker.main(["--repo", str(repo), "--base", "f" * 40, "--head", head]) == 2
    assert "commit-identity: ERROR" in capsys.readouterr().out

"""Fail when newly introduced commits carry a non-noreply author or committer address.

Issue #457 repository hygiene. This checks only the commits in ``base..head``:
the commits a pull request introduces, or the range newly pushed to ``main``.
Already-accepted historical commits outside that range are never re-checked,
rewritten, or failed.

Accepted addresses:
- ``<anything>@users.noreply.github.com`` (GitHub per-account noreply, bots included);
- ``noreply@github.com`` (GitHub web-flow committer).

Violations name the commit and the field, never the address itself, so the check
does not republish a personal address in public CI logs.

Boundary: a pull-request run cannot see the squash commit GitHub creates at merge
time. Preventing a personal address on that commit is the merging account's
"Keep my email addresses private" setting; the push-to-main run audits it after
the fact.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

GITHUB_USER_NOREPLY_SUFFIX = "@users.noreply.github.com"
GITHUB_WEB_FLOW_NOREPLY = "noreply@github.com"
ZERO_SHA = "0" * 40


def is_noreply_address(email: str) -> bool:
    """Return True only for GitHub noreply addresses."""

    normalized = email.strip().lower()
    if normalized == GITHUB_WEB_FLOW_NOREPLY:
        return True
    local, at, _ = normalized.partition("@")
    return bool(local) and bool(at) and normalized.endswith(GITHUB_USER_NOREPLY_SUFFIX)


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True
    ).stdout


def commits_in_range(repo: Path, base: str, head: str) -> list[str]:
    """Return commits introduced by ``base..head``; a zero base means only ``head``."""

    if not base or set(base) == {"0"}:
        return [_git(repo, "rev-parse", f"{head}^{{commit}}").strip()]
    return [line for line in _git(repo, "rev-list", f"{base}..{head}").splitlines() if line]


def check_range(repo: Path, base: str, head: str) -> list[str]:
    """Return one violation line per commit with a non-noreply author or committer."""

    violations: list[str] = []
    for sha in commits_in_range(repo, base, head):
        author, committer = _git(repo, "show", "-s", "--format=%ae%x00%ce", sha).strip().split(
            "\0"
        )
        fields = [
            field
            for field, email in (("author", author), ("committer", committer))
            if not is_noreply_address(email)
        ]
        if fields:
            violations.append(
                f"{sha}: {' and '.join(fields)} email is not a GitHub noreply address"
            )
    return violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", required=True, help="exclusive base commit (zero SHA allowed)")
    parser.add_argument("--head", required=True, help="inclusive head commit")
    parser.add_argument("--repo", default=".", help="repository path (default: current directory)")
    args = parser.parse_args(argv)

    repo = Path(args.repo)
    try:
        checked = len(commits_in_range(repo, args.base, args.head))
        violations = check_range(repo, args.base, args.head)
    except subprocess.CalledProcessError as error:
        # Fail closed: an unresolvable range is never reported as PASS.
        print(f"commit-identity: ERROR (cannot resolve {args.base}..{args.head}: {error.stderr.strip()})")
        return 2
    noun = "commit" if checked == 1 else "commits"
    if violations:
        print(f"commit-identity: FAIL ({len(violations)} of {checked} {noun})")
        for violation in violations:
            print(f"- {violation}")
        print(
            "Use a GitHub noreply address for both author and committer "
            "(Settings > Emails > Keep my email addresses private)."
        )
        return 1
    print(f"commit-identity: PASS ({checked} {noun} checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

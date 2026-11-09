"""Static detection and disposition of supported Data-Out mechanisms.

This module is deliberately non-authorizing.  It inventories syntax that can
create transport, delegation, executable discovery, temporary storage, or a
storage probe.  A registered site is not necessarily safe: the registry keeps
governed, unresolved, and frozen-scope-excluded sites distinct.

The registry is exact-call-site based.  Registering one call does not exempt the
rest of its module, so a new operation in an otherwise reviewed file fails the
checker until it receives an explicit disposition.
"""

from __future__ import annotations

import ast
import json
import re
from collections import Counter
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Iterable

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = Path(__file__).with_name("data_out_mechanism_dispositions.json")


class Mechanism(str, Enum):
    NETWORK_CLIENT = "network_client"
    PROCESS_DELEGATION = "process_delegation"
    APPLICATION_HANDOFF = "application_handoff"
    EXECUTABLE_DISCOVERY = "executable_discovery"
    TEMPORARY_STORAGE = "temporary_storage"
    STORAGE_DIAGNOSTIC = "storage_diagnostic"
    CONFIGURED_STORAGE_ROOT = "configured_storage_root"
    SETUP_ACQUISITION = "setup_acquisition"
    SETUP_SHELL_FOLDER = "setup_shell_folder"


class MechanismStatus(str, Enum):
    GOVERNED = "governed"
    UNRESOLVED = "unresolved"
    EXCLUDED = "excluded"


class ClosureFamily(str, Enum):
    EXTERNAL_READ_AND_SETUP = "F02_external_read_and_setup"
    OPENCLAW_PROVIDER_ROUTES = "F03_openclaw_provider_routes"
    INSTALLER_ACQUISITION = "F04_installer_acquisition"
    NON_OLLAMA_DELEGATION = "F05_non_ollama_delegation"
    TRUSTED_RUNTIME_ROOTS = "F06_trusted_runtime_roots"
    INSTALLATION_STATE_ROOTS = "F07_installation_state_roots"
    USER_AND_TEMP_PATHS = "F08_user_and_temp_paths"
    EXECUTABLE_DISCOVERY_ROOTS = "F09_executable_discovery_roots"
    SETUP_SHELL_FOLDERS = "F10_setup_shell_folders"
    STORAGE_DIAGNOSTICS_ROOTS = "F11_storage_diagnostics_roots"


@dataclass(frozen=True, order=True)
class MechanismSite:
    path: str
    line: int
    column: int


@dataclass(frozen=True, order=True)
class MechanismFinding:
    site: MechanismSite
    mechanism: Mechanism
    symbol: str

    @property
    def line(self) -> int:
        return self.site.line

    @property
    def column(self) -> int:
        return self.site.column


@dataclass(frozen=True)
class MechanismDisposition:
    site: MechanismSite
    mechanism: Mechanism
    symbol: str
    status: MechanismStatus
    closure_family: ClosureFamily | None
    reason: str
    boundary: str | None = None


@dataclass(frozen=True)
class FamilyDisposition:
    family: ClosureFamily
    status: MechanismStatus
    reason: str


@dataclass(frozen=True)
class DispositionReport:
    findings: tuple[MechanismFinding, ...]
    dispositions: tuple[MechanismDisposition, ...]
    families: tuple[FamilyDisposition, ...]
    registered: tuple[MechanismFinding, ...]
    unregistered: tuple[MechanismFinding, ...]
    stale: tuple[MechanismDisposition, ...]


@dataclass(frozen=True)
class DispositionRegistry:
    dispositions: tuple[MechanismDisposition, ...]
    families: tuple[FamilyDisposition, ...] = ()

    def compare(self, findings: Iterable[MechanismFinding]) -> DispositionReport:
        ordered_findings = tuple(sorted(findings))
        by_key = {
            (item.site, item.mechanism, item.symbol): item for item in self.dispositions
        }
        finding_keys = {
            (item.site, item.mechanism, item.symbol) for item in ordered_findings
        }
        registered = tuple(
            item
            for item in ordered_findings
            if (item.site, item.mechanism, item.symbol) in by_key
        )
        unregistered = tuple(
            item
            for item in ordered_findings
            if (item.site, item.mechanism, item.symbol) not in by_key
        )
        stale = tuple(
            item
            for item in self.dispositions
            if (item.site, item.mechanism, item.symbol) not in finding_keys
        )
        return DispositionReport(
            findings=ordered_findings,
            dispositions=self.dispositions,
            families=self.families,
            registered=registered,
            unregistered=unregistered,
            stale=stale,
        )


_PYTHON_CALLS: dict[str, Mechanism] = {
    "requests.get": Mechanism.NETWORK_CLIENT,
    "requests.post": Mechanism.NETWORK_CLIENT,
    "requests.put": Mechanism.NETWORK_CLIENT,
    "requests.patch": Mechanism.NETWORK_CLIENT,
    "requests.delete": Mechanism.NETWORK_CLIENT,
    "requests.request": Mechanism.NETWORK_CLIENT,
    "requests.Session": Mechanism.NETWORK_CLIENT,
    "httpx.Client": Mechanism.NETWORK_CLIENT,
    "httpx.AsyncClient": Mechanism.NETWORK_CLIENT,
    "httpx.get": Mechanism.NETWORK_CLIENT,
    "httpx.post": Mechanism.NETWORK_CLIENT,
    "urllib.request.urlopen": Mechanism.NETWORK_CLIENT,
    "urllib.request.build_opener": Mechanism.NETWORK_CLIENT,
    "urllib.request.urlretrieve": Mechanism.NETWORK_CLIENT,
    "socket.socket": Mechanism.NETWORK_CLIENT,
    "socket.create_connection": Mechanism.NETWORK_CLIENT,
    "socket.getaddrinfo": Mechanism.NETWORK_CLIENT,
    "aiohttp.ClientSession": Mechanism.NETWORK_CLIENT,
    "subprocess.run": Mechanism.PROCESS_DELEGATION,
    "subprocess.Popen": Mechanism.PROCESS_DELEGATION,
    "subprocess.call": Mechanism.PROCESS_DELEGATION,
    "subprocess.check_call": Mechanism.PROCESS_DELEGATION,
    "subprocess.check_output": Mechanism.PROCESS_DELEGATION,
    "os.system": Mechanism.PROCESS_DELEGATION,
    "webbrowser.open": Mechanism.APPLICATION_HANDOFF,
    "webbrowser.open_new": Mechanism.APPLICATION_HANDOFF,
    "webbrowser.open_new_tab": Mechanism.APPLICATION_HANDOFF,
    "os.startfile": Mechanism.APPLICATION_HANDOFF,
    "shutil.which": Mechanism.EXECUTABLE_DISCOVERY,
    "tempfile.NamedTemporaryFile": Mechanism.TEMPORARY_STORAGE,
    "tempfile.TemporaryDirectory": Mechanism.TEMPORARY_STORAGE,
    "tempfile.mkstemp": Mechanism.TEMPORARY_STORAGE,
    "tempfile.mkdtemp": Mechanism.TEMPORARY_STORAGE,
    "shutil.disk_usage": Mechanism.STORAGE_DIAGNOSTIC,
}

_CONFIGURED_STORAGE_VARIABLES = {
    "NOVA_RUNTIME_DIR",
    "NOVA_CALENDAR_ICS_PATH",
    "NOVA_PIPER_MODEL_PATH",
    "LOCALAPPDATA",
    "APPDATA",
    "TEMP",
    "TMP",
    "HOME",
    "USERPROFILE",
    "ProgramFiles",
    "ProgramFiles(x86)",
}

_TEXT_PATTERNS: tuple[tuple[re.Pattern[str], str, Mechanism], ...] = (
    (
        re.compile(r"(?i)^\s*winget(?:\.exe)?\s+install\b"),
        "winget install",
        Mechanism.SETUP_ACQUISITION,
    ),
    (
        re.compile(r"(?i)\bInvoke-ExternalStep\b.*-m\s+pip\s+install\b"),
        "pip install",
        Mechanism.SETUP_ACQUISITION,
    ),
    (
        re.compile(r"(?i)(?:\bStart-Process\b|&\s*\$[A-Za-z_][\w]*)"),
        "powershell process launch",
        Mechanism.PROCESS_DELEGATION,
    ),
    (
        re.compile(r"(?i)\b(?:xdg-open|open)\s+['\"$]"),
        "shell application handoff",
        Mechanism.APPLICATION_HANDOFF,
    ),
    (
        re.compile(r"(?i)\b(?:command\s+-v|Get-Command)\b"),
        "shell executable discovery",
        Mechanism.EXECUTABLE_DISCOVERY,
    ),
    (
        re.compile(r"(?i)\b(?:New-Item|Test-Path)\b"),
        "powershell filesystem probe",
        Mechanism.SETUP_SHELL_FOLDER,
    ),
    (
        re.compile(r"(?i)\.(?:CreateShortcut|Save)\s*\("),
        "shortcut write",
        Mechanism.SETUP_SHELL_FOLDER,
    ),
    (
        re.compile(r'(?i)^\s*Name:\s*"\{(?:group|autodesktop)\}'),
        "inno shortcut destination",
        Mechanism.SETUP_SHELL_FOLDER,
    ),
)

_PYTHON_SCAN_ROOTS = (
    Path("nova_backend/src"),
    Path("scripts/start_daemon.py"),
    Path("scripts/stop_daemon.py"),
    Path("scripts/fetch_models.py"),
)
_TEXT_SCAN_PATHS = (
    Path("installer/windows/installer_acquisition_admission.ps1"),
    Path("installer/windows/nova_bootstrap.ps1"),
    Path("installer/windows/nova_setup.iss"),
    Path("start_nova.sh"),
)


def _is_archive_or_quarantine(path: Path) -> bool:
    return any(
        "archive" in part.lower() or "quarantine" in part.lower()
        for part in path.parts
    )


def _attribute_name(node: ast.AST) -> str | None:
    parts: list[str] = []
    current = node
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if isinstance(current, ast.Name):
        parts.append(current.id)
        return ".".join(reversed(parts))
    return None


def _import_aliases(nodes: list[ast.stmt]) -> dict[str, str]:
    aliases: dict[str, str] = {}
    pending: list[ast.AST] = list(nodes)
    while pending:
        node = pending.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            continue
        if isinstance(node, ast.Import):
            for item in node.names:
                if item.asname:
                    aliases[item.asname] = item.name
                else:
                    root = item.name.split(".", 1)[0]
                    aliases[root] = root
        elif isinstance(node, ast.ImportFrom) and node.module:
            for item in node.names:
                if item.name == "*":
                    continue
                aliases[item.asname or item.name] = f"{node.module}.{item.name}"
        else:
            pending.extend(ast.iter_child_nodes(node))
    return aliases


def _canonical_name(raw_name: str, aliases: dict[str, str]) -> str:
    head, separator, tail = raw_name.partition(".")
    canonical_head = aliases.get(head, head)
    return canonical_head + (separator + tail if separator else "")


def _configured_storage_symbol(
    node: ast.Call, canonical: str, aliases: dict[str, str]
) -> str | None:
    if canonical not in {"os.getenv", "os.environ.get"} or not node.args:
        return None
    first = node.args[0]
    if not isinstance(first, ast.Constant) or not isinstance(first.value, str):
        return None
    if first.value not in _CONFIGURED_STORAGE_VARIABLES:
        return None
    return f"{canonical}:{first.value}"


def scan_python_file(
    path: Path, *, repository_root: Path = REPOSITORY_ROOT
) -> tuple[MechanismFinding, ...]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    relative = path.resolve().relative_to(repository_root.resolve()).as_posix()

    class MechanismVisitor(ast.NodeVisitor):
        def __init__(self) -> None:
            module_aliases = _import_aliases(tree.body)
            self.aliases = module_aliases
            self.closure_aliases = module_aliases
            self.findings: list[MechanismFinding] = []

        def _visit_function(
            self, node: ast.FunctionDef | ast.AsyncFunctionDef
        ) -> None:
            for decorator in node.decorator_list:
                self.visit(decorator)
            for default in (*node.args.defaults, *node.args.kw_defaults):
                if default is not None:
                    self.visit(default)
            previous_aliases = self.aliases
            previous_closure = self.closure_aliases
            local_aliases = dict(self.closure_aliases)
            local_aliases.update(_import_aliases(node.body))
            self.aliases = local_aliases
            self.closure_aliases = local_aliases
            for statement in node.body:
                self.visit(statement)
            self.aliases = previous_aliases
            self.closure_aliases = previous_closure

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            self._visit_function(node)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            self._visit_function(node)

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            for decorator in node.decorator_list:
                self.visit(decorator)
            for base in node.bases:
                self.visit(base)
            previous_aliases = self.aliases
            previous_closure = self.closure_aliases
            class_aliases = dict(self.closure_aliases)
            class_aliases.update(_import_aliases(node.body))
            self.aliases = class_aliases
            # Class-local names are not lexical closures for method bodies.
            for statement in node.body:
                self.visit(statement)
            self.aliases = previous_aliases
            self.closure_aliases = previous_closure

        def visit_Call(self, node: ast.Call) -> None:
            raw_name = _attribute_name(node.func)
            if raw_name is not None:
                canonical = _canonical_name(raw_name, self.aliases)
                mechanism = _PYTHON_CALLS.get(canonical)
                symbol = canonical
                storage_symbol = _configured_storage_symbol(
                    node, canonical, self.aliases
                )
                if storage_symbol is not None:
                    mechanism = Mechanism.CONFIGURED_STORAGE_ROOT
                    symbol = storage_symbol
                if mechanism is not None:
                    self.findings.append(
                        MechanismFinding(
                            site=MechanismSite(
                                relative, node.lineno, node.col_offset
                            ),
                            mechanism=mechanism,
                            symbol=symbol,
                        )
                    )
            self.generic_visit(node)

    visitor = MechanismVisitor()
    for statement in tree.body:
        visitor.visit(statement)
    return tuple(sorted(visitor.findings))


def scan_text_file(
    path: Path, *, repository_root: Path = REPOSITORY_ROOT
) -> tuple[MechanismFinding, ...]:
    relative = path.resolve().relative_to(repository_root.resolve()).as_posix()
    findings: list[MechanismFinding] = []
    in_block_comment = False
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        stripped = line.lstrip()
        if in_block_comment:
            if "#>" in stripped:
                in_block_comment = False
            continue
        if stripped.startswith("<#"):
            in_block_comment = "#>" not in stripped
            continue
        if not stripped or stripped.startswith(("#", ";")):
            continue
        for pattern, symbol, mechanism in _TEXT_PATTERNS:
            for match in pattern.finditer(line):
                findings.append(
                    MechanismFinding(
                        site=MechanismSite(relative, line_number, match.start()),
                        mechanism=mechanism,
                        symbol=symbol,
                    )
                )
    return tuple(sorted(findings))


def scan_repository(
    repository_root: Path = REPOSITORY_ROOT,
) -> tuple[MechanismFinding, ...]:
    findings: list[MechanismFinding] = []
    for configured in _PYTHON_SCAN_ROOTS:
        target = repository_root / configured
        paths = target.rglob("*.py") if target.is_dir() else (target,)
        for path in paths:
            if path.exists() and not _is_archive_or_quarantine(path):
                findings.extend(scan_python_file(path, repository_root=repository_root))
    for relative in _TEXT_SCAN_PATHS:
        path = repository_root / relative
        if path.exists():
            findings.extend(scan_text_file(path, repository_root=repository_root))
    return tuple(sorted(set(findings)))


def _load_registry(path: Path = REGISTRY_PATH) -> DispositionRegistry:
    payload: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    dispositions = tuple(
        MechanismDisposition(
            site=MechanismSite(
                path=str(item["path"]),
                line=int(item["line"]),
                column=int(item["column"]),
            ),
            mechanism=Mechanism(item["mechanism"]),
            symbol=str(item["symbol"]),
            status=MechanismStatus(item["status"]),
            closure_family=(
                ClosureFamily(item["closure_family"])
                if item.get("closure_family")
                else None
            ),
            reason=str(item["reason"]),
            boundary=str(item["boundary"]) if item.get("boundary") else None,
        )
        for item in payload["dispositions"]
    )
    families = tuple(
        FamilyDisposition(
            family=ClosureFamily(item["id"]),
            status=MechanismStatus(item["status"]),
            reason=str(item["reason"]),
        )
        for item in payload["closure_families"]
    )
    disposition_keys = [
        (item.site, item.mechanism, item.symbol) for item in dispositions
    ]
    if len(disposition_keys) != len(set(disposition_keys)):
        raise ValueError("Data-Out mechanism registry contains duplicate exact-site entries.")
    family_ids = [item.family for item in families]
    if len(family_ids) != len(set(family_ids)):
        raise ValueError("Data-Out mechanism registry contains duplicate closure families.")
    for item in dispositions:
        if item.status is MechanismStatus.UNRESOLVED and item.closure_family is None:
            raise ValueError(
                f"Unresolved Data-Out mechanism lacks a closure family: {item.site}"
            )
        if item.status is MechanismStatus.GOVERNED and not item.boundary:
            raise ValueError(
                f"Governed Data-Out mechanism lacks a boundary: {item.site}"
            )
    return DispositionRegistry(dispositions=dispositions, families=families)


def validate_repository_dispositions(
    repository_root: Path = REPOSITORY_ROOT,
    registry_path: Path = REGISTRY_PATH,
) -> DispositionReport:
    return _load_registry(registry_path).compare(scan_repository(repository_root))


def report_as_dict(report: DispositionReport) -> dict[str, Any]:
    def finding_payload(item: MechanismFinding) -> dict[str, Any]:
        return {
            "path": item.site.path,
            "line": item.site.line,
            "column": item.site.column,
            "mechanism": item.mechanism.value,
            "symbol": item.symbol,
        }

    status_counts = Counter(item.status.value for item in report.dispositions)
    return {
        "summary": {
            "detected": len(report.findings),
            "registered": len(report.registered),
            "unregistered": len(report.unregistered),
            "stale": len(report.stale),
            "governed": status_counts[MechanismStatus.GOVERNED.value],
            "unresolved": status_counts[MechanismStatus.UNRESOLVED.value],
            "excluded": status_counts[MechanismStatus.EXCLUDED.value],
        },
        "closure_families": [
            {
                "id": item.family.value,
                "status": item.status.value,
                "reason": item.reason,
            }
            for item in report.families
        ],
        "unregistered": [finding_payload(item) for item in report.unregistered],
        "stale": [
            {
                "path": item.site.path,
                "line": item.site.line,
                "column": item.site.column,
                "mechanism": item.mechanism.value,
                "symbol": item.symbol,
            }
            for item in report.stale
        ],
    }

# src/utils/path_resolver.py
"""
Local path resolution and project exploration utilities for the Nova brain server.

All functions here are pure or filesystem-read-only. No session state, no network,
no writes. Extracted from brain_server.py to keep the orchestration file focused
on routing and response shaping.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Optional

from src.websocket.intent_patterns import LOCAL_LOCATION_HINT_RE

# -------------------------------------------------
# Project surface / backend module hints
# -------------------------------------------------
PROJECT_SURFACE_HINTS = {
    "docs": "human guides, runtime truth, proofs, and design packets",
    "nova_backend": "backend runtime, governor flow, executors, and tests",
    "Nova-Frontend-Dashboard": "frontend/dashboard surface for the workspace UI",
    "nova_workspace": "workspace state and local project context",
    "NovaLIS-Governance": "governance and companion policy material",
    "scripts": "local scripts and helper tooling",
    "verification": "verification assets and support material",
}
BACKEND_MODULE_HINTS = {
    "governor": "governed capability routing and execution boundaries",
    "executors": "read-only and local-effect task implementations",
    "conversation": "input normalization, response shaping, and session routing",
    "working_context": "project thread and context continuity state",
    "memory": "governed memory storage and retrieval",
    "perception": "screen and local perception helpers",
    "personality": "style contract and interface presentation rules",
    "voice": "speech input and output runtime pieces",
}


# -------------------------------------------------
# Basic path helpers
# -------------------------------------------------

def _normalize_lookup_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value or "").strip().lower())


def _resolve_existing_local_path(raw_value: str) -> Path | None:
    cleaned = str(raw_value or "").strip().strip("\"'")
    if not cleaned:
        return None
    try:
        candidate = Path(cleaned)
        if not candidate.is_absolute():
            candidate = (Path.cwd() / candidate).resolve()
        else:
            candidate = candidate.resolve()
    except Exception:
        return None
    if candidate.exists():
        return candidate
    return None


def _split_local_location_hint(raw_value: str) -> tuple[str, str]:
    cleaned = str(raw_value or "").strip()
    if not cleaned:
        return "", ""

    match = LOCAL_LOCATION_HINT_RE.match(cleaned)
    if not match:
        return cleaned, ""

    target = str(match.group("target") or "").strip().strip("\"'")
    location = re.sub(r"\s+", " ", str(match.group("location") or "").strip().lower())
    return target, location


def _candidate_local_project_paths(
    working_context: Any,
    session_state: dict[str, Any],
) -> list[Path]:
    candidates: list[Path] = []
    seen: set[str] = set()

    def _add(path_value: Path | None) -> None:
        if path_value is None:
            return
        try:
            resolved = path_value.resolve()
        except Exception:
            return
        key = str(resolved).lower()
        if key in seen or not resolved.exists():
            return
        seen.add(key)
        candidates.append(resolved)

    try:
        cwd = Path.cwd().resolve()
    except Exception:
        cwd = None

    if cwd is not None:
        git_root = None
        for candidate in [cwd, *cwd.parents]:
            try:
                if (candidate / ".git").exists():
                    git_root = candidate
                    break
            except Exception:
                continue
        _add(git_root)
        _add(cwd)
        for parent in list(cwd.parents)[:3]:
            _add(parent)

    selected_file = str((working_context.to_dict() or {}).get("selected_file") or "").strip()
    if selected_file:
        selected_path = _resolve_existing_local_path(selected_file)
        if selected_path is not None:
            _add(selected_path if selected_path.is_dir() else selected_path.parent)

    last_object = str(session_state.get("last_object") or "").strip()
    if last_object:
        last_path = _resolve_existing_local_path(last_object)
        if last_path is not None:
            _add(last_path if last_path.is_dir() else last_path.parent)

    return candidates


def _resolve_local_project_path(
    target_text: str,
    *,
    working_context: Any,
    session_state: dict[str, Any],
) -> Path | None:
    raw_target = str(target_text or "").strip()
    if not raw_target:
        paths = _candidate_local_project_paths(working_context, session_state)
        return paths[0] if paths else None

    direct_path = _resolve_existing_local_path(raw_target)
    if direct_path is not None:
        return direct_path

    normalized_target = _normalize_lookup_key(raw_target)
    if normalized_target in {
        "thisrepo",
        "thisrepository",
        "thisproject",
        "thisfolder",
        "currentrepo",
        "currentproject",
        "currentfolder",
        "localrepo",
        "localproject",
        "localfolder",
    }:
        paths = _candidate_local_project_paths(working_context, session_state)
        return paths[0] if paths else None

    for candidate in _candidate_local_project_paths(working_context, session_state):
        candidate_key = _normalize_lookup_key(candidate.name)
        if normalized_target == candidate_key:
            return candidate

    return None


def _local_project_markers(path: Path) -> list[str]:
    markers = [
        ".git",
        "README.md",
        "pyproject.toml",
        "package.json",
        "requirements.txt",
        "docs",
        "src",
        "tests",
        "nova_backend",
    ]
    found: list[str] = []
    for marker in markers:
        try:
            if (path / marker).exists():
                found.append(marker)
        except Exception:
            continue
    return found


def _read_small_text_file(path: Path, max_chars: int = 6000) -> str:
    for encoding in ("utf-8-sig", "utf-8"):
        try:
            return path.read_text(encoding=encoding)[:max_chars]
        except UnicodeDecodeError:
            continue
        except Exception:
            return ""
    return ""


def _extract_markdown_paragraph(text: str) -> str:
    paragraph_lines: list[str] = []
    for raw_line in str(text or "").splitlines():
        line = str(raw_line or "").replace("\ufeff", "").strip()
        if not line:
            if paragraph_lines:
                break
            continue
        if line.startswith("#") or line.startswith("```"):
            if paragraph_lines:
                break
            continue
        if line.startswith("- ") or line.startswith("* ") or re.match(r"^\d+\.\s+", line):
            if paragraph_lines:
                break
            continue
        paragraph_lines.append(line)

    paragraph = " ".join(paragraph_lines).strip()
    paragraph = re.sub(r"\s+", " ", paragraph).strip()
    if len(paragraph) > 260:
        paragraph = paragraph[:257].rstrip() + "..."
    return paragraph


def _extract_markdown_bullets_after_line(text: str, anchor_line: str, limit: int = 5) -> list[str]:
    lines = str(text or "").splitlines()
    anchor = anchor_line.strip().lower()
    start_index = -1
    for idx, raw_line in enumerate(lines):
        if str(raw_line or "").strip().lower() == anchor:
            start_index = idx + 1
            break
    if start_index < 0:
        return []

    bullets: list[str] = []
    for raw_line in lines[start_index:]:
        line = str(raw_line or "").strip()
        if not line:
            if bullets:
                break
            continue
        if line.startswith("- ") or line.startswith("* "):
            bullets.append(line[2:].strip())
        else:
            if bullets:
                break
            if line.startswith("#"):
                break
        if len(bullets) >= limit:
            break
    return bullets


def _capability_registry_snapshot(path: Path) -> dict[str, Any]:
    registry_path = path / "nova_backend" / "src" / "config" / "registry.json"
    if not registry_path.exists():
        registry_path = path / "src" / "config" / "registry.json"
    if not registry_path.exists():
        return {}

    try:
        payload = json.loads(registry_path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    capabilities = list(payload.get("capabilities") or [])
    active = [cap for cap in capabilities if str(cap.get("status") or "").strip().lower() == "active"]
    active_names = [
        str(cap.get("name") or "").strip().replace("_", " ")
        for cap in active
        if str(cap.get("name") or "").strip()
    ]
    group_names = [
        str(name).replace("_", " ")
        for name, ids in dict(payload.get("capability_groups") or {}).items()
        if isinstance(ids, list) and ids
    ]
    return {
        "active_count": len(active),
        "group_names": group_names[:6],
        "active_names": active_names[:8],
    }


def _major_project_surfaces(path: Path, limit: int = 6) -> list[str]:
    surfaces: list[str] = []
    for name, description in PROJECT_SURFACE_HINTS.items():
        candidate = path / name
        if candidate.exists():
            surfaces.append(f"{name}: {description}")
        if len(surfaces) >= limit:
            break
    if surfaces:
        return surfaces

    try:
        directories = sorted(
            [entry.name for entry in path.iterdir() if entry.is_dir() and not entry.name.startswith(".")],
            key=str.lower,
        )
    except Exception:
        directories = []
    return directories[:limit]


def _major_backend_modules(path: Path, limit: int = 6) -> list[str]:
    src_root = path / "nova_backend" / "src"
    if not src_root.exists():
        src_root = path / "src"
    if not src_root.exists():
        return []

    modules: list[str] = []
    for name, description in BACKEND_MODULE_HINTS.items():
        candidate = src_root / name
        if candidate.exists():
            modules.append(f"{name}: {description}")
        if len(modules) >= limit:
            break
    return modules


# -------------------------------------------------
# Project rendering (read-only, no session state)
# -------------------------------------------------

def _render_local_codebase_summary(path: Path) -> tuple[str, list[dict[str, str]]]:
    target = path.resolve()
    readme_text = _read_small_text_file(target / "README.md")
    repo_map_text = _read_small_text_file(target / "REPO_MAP.md")
    guide_text = _read_small_text_file(target / "docs" / "reference" / "HUMAN_GUIDES" / "README.md")

    project_summary = (
        _extract_markdown_paragraph(readme_text)
        or _extract_markdown_paragraph(guide_text)
        or "I found the local project, but I could only extract a limited plain-language summary."
    )
    built_to_help = _extract_markdown_bullets_after_line(readme_text, "It is built to help with:")
    if not built_to_help:
        built_to_help = _extract_markdown_bullets_after_line(guide_text, "It is for people who want to understand:")
    surfaces = _major_project_surfaces(target)
    backend_modules = _major_backend_modules(target)
    registry_snapshot = _capability_registry_snapshot(target)
    repo_map_summary = _extract_markdown_paragraph(repo_map_text)

    lines = [
        "Local codebase summary",
        f"Target: {target}",
        "",
        "Plain-language orientation: NovaLIS is a private, offline-capable AI assistant with governed execution gates.",
        f"Project summary: {project_summary}",
    ]
    if repo_map_summary:
        lines.append(f"Repo orientation: {repo_map_summary}")
    if built_to_help:
        lines.append("What it appears to help with:")
        lines.extend(f"- {item}" for item in built_to_help[:5])
    if surfaces:
        lines.append("Major surfaces:")
        lines.extend(f"- {item}" for item in surfaces[:6])
    if backend_modules:
        lines.append("Backend modules:")
        lines.extend(f"- {item}" for item in backend_modules[:6])
    if registry_snapshot:
        active_count = int(registry_snapshot.get("active_count") or 0)
        groups = ", ".join(list(registry_snapshot.get("group_names") or [])[:4]) or "unlabeled groups"
        capability_examples = ", ".join(list(registry_snapshot.get("active_names") or [])[:6]) or "no clear capability names"
        lines.extend(
            [
                "Likely implemented capabilities:",
                f"- Registry signals {active_count} active governed capabilities across {groups}.",
                f"- Example active capabilities: {capability_examples}.",
            ]
        )
    lines.extend(
        [
            "Confidence note:",
            "- This summary is based on local README, repo map, folder structure, and registry signals.",
            "- It does not inspect every file in the repo.",
        ]
    )
    lines.extend(
        [
            "",
            "Try next:",
            "- audit this repo",
            "- what can Nova do based on its own code?",
            f"- create analysis report on {target.name} architecture",
        ]
    )

    suggestions = [
        {"label": "Audit this repo", "command": "audit this repo"},
        {"label": "Open folder", "command": f"open {target}"},
        {"label": "Create report", "command": f"create analysis report on {target.name} architecture"},
    ]
    return "\n".join(lines), suggestions


def _render_local_project_summary(path: Path) -> tuple[str, list[dict[str, str]]]:
    target = path.resolve()
    if target.is_file():
        message = (
            "I found a local file, not a folder.\n"
            f"Target: {target}\n\n"
            "If you want a file explanation, give me the file path explicitly or say 'explain this' while that file is visible."
        )
        suggestions = [
            {"label": "Open file", "command": f"open {target}"},
            {"label": "Explain this", "command": "explain this"},
        ]
        return message, suggestions

    try:
        entries = list(target.iterdir())
    except Exception:
        entries = []

    directories = sorted(
        [entry.name for entry in entries if entry.is_dir() and not entry.name.startswith(".")],
        key=str.lower,
    )[:6]
    files = sorted(
        [entry.name for entry in entries if entry.is_file() and not entry.name.startswith(".")],
        key=str.lower,
    )[:6]
    visible_dir_count = len([entry for entry in entries if entry.is_dir() and not entry.name.startswith(".")])
    visible_file_count = len([entry for entry in entries if entry.is_file() and not entry.name.startswith(".")])
    markers = _local_project_markers(target)
    is_repo = (target / ".git").exists()

    lines = [
        "Local project overview" if is_repo else "Local folder overview",
        f"Target: {target}",
        f"Type: {'Git repo folder' if is_repo else 'Local folder'}",
        f"Top level: {visible_dir_count} folder{'s' if visible_dir_count != 1 else ''} | {visible_file_count} file{'s' if visible_file_count != 1 else ''}",
    ]
    if markers:
        lines.append(f"Key markers: {', '.join(markers[:6])}")
    if directories:
        lines.append(f"Top-level folders: {', '.join(directories)}")
    if files:
        lines.append(f"Top-level files: {', '.join(files)}")
    lines.extend(
        [
            "",
            "Try next:",
            f"- open {target}",
            "- explain this while the folder is visible",
            f"- create analysis report on {target.name} architecture",
        ]
    )

    suggestions = [
        {"label": "Open folder", "command": f"open {target}"},
        {"label": "Explain this", "command": "explain this"},
        {"label": "Create report", "command": f"create analysis report on {target.name} architecture"},
    ]
    return "\n".join(lines), suggestions


def _render_local_architecture_report(path: Path) -> tuple[str, list[dict[str, str]]]:
    target = path.resolve()
    readme_text = _read_small_text_file(target / "README.md")
    repo_map_text = _read_small_text_file(target / "REPO_MAP.md")
    guide_text = _read_small_text_file(target / "docs" / "reference" / "HUMAN_GUIDES" / "README.md")

    project_summary = (
        _extract_markdown_paragraph(readme_text)
        or _extract_markdown_paragraph(guide_text)
        or "I found the local project, but I could only extract a limited architecture summary from the available docs."
    )
    repo_map_summary = _extract_markdown_paragraph(repo_map_text)
    markers = _local_project_markers(target)
    surfaces = _major_project_surfaces(target)
    backend_modules = _major_backend_modules(target)
    registry_snapshot = _capability_registry_snapshot(target)

    try:
        top_level_dirs = sorted(
            [entry.name for entry in target.iterdir() if entry.is_dir() and not entry.name.startswith(".")],
            key=str.lower,
        )[:6]
    except Exception:
        top_level_dirs = []

    lines = [
        "Local architecture report",
        f"Target: {target}",
        "",
        f"Project summary: {project_summary}",
    ]
    if repo_map_summary:
        lines.append(f"Architecture orientation: {repo_map_summary}")
    if markers:
        lines.append(f"Repo markers: {', '.join(markers[:6])}")
    if top_level_dirs:
        lines.append("Primary folders:")
        lines.extend(f"- {name}" for name in top_level_dirs)
    if surfaces:
        lines.append("Major surfaces:")
        lines.extend(f"- {item}" for item in surfaces[:6])
    if backend_modules:
        lines.append("Backend architecture:")
        lines.extend(f"- {item}" for item in backend_modules[:6])
    if registry_snapshot:
        active_count = int(registry_snapshot.get("active_count") or 0)
        group_names = ", ".join(list(registry_snapshot.get("group_names") or [])[:4]) or "unlabeled groups"
        capability_examples = ", ".join(list(registry_snapshot.get("active_names") or [])[:6]) or "no clear capability names"
        lines.extend(
            [
                "Implemented capability signals:",
                f"- Registry shows {active_count} active governed capabilities across {group_names}.",
                f"- Example active capabilities: {capability_examples}.",
            ]
        )
    lines.extend(
        [
            "Report note:",
            "- This is a local read-only architecture report built from README, REPO_MAP, folder structure, and registry signals.",
            "- It does not inspect every source file or claim a full code-level audit.",
            "",
            "Try next:",
            "- summarize this repo",
            "- audit this repo",
            "- what can Nova do based on its own code?",
        ]
    )

    suggestions = [
        {"label": "Summarize repo", "command": "summarize this repo"},
        {"label": "Audit this repo", "command": "audit this repo"},
        {"label": "Open folder", "command": f"open {target}"},
    ]
    return "\n".join(lines), suggestions


# -------------------------------------------------
# Project structure map (tree + graph data)
# -------------------------------------------------

def _project_tree_node(
    label: str,
    detail: str = "",
    children: Optional[list[dict[str, Any]]] = None,
) -> dict[str, Any]:
    return {
        "label": str(label or "").strip(),
        "detail": str(detail or "").strip(),
        "children": list(children or []),
    }


def _append_project_tree_lines(
    lines: list[str],
    nodes: list[dict[str, Any]],
    *,
    prefix: str = "",
) -> None:
    total = len(nodes)
    for index, node in enumerate(nodes):
        is_last = index == total - 1
        connector = "\\--" if is_last else "|--"
        label = str(node.get("label") or "").strip()
        detail = str(node.get("detail") or "").strip()
        rendered = f"{prefix}{connector} {label}"
        if detail:
            rendered += f" ({detail})"
        lines.append(rendered)
        children = [dict(item or {}) for item in list(node.get("children") or []) if dict(item or {}).get("label")]
        if children:
            child_prefix = prefix + ("    " if is_last else "|   ")
            _append_project_tree_lines(lines, children, prefix=child_prefix)


def _project_graph_id(*parts: str) -> str:
    cleaned = "-".join(str(part or "").strip().lower() for part in parts if str(part or "").strip())
    cleaned = re.sub(r"[^a-z0-9]+", "-", cleaned).strip("-")
    return cleaned or "node"


def _append_project_graph_data(
    *,
    nodes: list[dict[str, Any]],
    graph_nodes: list[dict[str, Any]],
    graph_edges: list[dict[str, Any]],
    parent_id: str,
    parent_label: str,
    prefix: str,
    level: int,
) -> None:
    for index, node in enumerate(nodes):
        label = str(node.get("label") or "").strip()
        detail = str(node.get("detail") or "").strip()
        if not label:
            continue
        node_id = _project_graph_id(prefix, label, str(index))
        graph_nodes.append(
            {
                "id": node_id,
                "label": label,
                "detail": detail,
                "kind": "surface" if level == 1 else "module",
                "level": level,
            }
        )
        graph_edges.append(
            {
                "source": parent_id,
                "target": node_id,
                "label": "contains",
                "detail": f"{parent_label} contains {label}",
            }
        )
        children = [dict(item or {}) for item in list(node.get("children") or []) if dict(item or {}).get("label")]
        if children:
            _append_project_graph_data(
                nodes=children,
                graph_nodes=graph_nodes,
                graph_edges=graph_edges,
                parent_id=node_id,
                parent_label=label,
                prefix=f"{prefix}-{index}",
                level=level + 1,
            )


def _project_relationship_edges(target: Path) -> list[dict[str, str]]:
    edges: list[dict[str, str]] = []
    backend_src = target / "nova_backend" / "src"
    backend_static = target / "nova_backend" / "static"
    if (backend_src / "brain_server.py").exists() and (backend_src / "governor").exists():
        edges.append(
            {
                "source": "brain_server.py",
                "target": "governor/",
                "label": "routes through",
                "detail": "Brain Server routes effectful work through the Governor layer.",
            }
        )
    if (backend_src / "brain_server.py").exists() and (backend_src / "executors").exists():
        edges.append(
            {
                "source": "brain_server.py",
                "target": "executors/",
                "label": "delegates to",
                "detail": "Governed executors perform the concrete actions Nova can actually take.",
            }
        )
    if (backend_src / "brain_server.py").exists() and (backend_src / "memory").exists():
        edges.append(
            {
                "source": "brain_server.py",
                "target": "memory/",
                "label": "grounds with",
                "detail": "Brain Server uses governed memory and continuity state for explicit persistence.",
            }
        )
    if (backend_static / "dashboard.js").exists() and (backend_src / "brain_server.py").exists():
        edges.append(
            {
                "source": "dashboard.js",
                "target": "brain_server.py",
                "label": "talks to",
                "detail": "The dashboard UI talks to the backend brain over the live websocket session.",
            }
        )
    return edges


def _build_local_project_structure_map_widget(path: Path) -> dict[str, Any]:
    target = path.resolve()
    readme_text = _read_small_text_file(target / "README.md")
    repo_map_text = _read_small_text_file(target / "REPO_MAP.md")
    project_summary = (
        _extract_markdown_paragraph(readme_text)
        or _extract_markdown_paragraph(repo_map_text)
        or "This local project already has enough structure for Nova to draw a high-signal map of the main surfaces."
    )

    children_by_surface: dict[str, list[dict[str, Any]]] = {}
    docs_path = target / "docs"
    if docs_path.exists():
        doc_children: list[dict[str, Any]] = []
        if (docs_path / "reference" / "HUMAN_GUIDES").exists():
            doc_children.append(_project_tree_node("reference/HUMAN_GUIDES/", "plain-language guides"))
        if (docs_path / "PROOFS").exists():
            doc_children.append(_project_tree_node("PROOFS/", "runtime verification and proof packets"))
        if (docs_path / "design").exists():
            doc_children.append(_project_tree_node("design/", "roadmaps, phase plans, and future direction"))
        if doc_children:
            children_by_surface["docs"] = doc_children

    backend_children: list[dict[str, Any]] = []
    backend_root = target / "nova_backend"
    backend_src = backend_root / "src"
    if backend_src.exists():
        src_children: list[dict[str, Any]] = []
        if (backend_src / "brain_server.py").exists():
            src_children.append(_project_tree_node("brain_server.py", "main orchestration hub"))
        for name in _major_backend_modules(target)[:6]:
            src_children.append(_project_tree_node(f"{name}/", BACKEND_MODULE_HINTS.get(name, "runtime subsystem")))
        if src_children:
            backend_children.append(_project_tree_node("src/", "runtime logic", src_children))
    if (backend_root / "tests").exists():
        backend_children.append(_project_tree_node("tests/", "regression and safety proof"))
    if (backend_root / "static").exists():
        backend_children.append(_project_tree_node("static/", "dashboard assets served by the backend"))
    if backend_children:
        children_by_surface["nova_backend"] = backend_children

    frontend_root = target / "Nova-Frontend-Dashboard"
    if frontend_root.exists():
        frontend_children: list[dict[str, Any]] = []
        if (frontend_root / "dashboard.js").exists():
            frontend_children.append(_project_tree_node("dashboard.js", "dashboard interaction layer"))
        if (frontend_root / "index.html").exists():
            frontend_children.append(_project_tree_node("index.html", "page shell and widget surfaces"))
        if frontend_children:
            children_by_surface["Nova-Frontend-Dashboard"] = frontend_children

    preferred_surfaces = [
        "docs",
        "nova_backend",
        "Nova-Frontend-Dashboard",
        "nova_workspace",
        "NovaLIS-Governance",
        "scripts",
    ]
    top_nodes: list[dict[str, Any]] = []
    seen_surfaces: set[str] = set()
    for surface in preferred_surfaces:
        surface_path = target / surface
        if not surface_path.exists():
            continue
        seen_surfaces.add(surface.lower())
        top_nodes.append(
            _project_tree_node(
                f"{surface}/",
                PROJECT_SURFACE_HINTS.get(surface, "project surface"),
                children_by_surface.get(surface, []),
            )
        )
    for entry in sorted(target.iterdir(), key=lambda item: item.name.lower()):
        if not entry.is_dir() or entry.name.startswith("."):
            continue
        if entry.name.lower() in seen_surfaces:
            continue
        top_nodes.append(_project_tree_node(f"{entry.name}/", "additional project surface"))
        if len(top_nodes) >= 8:
            break

    file_nodes: list[dict[str, Any]] = []
    for file_name, detail in [
        ("README.md", "project overview"),
        ("REPO_MAP.md", "repo orientation and navigation"),
        ("start_nova.bat", "local launch helper"),
    ]:
        if (target / file_name).exists():
            file_nodes.append(_project_tree_node(file_name, detail))

    root_nodes = top_nodes + file_nodes
    tree_lines = [target.name]
    _append_project_tree_lines(tree_lines, root_nodes)
    graph_nodes = [
        {
            "id": _project_graph_id(target.name, "root"),
            "label": target.name,
            "detail": "current workspace root",
            "kind": "root",
            "level": 0,
        }
    ]
    graph_edges: list[dict[str, Any]] = []
    _append_project_graph_data(
        nodes=root_nodes,
        graph_nodes=graph_nodes,
        graph_edges=graph_edges,
        parent_id=graph_nodes[0]["id"],
        parent_label=target.name,
        prefix=target.name,
        level=1,
    )
    relationship_edges = _project_relationship_edges(target)

    highlights = [
        {"label": "brain_server.py", "detail": "Coordinates conversation, routing, widgets, and local-project helpers."},
        {"label": "governor/", "detail": "Keeps authority and execution under policy instead of trusting raw model output."},
        {"label": "executors/", "detail": "Holds the concrete governed actions Nova can actually perform."},
        {"label": "memory/", "detail": "Stores explicit governed memory and keeps it inspectable."},
        {"label": "static/ + dashboard", "detail": "Turns backend state into the UI a person actually uses."},
    ]

    summary = (
        f"Structure map ready for {target.name}. "
        "This is a read-only human-facing view of the major surfaces and the backend spine."
    )
    return {
        "type": "project_structure_map",
        "target": str(target),
        "summary": summary,
        "project_summary": project_summary,
        "tree_lines": tree_lines,
        "highlights": highlights,
        "graph_summary": (
            f"Structured graph ready with {len(graph_nodes)} nodes and "
            f"{len(graph_edges) + len(relationship_edges)} visible relationships."
        ),
        "graph_nodes": graph_nodes[:24],
        "graph_edges": (graph_edges + relationship_edges)[:36],
        "graph_legend": [
            {"label": "Root", "detail": "The current repo or workspace root."},
            {"label": "Surface", "detail": "A major product surface like docs, backend, or dashboard."},
            {"label": "Module", "detail": "A high-signal file or subsystem inside a surface."},
            {"label": "Relationship", "detail": "A human-facing connection Nova can explain without claiming full code certainty."},
        ],
        "recommended_actions": [
            {"label": "Workspace Home", "command": "workspace home"},
            {"label": "Audit this repo", "command": "audit this repo"},
            {"label": "Architecture report", "command": f"create analysis report on {target.name} architecture"},
        ],
        "note": (
            "This map is grounded in local folder structure and high-signal files. "
            "It is meant to help a person understand the codebase quickly, not to claim a full file-by-file audit."
        ),
    }


def _render_local_project_structure_map(path: Path) -> tuple[str, list[dict[str, str]], dict[str, Any]]:
    widget = _build_local_project_structure_map_widget(path)
    lines = [
        "Local project structure map",
        f"Target: {widget.get('target')}",
        "",
        f"Project summary: {widget.get('project_summary')}",
        f"Graph summary: {widget.get('graph_summary')}",
        "",
        "Visual orientation:",
        *list(widget.get("tree_lines") or []),
        "",
        "Key nodes:",
    ]
    for item in list(widget.get("highlights") or [])[:5]:
        label = str(item.get("label") or "").strip()
        detail = str(item.get("detail") or "").strip()
        if label and detail:
            lines.append(f"- {label}: {detail}")
    lines.extend(
        [
            "",
            "Structured relationships:",
            *[
                f"- {str(item.get('source') or '').strip()} {str(item.get('label') or 'links to').strip()} {str(item.get('target') or '').strip()}"
                for item in list(widget.get("graph_edges") or [])[:4]
                if str(item.get("source") or "").strip() and str(item.get("target") or "").strip()
            ],
            "",
            "Map note:",
            f"- {widget.get('note')}",
            "",
            "Try next:",
            "- workspace home",
            "- audit this repo",
            f"- create analysis report on {path.resolve().name} architecture",
        ]
    )
    suggestions = [dict(item or {}) for item in list(widget.get("recommended_actions") or [])[:4]]
    return "\n".join(lines), suggestions, widget

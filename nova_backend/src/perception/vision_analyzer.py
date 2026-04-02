from __future__ import annotations

import re
from typing import Any, Mapping


class VisionAnalyzer:
    """Read-only screen interpretation scaffold."""

    _INSTALL_QUERY_HINTS = (
        "which one should i download",
        "what should i download",
        "which download",
        "help me do this",
        "help me do it",
        "how do i do this",
        "what should i click",
        "install",
        "download",
    )

    _LANDING_PAGE_HINTS = ("pricing", "book now", "contact", "features", "get started", "learn more")
    _FORM_HINTS = ("email", "password", "submit", "sign in", "log in", "continue")
    _DASHBOARD_HINTS = ("dashboard", "analytics", "overview", "report", "revenue", "traffic")
    _ARTICLE_HINTS = ("read more", "published", "author", "minutes read", "share")

    @staticmethod
    def _normalized_text(*parts: str) -> str:
        return " ".join(str(part or "") for part in parts).strip().lower()

    @staticmethod
    def _snippet(text: str, limit: int = 220) -> str:
        clean = re.sub(r"\s+", " ", str(text or "")).strip()
        if len(clean) <= limit:
            return clean
        return clean[: limit - 3].rstrip() + "..."

    @staticmethod
    def _missing_module_name(text: str) -> str:
        match = re.search(r"ModuleNotFoundError:\s+No module named ['\"]([^'\"]+)['\"]", str(text or ""), re.IGNORECASE)
        return str(match.group(1)).strip() if match else ""

    @staticmethod
    def _key_error_name(text: str) -> str:
        match = re.search(r"KeyError:\s*['\"]?([^'\"\n]+)", str(text or ""), re.IGNORECASE)
        return str(match.group(1)).strip() if match else ""

    @classmethod
    def _classify_page_kind(cls, *, page_title: str, active_url: str, ocr_text: str) -> str:
        combined = cls._normalized_text(page_title, active_url, ocr_text)
        if any(token in combined for token in cls._FORM_HINTS):
            return "form"
        if any(token in combined for token in cls._DASHBOARD_HINTS):
            return "dashboard"
        if any(token in combined for token in cls._ARTICLE_HINTS):
            return "article"
        if any(token in combined for token in cls._LANDING_PAGE_HINTS):
            return "landing_page"
        if "settings" in combined or "preferences" in combined:
            return "settings"
        if "docs" in combined or "documentation" in combined:
            return "documentation"
        return "general_page"

    @staticmethod
    def _page_kind_label(page_kind: str) -> str:
        labels = {
            "form": "a form or sign-in style page",
            "dashboard": "a dashboard or reporting page",
            "article": "an article or reading page",
            "landing_page": "a landing page or marketing page",
            "settings": "a settings page",
            "documentation": "a documentation page",
            "general_page": "a general page",
        }
        return labels.get(page_kind, "a general page")

    @staticmethod
    def _extract_key_actions(ocr_text: str) -> list[str]:
        matches = re.findall(
            r"\b(book now|get started|learn more|contact|continue|submit|sign in|log in|download|open|save|next)\b",
            str(ocr_text or ""),
            re.IGNORECASE,
        )
        deduped: list[str] = []
        for match in matches:
            normalized = str(match).strip().lower()
            if normalized and normalized not in deduped:
                deduped.append(normalized)
        return deduped[:4]

    @staticmethod
    def _compose_general_next_steps(*, page_kind: str, key_actions: list[str], query: str) -> list[str]:
        query_lower = str(query or "").strip().lower()
        steps: list[str] = []
        if page_kind == "landing_page":
            steps.extend([
                "Focus on the main offer and the strongest call to action first.",
                "Check whether the pricing, booking, or contact path is clear.",
            ])
        elif page_kind == "form":
            steps.extend([
                "Check the required fields before you continue.",
                "Make sure the next button or submit action matches what you expect.",
            ])
        elif page_kind == "dashboard":
            steps.extend([
                "Start with the headline metrics or summary cards first.",
                "Look for the filter, date range, or export controls if you need a narrower view.",
            ])
        elif page_kind == "article":
            steps.extend([
                "Start with the headline, subhead, and any highlighted key points.",
                "Decide whether you want a quick summary or a deeper read.",
            ])
        else:
            steps.append("Start with the clearest title, main section, or primary action on the page.")

        if key_actions:
            steps.append(f"The visible action to check first is: {key_actions[0]}.")
        if "what matters" in query_lower:
            steps.append("Ask for the most important section if you want Nova to narrow the page down further.")
        return steps[:4]

    @staticmethod
    def _compose_what_matters(*, page_kind: str, text_snippet: str, key_actions: list[str]) -> str:
        if page_kind == "landing_page":
            return "The page seems to be guiding you toward a core offer and a next action."
        if page_kind == "form":
            return "The important part is the path to continue safely without missing a required field."
        if page_kind == "dashboard":
            return "The important part is the headline metrics and the controls that change the view."
        if page_kind == "article":
            return "The important part is the main claim and whether you want a quick summary or the full read."
        if key_actions:
            return f"The clearest visible action is {key_actions[0]}."
        if text_snippet:
            return f"The strongest visible signal is: {text_snippet}"
        return "The page context is limited, so the next move is to focus on the title or main action."

    @staticmethod
    def _looks_like_python_download_context(*, page_title: str, active_url: str, ocr_text: str) -> bool:
        combined = " ".join([str(page_title or ""), str(active_url or ""), str(ocr_text or "")]).lower()
        return "python" in combined and any(token in combined for token in ("download", "installer", "release"))

    @classmethod
    def _looks_like_install_help_query(cls, query: str) -> bool:
        lowered = str(query or "").strip().lower()
        if not lowered:
            return False
        return any(token in lowered for token in cls._INSTALL_QUERY_HINTS)

    @staticmethod
    def _download_guidance_for_os(os_name: str) -> tuple[str, list[str]]:
        lowered = str(os_name or "").strip().lower()
        if "windows" in lowered:
            return (
                "Windows installer (64-bit)",
                [
                    "Select Windows installer (64-bit).",
                    "Avoid embeddable/ZIP packages unless you need a portable setup.",
                    "Run the installer and keep default PATH options enabled.",
                ],
            )
        if "mac" in lowered or "darwin" in lowered:
            return (
                "macOS 64-bit universal2 installer",
                [
                    "Choose the macOS 64-bit universal2 installer.",
                    "Open the .pkg file and follow the installer prompts.",
                    "Verify install with 'python3 --version' in Terminal.",
                ],
            )
        if "linux" in lowered:
            return (
                "your distro package manager",
                [
                    "Use your distro package manager first (apt/dnf/pacman).",
                    "If you need the newest release, use the official tarball instructions.",
                    "Confirm install with 'python3 --version'.",
                ],
            )
        return (
            "the installer matching your operating system",
            [
                "Choose the installer that matches your operating system and architecture.",
                "Prefer standard installer packages over embeddable archives.",
                "Verify with a version check after install.",
            ],
        )

    def analyze(
        self,
        *,
        image_path: str,
        ocr_text: str,
        context_snapshot: Mapping[str, Any] | None = None,
        working_context: Mapping[str, Any] | None = None,
        user_query: str = "",
    ) -> dict[str, Any]:
        snapshot = dict(context_snapshot or {})
        context = dict(working_context or {})
        active_window = dict(snapshot.get("active_window") or {})
        browser = dict(snapshot.get("browser") or {})
        system = dict(snapshot.get("system") or {})
        system_context = dict(context.get("system_context") or {})

        page_title = str(
            browser.get("page_title")
            or active_window.get("title")
            or context.get("active_window")
            or ""
        ).strip()
        active_url = str(browser.get("url") or context.get("active_url") or "").strip()
        os_name = str(system.get("os") or system_context.get("os") or "").strip()
        text_snippet = self._snippet(ocr_text, limit=240)
        query = str(user_query or "").strip()
        task_type = str(context.get("task_type") or "").strip().lower()
        page_kind = self._classify_page_kind(page_title=page_title, active_url=active_url, ocr_text=ocr_text)
        key_actions = self._extract_key_actions(ocr_text)

        module_name = self._missing_module_name(ocr_text)
        if module_name:
            summary = (
                f"This shows a Python import error: module '{module_name}' is missing. "
                f"Typical fix: run 'pip install {module_name}' in the same environment, then rerun your command."
            )
            return {
                "summary": summary,
                "confidence": 0.86,
                "next_steps": [
                    f"Install module with: pip install {module_name}",
                    "Confirm by rerunning the original command.",
                ],
                "signals": {
                    "page_title": page_title,
                    "active_url": active_url,
                    "ocr_snippet": text_snippet,
                    "os": os_name,
                    "image_path": str(image_path or ""),
                    "diagnostic": "module_not_found",
                },
            }

        key_name = self._key_error_name(ocr_text)
        if key_name:
            summary = (
                f"This looks like a KeyError for '{key_name}', meaning code requested a dictionary key that was not present. "
                "Check key existence before access (for example with dict.get)."
            )
            return {
                "summary": summary,
                "confidence": 0.80,
                "next_steps": [
                    f"Inspect where key '{key_name}' is read.",
                    "Validate available keys before indexing.",
                ],
                "signals": {
                    "page_title": page_title,
                    "active_url": active_url,
                    "ocr_snippet": text_snippet,
                    "os": os_name,
                    "image_path": str(image_path or ""),
                    "diagnostic": "key_error",
                },
            }

        if self._looks_like_python_download_context(page_title=page_title, active_url=active_url, ocr_text=ocr_text) and (
            self._looks_like_install_help_query(query) or task_type == "software_install"
        ):
            recommendation, steps = self._download_guidance_for_os(os_name)
            summary = (
                f"You're on a Python download page. Based on your environment, choose {recommendation}. "
                "I added practical next steps so you can finish quickly."
            )
            return {
                "summary": summary,
                "confidence": 0.83,
                "next_steps": steps,
                "signals": {
                    "page_title": page_title,
                    "active_url": active_url,
                    "ocr_snippet": text_snippet,
                    "os": os_name,
                    "image_path": str(image_path or ""),
                    "diagnostic": "python_download_guidance",
                    "recommended_download": recommendation,
                },
            }

        summary_lines = []
        summary_lines.append(f"This looks like {self._page_kind_label(page_kind)}.")
        if page_title:
            summary_lines.append(f"Page title: {page_title}.")
        if active_url:
            summary_lines.append(f"Page context: {active_url}.")
        if key_actions:
            summary_lines.append(f"Visible actions: {', '.join(key_actions)}.")
        what_matters = self._compose_what_matters(
            page_kind=page_kind,
            text_snippet=text_snippet,
            key_actions=key_actions,
        )
        if what_matters:
            summary_lines.append(f"What matters here: {what_matters}")
        if text_snippet:
            summary_lines.append(f"Visible text signal: {text_snippet}")
        else:
            summary_lines.append("I captured the region, but OCR text is limited.")
        if query:
            summary_lines.append(f"Request interpreted as: {query}.")
        if task_type:
            summary_lines.append(f"Current task context: {task_type.replace('_', ' ')}.")
        if os_name:
            summary_lines.append(f"Detected environment: {os_name}.")

        next_steps = self._compose_general_next_steps(
            page_kind=page_kind,
            key_actions=key_actions,
            query=query,
        )
        follow_up_prompts = [
            "what matters most here",
            "what should i click next",
            "read the important part",
            "summarize this page",
        ]

        return {
            "summary": " ".join(summary_lines),
            "confidence": 0.55 if text_snippet else 0.30,
            "next_steps": next_steps,
            "what_matters": what_matters,
            "page_kind": page_kind,
            "key_actions": key_actions,
            "follow_up_prompts": follow_up_prompts,
            "signals": {
                "page_title": page_title,
                "active_url": active_url,
                "ocr_snippet": text_snippet,
                "os": os_name,
                "image_path": str(image_path or ""),
            },
        }

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
        if page_title:
            summary_lines.append(f"You appear to be viewing: {page_title}.")
        if active_url:
            summary_lines.append(f"Page context: {active_url}.")
        if os_name:
            summary_lines.append(f"Detected environment: {os_name}.")
        if text_snippet:
            summary_lines.append(f"Visible text signal: {text_snippet}")
        else:
            summary_lines.append("I captured the region, but OCR text is limited.")
        if query:
            summary_lines.append(f"Request interpreted as: {query}.")
        if task_type:
            summary_lines.append(f"Current task context: {task_type.replace('_', ' ')}.")

        return {
            "summary": " ".join(summary_lines),
            "confidence": 0.55 if text_snippet else 0.30,
            "signals": {
                "page_title": page_title,
                "active_url": active_url,
                "ocr_snippet": text_snippet,
                "os": os_name,
                "image_path": str(image_path or ""),
            },
        }

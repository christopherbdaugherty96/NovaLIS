from __future__ import annotations

import re

from src.personality.nova_style_contract import NovaStyleContract
from src.personality.tone_profile_store import ToneProfileStore


class PersonalityInterfaceAgent:
    """Presentation-only personality layer for outbound chat messages."""

    _DETAILED_SECTION_HEADERS = (
        "Summary:",
        "Core answer:",
        "Key drivers:",
        "Risks and uncertainties:",
        "What to verify next:",
        "Try next:",
    )

    _SYSTEM_TOKEN_PATTERNS = (
        re.compile(r"<function_call[^>]*>", re.IGNORECASE),
        re.compile(r"\btool_call\b", re.IGNORECASE),
        re.compile(r"\bcapability\s*[_-]?id\s*[:=]?\s*\d+\b", re.IGNORECASE),
        re.compile(r"\bexecutor\s*[_-]?id\s*[:=]?\s*\d+\b", re.IGNORECASE),
    )

    _AUTHORITY_REPLACEMENTS = (
        (re.compile(r"\bi recommend(?:\s+that)?\b", re.IGNORECASE), "A reasonable option is to"),
        (re.compile(r"\byou should\b", re.IGNORECASE), "A useful next step is to"),
        (re.compile(r"\bi think\b", re.IGNORECASE), "The analysis suggests"),
        (re.compile(r"\bi believe\b", re.IGNORECASE), "The analysis suggests"),
        (re.compile(r"\btrust me\b", re.IGNORECASE), "Based on available information"),
    )

    _EMOTIONAL_REPLACEMENTS = (
        (re.compile(r"\bi[' ]?m here for you\b", re.IGNORECASE), "I can help with the task details"),
        (re.compile(r"\bdon[' ]?t worry\b", re.IGNORECASE), "Let's focus on the next step"),
        (re.compile(r"\bthat must be hard\b", re.IGNORECASE), "This can be frustrating"),
        (re.compile(r"\bi understand how you feel\b", re.IGNORECASE), "I can help clarify the situation"),
    )

    _FORMAL_REPLACEMENTS = (
        (re.compile(r"\bcan't\b", re.IGNORECASE), "cannot"),
        (re.compile(r"\bdon't\b", re.IGNORECASE), "do not"),
        (re.compile(r"\bwon't\b", re.IGNORECASE), "will not"),
        (re.compile(r"\bit's\b", re.IGNORECASE), "it is"),
        (re.compile(r"\blet's\b", re.IGNORECASE), "let us"),
    )

    def __init__(self, *, tone_store: ToneProfileStore | None = None) -> None:
        self._tone_store = tone_store or ToneProfileStore()

    def present(self, text: str, *, domain: str = "general") -> str:
        clean = (text or "").replace("\r\n", "\n").strip()
        if not clean:
            return ""

        for pattern in self._SYSTEM_TOKEN_PATTERNS:
            clean = pattern.sub("", clean)

        for pattern, replacement in self._AUTHORITY_REPLACEMENTS:
            clean = pattern.sub(replacement, clean)

        for pattern, replacement in self._EMOTIONAL_REPLACEMENTS:
            clean = pattern.sub(replacement, clean)

        clean = re.sub(r"\bto to\b", "to", clean, flags=re.IGNORECASE)
        clean = re.sub(r"\s+\n", "\n", clean)
        clean = re.sub(r"\n\s+", "\n", clean)
        clean = re.sub(r"[ \t]{2,}", " ", clean)
        clean = re.sub(r"\n{3,}", "\n\n", clean)
        clean = re.sub(r"!+", ".", clean)
        clean = re.sub(r"\s{2,}", " ", clean)
        clean = NovaStyleContract.normalize(clean)
        clean = self._apply_tone_profile(clean.strip(), domain=domain)
        return clean.strip()

    def present_agent_result(
        self,
        task_title: str,
        result_text: str,
        *,
        opener: str = "",
        domain: str = "daily",
    ) -> str:
        del task_title
        body = self.present(str(result_text or "").strip(), domain=domain)
        if not body:
            return ""
        if opener:
            return NovaStyleContract.normalize(f"{str(opener).strip()} {body}".strip()).strip()
        return body

    def current_tone_profile(self, domain: str = "general") -> str:
        try:
            return self._tone_store.effective_profile(domain)
        except Exception:
            return "balanced"

    def tone_snapshot(self) -> dict:
        try:
            return self._tone_store.snapshot()
        except Exception:
            return {}

    def set_global_tone(self, profile: str) -> dict:
        return self._tone_store.set_global_profile(profile)

    def set_domain_tone(self, domain: str, profile: str) -> dict:
        return self._tone_store.set_domain_profile(domain, profile)

    def reset_domain_tone(self, domain: str) -> dict:
        return self._tone_store.reset_domain(domain)

    def reset_all_tone(self) -> dict:
        return self._tone_store.reset_all()

    def _apply_tone_profile(self, text: str, *, domain: str) -> str:
        profile = self.current_tone_profile(domain)
        if profile == "formal":
            for pattern, replacement in self._FORMAL_REPLACEMENTS:
                text = pattern.sub(replacement, text)
            return text
        if profile == "concise":
            return self._apply_concise_profile(text)
        if profile == "detailed":
            return self._apply_detailed_profile(text)
        return text

    def _apply_concise_profile(self, text: str) -> str:
        lines = text.splitlines()
        compacted: list[str] = []
        in_try_next = False
        suggestion_lines: list[str] = []

        for line in lines:
            stripped = line.strip()
            if stripped.lower() == "try next:":
                in_try_next = True
                compacted.append(line)
                continue

            if in_try_next and stripped.startswith("-"):
                suggestion_lines.append(line)
                continue

            if in_try_next:
                compacted.extend(self._trim_suggestions(suggestion_lines))
                suggestion_lines = []
                in_try_next = False

            compacted.append(line)

        if in_try_next:
            compacted.extend(self._trim_suggestions(suggestion_lines))

        return "\n".join(compacted).strip()

    def _trim_suggestions(self, lines: list[str]) -> list[str]:
        if len(lines) <= 2:
            return lines
        trimmed = list(lines[:2])
        trimmed.append("- Ask for more options if you want a longer list.")
        return trimmed

    def _apply_detailed_profile(self, text: str) -> str:
        expanded = text
        for header in self._DETAILED_SECTION_HEADERS:
            pattern = re.compile(rf"([^\n])\s+({re.escape(header)})", re.IGNORECASE)
            expanded = pattern.sub(r"\1\n\n\2", expanded)
        expanded = re.sub(r"(Try next:)\s*-\s*", r"\1\n- ", expanded, flags=re.IGNORECASE)
        expanded = re.sub(r"\n-([^\s])", r"\n- \1", expanded)
        expanded = re.sub(r"\n{3,}", "\n\n", expanded)
        return expanded.strip()

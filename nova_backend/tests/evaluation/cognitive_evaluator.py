from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class CognitiveEvaluationResult:
    has_summary: bool
    has_key_findings: bool
    has_sources: bool
    has_confidence: bool
    source_count: int
    contradiction_detected: bool
    coherence_pass: bool
    summary_compression_ratio: float
    quality_score: float


class CognitiveEvaluator:
    """Deterministic output-quality evaluator for Nova cognitive responses."""

    SECTION_PATTERNS = {
        "summary": re.compile(r"\bsummary\b", re.IGNORECASE),
        "key_findings": re.compile(r"\bkey findings\b", re.IGNORECASE),
        "sources": re.compile(r"\bsources?\b", re.IGNORECASE),
        "confidence": re.compile(r"\bconfidence\b", re.IGNORECASE),
    }

    CONTRADICTION_RE = re.compile(r"\bcontradictions?\b|\bhowever\b|\bon the other hand\b", re.IGNORECASE)

    @classmethod
    def evaluate_intelligence_brief(cls, text: str) -> CognitiveEvaluationResult:
        raw = str(text or "")
        lowered = raw.lower()

        has_summary = bool(cls.SECTION_PATTERNS["summary"].search(raw))
        has_key_findings = bool(cls.SECTION_PATTERNS["key_findings"].search(raw))
        has_sources = bool(cls.SECTION_PATTERNS["sources"].search(raw))
        has_confidence = bool(cls.SECTION_PATTERNS["confidence"].search(raw))
        contradiction_detected = bool(cls.CONTRADICTION_RE.search(raw))

        source_count = cls._count_sources(raw)
        coherence_pass = cls._coherence_check(lowered)
        compression_ratio = cls._summary_compression_ratio(raw)

        score = 0.0
        score += 2.5 if has_summary else 0.0
        score += 2.5 if has_key_findings else 0.0
        score += 2.0 if has_sources else 0.0
        score += 1.0 if has_confidence else 0.0
        score += 1.0 if source_count >= 2 else 0.0
        score += 1.0 if coherence_pass else 0.0

        return CognitiveEvaluationResult(
            has_summary=has_summary,
            has_key_findings=has_key_findings,
            has_sources=has_sources,
            has_confidence=has_confidence,
            source_count=source_count,
            contradiction_detected=contradiction_detected,
            coherence_pass=coherence_pass,
            summary_compression_ratio=compression_ratio,
            quality_score=round(score, 2),
        )

    @staticmethod
    def _count_sources(text: str) -> int:
        lines = [line.strip() for line in str(text or "").splitlines() if line.strip()]
        count = 0
        for line in lines:
            if re.match(r"^[-*]\s+", line):
                if any(token in line.lower() for token in (".com", ".org", "news", "reuters", "bbc", "ap", "fox", "abc", "cnn")):
                    count += 1
            elif re.match(r"^\d+[.)]\s+", line):
                if any(token in line.lower() for token in (".com", ".org", "news", "reuters", "bbc", "ap", "fox", "abc", "cnn")):
                    count += 1
        return count

    @staticmethod
    def _coherence_check(lowered_text: str) -> bool:
        # Minimal deterministic coherence check: must include at least one finding bullet
        # and a summary section marker if response is long.
        if len(lowered_text) < 120:
            return True
        has_bullet = bool(re.search(r"(^|\n)\s*[-*]\s+", lowered_text))
        has_summary = "summary" in lowered_text
        return has_bullet and has_summary

    @staticmethod
    def _summary_compression_ratio(text: str) -> float:
        raw = str(text or "")
        if not raw.strip():
            return 0.0
        summary_block = ""
        block_match = re.search(
            r"summary\s*\n[-\s]*\n(?P<body>.+?)(?:\n\s*\n|\n[a-zA-Z][^\n]{0,80}\n[-]{2,}|\Z)",
            raw,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if block_match:
            summary_block = (block_match.group("body") or "").strip()
        else:
            lines = [line.strip() for line in raw.splitlines() if line.strip()]
            for idx, line in enumerate(lines):
                if "summary" in line.lower() and idx + 1 < len(lines):
                    summary_block = lines[idx + 1]
                    break
        if not summary_block:
            return 0.0
        total_words = max(1, len(re.findall(r"\w+", raw)))
        summary_words = len(re.findall(r"\w+", summary_block))
        return round(summary_words / total_words, 3)

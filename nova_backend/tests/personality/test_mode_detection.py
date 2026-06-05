"""Phase 2 — ModeDetector tests.

Written before implementation. Proves:
  - Mode changes presentation only
  - Mode never changes permissions
  - Mode is visible and overridable
  - Low confidence defaults to home
"""
from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Structural tests (no implementation needed yet)
# ---------------------------------------------------------------------------

class TestModeDetectorStructure:

    def test_mode_result_is_frozen_snapshot(self):
        from src.personality.mode_detection import ModeDetectionResult
        result = ModeDetectionResult(
            mode="home",
            confidence="default",
            reason="No signals available",
            override_active=False,
        )
        with pytest.raises(AttributeError):
            result.mode = "business"

    def test_mode_detector_output_contains_no_capability_ids(self):
        from src.personality.mode_detection import ModeDetector
        detector = ModeDetector()
        result = detector.detect()
        result_str = str(result).lower()
        assert "capability_id" not in result_str
        assert "cap_id" not in result_str
        assert "executor" not in result_str

    def test_mode_detector_never_returns_authority_flags(self):
        from src.personality.mode_detection import ModeDetector
        detector = ModeDetector()
        for text in ["shopify report", "open documents", "hello", ""]:
            result = detector.detect(user_text=text)
            result_dict = {
                "mode": result.mode,
                "confidence": result.confidence,
                "reason": result.reason,
                "override_active": result.override_active,
            }
            for key in result_dict:
                assert key not in {
                    "can_execute", "bypass_gate", "skip_confirmation",
                    "authority", "permission", "grant",
                }
            assert not hasattr(result, "can_execute")
            assert not hasattr(result, "bypass_gate")
            assert not hasattr(result, "skip_confirmation")


# ---------------------------------------------------------------------------
# Default behavior
# ---------------------------------------------------------------------------

class TestModeDetectorDefaults:

    def test_mode_detector_defaults_to_home_on_low_confidence(self):
        from src.personality.mode_detection import ModeDetector
        detector = ModeDetector()
        result = detector.detect()
        assert result.mode == "home"
        assert result.confidence == "default"

    def test_mode_detector_defaults_to_home_on_empty_text(self):
        from src.personality.mode_detection import ModeDetector
        detector = ModeDetector()
        result = detector.detect(user_text="")
        assert result.mode == "home"

    def test_mode_detector_defaults_to_home_on_ambiguous_text(self):
        from src.personality.mode_detection import ModeDetector
        detector = ModeDetector()
        result = detector.detect(user_text="hello")
        assert result.mode == "home"


# ---------------------------------------------------------------------------
# Explicit override
# ---------------------------------------------------------------------------

class TestModeDetectorOverride:

    def test_mode_detector_respects_explicit_override(self):
        from src.personality.mode_detection import ModeDetector
        detector = ModeDetector()
        result = detector.detect(explicit_override="business")
        assert result.mode == "business"
        assert result.confidence == "explicit"
        assert result.override_active is True

    def test_mode_detector_override_beats_signals(self):
        """Explicit override wins even when signals point elsewhere."""
        from src.personality.mode_detection import ModeDetector
        detector = ModeDetector()
        result = detector.detect(
            user_text="shopify revenue report",
            hour=22,
            explicit_override="development",
        )
        assert result.mode == "development"
        assert result.confidence == "explicit"

    def test_mode_detector_clear_override(self):
        from src.personality.mode_detection import ModeDetector
        detector = ModeDetector()
        result = detector.clear_override()
        assert result.override_active is False
        assert result.confidence == "default"

    def test_mode_detector_override_accepts_all_valid_modes(self):
        from src.personality.mode_detection import ModeDetector
        detector = ModeDetector()
        for mode in ("home", "business", "development"):
            result = detector.detect(explicit_override=mode)
            assert result.mode == mode

    def test_mode_detector_override_rejects_invalid_mode(self):
        from src.personality.mode_detection import ModeDetector
        detector = ModeDetector()
        result = detector.detect(explicit_override="admin_mode")
        assert result.mode == "home"
        assert result.override_active is False


# ---------------------------------------------------------------------------
# Signal-based detection
# ---------------------------------------------------------------------------

class TestModeDetectorSignals:

    def test_mode_detector_detects_business_from_shopify_context(self):
        from src.personality.mode_detection import ModeDetector
        detector = ModeDetector()
        result = detector.detect(
            user_text="shopify report",
            recent_capabilities=[65],
        )
        assert result.mode == "business"
        assert result.confidence == "inferred"

    def test_mode_detector_detects_business_from_keywords(self):
        from src.personality.mode_detection import ModeDetector
        detector = ModeDetector()
        for text in [
            "revenue this quarter",
            "how are store orders doing",
            "shopify metrics",
            "client meeting prep",
        ]:
            result = detector.detect(user_text=text)
            assert result.mode == "business", f"Expected business for: {text}"

    def test_mode_detector_detects_development_from_repo_context(self):
        from src.personality.mode_detection import ModeDetector
        detector = ModeDetector()
        for text in [
            "what branch am I on",
            "run the test suite",
            "check the deployment",
            "git status",
            "debug this error",
        ]:
            result = detector.detect(user_text=text)
            assert result.mode == "development", (
                f"Expected development for: {text}"
            )

    def test_mode_detector_detects_home_from_evening_hour(self):
        from src.personality.mode_detection import ModeDetector
        detector = ModeDetector()
        result = detector.detect(user_text="what's on my list", hour=21)
        assert result.mode == "home"

    def test_mode_detector_detects_home_from_early_morning(self):
        from src.personality.mode_detection import ModeDetector
        detector = ModeDetector()
        result = detector.detect(user_text="good morning", hour=6)
        assert result.mode == "home"

    def test_mode_detector_business_hours_with_neutral_text(self):
        """During business hours with no strong signals, default home."""
        from src.personality.mode_detection import ModeDetector
        detector = ModeDetector()
        result = detector.detect(user_text="hello", hour=10)
        assert result.mode == "home"

    def test_mode_detector_recent_capabilities_influence_mode(self):
        from src.personality.mode_detection import ModeDetector
        detector = ModeDetector()
        # Cap 65 = Shopify → business
        result = detector.detect(recent_capabilities=[65, 65, 56])
        assert result.mode == "business"

    def test_mode_detector_reason_is_human_readable(self):
        from src.personality.mode_detection import ModeDetector
        detector = ModeDetector()
        result = detector.detect(user_text="shopify stats")
        assert isinstance(result.reason, str)
        assert len(result.reason) > 5


# ---------------------------------------------------------------------------
# Import boundary
# ---------------------------------------------------------------------------

class TestModeDetectorImportBoundary:

    def test_mode_detector_has_no_governance_imports(self):
        source_path = (
            Path(__file__).resolve().parents[2]
            / "src" / "personality" / "mode_detection.py"
        )
        assert source_path.exists(), f"Source file not found: {source_path}"
        source = source_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                module = ""
                if isinstance(node, ast.ImportFrom) and node.module:
                    module = node.module
                elif isinstance(node, ast.Import):
                    module = ".".join(
                        alias.name for alias in node.names
                    )
                module_lower = module.lower()
                assert "governor" not in module_lower, (
                    f"Governance import found: {module}"
                )
                assert "executor" not in module_lower, (
                    f"Executor import found: {module}"
                )
                assert "ledger" not in module_lower, (
                    f"Ledger import found: {module}"
                )
                assert "network_mediator" not in module_lower, (
                    f"NetworkMediator import found: {module}"
                )

    def test_mode_detector_has_no_capability_dispatch(self):
        source_path = (
            Path(__file__).resolve().parents[2]
            / "src" / "personality" / "mode_detection.py"
        )
        source = source_path.read_text(encoding="utf-8")
        assert "capability_registry" not in source.lower()
        assert "execute_boundary" not in source.lower()
        assert "invoke" not in source.lower() or "invocation" not in source.lower()

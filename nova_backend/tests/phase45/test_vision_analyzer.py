from __future__ import annotations

from src.perception.vision_analyzer import VisionAnalyzer


def test_vision_analyzer_interprets_missing_python_module_error():
    analyzer = VisionAnalyzer()
    result = analyzer.analyze(
        image_path="capture.png",
        ocr_text="Traceback... ModuleNotFoundError: No module named 'requests'",
        context_snapshot={"system": {"os": "Windows"}},
        user_query="what is this error",
    )
    assert "pip install requests" in result["summary"]
    assert result.get("signals", {}).get("diagnostic") == "module_not_found"
    assert float(result.get("confidence") or 0) >= 0.8


def test_vision_analyzer_provides_python_download_guidance_for_windows():
    analyzer = VisionAnalyzer()
    result = analyzer.analyze(
        image_path="capture.png",
        ocr_text="Download Python for Windows. Windows installer (64-bit).",
        context_snapshot={
            "browser": {"page_title": "Python Downloads", "url": "https://www.python.org/downloads/"},
            "system": {"os": "Windows 11"},
        },
        working_context={"task_type": "software_install"},
        user_query="which one should i download",
    )
    assert "Windows installer (64-bit)" in result["summary"]
    assert result.get("signals", {}).get("diagnostic") == "python_download_guidance"
    assert result.get("next_steps")


def test_vision_analyzer_summarizes_general_landing_page_context():
    analyzer = VisionAnalyzer()
    result = analyzer.analyze(
        image_path="capture.png",
        ocr_text="Mobile Bar Booking Pricing Contact Book Now Learn More",
        context_snapshot={
            "browser": {"page_title": "Insight Mobile Bar", "url": "https://example.com"},
            "system": {"os": "Windows 11"},
        },
        user_query="what matters most here",
    )

    assert result.get("page_kind") == "landing_page"
    assert "what matters here" in result["summary"].lower()
    assert result.get("key_actions")
    assert result.get("next_steps")
    assert result.get("follow_up_prompts")
